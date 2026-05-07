# syntax=docker/dockerfile:1.6

# --- Stage 1: build the React frontend ---
FROM node:20-alpine AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# --- Stage 2: Python runtime serving FastAPI + built frontend ---
FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install backend dependencies. We install directly from the deps list in
# pyproject.toml using pip rather than uv to keep the image small.
COPY backend/pyproject.toml backend/README.md* ./backend/
RUN pip install --upgrade pip && \
    pip install \
        "fastapi>=0.115" \
        "uvicorn[standard]>=0.32" \
        "anthropic>=0.40" \
        "python-dotenv>=1.0" \
        "sse-starlette>=2.1" \
        "pydantic>=2.9"

# Copy backend source.
COPY backend/ ./backend/

# Copy built frontend from stage 1 into the location main.py expects:
# `<repo>/frontend/dist` relative to `backend/app/main.py`.
COPY --from=frontend /app/frontend/dist ./frontend/dist

WORKDIR /app/backend
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
