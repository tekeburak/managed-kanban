#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

echo "[setup] installing frontend deps..."
(cd frontend && npm install && npm run build)

echo "[setup] installing backend deps..."
(cd backend && pip install -e .)

echo "[setup] done."
