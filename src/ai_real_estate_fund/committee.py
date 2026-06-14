from __future__ import annotations

from .data_sources import LocalDataProvider
from .institutional import InstitutionalCommittee
from .institutional.analysts import run_llm_analysts
from .institutional.models import InstitutionalDecision, InvestmentPolicy
from .llm import LLMClient
from .models import PropertyInput


def run_institutional_committee(
    prop: PropertyInput,
    *,
    data_provider: LocalDataProvider | None = None,
    policy: InvestmentPolicy | None = None,
    llm_client: LLMClient | None = None,
) -> InstitutionalDecision:
    """Run the institutional diligence workflow.

    The committee itself is deterministic. When ``llm_client`` is provided,
    LLM analyst personas (bull, bear, risk, chair) debate the committee's
    structured findings and their commentary is attached to the decision;
    the deterministic scores and recommendation are never modified.
    """
    decision = InstitutionalCommittee(data_provider=data_provider, policy=policy).run(prop)
    if llm_client is not None:
        decision.llm_review = run_llm_analysts(decision, llm_client)
    return decision

