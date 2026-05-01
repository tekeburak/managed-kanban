from __future__ import annotations

import asyncio
from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timezone

from app.models import Column, LogEntry, SessionInfo, SessionStatus, Ticket
from app.seed import SEED_TICKETS


class TicketStore:
    """In-memory store with per-ticket fan-out for SSE subscribers.

    Demo-grade: a process restart loses all session state. Swap in a database
    if you ever care about persistence.
    """

    def __init__(self) -> None:
        self._tickets: dict[str, Ticket] = {t.id: deepcopy(t) for t in SEED_TICKETS}
        self._subscribers: dict[str, list[asyncio.Queue[Ticket]]] = defaultdict(list)
        self._sessions: dict[str, SessionInfo] = {}
        self._memory_notes: str = ""
        self._lock = asyncio.Lock()

    def list(self) -> list[Ticket]:
        return [deepcopy(t) for t in self._tickets.values()]

    def get(self, ticket_id: str) -> Ticket | None:
        ticket = self._tickets.get(ticket_id)
        return deepcopy(ticket) if ticket else None

    async def update(self, ticket_id: str, mutate) -> Ticket:
        async with self._lock:
            ticket = self._tickets[ticket_id]
            mutate(ticket)
            snapshot = deepcopy(ticket)
        await self._broadcast(ticket_id, snapshot)
        return snapshot

    async def append_log(self, ticket_id: str, entry: LogEntry) -> Ticket:
        return await self.update(
            ticket_id,
            lambda t: t.log.append(entry),
        )

    async def move(self, ticket_id: str, column: Column) -> Ticket:
        return await self.update(
            ticket_id,
            lambda t: setattr(t, "column", column),
        )

    def subscribe(self, ticket_id: str) -> asyncio.Queue[Ticket]:
        queue: asyncio.Queue[Ticket] = asyncio.Queue(maxsize=256)
        self._subscribers[ticket_id].append(queue)
        return queue

    def unsubscribe(self, ticket_id: str, queue: asyncio.Queue[Ticket]) -> None:
        if queue in self._subscribers[ticket_id]:
            self._subscribers[ticket_id].remove(queue)

    async def _broadcast(self, ticket_id: str, snapshot: Ticket) -> None:
        for queue in list(self._subscribers[ticket_id]):
            try:
                queue.put_nowait(snapshot)
            except asyncio.QueueFull:
                # Slow subscriber; drop and let them resync via GET.
                pass

    # --- session history ---------------------------------------------------

    def record_session(self, *, session_id: str, ticket_id: str) -> None:
        ticket = self._tickets.get(ticket_id)
        title = ticket.title if ticket else ticket_id
        self._sessions[session_id] = SessionInfo(
            id=session_id,
            ticket_id=ticket_id,
            ticket_title=title,
            status=SessionStatus.RUNNING,
            started_at=datetime.now(timezone.utc),
        )

    def increment_session_metric(self, session_id: str, *, tool: bool = False) -> None:
        info = self._sessions.get(session_id)
        if info is None:
            return
        info.log_entries += 1
        if tool:
            info.tool_calls += 1

    def finalize_session(self, session_id: str, *, failed: bool = False) -> None:
        info = self._sessions.get(session_id)
        if info is None:
            return
        info.status = SessionStatus.FAILED if failed else SessionStatus.COMPLETED
        info.finished_at = datetime.now(timezone.utc)

    def list_sessions(self) -> list[SessionInfo]:
        # Newest first
        return sorted(
            (deepcopy(s) for s in self._sessions.values()),
            key=lambda s: s.started_at,
            reverse=True,
        )

    # --- memory notes ------------------------------------------------------

    def get_memory_notes(self) -> str:
        return self._memory_notes

    def set_memory_notes(self, notes: str) -> None:
        self._memory_notes = notes


store = TicketStore()
