"""In-process agent + environment bootstrap, no filesystem writes.

Mirrors `agent_setup.main()` but returns the IDs instead of persisting to .env.
Used by the Streamlit entrypoint where there is no CLI step to run setup, and
where the local filesystem is ephemeral on Streamlit Cloud.
"""
from __future__ import annotations

import os

from anthropic import Anthropic

from app.agent_setup import SYSTEM_PROMPT


def ensure_agent_and_environment() -> tuple[str, str]:
    agent_id = os.environ.get("MANAGED_AGENT_ID") or None
    environment_id = os.environ.get("MANAGED_ENVIRONMENT_ID") or None

    if agent_id and environment_id:
        return agent_id, environment_id

    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise RuntimeError("ANTHROPIC_API_KEY is not set")

    client = Anthropic()

    if not agent_id:
        agent = client.beta.agents.create(
            name="managed-kanban",
            model="claude-opus-4-7",
            system=SYSTEM_PROMPT,
            tools=[{"type": "agent_toolset_20260401"}],
        )
        agent_id = agent.id

    if not environment_id:
        environment = client.beta.environments.create(
            name="managed-kanban-env",
            config={"type": "cloud", "networking": {"type": "unrestricted"}},
        )
        environment_id = environment.id

    os.environ["MANAGED_AGENT_ID"] = agent_id
    os.environ["MANAGED_ENVIRONMENT_ID"] = environment_id
    return agent_id, environment_id
