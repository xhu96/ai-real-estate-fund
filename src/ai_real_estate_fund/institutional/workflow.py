from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from uuid import uuid4

from ..data_sources import LocalDataProvider
from ..finance import underwrite_property
from ..models import AgentFinding, DiligenceDataBundle, PropertyInput, Recommendation, RiskItem
from ..scenarios import build_scenarios
from .agents import build_default_institutional_agents
from .agents.base import InstitutionalAgent
from .capital_stack import build_allocation_plan, build_capital_stack
from .data_room import build_data_room_manifest, missing_document_actions
from .models import CommitteeMinute, CommitteeStage, InstitutionalDecision, InvestmentPolicy, ScoreFactor, Scorecard
from .policy import evaluate_policy
from .proforma import build_operating_plan
from .scoring import dissent_level, recommendation_with_policy, top_findings, weakest_findings, weighted_agent_score


def _scorecards_from_findings(findings: list[AgentFinding]) -> list[Scorecard]:
    grouped: dict[str, list[AgentFinding]] = defaultdict(list)
    for finding in findings:
        # role format: "Institutional diligence workstream: category".
        category = finding.role.rsplit(":", 1)[-1].strip() if ":" in finding.role else "general"
        grouped[category].append(finding)
    scorecards: list[Scorecard] = []
    for category, items in sorted(grouped.items()):
        factors = [
            ScoreFactor(
                name=item.agent_name,
                value=item.score,
                score=item.score,
                weight=item.weight,
                explanation=item.thesis,
                source=item.model,
            )
            for item in items
        ]
        confidence = round(sum(item.confidence for item in items) / len(items), 2) if items else 0.50
        scorecards.append(
            Scorecard(
                name=f"{category.title()} Scorecard",
                category=category,
                factors=factors,
                confidence=confidence,
                owner=f"{category}_lead",
            )
        )
    return scorecards


def _risk_register(findings: list[AgentFinding], data: DiligenceDataBundle) -> list[RiskItem]:
    risks: list[RiskItem] = []
    for finding in weakest_findings(findings, n=15):
        if finding.score >= 60:
            continue
        risks.append(
            RiskItem(
                name=finding.agent_name.replace(" Agent", " risk"),
                severity="high" if finding.score < 45 else "medium",
                probability="high" if finding.confidence >= 0.75 else "medium",
                mitigation=finding.actions[0] if finding.actions else "Assign a diligence owner and close the issue.",
                owner="investment_committee",
            )
        )
    if data.data_quality and data.data_quality.completeness_score < 70:
        risks.append(
            RiskItem(
                name="Data-room readiness risk",
                severity="high",
                probability="high",
                mitigation="Collect missing source documents and tag every material assumption before final IC.",
                owner="deal_team",
            )
        )
    return risks or [
        RiskItem(
            name="Residual model and execution risk",
            severity="medium",
            probability="medium",
            mitigation="Maintain reserves, track KPIs, and verify all assumptions with professionals.",
            owner="asset_management",
        )
    ]


def _committee_minutes(decision_score: float, recommendation: Recommendation, findings: list[AgentFinding]) -> list[CommitteeMinute]:
    minutes = [
        CommitteeMinute(
            stage=CommitteeStage.SCREENING,
            speaker="Deal Team",
            topic="Initial screen",
            summary=f"The deal entered committee review with a preliminary weighted score of {decision_score:.1f}.",
            decision="advance" if decision_score >= 52 else "hold",
            action_owner="deal_lead",
        ),
        CommitteeMinute(
            stage=CommitteeStage.DILIGENCE,
            speaker="Risk Manager",
            topic="Dissent level",
            summary=f"Agent-score dispersion indicates {dissent_level(findings)} dissent across workstreams.",
            decision="noted",
            action_owner="risk_lead",
        ),
        CommitteeMinute(
            stage=CommitteeStage.INVESTMENT_COMMITTEE,
            speaker="IC Chair",
            topic="Recommendation",
            summary=f"The institutional committee recommendation is {recommendation.value}.",
            decision=recommendation.value.lower(),
            action_owner="ic_chair",
        ),
    ]
    for finding in weakest_findings(findings, n=3):
        minutes.append(
            CommitteeMinute(
                stage=CommitteeStage.DILIGENCE,
                speaker=finding.agent_name,
                topic="Open diligence item",
                summary=finding.concerns[0] if finding.concerns else finding.thesis,
                decision="condition",
                action_owner="deal_team",
            )
        )
    return minutes


def _thesis(findings: list[AgentFinding]) -> str:
    strongest = top_findings(findings, n=5)
    bullets = [item.positives[0] for item in strongest if item.positives]
    return " ".join(bullets) if bullets else "The deal has a reviewable but not yet decisive investment thesis."


def _bear_case(findings: list[AgentFinding]) -> str:
    weakest = weakest_findings(findings, n=5)
    bullets = [item.concerns[0] for item in weakest if item.concerns]
    return " ".join(bullets) if bullets else "The bear case is that fixture-backed assumptions overstate income, exit value, or execution capacity."


def _next_steps(findings: list[AgentFinding], missing_docs: list[str]) -> list[str]:
    steps: list[str] = []
    steps.extend(missing_docs[:6])
    for finding in weakest_findings(findings, n=8):
        for action in finding.actions[:1]:
            if action not in steps:
                steps.append(action)
    steps.append("Run legal, tax, lending, insurance, environmental, and inspection review before any real-world decision.")
    return steps[:14]


class InstitutionalCommittee:
    """Production-style alpha orchestration layer for institutional real-estate diligence."""

    def __init__(
        self,
        *,
        data_provider: LocalDataProvider | None = None,
        policy: InvestmentPolicy | None = None,
        agents: list[InstitutionalAgent] | None = None,
    ) -> None:
        self.data_provider = data_provider or LocalDataProvider()
        self.policy = policy or InvestmentPolicy()
        self.agents = agents or build_default_institutional_agents()

    def run(self, prop: PropertyInput) -> InstitutionalDecision:
        prop.validate()
        metrics = underwrite_property(prop)
        data = self.data_provider.build_bundle(prop)
        scenarios = build_scenarios(prop)
        findings: list[AgentFinding] = []
        for agent in self.agents:
            findings.append(agent.analyze(prop, metrics, data, findings))
        base_score = weighted_agent_score(findings)
        manifest = build_data_room_manifest(prop, data)
        data_room_score = manifest.completeness_score()
        score = round(base_score * 0.88 + data_room_score * 0.12, 1)
        policy_results = evaluate_policy(self.policy, prop, metrics, data, score)
        recommendation = recommendation_with_policy(score, policy_results)
        risk_score = next((finding.score for finding in findings if "Risk" in finding.agent_name), score)
        data_quality = data.data_quality.completeness_score if data.data_quality else data_room_score
        operating_plan = build_operating_plan(prop, metrics)
        stack = build_capital_stack(prop, metrics)
        allocation_plan = build_allocation_plan(prop, metrics, score, risk_score, data_quality)
        missing_docs = missing_document_actions(manifest)
        return InstitutionalDecision(
            run_id=str(uuid4()),
            created_at=datetime.now(timezone.utc).isoformat(),
            property=prop,
            metrics=metrics,
            data=data,
            findings=findings,
            scorecards=_scorecards_from_findings(findings),
            policy=self.policy,
            policy_results=policy_results,
            data_room=manifest,
            capital_stack=stack,
            operating_plan=operating_plan,
            risk_register=_risk_register(findings, data),
            scenarios=scenarios,
            committee_minutes=_committee_minutes(score, recommendation, findings),
            allocation_plan=allocation_plan,
            overall_score=score,
            recommendation=recommendation,
            thesis=_thesis(findings),
            bear_case=_bear_case(findings),
            next_steps=_next_steps(findings, missing_docs),
        )


def run_institutional_committee(
    prop: PropertyInput,
    *,
    data_provider: LocalDataProvider | None = None,
    policy: InvestmentPolicy | None = None,
) -> InstitutionalDecision:
    return InstitutionalCommittee(data_provider=data_provider, policy=policy).run(prop)

