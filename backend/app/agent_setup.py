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

Output protocol — VERY IMPORTANT:
* Whenever your high-level phase changes, write one line on its own:
      STATUS: <short phrase, max 6 words>
  Examples:
      STATUS: Reading current site
      STATUS: Running Lighthouse baseline
      STATUS: Self-grading against rubric...
      STATUS: Self-grading... (Attempt 2 of 3)
* When you measure a numeric score (Lighthouse, latency, anything 0-100), write:
      SCORE: <before> -> <after>
  Always emit both numbers; on the first measurement set both equal.
* Otherwise write normal prose narrating what you just did.
* Keep narration to 1-2 short paragraphs per action.
* If a ticket has a self-grading rubric, run up to 3 attempts. Stop early if
  you exceed the threshold.

The kanban board parses STATUS: and SCORE: lines and renders them as pills and
widgets on the ticket card. Other tools (bash, edit, etc.) are surfaced as
"Running: <tool>" automatically — you do not need to announce them.
"""


def main() -> int:
    load_dotenv(ENV_FILE)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY is not set.", file=sys.stderr)
        print(f"Copy .env.example to .env and fill it in.", file=sys.stderr)
        return 1

    existing_agent = os.environ.get("MANAGED_AGENT_ID")
    existing_env = os.environ.get("MANAGED_ENVIRONMENT_ID")
    if existing_agent and existing_env:
        print(f"Already configured. Reusing existing resources:")
        print(f"  MANAGED_AGENT_ID       = {existing_agent}")
        print(f"  MANAGED_ENVIRONMENT_ID = {existing_env}")
        return 0

    client = Anthropic()

    print("Creating managed-kanban agent...")
    agent = client.beta.agents.create(
        name="managed-kanban",
        model="claude-opus-4-7",
        system=SYSTEM_PROMPT,
        tools=[{"type": "agent_toolset_20260401"}],
    )
    print(f"  agent.id      = {agent.id}")
    print(f"  agent.version = {agent.version}")

    print("Creating managed-kanban environment...")
    environment = client.beta.environments.create(
        name="managed-kanban-env",
        config={
            "type": "cloud",
            "networking": {"type": "unrestricted"},
        },
    )
    print(f"  environment.id = {environment.id}")

    _persist_env(agent_id=agent.id, environment_id=environment.id)
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
