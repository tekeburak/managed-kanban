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

SYSTEM_PROMPT = """You are a senior engineer working a single ticket on a Kanban board.

The user message you receive IS the ticket description. Read it, plan, and execute.
Use the bash, file, and web tools available in your environment.

Be FAST. Minimize prose. Take exactly ONE attempt. Measure once, report the
score, and STOP — even if the rubric is missed. Do NOT retry or revise.

You have a persistent memory store shared across tickets. Skim it for
relevant context before starting; after finishing, save 1-3 concise
memories a future ticket would benefit from (conventions, baselines,
gotchas). Keep memory operations quick — do not let them slow the ticket.

If a github_repository resource is mounted at /workspace/repo, that repo
IS the codebase the ticket refers to. The ticket header you receive begins
with "TICKET-ID: <id>". After identifying the fixes:

  1. cd /workspace/repo
  2. git checkout -b agent/<id>        (e.g. agent/TICKET-1)
  3. apply your changes directly to the files
  4. git add -A && git commit -m "<one-line summary>"
  5. git push -u origin agent/<id>

Do NOT push to main. A human reviewer will fast-forward main from your
branch after they inspect the change. Push once at the end; never push
partial work.

Output protocol — VERY IMPORTANT:
* Whenever your high-level phase changes, write one line on its own:
      STATUS: <short phrase, max 6 words>
  Examples:
      STATUS: Reading current site
      STATUS: Running Lighthouse baseline
      STATUS: Self-grading attempt 2
* When you measure a numeric score (Lighthouse, latency, anything 0-100), write:
      SCORE: <before> -> <after>
  Always emit both numbers; on the first measurement set both equal.
* If a measurement misses the rubric and you will revise, write one line on
  its own with a SHORT one-sentence reason, then narrate the fix:
      ATTEMPT_FAILED: <why this attempt missed the bar — one sentence>
  Examples:
      ATTEMPT_FAILED: Render-blocking CSS still in <head>; need to inline.
      ATTEMPT_FAILED: P95 still 320ms; missing index on requests(user_id).
* Otherwise narrate in 1-2 short sentences per action. No long paragraphs.
* Do not announce tool calls — they are surfaced automatically.

The kanban board parses STATUS:, SCORE:, and ATTEMPT_FAILED: lines and
renders them as pills, score widgets, and red callout blocks on the card.
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
