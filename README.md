# managed-kanban

A Kanban board where dragging a ticket into **In Progress** spins up an
[Anthropic Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview)
session that works the ticket autonomously and streams its progress back to the
card in real time.

Inspired by Anthropic's Managed Agents launch demo and the broader
[vibe-kanban](https://github.com/BloopAI/vibe-kanban) family of agent kanbans —
but stripped to a single, hosted-only integration so the wiring is easy to read.

## Architecture

```
Browser (React + dnd-kit)
   │
   │  drag → POST /api/tickets/:id/move
   ▼
FastAPI on :8000
   │
   │  client.beta.sessions.create(agent, environment)
   │  client.beta.sessions.events.send(user.message)
   │  client.beta.sessions.events.stream(...)
   ▼
Anthropic Managed Agents (hosted runtime)
   │
   │  agent.message / agent.tool_use / session.status_idle
   ▼
FastAPI relays via SSE → Browser updates the card live
```

The agent emits `STATUS:` and `SCORE:` lines in its prose. The backend parses
them out of `agent.message` events to drive the colored status pill and the
score widget on the active card. Built-in tool calls (`bash`, `edit`, etc.) are
surfaced automatically as "Running: <tool>" via the `agent.tool_use` events.

When the session emits `session.status_idle`, the card auto-moves from **In
Progress** to **Review** for human inspection.

## Repository layout

```
managed-kanban/
├── backend/
│   ├── pyproject.toml
│   └── app/
│       ├── main.py              # FastAPI: routes, SSE relay, static SPA
│       ├── managed_agents.py    # Anthropic SDK wrapper, event handlers
│       ├── agent_setup.py       # one-time Agent + Environment creation
│       ├── store.py             # in-memory ticket store w/ per-ticket fan-out
│       ├── models.py            # Pydantic models
│       └── seed.py              # the three demo tickets
└── frontend/
    ├── package.json
    ├── vite.config.ts           # proxies /api → :8000 in dev
    └── src/
        ├── App.tsx
        ├── components/          # Board, Column, TicketCard, ActiveCardBody, Sidebar, Header
        └── lib/                 # api client, types
```

## Prerequisites

- [`uv`](https://docs.astral.sh/uv/) (Python package manager) — `brew install uv`
- Node 18+
- An Anthropic API key with Managed Agents access (enabled by default for all
  API accounts as of the `managed-agents-2026-04-01` beta)

## Quick start

```bash
cp .env.example .env                # then put your ANTHROPIC_API_KEY in .env
make install                        # installs backend (uv sync) + frontend (npm)
make setup                          # one-time: creates the Agent + Environment in your Anthropic account
```

Then in two terminals:

```bash
make backend     # FastAPI on :8000 with reload
make frontend    # Vite dev server on :5173
```

Open http://localhost:5173. Drag a ticket from **Backlog** to **In Progress** —
a Managed Agents session is created, the card morphs to its active state, and
the agent's tool calls / narration / scores stream in live.

## Production-style single-port run

```bash
make prod        # builds the frontend, then serves everything from FastAPI on :8000
# open http://localhost:8000
```

## Keyboard shortcuts

| Key | Action |
|---|---|
| `1` | Switch to Board |
| `2` | Switch to Sessions |
| `3` | Switch to Memory Store |
| `4` | Switch to Settings |
| `/` | Focus the search input |

Shortcuts are suppressed while you're typing in a form field.

## All Make targets

```bash
make help        # show every target with a one-line description
make install     # install backend + frontend deps
make setup       # one-time: create Agent + Environment, save IDs to .env
make backend     # run FastAPI dev server (:8000, reload)
make frontend    # run Vite dev server (:5173)
make build       # build frontend bundle into frontend/dist
make prod        # build + serve from FastAPI on :8000
make fmt         # ruff format the backend
make lint        # ruff check + frontend tsc --noEmit
make reset       # forget the Anthropic resource IDs (forces re-setup)
make clean       # nuke .venv, node_modules, caches
```

## The three seed tickets

| ID | Title | Showcases |
|---|---|---|
| TICKET-1 | Optimize website performance | bash + edit tools, self-grading loop, before/after Lighthouse score |
| TICKET-2 | SaaS pricing audit and weekly report | web search/fetch, file writes, persistent memory across runs |
| TICKET-3 | Incident response: API latency spike | log analysis, postmortem authoring, structured status updates |

Edit `backend/app/seed.py` to change them.

## How the agent drives the UI

The agent's system prompt (defined in `app/agent_setup.py`) instructs it to
emit two structured lines whenever appropriate:

```
STATUS: Self-grading... (Attempt 2 of 3)
SCORE: 62 -> 96
```

The backend's `managed_agents.py` extracts these from `agent.message` events
and pushes them into the ticket's status pill and score widget. Everything else
is logged as plain narration. This avoids the need to host a separate MCP
control server reachable from Anthropic's cloud — V2 can swap it in without
changing the frontend.

## Cost

Standard token rates plus **$0.08 per session-hour** of container time
([pricing reference](https://platform.claude.com/docs/en/managed-agents/overview)).
A fast demo session costs approximately nothing.

## License

MIT — see [LICENSE](./LICENSE).
