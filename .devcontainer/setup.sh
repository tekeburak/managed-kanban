#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "[setup] installing frontend deps..."
(cd frontend && npm install && npm run build)

echo "[setup] installing backend deps..."
(cd backend && pip install -e .)

# Roll the latest SYSTEM_PROMPT out to the live agent so a fresh codespace
# never runs with a stale prompt. No-op if MANAGED_AGENT_ID isn't set.
if [ -n "${MANAGED_AGENT_ID:-}" ] && [ -n "${ANTHROPIC_API_KEY:-}" ]; then
  echo "[setup] updating live agent system prompt..."
  (cd backend && python -m app.update_agent) || echo "[setup] agent update failed (non-fatal)"
else
  echo "[setup] skipping agent prompt update (MANAGED_AGENT_ID or ANTHROPIC_API_KEY not set)"
fi

echo "[setup] done."
