from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class Column(str, Enum):
    BACKLOG = "backlog"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class LogEntry(BaseModel):
    kind: Literal["status", "tool_use", "agent_text", "score", "system"]
    text: str
    at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Ticket(BaseModel):
    id: str
    title: str
    description: str
    priority: Priority
    tag: str
    column: Column = Column.BACKLOG

    session_id: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None

    status_pill: str | None = None
    score_before: int | None = None
    score_after: int | None = None
    log: list[LogEntry] = Field(default_factory=list)


class MoveRequest(BaseModel):
    column: Column


class SessionStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class SessionInfo(BaseModel):
    id: str
    ticket_id: str
    ticket_title: str
    status: SessionStatus
    started_at: datetime
    finished_at: datetime | None = None
    tool_calls: int = 0
    log_entries: int = 0


class MemoryNotes(BaseModel):
    notes: str = ""


class Settings(BaseModel):
    agent_id: str | None
    environment_id: str | None
    model: str
    system_prompt: str
    total_sessions: int
    active_sessions: int
