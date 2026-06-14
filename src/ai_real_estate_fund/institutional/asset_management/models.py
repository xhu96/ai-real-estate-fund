from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class MonitoringKPI:
    name: str
    actual: float
    target: float
    tolerance: float
    unit: str = ""
    owner: str = "asset_manager"
    notes: str = ""

    def variance(self) -> float:
        return self.actual - self.target

    def variance_pct(self) -> float:
        return self.variance() / self.target if self.target else 0.0

    def in_tolerance(self) -> bool:
        return abs(self.variance_pct()) <= self.tolerance if self.target else True

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["variance"] = self.variance()
        payload["variance_pct"] = self.variance_pct()
        payload["in_tolerance"] = self.in_tolerance()
        return payload


@dataclass(slots=True)
class MonitoringReport:
    period: str
    asset_name: str
    kpis: list[MonitoringKPI]
    watch_items: list[str]
    action_items: list[str]

    def health_score(self) -> float:
        if not self.kpis:
            return 50.0
        passed = sum(1 for kpi in self.kpis if kpi.in_tolerance())
        return round(passed / len(self.kpis) * 100.0, 1)

    def to_dict(self) -> dict[str, Any]:
        return {
            "period": self.period,
            "asset_name": self.asset_name,
            "health_score": self.health_score(),
            "kpis": [kpi.to_dict() for kpi in self.kpis],
            "watch_items": self.watch_items,
            "action_items": self.action_items,
        }

