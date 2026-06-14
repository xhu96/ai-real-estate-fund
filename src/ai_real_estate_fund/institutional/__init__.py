"""Institutional diligence workflow.

This package adds a larger, production-style alpha architecture around the
original deterministic underwriting engine. It introduces an institutional
committee packet, data-room review, investment-policy gates, capital-stack
analysis, richer agent scoring, and frontend/API surface area.
"""

from .workflow import InstitutionalCommittee, run_institutional_committee
from .models import InstitutionalDecision, InvestmentPolicy, PolicyResult, DataRoomManifest

__all__ = [
    "InstitutionalCommittee",
    "run_institutional_committee",
    "InstitutionalDecision",
    "InvestmentPolicy",
    "PolicyResult",
    "DataRoomManifest",
]

