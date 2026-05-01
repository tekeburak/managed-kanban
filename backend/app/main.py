from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse

from app.agent_setup import SYSTEM_PROMPT
from app.managed_agents import launch_session_task
from app.models import (
    Column,
    MemoryNotes,
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

    snapshot = await store.move(ticket_id, column)

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
def get_memory() -> MemoryNotes:
    return MemoryNotes(notes=store.get_memory_notes())


@app.put("/api/memory")
def put_memory(payload: MemoryNotes) -> MemoryNotes:
    store.set_memory_notes(payload.notes)
    return MemoryNotes(notes=store.get_memory_notes())


@app.get("/api/settings")
def get_settings() -> Settings:
    sessions = store.list_sessions()
    return Settings(
        agent_id=os.environ.get("MANAGED_AGENT_ID"),
        environment_id=os.environ.get("MANAGED_ENVIRONMENT_ID"),
        model="claude-opus-4-7",
        system_prompt=SYSTEM_PROMPT,
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
