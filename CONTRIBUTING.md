# Contributing to managed-kanban

Thanks for poking around. This is a demo project, so the bar is "stays
readable" rather than "production-grade." A few notes to make changes painless.

## Local setup

See [README.md](./README.md#quick-start). Short version:

```bash
cp .env.example .env   # add your ANTHROPIC_API_KEY
make install
make setup
make backend           # in one terminal
make frontend          # in another
```

## Project layout

| Path | What lives here |
|---|---|
| `backend/app/main.py` | FastAPI app — HTTP routes and SSE relay |
| `backend/app/managed_agents.py` | Anthropic SDK wrapper, `agent.message` parsing, fire-and-forget session task |
| `backend/app/agent_setup.py` | One-time creation of the Agent + Environment in your Anthropic account |
| `backend/app/store.py` | In-memory ticket store with per-ticket fan-out queues |
| `backend/app/seed.py` | The three demo tickets |
| `backend/app/models.py` | Pydantic models shared by the routes and store |
| `frontend/src/components/Board.tsx` | DndContext, optimistic moves, per-ticket SSE subscribe |
| `frontend/src/components/TicketCard.tsx` | Draggable card; dispatches to idle vs active body |
| `frontend/src/components/ActiveCardBody.tsx` | Status pill, score widget, scrollable log |
| `frontend/src/lib/api.ts` | Tiny fetch + EventSource client |

## How to add a new ticket type

1. Append a `Ticket(...)` to `backend/app/seed.py`.
2. (Optional) Add a tag color in `frontend/src/components/TicketCard.tsx` →
   `TAG_COLORS`.
3. Restart the backend. Tickets are loaded into the in-memory store on startup.

The agent works whatever description you give it — there's no
ticket-type-specific code path. If your task needs different tools or extra
packages installed in the environment, see the next section.

## How to give the agent more capabilities

The agent receives the toolset declared in `agent_setup.py`:

```python
tools=[{"type": "agent_toolset_20260401"}]
```

That bundle includes `bash`, `read`/`write`/`edit`/`glob`/`grep`, web search,
and web fetch — enough for the three seed tickets.

To add **custom MCP tools** (e.g. a real "update ticket status" tool instead
of the prompt-engineered `STATUS:` lines), expose an HTTP MCP server reachable
from Anthropic's cloud and reference it in the agent's tool list. See
[Tools — Claude API Docs](https://platform.claude.com/docs/en/managed-agents/tools).

To **preinstall packages** in the agent's container, configure the environment
in `agent_setup.py`:

```python
client.beta.environments.create(
    name="managed-kanban-env",
    config={
        "type": "cloud",
        "networking": {"type": "unrestricted"},
        # add: "packages": {"npm": ["lighthouse"]} or similar
    },
)
```

After changing the agent or environment, run `make reset && make setup` to
force re-creation.

## Style and conventions

- **Python:** ruff is the source of truth. `make fmt` formats, `make lint`
  checks. Line length 100. Default to no comments unless the *why* is
  non-obvious.
- **TypeScript:** `tsc --noEmit` via `make lint` (no separate ESLint config —
  type checking catches the things that matter for a project this size).
- **Imports:** absolute imports inside `backend/app/` (`from app.foo import
  bar`), relative inside `frontend/src/`.
- **Comments:** describe the *why* a future reader couldn't infer from the
  code, not the *what*.

## Pull requests

Open a PR against `main` from your fork. The repo is wired up so a Managed
Agents code reviewer comments on every PR — be patient with it; it tries to be
helpful but is occasionally enthusiastic about preferences.

A good PR description includes:

- What problem this solves (or what it demonstrates)
- What you tested manually
- A screenshot or short clip if it's a UI change

## Known sharp edges

- The `STATUS:` / `SCORE:` protocol is prompt-engineered, not enforced. If the
  agent skips a `STATUS:` line, the pill stays on the previous value. The fix
  is to wire a real MCP server (see above) — patches welcome.
- The ticket store is in-memory; a process restart wipes session state. Swap
  to SQLite if persistence matters to you.
- Sessions are launched via `asyncio.create_task` — there is no graceful
  shutdown that waits for them to drain. For a demo this is fine; for a long-
  running deployment, hook into FastAPI's `lifespan` to track and cancel
  outstanding tasks.

## License

By contributing, you agree your contributions are licensed under the MIT
License (see [LICENSE](./LICENSE)).
