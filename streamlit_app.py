"""Streamlit port of managed-kanban.

Reuses the existing `backend/app/*` package (store, models, managed_agents)
and renders a drag-and-drop kanban with `streamlit-sortables`. A dedicated
asyncio loop runs in a background thread so Anthropic Managed Agents
sessions can stream events while Streamlit reruns the script on user input.
"""
from __future__ import annotations

import asyncio
import os
import sys
import threading
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

# Make `from app.* import ...` work without installing the backend package.
_BACKEND = Path(__file__).resolve().parent / "backend"
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))


def _hydrate_env_from_secrets() -> None:
    """Copy known keys from st.secrets into os.environ.

    Anthropic SDK reads ANTHROPIC_API_KEY from the environment, and our
    backend modules read MANAGED_AGENT_ID / MANAGED_ENVIRONMENT_ID the same
    way. st.secrets is a dict-like that errors on missing keys, so we guard.
    """
    for key in ("ANTHROPIC_API_KEY", "MANAGED_AGENT_ID", "MANAGED_ENVIRONMENT_ID"):
        try:
            value = st.secrets.get(key)
        except (FileNotFoundError, KeyError):
            value = None
        if value and not os.environ.get(key):
            os.environ[key] = str(value)


_hydrate_env_from_secrets()

from app.agent_bootstrap import ensure_agent_and_environment  # noqa: E402
from app.agent_setup import SYSTEM_PROMPT  # noqa: E402
from app.managed_agents import run_session_for_ticket  # noqa: E402
from app.models import Column, LogEntry, Ticket  # noqa: E402
from app.store import store  # noqa: E402


# ---------------------------------------------------------------------------
# Background asyncio loop
# ---------------------------------------------------------------------------


@st.cache_resource
def _get_loop() -> asyncio.AbstractEventLoop:
    loop = asyncio.new_event_loop()
    threading.Thread(target=loop.run_forever, daemon=True, name="kanban-loop").start()
    return loop


def _run_coro_sync(coro, *, timeout: float = 10.0):
    return asyncio.run_coroutine_threadsafe(coro, _get_loop()).result(timeout=timeout)


def _schedule(coro) -> None:
    asyncio.run_coroutine_threadsafe(coro, _get_loop())


# ---------------------------------------------------------------------------
# Session orchestration
# ---------------------------------------------------------------------------


async def _safe_run_session(ticket_id: str) -> None:
    try:
        await run_session_for_ticket(ticket_id)
    except Exception as exc:  # surface to the UI; don't crash the loop
        await store.append_log(
            ticket_id, LogEntry(kind="system", text=f"Session failed: {exc}")
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


async def _reset_and_launch(ticket_id: str) -> None:
    await store.update(
        ticket_id,
        lambda t: (
            setattr(t, "column", Column.IN_PROGRESS),
            setattr(t, "started_at", datetime.now(timezone.utc)),
            setattr(t, "finished_at", None),
            setattr(t, "session_id", None),
            setattr(t, "status_pill", None),
            setattr(t, "score_before", None),
            setattr(t, "score_after", None),
            t.log.clear(),
        ),
    )


# ---------------------------------------------------------------------------
# Streamlit page
# ---------------------------------------------------------------------------

st.set_page_config(page_title="managed-kanban", layout="wide", page_icon=None)

st.title("managed-kanban")
st.caption(
    "Drag a ticket into **In Progress** to spin up an Anthropic Managed Agents "
    "session. Updates stream into the active card live."
)


# Bail early with a friendly message if the API key is missing. The rest of
# the page would just throw on first agent action otherwise.
if not os.environ.get("ANTHROPIC_API_KEY"):
    st.error(
        "ANTHROPIC_API_KEY is not configured. On Streamlit Cloud, set it under "
        "**Settings → Secrets** as `ANTHROPIC_API_KEY = \"sk-ant-...\"`. Locally, "
        "put it in `.streamlit/secrets.toml` or export it before launch."
    )
    st.stop()


# Lazy create the Agent + Environment on first run. Cached for the life of
# the Streamlit process so we do not recreate on every rerun.
@st.cache_resource(show_spinner="Provisioning Anthropic agent + environment...")
def _bootstrap() -> tuple[str, str]:
    return ensure_agent_and_environment()


try:
    AGENT_ID, ENVIRONMENT_ID = _bootstrap()
except Exception as exc:
    st.error(f"Failed to provision Anthropic resources: {exc}")
    st.stop()


# ---------------------------------------------------------------------------
# Sidebar: settings, memory, sessions
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("Settings")
    st.text_input("Agent ID", value=AGENT_ID, disabled=True)
    st.text_input("Environment ID", value=ENVIRONMENT_ID, disabled=True)
    st.text_input("Model", value="claude-opus-4-7", disabled=True)
    with st.expander("System prompt", expanded=False):
        st.code(SYSTEM_PROMPT, language="markdown")

    st.divider()
    st.header("Memory notes")
    notes_value = st.text_area(
        "Standing notes prepended to every ticket run",
        value=store.get_memory_notes(),
        height=140,
        label_visibility="collapsed",
    )
    if st.button("Save memory", use_container_width=True):
        store.set_memory_notes(notes_value)
        st.toast("Memory saved")

    st.divider()
    st.header("Sessions")
    sessions = store.list_sessions()
    if not sessions:
        st.caption("No sessions yet.")
    for s in sessions[:20]:
        status_color = {"running": "blue", "completed": "green", "failed": "red"}.get(
            s.status.value, "gray"
        )
        st.markdown(
            f":{status_color}[**{s.status.value}**] · {s.ticket_title}  \n"
            f"`{s.id}` · tools: {s.tool_calls} · entries: {s.log_entries}"
        )


# ---------------------------------------------------------------------------
# Kanban (drag-and-drop via streamlit-sortables)
# ---------------------------------------------------------------------------

try:
    from streamlit_sortables import sort_items
except Exception as exc:
    st.error(
        "The `streamlit-sortables` package is not installed. Run "
        "`pip install streamlit-sortables` (or rely on requirements.txt). "
        f"Import error: {exc}"
    )
    st.stop()


COLUMN_ORDER: list[tuple[Column, str]] = [
    (Column.BACKLOG, "Backlog"),
    (Column.IN_PROGRESS, "In Progress"),
    (Column.REVIEW, "Review"),
    (Column.DONE, "Done"),
]
HEADER_TO_COLUMN = {h: c for c, h in COLUMN_ORDER}


def _label(t: Ticket) -> str:
    return f"{t.id} — {t.title}  [{t.priority.value}]"


def _label_to_id(label: str) -> str:
    return label.split(" — ", 1)[0]


tickets = store.list()
by_id = {t.id: t for t in tickets}

initial_state = [
    {
        "header": header,
        "items": [_label(t) for t in tickets if t.column == col],
    }
    for col, header in COLUMN_ORDER
]

# A unique key tied to the current placement so the sortable widget is
# re-rendered after we move tickets programmatically (e.g. auto-move to
# Review when a session ends). Without this, the widget would keep showing
# stale columns until the user interacted again.
placement_key = "|".join(f"{t.id}:{t.column.value}" for t in tickets)
sort_key = f"kanban::{placement_key}"

new_state = sort_items(
    initial_state,
    multi_containers=True,
    direction="horizontal",
    key=sort_key,
)

# Diff the returned state against the store and propagate any moves.
new_columns: dict[str, Column] = {}
for entry in new_state:
    col = HEADER_TO_COLUMN.get(entry.get("header"))
    if col is None:
        continue
    for label in entry.get("items", []):
        new_columns[_label_to_id(label)] = col

for tid, new_col in new_columns.items():
    current = by_id.get(tid)
    if current is None or current.column == new_col:
        continue
    if new_col == Column.IN_PROGRESS:
        _run_coro_sync(_reset_and_launch(tid))
        _schedule(_safe_run_session(tid))
    else:
        _run_coro_sync(store.move(tid, new_col))


# ---------------------------------------------------------------------------
# Active / recent ticket detail panel
# ---------------------------------------------------------------------------

st.divider()

tickets = store.list()  # refresh after any moves above
focus = next(
    (t for t in tickets if t.column == Column.IN_PROGRESS),
    next((t for t in tickets if t.column == Column.REVIEW), None),
)

KIND_LABELS = {
    "status": "STATUS",
    "tool_use": "TOOL",
    "agent_text": "AGENT",
    "score": "SCORE",
    "system": "SYSTEM",
}

if focus is None:
    st.info("No ticket in progress. Drag one into **In Progress** above to start.")
else:
    with st.container(border=True):
        head_cols = st.columns([5, 2, 2])
        head_cols[0].markdown(f"### {focus.id} — {focus.title}")
        if focus.status_pill:
            head_cols[1].markdown(f"**Status**  \n:blue[{focus.status_pill}]")
        else:
            head_cols[1].markdown(f"**Column**  \n{focus.column.value}")
        if focus.score_after is not None:
            delta = (
                focus.score_after - focus.score_before
                if focus.score_before is not None
                else None
            )
            head_cols[2].metric("Score", focus.score_after, delta=delta)

        st.caption(focus.description)

        st.markdown("**Activity log**")
        if not focus.log:
            st.caption("Waiting for the first event...")
        for entry in focus.log[-200:]:
            tag = KIND_LABELS.get(entry.kind, entry.kind.upper())
            st.markdown(f"`{tag}` {entry.text}")


# ---------------------------------------------------------------------------
# Auto-refresh while any session is running so the log streams live.
# ---------------------------------------------------------------------------

any_running = any(t.column == Column.IN_PROGRESS for t in tickets)
if any_running:
    try:
        from streamlit_autorefresh import st_autorefresh

        st_autorefresh(interval=1500, key="kanban-autorefresh")
    except Exception:
        # Soft-fail: the user can still hit "Rerun" manually.
        st.caption("(install `streamlit-autorefresh` for live updates)")
