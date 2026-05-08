"""Update the existing managed agent's system prompt to the latest SYSTEM_PROMPT.

Run inside the codespace after pulling new code:
    cd backend && python -m app.update_agent

Reads MANAGED_AGENT_ID from env and creates a new agent version with the
SYSTEM_PROMPT defined in agent_setup.py.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

from app.agent_setup import SYSTEM_PROMPT

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


def main() -> int:
    load_dotenv(ENV_FILE)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY is not set.", file=sys.stderr)
        return 1

    agent_id = os.environ.get("MANAGED_AGENT_ID")
    if not agent_id:
        print("ERROR: MANAGED_AGENT_ID is not set.", file=sys.stderr)
        return 1

    client = Anthropic()
    current = client.beta.agents.retrieve(agent_id)
    print(f"Current agent version: {current.version}")

    updated = client.beta.agents.update(
        agent_id,
        version=current.version,
        system=SYSTEM_PROMPT,
    )
    print(f"New agent version:     {updated.version}")
    print("System prompt updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
