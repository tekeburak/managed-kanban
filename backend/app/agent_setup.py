"""One-time setup: create the Managed Agent and Environment, save IDs to .env.

Run once after cloning:
    cd backend && python -m app.agent_setup

It is idempotent: if .env already has MANAGED_AGENT_ID and
MANAGED_ENVIRONMENT_ID, it prints them and exits without recreating.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

SYSTEM_PROMPT = """You are a senior engineer executing a single kanban ticket.

The user message IS the ticket. It tells you exactly what to do. Follow it
literally. Do not deviate, re-plan, or explore.

Speed is the priority.
* Take exactly ONE attempt. No retries, no verification reads, no
  "let me double-check" steps.
* Do not narrate analysis. Do not read files unless the ticket explicitly
  names them. Do not summarize the diff after editing.
* Do not call the memory store unless the ticket asks for it.

Git workflow:

The ticket gives you a `git clone https://x-access-token:<token>@…` URL
and the full step-by-step sequence. Run each step as a SEPARATE bash call
(the sandbox has a 5-minute per-call timeout — chaining them with && is
what was killing previous runs by cutting off the push step mid-flight).

Do NOT search for credentials. Do NOT inspect the github_repository
mount. There is no mount; the token is already in the URL the ticket
gives you. Just run the steps in order.

Push ONLY agent/<TICKET-ID>. Never push to main. A reviewer fast-forwards
main from your branch when they accept it.

Output protocol (the kanban UI parses these):
* STATUS: <max 6 words>           — emit once when starting, once before push
* SCORE: <before> -> <after>      — emit once, near the end
* Otherwise stay silent. No long narration.
"""


def main() -> int:
    load_dotenv(ENV_FILE)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY is not set.", file=sys.stderr)
        print("Copy .env.example to .env and fill it in.", file=sys.stderr)
        return 1

    agent_id = os.environ.get("MANAGED_AGENT_ID") or None
    environment_id = os.environ.get("MANAGED_ENVIRONMENT_ID") or None
    memory_store_id = os.environ.get("MANAGED_MEMORY_STORE_ID") or None

    if agent_id and environment_id and memory_store_id:
        print("Already configured. Reusing existing resources:")
        print(f"  MANAGED_AGENT_ID        = {agent_id}")
        print(f"  MANAGED_ENVIRONMENT_ID  = {environment_id}")
        print(f"  MANAGED_MEMORY_STORE_ID = {memory_store_id}")
        return 0

    client = Anthropic()

    if agent_id:
        print(f"Reusing existing agent:     {agent_id}")
    else:
        print("Creating managed-kanban agent...")
        agent = client.beta.agents.create(
            name="managed-kanban",
            model="claude-opus-4-7",
            system=SYSTEM_PROMPT,
            tools=[{"type": "agent_toolset_20260401"}],
        )
        agent_id = agent.id
        print(f"  agent.id      = {agent_id}")
        print(f"  agent.version = {agent.version}")

    if environment_id:
        print(f"Reusing existing environment: {environment_id}")
    else:
        print("Creating managed-kanban environment...")
        environment = client.beta.environments.create(
            name="managed-kanban-env",
            config={
                "type": "cloud",
                "networking": {"type": "unrestricted"},
            },
        )
        environment_id = environment.id
        print(f"  environment.id = {environment_id}")

    if memory_store_id:
        print(f"Reusing existing memory store: {memory_store_id}")
    else:
        print("Creating managed-kanban memory store...")
        memory_store = client.beta.memory_stores.create(
            name="managed-kanban-memory",
            description="Shared memory for kanban ticket agents",
        )
        memory_store_id = memory_store.id
        print(f"  memory_store.id = {memory_store_id}")

    _persist_env(
        agent_id=agent_id,
        environment_id=environment_id,
        memory_store_id=memory_store_id,
    )
    print(f"\nSaved IDs to {ENV_FILE}.")
    return 0


def _persist_env(*, agent_id: str, environment_id: str, memory_store_id: str) -> None:
    lines: list[str] = []
    if ENV_FILE.exists():
        lines = ENV_FILE.read_text().splitlines()

    def upsert(key: str, value: str) -> None:
        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = f"{key}={value}"
                return
        lines.append(f"{key}={value}")

    upsert("MANAGED_AGENT_ID", agent_id)
    upsert("MANAGED_ENVIRONMENT_ID", environment_id)
    upsert("MANAGED_MEMORY_STORE_ID", memory_store_id)
    ENV_FILE.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
