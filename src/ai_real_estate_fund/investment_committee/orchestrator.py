from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from ..data_sources import LocalDataProvider
from ..finance import max_price_for_target_cap_rate, underwrite_property
from ..models import AgentFinding, CommitteeDecision, PropertyInput, Recommendation, RiskItem
from ..scenarios import build_scenarios, recommendation_from_score
from .base import CommitteeAgent
from .registry import build_default_agents


def _weighted_score(findings: list[AgentFinding]) -> float:
    if not findings:
        return 0.0
    total_weight = sum(max(f.weight, 0.01) for f in findings)
    return round(sum(f.score * max(f.weight, 0.01) for f in findings) / total_weight, 1)


def _suggested_allocation(score: float, recommendation: Recommendation, risk_score: float, data_quality_score: float) -> float:
    if recommendation == Recommendation.PASS:
        return 0.0
    base = max(0.0, min(0.14, (score - 55) / 300))
    risk_modifier = max(0.25, min(1.0, risk_score / 85))
    quality_modifier = max(0.30, min(1.0, data_quality_score / 90))
    return round(base * risk_modifier * quality_modifier, 4)


def _hard_pass(findings: list[AgentFinding]) -> bool:
    hard_names = {"Risk Manager Agent", "Debt Capital Markets Agent", "Acquisition Pricing Agent"}
    return any(f.agent_name in hard_names and f.score < 35 for f in findings)


def _risk_register(prop: PropertyInput, findings: list[AgentFinding]) -> list[RiskItem]:
    register: list[RiskItem] = []
    for finding in findings:
        if finding.score < 55:
            register.append(
                RiskItem(
                    name=finding.agent_name.replace(" Agent", " risk"),
                    severity="high" if finding.score < 40 else "medium",
                    probability="medium" if finding.confidence < 0.75 else "high",
                    mitigation=finding.actions[0] if finding.actions else "Create a diligence action owner and close the issue before investment.",
                    owner="investment_committee",
                )
            )
    if not register:
        register.append(
            RiskItem(
                name="Model and data risk",
                severity="medium",
                probability="medium",
                mitigation="Replace fixtures with verified sources and re-run the committee before capital allocation.",
                owner="sponsor",
            )
        )
    return register[:12]


def _thesis(prop: PropertyInput, findings: list[AgentFinding]) -> str:
    strongest = sorted(findings, key=lambda f: f.score, reverse=True)[:4]
    fragments = [p for f in strongest for p in f.positives[:1]]
    if fragments:
        return " ".join(fragments)
    return f"{prop.name} has an unresolved but reviewable investment thesis."


def _bear_case(findings: list[AgentFinding]) -> str:
    weakest = sorted(findings, key=lambda f: f.score)[:4]
    fragments = [c for f in weakest for c in f.concerns[:1]]
    if fragments:
        return " ".join(fragments)
    return "The main bear case is that fixture-backed assumptions overstate true rent, condition, financing, or exit value."


def _next_steps(findings: list[AgentFinding], recommendation: Recommendation) -> list[str]:
    steps: list[str] = []
    for finding in findings:
        for action in finding.actions[:1]:
            if action not in steps:
                steps.append(action)
    if recommendation in {Recommendation.BUY, Recommendation.NEGOTIATE}:
        steps.insert(0, "Negotiate final price, seller credits, financing contingency, and reserve requirements.")
    steps.append("Have qualified legal, tax, lending, insurance, and inspection professionals verify the assumptions.")
    return steps[:10]


class ScreeningCommittee:
    """Orchestrates a deterministic multi-agent real estate investment committee."""

    def __init__(self, data_provider: LocalDataProvider | None = None, agents: list[CommitteeAgent] | None = None) -> None:
        self.data_provider = data_provider or LocalDataProvider()
        self.agents = agents or build_default_agents()

    def run(self, prop: PropertyInput) -> CommitteeDecision:
        prop.validate()
        metrics = underwrite_property(prop)
        data = self.data_provider.build_bundle(prop)
        scenarios = build_scenarios(prop)
        findings: list[AgentFinding] = []
        for agent in self.agents:
            findings.append(agent.analyze(prop, metrics, data, findings))
        score = _weighted_score(findings)
        recommendation = recommendation_from_score(score)
        if _hard_pass(findings):
            recommendation = Recommendation.PASS
        risk_score = next((f.score for f in findings if f.agent_name == "Risk Manager Agent"), score)
        data_quality_score = data.data_quality.completeness_score if data.data_quality else 55.0
        max_offer = max_price_for_target_cap_rate(prop)
        margin = (max_offer - prop.purchase_price) / prop.purchase_price if prop.purchase_price else 0.0
        return CommitteeDecision(
            run_id=str(uuid4()),
            created_at=datetime.now(timezone.utc).isoformat(),
            property=prop,
            metrics=metrics,
            data=data,
            findings=findings,
            scenarios=scenarios,
            risk_register=_risk_register(prop, findings),
            overall_score=score,
            recommendation=recommendation,
            suggested_allocation_pct=_suggested_allocation(score, recommendation, risk_score, data_quality_score),
            max_offer_price=max_offer,
            margin_of_safety=margin,
            thesis=_thesis(prop, findings),
            bear_case=_bear_case(findings),
            next_steps=_next_steps(findings, recommendation),
        )


def run_property_committee(prop: PropertyInput, *, data_provider: LocalDataProvider | None = None) -> CommitteeDecision:
    return ScreeningCommittee(data_provider=data_provider).run(prop)
