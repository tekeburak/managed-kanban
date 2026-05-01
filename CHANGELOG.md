# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
once it ships a 1.0.0.

## [Unreleased]

### Added
- Keyboard shortcuts for global navigation: `1`–`4` switches between
  Board / Sessions / Memory Store / Settings, and `/` focuses the top
  search input. Shortcuts are suppressed while the user is typing in any
  form field so they don't hijack textarea input.

## [0.1.0] - 2026-05-01

Initial scaffold.

### Added
- FastAPI backend on `:8000` exposing:
  - `GET /api/tickets`, `GET /api/tickets/{id}`,
    `POST /api/tickets/{id}/move`, `GET /api/tickets/{id}/stream` (SSE)
  - `GET /api/sessions` — every Managed Agents session ever launched
  - `GET/PUT /api/memory` — standing notes prepended to ticket prompts
  - `GET /api/settings` — agent + environment IDs, model, system prompt
- One-time `python -m app.agent_setup` that creates the Anthropic Agent +
  Environment and caches their IDs in `.env`. Idempotent; reuses an
  existing agent or environment if already configured.
- React + Vite + Tailwind frontend with:
  - Drag-and-drop kanban (Backlog, In Progress, Review, Done) via
    `@dnd-kit/core`
  - Live ticket card streaming via SSE — status pill, score widget,
    scrollable log, session ID
  - Sessions view with live-polled table of every session
  - Memory Store with notes editor that round-trips to backend
  - Settings view exposing the bound Anthropic resources
  - Search bar that filters Board and Sessions
- `Makefile` with one-liner targets: `install`, `setup`, `backend`,
  `frontend`, `build`, `prod`, `fmt`, `lint`, `reset`, `clean`.
- `uv` for backend dependency management; `npm` for frontend.
- README, CONTRIBUTING, MIT LICENSE.

### Architectural notes
- The agent's `STATUS:` and `SCORE:` output protocol drives the active
  card's pill and score widget. This is prompt-engineered, not enforced
  by an MCP server. A future iteration can swap in a real MCP control
  server without changing the frontend.
- All state is in-memory; a backend restart wipes session and memory
  history. Suitable for demos; swap in SQLite for persistence.
