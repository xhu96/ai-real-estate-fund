from __future__ import annotations

from abc import ABC, abstractmethod
from statistics import mean

from ...finance import clamp
from ...models import AgentFinding, DiligenceDataBundle, EvidenceItem, PropertyInput, Recommendation, UnderwritingMetrics
from ..scoring import confidence_from_evidence, score_range, score_threshold


def _recommendation(score: float) -> Recommendation:
    if score >= 78:
        return Recommendation.BUY
    if score >= 66:
        return Recommendation.NEGOTIATE
    if score >= 52:
        return Recommendation.WATCHLIST
    return Recommendation.PASS


class InstitutionalAgent(ABC):
    name = "Institutional Agent"
    role = "Reviews an institutional real-estate diligence workstream."
    category = "general"
    weight = 1.0
    model = "deterministic-rules"

    @abstractmethod
    def analyze(
        self,
        prop: PropertyInput,
        metrics: UnderwritingMetrics,
        data: DiligenceDataBundle,
        prior_findings: list[AgentFinding],
    ) -> AgentFinding:
        raise NotImplementedError

    def finding(
        self,
        *,
        score: float,
        thesis: str,
        positives: list[str] | None = None,
        concerns: list[str] | None = None,
        actions: list[str] | None = None,
        evidence: list[EvidenceItem] | None = None,
        confidence: float | None = None,
    ) -> AgentFinding:
        clean_score = round(clamp(score), 1)
        ev = evidence or []
        if confidence is None:
            confidence = confidence_from_evidence(
                len(ev),
                55.0 if not ev else 70.0,
                prior_count=0,
            )
        return AgentFinding(
            agent_name=self.name,
            role=self.role,
            score=clean_score,
            recommendation=_recommendation(clean_score),
            confidence=round(clamp(confidence, 0.0, 1.0), 2),
            thesis=thesis,
            positives=positives or [],
            concerns=concerns or [],
            evidence=ev,
            actions=actions or [],
            weight=self.weight,
            model=self.model,
        )

    def evidence(self, label: str, value: object, *, category: str = "institutional", confidence: float = 0.72) -> EvidenceItem:
        if not isinstance(value, (str, int, float, bool)) and value is not None:
            value = str(value)
        return EvidenceItem(
            source="institutional_workflow",
            label=label,
            value=value,
            category=category,
            confidence=confidence,
        )

    def blended_score(self, components: list[tuple[float, float]]) -> float:
        if not components:
            return 50.0
        total_weight = sum(max(weight, 0.0) for _, weight in components)
        if total_weight <= 0:
            return 50.0
        return clamp(sum(score * max(weight, 0.0) for score, weight in components) / total_weight)

    def prior_average(self, prior_findings: list[AgentFinding]) -> float:
        if not prior_findings:
            return 55.0
        return mean(finding.score for finding in prior_findings[-8:])

    def core_metric_components(self, prop: PropertyInput, metrics: UnderwritingMetrics, data: DiligenceDataBundle) -> dict[str, float]:
        data_quality = data.data_quality.completeness_score if data.data_quality else 50.0
        market = data.market_snapshot
        property_age = 2026 - prop.year_built if prop.year_built else 45
        return {
            "cap_rate": score_threshold(metrics.cap_rate, 0.065, tolerance=0.50),
            "cash_on_cash": score_threshold(metrics.cash_on_cash_return, 0.07, tolerance=0.75),
            # A no-debt deal has metrics.dscr == inf; score_threshold clamps it to the band top (100).
            "dscr": score_threshold(metrics.dscr, 1.25, tolerance=0.30),
            "ltc": score_range(metrics.loan_to_cost, 0.55, 0.85, invert=True),
            "break_even": score_range(metrics.break_even_occupancy, 0.65, 0.95, invert=True),
            "market_growth": self.blended_score([
                (score_range(market.population_growth_yoy, -0.02, 0.04), 1.0),
                (score_range(market.job_growth_yoy, -0.02, 0.05), 1.0),
                (score_range(market.rent_growth_yoy, -0.01, 0.08), 1.0),
            ]),
            "vacancy": score_range(max(prop.vacancy_rate, market.vacancy_rate), 0.02, 0.14, invert=True),
            "liquidity": score_range(max(prop.liquidity_score, market.liquidity_score), 1.0, 10.0),
            "landlord_law": score_range(max(prop.landlord_friendliness_score, market.landlord_friendliness_score), 1.0, 10.0),
            "crime": score_range(max(prop.crime_risk_score, market.crime_risk_score), 1.0, 10.0, invert=True),
            "school": score_range(max(prop.school_score, market.school_score), 1.0, 10.0),
            "data_quality": data_quality,
            "rehab_load": score_range(prop.rehab_budget / metrics.total_project_cost if metrics.total_project_cost else 0.0, 0.0, 0.35, invert=True),
            "age": score_range(property_age, 0, 90, invert=True),
            "expense_ratio": score_range(metrics.operating_expenses / metrics.effective_gross_income if metrics.effective_gross_income else 1.0, 0.25, 0.65, invert=True),
            # After-tax depreciation shield: residential improvements depreciate over
            # 27.5 years (IRS Publication 527); score the share of year-one
            # pre-depreciation taxable income sheltered by depreciation.
            "tax_shield": score_range(
                min(
                    ((prop.purchase_price * 0.80) / 27.5)
                    / max(metrics.noi - prop.loan_amount * prop.annual_interest_rate, 1.0),
                    1.5,
                ),
                0.20,
                1.00,
            ),
            # Market cycle position (Linneman ch. 26): rent growth supported by job
            # growth, penalized by excess vacancy, reads as early/mid cycle.
            "cycle_position": score_range(
                market.rent_growth_yoy + market.job_growth_yoy * 0.5 - max(market.vacancy_rate - 0.06, 0.0) * 0.5,
                -0.01,
                0.05,
            ),
            # Required-return spread (Hartzell & Baum ch. 4): going-in cap rate plus
            # expected growth must clear the cost of debt plus an equity premium.
            "return_spread": score_range(
                (metrics.cap_rate + prop.expected_annual_appreciation) - (prop.annual_interest_rate + 0.025),
                -0.02,
                0.04,
            ),
            # EPA Lead-Based Paint Disclosure Rule (40 CFR 745) applies to pre-1978 housing.
            "lead_paint_era": 85.0 if (prop.year_built or 1970) >= 1978 else 45.0,
        }

    def evidence_from_components(self, components: dict[str, float], names: list[str]) -> list[EvidenceItem]:
        items = []
        for name in names:
            if name in components:
                items.append(self.evidence(name.replace("_", " "), round(components[name], 1), category="score_component"))
        return items



class WorkstreamAgent(InstitutionalAgent):
    """Deterministic diligence agent configured entirely by an ``AgentSpec``.

    Every committee workstream shares one auditable scoring procedure: blend a
    small set of named underwriting/market/data-quality components, weight the
    primary component highest, fold in the committee's prior findings, and emit
    an evidence-backed finding with explicit positives, concerns, and follow-up
    actions. What differs per workstream is configuration (name, category,
    weight, focus components, and report language), not code.
    """

    positive_template = "Workstream indicators are supportive."
    concern_template = "Workstream indicators are a diligence constraint."
    action_template = "Review this workstream with the deal team."

    def __init__(
        self,
        *,
        name: str | None = None,
        role: str | None = None,
        category: str | None = None,
        weight: float | None = None,
        focus_components: list[str] | None = None,
        positive_template: str | None = None,
        concern_template: str | None = None,
        action_template: str | None = None,
        sources: tuple[str, ...] = (),
    ) -> None:
        self.sources = sources
        if name is not None:
            self.name = name
        if role is not None:
            self.role = role
        if category is not None:
            self.category = category
        if weight is not None:
            self.weight = weight
        if focus_components is not None:
            self.focus_components = focus_components
        if positive_template is not None:
            self.positive_template = positive_template
        if concern_template is not None:
            self.concern_template = concern_template
        if action_template is not None:
            self.action_template = action_template

    def analyze(
        self,
        prop: PropertyInput,
        metrics: UnderwritingMetrics,
        data: DiligenceDataBundle,
        prior_findings: list[AgentFinding],
    ) -> AgentFinding:
        components = self.core_metric_components(prop, metrics, data)
        contextual_prior = self.prior_average(prior_findings)
        weighted_components: list[tuple[float, float]] = []
        for index, component_name in enumerate(self.focus_components):
            score = components.get(component_name, contextual_prior)
            component_weight = 1.35 if index == 0 else 1.0
            weighted_components.append((score, component_weight))
        if prior_findings:
            weighted_components.append((contextual_prior, 0.20))
        score = self.blended_score(weighted_components)
        evidence = self.evidence_from_components(components, [name for name in self.focus_components if name in components])
        if not evidence:
            evidence = [self.evidence("contextual prior", round(contextual_prior, 1), category="committee_context")]
        positives: list[str] = []
        concerns: list[str] = []
        if score >= 62:
            positives.append(self.positive_template)
        else:
            concerns.append(self.concern_template)
        if score >= 78:
            positives.append("Score clears the institutional approval band for this workstream.")
        if score < 52:
            concerns.append("Score is below the watchlist band and requires remediation before approval.")
        thesis = (
            f"{self.name} scored {score:.1f}/100 using {', '.join(self.focus_components)}. "
            f"The workstream is {'supportive' if score >= 62 else 'a diligence constraint'} for {prop.name}."
        )
        actions = [self.action_template]
        if score < 55:
            actions.append("Escalate this workstream in the investment committee agenda.")
        return self.finding(
            score=score,
            thesis=thesis,
            positives=positives,
            concerns=concerns,
            actions=actions,
            evidence=evidence,
            confidence=min(0.94, 0.55 + len(evidence) * 0.04 + (data.data_quality.completeness_score if data.data_quality else 55.0) / 500.0),
        )
