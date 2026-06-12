"""Production-style real estate investment committee agents.

The package is intentionally deterministic by default. Optional language-model
summaries can be layered on top of these findings, but the numeric signals remain
auditable and reproducible.
"""

from .orchestrator import ScreeningCommittee, run_property_committee
from .registry import DEFAULT_AGENT_REGISTRY, build_default_agents

__all__ = [
    "ScreeningCommittee",
    "run_property_committee",
    "DEFAULT_AGENT_REGISTRY",
    "build_default_agents",
]
