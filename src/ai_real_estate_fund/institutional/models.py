from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any

from ..models import AgentFinding, CommitteeDecision, DiligenceDataBundle, PropertyInput, Recommendation, RiskItem, ScenarioResult, UnderwritingMetrics, normalize_for_json


class CommitteeStage(str, Enum):
    SCREENING = "screening"
    DILIGENCE = "diligence"
    INVESTMENT_COMMITTEE = "investment_committee"
    CLOSING = "closing"
    ASSET_MANAGEMENT = "asset_management"


class GateSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    HARD_STOP = "hard_stop"


@dataclass(slots=True)
class ScoreFactor:
    name: str
    value: float
    score: float
    weight: float = 1.0
    explanation: str = ""
    source: str = "rules"

    def contribution(self) -> float:
        return self.score * max(self.weight, 0.0)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class Scorecard:
    name: str
    category: str
    factors: list[ScoreFactor] = field(default_factory=list)
    confidence: float = 0.70
    owner: str = "investment_committee"

    def weighted_score(self) -> float:
        if not self.factors:
            return 0.0
        total = sum(max(f.weight, 0.0) for f in self.factors)
        if total <= 0:
            return 0.0
        return round(sum(f.contribution() for f in self.factors) / total, 1)

    def weak_factors(self, threshold: float = 55.0) -> list[ScoreFactor]:
        return [factor for factor in self.factors if factor.score < threshold]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category,
            "score": self.weighted_score(),
            "confidence": self.confidence,
            "owner": self.owner,
            "factors": [factor.to_dict() for factor in self.factors],
        }


@dataclass(slots=True)
class PolicyLimit:
    name: str
    metric: str
    min_value: float | None = None
    max_value: float | None = None
    severity: GateSeverity = GateSeverity.WARNING
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["severity"] = self.severity.value
        return payload


@dataclass(slots=True)
class PolicyResult:
    limit: PolicyLimit
    value: float
    passed: bool
    message: str
    remediation: str = ""

    @property
    def severity(self) -> GateSeverity:
        return self.limit.severity

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.limit.name,
            "metric": self.limit.metric,
            "value": self.value,
            "passed": self.passed,
            "severity": self.limit.severity.value,
            "message": self.message,
            "remediation": self.remediation,
            "limit": self.limit.to_dict(),
        }


@dataclass(slots=True)
class InvestmentPolicy:
    name: str = "Base Rental Housing Policy"
    minimum_dscr: float = 1.20
    minimum_debt_yield: float = 0.085
    maximum_ltc: float = 0.78
    maximum_break_even_occupancy: float = 0.88
    minimum_data_quality: float = 70.0
    minimum_liquidity_score: float = 5.5
    maximum_rehab_to_cost: float = 0.30
    minimum_cash_on_cash: float = 0.04
    minimum_cap_rate: float = 0.055
    maximum_crime_risk_score: float = 7.5
    maximum_single_market_allocation: float = 0.25
    minimum_committee_score: float = 62.0
    allow_policy_override: bool = True

    def limits(self) -> list[PolicyLimit]:
        return [
            PolicyLimit("Debt-service coverage", "dscr", min_value=self.minimum_dscr, severity=GateSeverity.HARD_STOP, description="Base-case NOI should cover amortizing debt."),
            PolicyLimit("Debt yield", "debt_yield", min_value=self.minimum_debt_yield, severity=GateSeverity.WARNING, description="NOI divided by loan amount should clear lender-quality thresholds."),
            PolicyLimit("Loan-to-cost", "loan_to_cost", max_value=self.maximum_ltc, severity=GateSeverity.WARNING, description="Leverage should not consume the margin of safety."),
            PolicyLimit("Break-even occupancy", "break_even_occupancy", max_value=self.maximum_break_even_occupancy, severity=GateSeverity.WARNING, description="The asset should survive moderate vacancy pressure."),
            PolicyLimit("Data quality", "data_quality", min_value=self.minimum_data_quality, severity=GateSeverity.HARD_STOP, description="Institutional review requires sufficient evidence."),
            PolicyLimit("Liquidity", "liquidity_score", min_value=self.minimum_liquidity_score, severity=GateSeverity.WARNING, description="Exit market should have enough buyer depth."),
            PolicyLimit("Rehab intensity", "rehab_to_cost", max_value=self.maximum_rehab_to_cost, severity=GateSeverity.WARNING, description="Heavy rehab requires execution controls and contingency."),
            PolicyLimit("Cash-on-cash", "cash_on_cash", min_value=self.minimum_cash_on_cash, severity=GateSeverity.WARNING, description="Yield should compensate for operating risk."),
            PolicyLimit("Cap rate", "cap_rate", min_value=self.minimum_cap_rate, severity=GateSeverity.WARNING, description="In-place yield should not rely entirely on appreciation."),
            PolicyLimit("Crime risk", "crime_risk_score", max_value=self.maximum_crime_risk_score, severity=GateSeverity.WARNING, description="Neighborhood safety can affect leasing, exit value, and insurance."),
            PolicyLimit("Committee score", "committee_score", min_value=self.minimum_committee_score, severity=GateSeverity.HARD_STOP, description="Weighted agent score must clear the IC threshold."),
        ]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class CapitalStackLayer:
    name: str
    amount: float
    priority: int
    coupon_or_required_return: float = 0.0
    amortizing: bool = False
    maturity_years: int = 0
    notes: str = ""

    def cost_weight(self, total_capital: float) -> float:
        if total_capital <= 0:
            return 0.0
        return self.amount / total_capital

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class OperatingPlanYear:
    year: int
    gross_potential_income: float
    vacancy_loss: float
    effective_gross_income: float
    operating_expenses: float
    noi: float
    debt_service: float
    capital_reserve: float
    cash_flow_before_tax: float
    ending_loan_balance: float
    projected_asset_value: float

    def debt_service_coverage(self) -> float:
        return self.noi / self.debt_service if self.debt_service else 999.0

    def expense_ratio(self) -> float:
        return self.operating_expenses / self.effective_gross_income if self.effective_gross_income else 0.0

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["dscr"] = self.debt_service_coverage()
        payload["expense_ratio"] = self.expense_ratio()
        return payload


@dataclass(slots=True)
class DataRoomDocument:
    name: str
    category: str
    required: bool = True
    received: bool = False
    freshness_days: int | None = None
    source: str = "manual"
    notes: str = ""

    def score(self) -> float:
        if self.received and (self.freshness_days is None or self.freshness_days <= 365):
            return 100.0
        if self.received:
            return 75.0
        return 0.0 if self.required else 50.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DataRoomManifest:
    documents: list[DataRoomDocument] = field(default_factory=list)
    generated_from: str = "fixtures"

    def required_documents(self) -> list[DataRoomDocument]:
        return [doc for doc in self.documents if doc.required]

    def missing_required_documents(self) -> list[DataRoomDocument]:
        return [doc for doc in self.documents if doc.required and not doc.received]

    def completeness_score(self) -> float:
        required = self.required_documents()
        if not required:
            return 100.0
        return round(sum(doc.score() for doc in required) / len(required), 1)

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_from": self.generated_from,
            "completeness_score": self.completeness_score(),
            "missing_required_documents": [doc.name for doc in self.missing_required_documents()],
            "documents": [doc.to_dict() for doc in self.documents],
        }


@dataclass(slots=True)
class CommitteeMinute:
    stage: CommitteeStage
    speaker: str
    topic: str
    summary: str
    decision: str = "noted"
    action_owner: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage": self.stage.value,
            "speaker": self.speaker,
            "topic": self.topic,
            "summary": self.summary,
            "decision": self.decision,
            "action_owner": self.action_owner,
        }


@dataclass(slots=True)
class AllocationPlan:
    target_allocation_pct: float
    maximum_allocation_pct: float
    equity_commitment: float
    reserve_commitment: float
    reasons: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class InstitutionalDecision:
    run_id: str
    created_at: str
    property: PropertyInput
    metrics: UnderwritingMetrics
    data: DiligenceDataBundle
    findings: list[AgentFinding]
    scorecards: list[Scorecard]
    policy: InvestmentPolicy
    policy_results: list[PolicyResult]
    data_room: DataRoomManifest
    capital_stack: list[CapitalStackLayer]
    operating_plan: list[OperatingPlanYear]
    risk_register: list[RiskItem]
    scenarios: list[ScenarioResult]
    committee_minutes: list[CommitteeMinute]
    allocation_plan: AllocationPlan
    overall_score: float
    recommendation: Recommendation
    thesis: str
    bear_case: str
    next_steps: list[str]
    llm_review: Any | None = None
    stage: CommitteeStage = CommitteeStage.INVESTMENT_COMMITTEE
    disclaimer: str = (
        "Educational software only. This is not financial, legal, tax, lending, "
        "or investment advice. Replace fixtures with verified licensed data and "
        "obtain professional review before any real-world decision."
    )

    def hard_stops(self) -> list[PolicyResult]:
        return [result for result in self.policy_results if not result.passed and result.severity == GateSeverity.HARD_STOP]

    def to_committee_decision(self) -> CommitteeDecision:
        return CommitteeDecision(
            run_id=self.run_id,
            created_at=self.created_at,
            property=self.property,
            metrics=self.metrics,
            data=self.data,
            findings=self.findings,
            scenarios=self.scenarios,
            risk_register=self.risk_register,
            overall_score=self.overall_score,
            recommendation=self.recommendation,
            suggested_allocation_pct=self.allocation_plan.target_allocation_pct,
            max_offer_price=self.metrics.noi / max(self.policy.minimum_cap_rate, 0.001) if self.metrics.noi > 0 else 0.0,
            margin_of_safety=((self.metrics.noi / max(self.policy.minimum_cap_rate, 0.001)) - self.property.purchase_price) / self.property.purchase_price if self.property.purchase_price else 0.0,
            thesis=self.thesis,
            bear_case=self.bear_case,
            next_steps=self.next_steps,
            disclaimer=self.disclaimer,
        )

    def to_dict(self) -> dict[str, Any]:
        return normalize_for_json({
            "run_id": self.run_id,
            "created_at": self.created_at,
            "stage": self.stage,
            "property": self.property,
            "metrics": self.metrics,
            "data": self.data,
            "findings": self.findings,
            "scorecards": self.scorecards,
            "policy": self.policy,
            "policy_results": self.policy_results,
            "data_room": self.data_room,
            "capital_stack": self.capital_stack,
            "operating_plan": self.operating_plan,
            "risk_register": self.risk_register,
            "scenarios": self.scenarios,
            "committee_minutes": self.committee_minutes,
            "allocation_plan": self.allocation_plan,
            "overall_score": self.overall_score,
            "recommendation": self.recommendation,
            "thesis": self.thesis,
            "bear_case": self.bear_case,
            "next_steps": self.next_steps,
            "hard_stops": self.hard_stops(),
            "llm_review": self.llm_review.to_dict() if self.llm_review is not None else None,
            "disclaimer": self.disclaimer,
        })

