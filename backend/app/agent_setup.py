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

Be efficient. Minimize prose. Up to 3 attempts when the ticket has a rubric;
stop early once you exceed the threshold.

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

    if agent_id and environment_id:
        print("Already configured. Reusing existing resources:")
        print(f"  MANAGED_AGENT_ID       = {agent_id}")
        print(f"  MANAGED_ENVIRONMENT_ID = {environment_id}")
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

    _persist_env(agent_id=agent_id, environment_id=environment_id)
    print(f"\nSaved IDs to {ENV_FILE}.")
    return 0


def _persist_env(*, agent_id: str, environment_id: str) -> None:
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
    ENV_FILE.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
