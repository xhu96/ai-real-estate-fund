"""Institutional committee agents: one deterministic engine, a config-driven roster."""

from .base import InstitutionalAgent, WorkstreamAgent
from .registry import build_agent, build_default_institutional_agents
from .specs import AGENT_SPECS, AgentSpec

__all__ = [
    "AGENT_SPECS",
    "AgentSpec",
    "InstitutionalAgent",
    "WorkstreamAgent",
    "build_agent",
    "build_default_institutional_agents",
]
