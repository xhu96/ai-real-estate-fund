from __future__ import annotations

"""Institutional committee registry.

Every committee workstream uses the same deterministic, auditable scoring
procedure (``WorkstreamAgent``). The committee roster is therefore data, not
code: ``specs.AGENT_SPECS`` declares each workstream's name, category, weight,
focus components, and report language. Adding a workstream means adding one
``AgentSpec`` entry.
"""

from .base import InstitutionalAgent, WorkstreamAgent
from .specs import AGENT_SPECS, AgentSpec


def build_agent(spec: AgentSpec) -> WorkstreamAgent:
    return WorkstreamAgent(
        name=spec.name,
        role=spec.role,
        category=spec.category,
        weight=spec.weight,
        focus_components=list(spec.focus_components),
        positive_template=spec.positive,
        concern_template=spec.concern,
        action_template=spec.action,
        sources=spec.sources,
    )


def build_default_institutional_agents() -> list[InstitutionalAgent]:
    return [build_agent(spec) for spec in AGENT_SPECS]
