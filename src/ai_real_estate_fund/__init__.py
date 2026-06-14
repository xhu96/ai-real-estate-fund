"""AI Real Estate Fund.

Multi-agent real estate underwriting and institutional diligence toolkit with
production-oriented auth, audit, readiness, observability, deployment, and
model-risk controls.
"""

from .committee import run_institutional_committee
from .investment_committee import run_property_committee
from .models import CommitteeDecision, PropertyInput

__all__ = ["PropertyInput", "CommitteeDecision", "run_property_committee", "run_institutional_committee"]
__version__ = "0.8.0"
