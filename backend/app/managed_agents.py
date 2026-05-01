from __future__ import annotations

import asyncio
import os
import re
from datetime import datetime, timezone
from typing import Any

from anthropic import AsyncAnthropic

from app.models import Column, LogEntry
from app.store import store

_client: AsyncAnthropic | None = None


def client() -> AsyncAnthropic:
    global _client
    if _client is None:
        _client = AsyncAnthropic()  # picks up ANTHROPIC_API_KEY from env
    return _client


def _agent_id() -> str:
    value = os.environ.get("MANAGED_AGENT_ID")
    if not value:
        raise RuntimeError(
            "MANAGED_AGENT_ID is not set. Run `python -m app.agent_setup` first."
        )
    return value


def _environment_id() -> str:
    value = os.environ.get("MANAGED_ENVIRONMENT_ID")
    if not value:
        raise RuntimeError(
            "MANAGED_ENVIRONMENT_ID is not set. Run `python -m app.agent_setup` first."
        )
    return value


# Agent system prompt asks for STATUS:/SCORE: lines so the frontend can lift
# them out of the message stream and render them as pills/widgets — without
# needing a separately-hosted MCP control server.
STATUS_RE = re.compile(r"^\s*STATUS:\s*(.+?)\s*$", re.MULTILINE)
SCORE_RE = re.compile(r"^\s*SCORE:\s*(\d+)\s*->\s*(\d+)\s*$", re.MULTILINE)


async def run_session_for_ticket(ticket_id: str) -> None:
    """Drive a Managed Agents session for a ticket and relay events to the store.

    Creates the session, sends the ticket's description as a user.message,
    streams every event back, and updates the ticket's status pill, score,
    and log as the agent works. Auto-moves the card to Review on idle.
    """
    ticket = store.get(ticket_id)
    if ticket is None:
        return

    api = client()

    session = await api.beta.sessions.create(
        agent=_agent_id(),
        environment_id=_environment_id(),
        title=f"{ticket.id}: {ticket.title}",
    )

    store.record_session(session_id=session.id, ticket_id=ticket_id)

    await store.update(
        ticket_id,
        lambda t: (
            setattr(t, "session_id", session.id),
            setattr(t, "status_pill", "Starting agent session..."),
            t.log.append(LogEntry(kind="system", text=f"Session created: {session.id}")),
        ),
    )

    notes = store.get_memory_notes().strip()
    user_text = (
        f"Standing notes / memory:\n{notes}\n\n---\n\n{ticket.description}"
        if notes
        else ticket.description
    )

    # events.stream() is an async function that returns an AsyncStream context
    # manager — hence the doubled `async with await ...`.
    async with await api.beta.sessions.events.stream(session.id) as stream:
        await api.beta.sessions.events.send(
            session.id,
            events=[
                {
                    "type": "user.message",
                    "content": [{"type": "text", "text": user_text}],
                }
            ],
        )

        async for event in stream:
            await _handle_event(ticket_id, event, session_id=session.id)
            # session.status_idle means "agent has nothing more to do" —
            # break to close the stream and proceed with auto-move-to-Review.
            # Without this, the iterator stays open until the session is
            # deleted server-side, so the card never advances.
            if getattr(event, "type", None) == "session.status_idle":
                break

    store.finalize_session(session.id)
    await store.update(
        ticket_id,
        lambda t: (
            setattr(t, "column", Column.REVIEW),
            setattr(t, "status_pill", "Awaiting human review"),
            setattr(t, "finished_at", datetime.now(timezone.utc)),
        ),
    )


async def _handle_event(ticket_id: str, event: Any, *, session_id: str) -> None:
    etype = getattr(event, "type", None)

    if etype == "agent.message":
        text = "".join(
            getattr(block, "text", "") or "" for block in getattr(event, "content", [])
        )
        if not text:
            return
        store.increment_session_metric(session_id)
        await _consume_agent_text(ticket_id, text)

    elif etype == "agent.tool_use":
        name = getattr(event, "name", "tool")
        store.increment_session_metric(session_id, tool=True)
        await store.append_log(
            ticket_id,
            LogEntry(kind="tool_use", text=f"Running: {name}"),
        )
        await store.update(
            ticket_id,
            lambda t: setattr(t, "status_pill", f"Running: {name}"),
        )

    elif etype == "session.status_idle":
        await store.append_log(
            ticket_id,
            LogEntry(kind="system", text="Agent finished."),
        )


async def _consume_agent_text(ticket_id: str, text: str) -> None:
    """Pull STATUS:/SCORE: lines out of agent text; log the rest as narration."""
    for m in STATUS_RE.finditer(text):
        pill = m.group(1)
        await store.update(
            ticket_id,
            lambda t, p=pill: (
                setattr(t, "status_pill", p),
                t.log.append(LogEntry(kind="status", text=p)),
            ),
        )

    for m in SCORE_RE.finditer(text):
        before, after = int(m.group(1)), int(m.group(2))
        await store.update(
            ticket_id,
            lambda t, b=before, a=after: (
                setattr(t, "score_before", b),
                setattr(t, "score_after", a),
                t.log.append(LogEntry(kind="score", text=f"{b} -> {a}")),
            ),
        )

    narration = STATUS_RE.sub("", text)
    narration = SCORE_RE.sub("", narration).strip()
    if narration:
        await store.append_log(
            ticket_id,
            LogEntry(kind="agent_text", text=narration),
        )


def launch_session_task(ticket_id: str) -> asyncio.Task[None]:
    """Fire-and-forget: run the session in the background.

    The HTTP request returns immediately while the long-running session
    continues to push updates into the per-ticket queue.
    """

    async def runner() -> None:
        try:
            await run_session_for_ticket(ticket_id)
        except Exception as exc:  # surface to the UI; don't crash the server
            await store.append_log(
                ticket_id,
                LogEntry(kind="system", text=f"Session failed: {exc}"),
            )
            await store.update(
                ticket_id,
                lambda t: (
                    setattr(t, "status_pill", "Session failed"),
                    setattr(t, "finished_at", datetime.now(timezone.utc)),
                ),
            )
            current = store.get(ticket_id)
            if current and current.session_id:
                store.finalize_session(current.session_id, failed=True)

    return asyncio.create_task(runner())
