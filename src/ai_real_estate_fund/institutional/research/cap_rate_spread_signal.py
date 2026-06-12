from __future__ import annotations

"""Research signal for cap-rate spread to debt."""

from dataclasses import asdict, dataclass
from typing import Any

from ...finance import clamp
from ...models import DiligenceDataBundle, PropertyInput, UnderwritingMetrics


@dataclass(slots=True)
class CapRateSpreadSignalObservation:
    signal_name: str
    raw_value: float
    normalized_score: float
    confidence: float
    interpretation: str
    drivers: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class CapRateSpreadSignal:
    name = 'cap-rate spread to debt'

    def raw_value(self, prop: PropertyInput, metrics: UnderwritingMetrics, data: DiligenceDataBundle) -> float:
        market = data.market_snapshot
        rent_comp_depth = len(data.rent_comps)
        sale_comp_depth = len(data.sale_comps)
        base = (
            market.population_growth_yoy * 1800.0
            + market.job_growth_yoy * 1500.0
            + market.rent_growth_yoy * 1200.0
            - market.vacancy_rate * 600.0
            + prop.liquidity_score * 4.0
            + prop.school_score * 2.0
            - prop.crime_risk_score * 3.0
            + rent_comp_depth * 1.5
            + sale_comp_depth * 1.25
            + metrics.cap_rate * 300.0
            + metrics.cash_on_cash_return * 220.0
        )
        return round(base, 3)

    def normalized_score(self, raw_value: float) -> float:
        return round(clamp(50.0 + raw_value / 4.0), 1)

    def confidence(self, data: DiligenceDataBundle) -> float:
        quality = data.data_quality.completeness_score if data.data_quality else 50.0
        evidence_bonus = min(0.15, (len(data.rent_comps) + len(data.sale_comps)) * 0.015)
        return round(max(0.35, min(0.95, 0.45 + quality / 250.0 + evidence_bonus)), 2)

    def interpret(self, score: float) -> str:
        if score >= 75:
            return "strongly supportive"
        if score >= 60:
            return "supportive"
        if score >= 45:
            return "mixed"
        return "adverse"

    def evaluate(self, prop: PropertyInput, metrics: UnderwritingMetrics, data: DiligenceDataBundle) -> CapRateSpreadSignalObservation:
        raw = self.raw_value(prop, metrics, data)
        score = self.normalized_score(raw)
        drivers = [
            f"Market rent growth: {data.market_snapshot.rent_growth_yoy:.1%}",
            f"Market vacancy: {data.market_snapshot.vacancy_rate:.1%}",
            f"Rent comps available: {len(data.rent_comps)}",
            f"Sale comps available: {len(data.sale_comps)}",
            f"Cap rate: {metrics.cap_rate:.1%}",
        ]
        return CapRateSpreadSignalObservation(
            signal_name=self.name,
            raw_value=raw,
            normalized_score=score,
            confidence=self.confidence(data),
            interpretation=self.interpret(score),
            drivers=drivers,
        )

