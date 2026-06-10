from __future__ import annotations

import asyncio
import json
import os
import re
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse

from app.agent_setup import SYSTEM_PROMPT
from app.managed_agents import cancel_session_task, launch_session_task
from app.models import (
    Column,
    LogEntry,
    MemoryItem,
    MemoryNotes,
    MemoryState,
    SessionInfo,
    SessionStatus,
    Settings,
    Ticket,
)
from app.store import store

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

app = FastAPI(title="managed-kanban", version="0.1.0")

# Vite dev server origin during development; not required in prod since the
# built frontend is served from this same FastAPI process.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/tickets")
def list_tickets() -> list[Ticket]:
    return store.list()


@app.get("/api/tickets/{ticket_id}")
def get_ticket(ticket_id: str) -> Ticket:
    ticket = store.get(ticket_id)
    if ticket is None:
        raise HTTPException(404, "ticket not found")
    return ticket


@app.post("/api/tickets/{ticket_id}/move")
async def move_ticket(ticket_id: str, payload: dict) -> Ticket:
    target = payload.get("column")
    if target not in {c.value for c in Column}:
        raise HTTPException(400, "invalid column")

    column = Column(target)
    current = store.get(ticket_id)
    if current is None:
        raise HTTPException(404, "ticket not found")

    # If the user drags an actively-running ticket out of IN_PROGRESS, cancel
    # the agent session so we stop billing tokens and don't race the auto-
    # finish update.
    if current.column == Column.IN_PROGRESS and column != Column.IN_PROGRESS:
        await cancel_session_task(ticket_id)

    snapshot = await store.move(ticket_id, column)

    # Drag from Review to Done is the human approval — fast-forward the
    # repo's main to the agent branch so Cloudflare Pages redeploys.
    if column == Column.DONE and current.column == Column.REVIEW:
        try:
            merged = await _ff_agent_branch_to_main(current)
            if merged:
                await store.append_log(
                    ticket_id,
                    LogEntry(kind="system", text=f"Merged {merged} → main."),
                )
        except Exception as exc:
            await store.append_log(
                ticket_id,
                LogEntry(kind="system", text=f"Merge failed: {exc}"),
            )

    # Drag into "In Progress" is the trigger that fires a Managed Agents
    # session. Every other transition is just a UI move.
    if column == Column.IN_PROGRESS and current.column != Column.IN_PROGRESS:
        # Reset run-specific state so a retry starts from a clean card.
        await store.update(
            ticket_id,
            lambda t: (
                setattr(t, "started_at", datetime.now(timezone.utc)),
                setattr(t, "finished_at", None),
                setattr(t, "session_id", None),
                setattr(t, "status_pill", None),
                setattr(t, "score_before", None),
                setattr(t, "score_after", None),
                setattr(t, "attempt_number", 1),
                setattr(t, "failed_attempt", None),
                t.log.clear(),
            ),
        )
        launch_session_task(ticket_id)
        # Re-read so the response reflects the cleared fields, not the
        # pre-reset snapshot we captured before the update above.
        snapshot = store.get(ticket_id) or snapshot

    return snapshot


@app.get("/api/tickets/{ticket_id}/stream")
async def stream_ticket(ticket_id: str):
    if store.get(ticket_id) is None:
        raise HTTPException(404, "ticket not found")

    async def event_source():
        # Push the current snapshot first so the client has state immediately.
        snapshot = store.get(ticket_id)
        if snapshot is not None:
            yield {"event": "ticket", "data": snapshot.model_dump_json()}

        queue = store.subscribe(ticket_id)
        try:
            while True:
                try:
                    update = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield {"event": "ticket", "data": update.model_dump_json()}
                except asyncio.TimeoutError:
                    # Comment line keeps the connection warm through proxies.
                    yield {"event": "ping", "data": json.dumps({"t": datetime.now(timezone.utc).isoformat()})}
        finally:
            store.unsubscribe(ticket_id, queue)

    return EventSourceResponse(event_source())


@app.get("/api/sessions")
def list_sessions() -> list[SessionInfo]:
    return store.list_sessions()


@app.get("/api/memory")
def get_memory() -> MemoryState:
    """Local standing notes + the agent's actual Managed Agents memories."""
    state = MemoryState(
        notes=store.get_memory_notes(),
        store_id=os.environ.get("MANAGED_MEMORY_STORE_ID"),
    )
    if not state.store_id:
        return state
    try:
        client = Anthropic()
        page = client.beta.memory_stores.memories.list(
            state.store_id,
            view="full",
            order="desc",
            limit=50,
        )
        state.memories = [
            MemoryItem(
                path=m.path,
                content=getattr(m, "content", None),
                updated_at=getattr(m, "updated_at", None),
            )
            for m in page
            if getattr(m, "type", None) == "memory"
        ]
    except Exception as exc:
        state.error = f"could not list memories: {exc}"
    return state


@app.put("/api/memory")
def put_memory(payload: MemoryNotes) -> MemoryNotes:
    store.set_memory_notes(payload.notes)
    return MemoryNotes(notes=store.get_memory_notes())


_GH_REPO_RE = re.compile(
    r"https?://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+?)(?:\.git)?(?:/|\s|$)",
    re.IGNORECASE,
)


def _extract_owner_repo(text: str) -> tuple[str, str] | None:
    m = _GH_REPO_RE.search(text)
    if not m:
        return None
    return m.group(1), m.group(2)


async def _ff_agent_branch_to_main(ticket: Ticket) -> str | None:
    """Fast-forward main to the agent's branch for this ticket.

    Returns the branch name on success, None if there is no repo/token or
    no agent branch exists yet.
    """
    token = os.environ.get("PORTFOLIO_GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        return None
    pair = _extract_owner_repo(ticket.description)
    if not pair:
        return None
    owner, repo = pair
    branch = f"agent/{ticket.id}"

    def _api(method: str, path: str, body: dict | None = None) -> dict:
        req = urllib.request.Request(
            f"https://api.github.com{path}",
            method=method,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            data=json.dumps(body).encode() if body else None,
        )
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read() or b"{}")

    def _do_merge() -> str:
        # Look up the branch SHA — raises 404 if the agent didn't push.
        branch_info = _api("GET", f"/repos/{owner}/{repo}/branches/{branch}")
        sha = branch_info["commit"]["sha"]
        # Fast-forward main to that SHA.
        _api(
            "PATCH",
            f"/repos/{owner}/{repo}/git/refs/heads/main",
            {"sha": sha, "force": False},
        )
        return branch

    return await asyncio.to_thread(_do_merge)


_AGENT_CACHE: dict[str, tuple[float, str, str]] = {}
_AGENT_TTL = 30.0


def _fetch_agent_meta(agent_id: str) -> tuple[str, str]:
    """Return (model, system_prompt) for the agent, cached for _AGENT_TTL seconds."""
    now = time.monotonic()
    cached = _AGENT_CACHE.get(agent_id)
    if cached and now - cached[0] < _AGENT_TTL:
        return cached[1], cached[2]

    client = Anthropic()
    agent = client.beta.agents.retrieve(agent_id)
    # `agent.model` is a ModelConfig object whose `.id` is the actual model name.
    model_obj = getattr(agent, "model", None)
    model = getattr(model_obj, "id", "") if model_obj is not None else ""
    system = getattr(agent, "system", None) or SYSTEM_PROMPT
    _AGENT_CACHE[agent_id] = (now, model, system)
    return model, system


@app.get("/api/settings")
def get_settings() -> Settings:
    sessions = store.list_sessions()
    agent_id = os.environ.get("MANAGED_AGENT_ID")
    model = ""
    system_prompt = SYSTEM_PROMPT
    if agent_id:
        try:
            model, system_prompt = _fetch_agent_meta(agent_id)
        except Exception:
            # Fall back to empty model and the static prompt if the API is
            # unreachable; settings should still render.
            pass
    return Settings(
        agent_id=agent_id,
        environment_id=os.environ.get("MANAGED_ENVIRONMENT_ID"),
        model=model,
        system_prompt=system_prompt,
        total_sessions=len(sessions),
        active_sessions=sum(1 for s in sessions if s.status == SessionStatus.RUNNING),
    )


# Serve the built frontend in production. In dev, Vite runs on :5173 and
# proxies /api to this server, so this block is a no-op when dist/ is absent.
_FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if _FRONTEND_DIST.exists():
    app.mount(
        "/assets",
        StaticFiles(directory=_FRONTEND_DIST / "assets"),
        name="assets",
    )

    @app.get("/{full_path:path}")
    def spa_fallback(full_path: str):
        # Anything not handled by /api or /assets falls back to index.html
        # so client-side routing works.
        index = _FRONTEND_DIST / "index.html"
        if index.exists():
            return FileResponse(index)
        raise HTTPException(404, "frontend not built")
