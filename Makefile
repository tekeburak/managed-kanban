.PHONY: help install setup backend frontend build prod fmt lint clean reset

help:  ## Show this help
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install:  ## Install backend (uv) and frontend (npm) deps
	cd backend && uv sync
	cd frontend && npm install

setup:  ## One-time: create the Anthropic Agent + Environment, save IDs to .env
	cd backend && uv run python -m app.agent_setup

backend:  ## Run the FastAPI dev server on :8000 (with reload)
	cd backend && uv run uvicorn app.main:app --port 8000 --reload

frontend:  ## Run the Vite dev server on :5173
	cd frontend && npm run dev

build:  ## Build the production frontend bundle into frontend/dist
	cd frontend && npm run build

prod: build  ## Build frontend, then serve everything from FastAPI on :8000
	cd backend && uv run uvicorn app.main:app --port 8000

fmt:  ## Format Python with ruff
	cd backend && uv run ruff format app

lint:  ## Lint Python with ruff and type-check the frontend
	cd backend && uv run ruff check app
	cd frontend && npm run lint

clean:  ## Remove build artifacts and caches
	rm -rf backend/.venv backend/.ruff_cache
	find backend -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf frontend/node_modules frontend/dist frontend/.vite

reset:  ## Wipe local Anthropic resource IDs from .env (forces re-setup)
	@if [ -f .env ]; then \
		sed -i.bak '/^MANAGED_AGENT_ID=/d;/^MANAGED_ENVIRONMENT_ID=/d' .env && rm .env.bak; \
		echo "Cleared MANAGED_AGENT_ID and MANAGED_ENVIRONMENT_ID from .env"; \
	else \
		echo "No .env file found"; \
	fi
