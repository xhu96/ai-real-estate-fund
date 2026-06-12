from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class Recommendation(str, Enum):
    BUY = "BUY"
    WATCHLIST = "WATCHLIST"
    NEGOTIATE = "NEGOTIATE"
    PASS = "PASS"


@dataclass(slots=True)
class PropertyInput:
    """Input assumptions for a rental property underwriting run.

    Percent fields are decimals, not whole numbers. Example: 5% is ``0.05``.
    Scores are 1-10 unless otherwise noted.

    The core MVP fields remain intentionally simple. The optional physical and
    source fields give the v2 diligence engine enough context to compare rent
    and sale comps without forcing every user to maintain a large schema.
    """

    name: str
    address: str
    market: str
    property_type: str = "single_family"

    purchase_price: float = 0.0
    estimated_arv: float = 0.0
    monthly_rent: float = 0.0
    other_monthly_income: float = 0.0

    vacancy_rate: float = 0.05
    property_taxes_annual: float = 0.0
    insurance_annual: float = 0.0
    repairs_annual: float = 0.0
    utilities_annual: float = 0.0
    hoa_annual: float = 0.0
    capex_annual: float = 0.0
    management_rate: float = 0.08

    acquisition_costs: float = 0.0
    rehab_budget: float = 0.0
    loan_amount: float = 0.0
    annual_interest_rate: float = 0.07
    loan_term_years: int = 30

    holding_period_years: int = 5
    expected_annual_rent_growth: float = 0.03
    expected_annual_expense_growth: float = 0.03
    expected_annual_appreciation: float = 0.03
    selling_cost_rate: float = 0.06

    neighborhood_score: float = 6.0
    school_score: float = 6.0
    liquidity_score: float = 6.0
    crime_risk_score: float = 4.0
    landlord_friendliness_score: float = 6.0

    # v2 diligence context. These are optional and default-safe.
    unit_count: int = 1
    square_feet: float = 0.0
    bedrooms: int = 0
    bathrooms: float = 0.0
    year_built: int | None = None
    listing_url: str = ""
    source: str = "manual"

    notes: str = ""

    def validate(self) -> None:
        if self.purchase_price <= 0:
            raise ValueError("purchase_price must be greater than zero")
        if self.monthly_rent < 0 or self.other_monthly_income < 0:
            raise ValueError("income values cannot be negative")
        if self.loan_amount < 0:
            raise ValueError("loan_amount cannot be negative")
        if self.loan_amount > self.purchase_price + self.rehab_budget + self.acquisition_costs:
            raise ValueError("loan_amount is unusually high relative to project cost")
        for field_name in (
            "vacancy_rate",
            "management_rate",
            "annual_interest_rate",
            "expected_annual_rent_growth",
            "expected_annual_expense_growth",
            "expected_annual_appreciation",
            "selling_cost_rate",
        ):
            value = getattr(self, field_name)
            if value < 0 or value > 1:
                raise ValueError(f"{field_name} must be a decimal between 0 and 1")
        for field_name in (
            "neighborhood_score",
            "school_score",
            "liquidity_score",
            "crime_risk_score",
            "landlord_friendliness_score",
        ):
            value = getattr(self, field_name)
            if value < 1 or value > 10:
                raise ValueError(f"{field_name} must be between 1 and 10")
        if self.loan_term_years <= 0:
            raise ValueError("loan_term_years must be positive")
        if self.holding_period_years <= 0:
            raise ValueError("holding_period_years must be positive")
        if self.unit_count <= 0:
            raise ValueError("unit_count must be positive")
        if self.square_feet < 0:
            raise ValueError("square_feet cannot be negative")
        if self.bedrooms < 0 or self.bathrooms < 0:
            raise ValueError("bedrooms and bathrooms cannot be negative")
        current_year = datetime.now(timezone.utc).year
        if self.year_built is not None and not (1700 <= self.year_built <= current_year + 1):
            raise ValueError("year_built is outside a reasonable range")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PropertyInput":
        allowed = set(cls.__dataclass_fields__.keys())
        unknown = set(data) - allowed
        if unknown:
            raise ValueError(f"Unknown property input fields: {sorted(unknown)}")
        prop = cls(**data)
        prop.validate()
        return prop

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class UnderwritingMetrics:
    gross_potential_income: float
    vacancy_loss: float
    effective_gross_income: float
    operating_expenses: float
    management_fee: float
    noi: float
    annual_debt_service: float
    cash_flow_before_tax: float
    total_project_cost: float
    cash_invested: float
    loan_to_cost: float
    cap_rate: float
    cash_on_cash_return: float
    dscr: float
    break_even_occupancy: float
    projected_sale_price: float
    projected_loan_balance: float
    projected_net_sale_proceeds: float
    equity_multiple: float
    irr: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class AgentSignal:
    agent_name: str
    score: float
    recommendation: Recommendation
    confidence: float
    summary: str
    positives: list[str] = field(default_factory=list)
    concerns: list[str] = field(default_factory=list)
    weight: float = 1.0

    def weighted_score(self) -> float:
        return self.score * self.weight

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["recommendation"] = self.recommendation.value
        return payload


@dataclass(slots=True)
class InvestmentMemo:
    property: PropertyInput
    metrics: UnderwritingMetrics
    agent_signals: list[AgentSignal]
    overall_score: float
    recommendation: Recommendation
    suggested_allocation_pct: float
    max_offer_price: float
    margin_of_safety: float
    thesis: str
    bear_case: str
    next_steps: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "property": self.property.to_dict(),
            "metrics": self.metrics.to_dict(),
            "agent_signals": [signal.to_dict() for signal in self.agent_signals],
            "overall_score": self.overall_score,
            "recommendation": self.recommendation.value,
            "suggested_allocation_pct": self.suggested_allocation_pct,
            "max_offer_price": self.max_offer_price,
            "margin_of_safety": self.margin_of_safety,
            "thesis": self.thesis,
            "bear_case": self.bear_case,
            "next_steps": self.next_steps,
        }


@dataclass(slots=True)
class EvidenceItem:
    """An auditable fact used by a diligence agent."""

    source: str
    label: str
    value: str | float | int | bool | None
    category: str = "assumption"
    confidence: float = 0.75
    as_of: str = ""
    url: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class RentComp:
    address: str
    monthly_rent: float
    bedrooms: int = 0
    bathrooms: float = 0.0
    square_feet: float = 0.0
    unit_count: int = 1
    distance_miles: float = 0.0
    source: str = "manual"
    confidence: float = 0.70
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class SaleComp:
    address: str
    sale_price: float
    square_feet: float = 0.0
    unit_count: int = 1
    bedrooms: int = 0
    bathrooms: float = 0.0
    distance_miles: float = 0.0
    sale_date: str = ""
    source: str = "manual"
    confidence: float = 0.70
    notes: str = ""

    def price_per_unit(self) -> float:
        return self.sale_price / self.unit_count if self.unit_count else 0.0

    def price_per_sqft(self) -> float:
        return self.sale_price / self.square_feet if self.square_feet else 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class MarketSnapshot:
    market: str
    rent_growth_yoy: float = 0.03
    appreciation_yoy: float = 0.03
    vacancy_rate: float = 0.06
    property_tax_rate: float = 0.012
    insurance_rate: float = 0.006
    unemployment_rate: float = 0.045
    population_growth_yoy: float = 0.01
    job_growth_yoy: float = 0.015
    landlord_friendliness_score: float = 6.0
    liquidity_score: float = 6.0
    crime_risk_score: float = 4.0
    school_score: float = 6.0
    source: str = "manual_fixture"
    as_of: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DataQualityReport:
    completeness_score: float
    confidence_score: float
    missing_fields: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    evidence_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class DiligenceDataBundle:
    market_snapshot: MarketSnapshot
    rent_comps: list[RentComp] = field(default_factory=list)
    sale_comps: list[SaleComp] = field(default_factory=list)
    evidence: list[EvidenceItem] = field(default_factory=list)
    data_quality: DataQualityReport | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "market_snapshot": self.market_snapshot.to_dict(),
            "rent_comps": [comp.to_dict() for comp in self.rent_comps],
            "sale_comps": [comp.to_dict() for comp in self.sale_comps],
            "evidence": [item.to_dict() for item in self.evidence],
            "data_quality": None if self.data_quality is None else self.data_quality.to_dict(),
        }


@dataclass(slots=True)
class AgentFinding:
    agent_name: str
    role: str
    score: float
    recommendation: Recommendation
    confidence: float
    thesis: str
    positives: list[str] = field(default_factory=list)
    concerns: list[str] = field(default_factory=list)
    evidence: list[EvidenceItem] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)
    weight: float = 1.0
    model: str = "rules"

    def to_signal(self) -> AgentSignal:
        return AgentSignal(
            agent_name=self.agent_name,
            score=self.score,
            recommendation=self.recommendation,
            confidence=self.confidence,
            summary=self.thesis,
            positives=self.positives,
            concerns=self.concerns,
            weight=self.weight,
        )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["recommendation"] = self.recommendation.value
        payload["evidence"] = [item.to_dict() for item in self.evidence]
        return payload


@dataclass(slots=True)
class ScenarioResult:
    name: str
    score: float
    recommendation: Recommendation
    cap_rate: float
    cash_on_cash_return: float
    dscr: float
    irr: float | None
    cash_flow_before_tax: float
    noi: float
    assumptions: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["recommendation"] = self.recommendation.value
        return payload


@dataclass(slots=True)
class RiskItem:
    name: str
    severity: str
    probability: str
    mitigation: str
    owner: str = "sponsor"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class CommitteeDecision:
    run_id: str
    created_at: str
    property: PropertyInput
    metrics: UnderwritingMetrics
    data: DiligenceDataBundle
    findings: list[AgentFinding]
    scenarios: list[ScenarioResult]
    risk_register: list[RiskItem]
    overall_score: float
    recommendation: Recommendation
    suggested_allocation_pct: float
    max_offer_price: float
    margin_of_safety: float
    thesis: str
    bear_case: str
    next_steps: list[str]
    disclaimer: str = (
        "Educational software only. This is not financial, legal, tax, lending, "
        "or investment advice. Verify every assumption with qualified professionals."
    )

    def to_investment_memo(self) -> InvestmentMemo:
        return InvestmentMemo(
            property=self.property,
            metrics=self.metrics,
            agent_signals=[finding.to_signal() for finding in self.findings],
            overall_score=self.overall_score,
            recommendation=self.recommendation,
            suggested_allocation_pct=self.suggested_allocation_pct,
            max_offer_price=self.max_offer_price,
            margin_of_safety=self.margin_of_safety,
            thesis=self.thesis,
            bear_case=self.bear_case,
            next_steps=self.next_steps,
        )

    def to_dict(self) -> dict[str, Any]:
        return normalize_for_json({
            "run_id": self.run_id,
            "created_at": self.created_at,
            "property": self.property.to_dict(),
            "metrics": self.metrics.to_dict(),
            "data": self.data.to_dict(),
            "findings": [finding.to_dict() for finding in self.findings],
            "scenarios": [scenario.to_dict() for scenario in self.scenarios],
            "risk_register": [risk.to_dict() for risk in self.risk_register],
            "overall_score": self.overall_score,
            "recommendation": self.recommendation.value,
            "suggested_allocation_pct": self.suggested_allocation_pct,
            "max_offer_price": self.max_offer_price,
            "margin_of_safety": self.margin_of_safety,
            "thesis": self.thesis,
            "bear_case": self.bear_case,
            "next_steps": self.next_steps,
            "disclaimer": self.disclaimer,
        })


def normalize_for_json(value: Any) -> Any:
    """Recursively convert dataclasses/enums into JSON-safe values.

    Non-finite floats (e.g., an infinite DSCR on an all-cash deal) become None
    so every payload is strict-JSON serializable.
    """
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        to_dict = getattr(value, "to_dict", None)
        if callable(to_dict):
            return normalize_for_json(to_dict())
        return {key: normalize_for_json(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {str(key): normalize_for_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [normalize_for_json(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value
