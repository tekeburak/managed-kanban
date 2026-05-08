#!/usr/bin/env bash
cd "$(dirname "$0")/../backend"

if pgrep -f "uvicorn app.main:app" >/dev/null 2>&1; then
  echo "[start] uvicorn already running"
  exit 0
fi

mkdir -p /tmp/managed-kanban
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 \
  > /tmp/managed-kanban/uvicorn.log 2>&1 &

echo "[start] uvicorn started on port 8000 (logs: /tmp/managed-kanban/uvicorn.log)"
