from __future__ import annotations

"""Asset-management monitor for tax escrow.

These modules are designed to make the repository feel like a real fund
system after acquisition: the diligence thesis is converted into KPIs,
tolerances, watch items, and action ownership. The calculations are
deterministic and intentionally simple, but the interfaces mirror the
components a production system would connect to accounting, property
management, construction, lender reporting, and investor reporting data.
"""

from dataclasses import dataclass

from ...models import PropertyInput, UnderwritingMetrics
from .models import MonitoringKPI, MonitoringReport


@dataclass(slots=True)
class TaxEscrowMonitorConfig:
    target: float = 1.0
    tolerance: float = 0.10
    unit: str = "ratio"
    owner: str = 'controller'
    enabled: bool = True


class TaxEscrowMonitor:
    name = 'tax escrow'
    description = 'escrow balance versus projected tax bill'
    owner = 'controller'

    def __init__(self, config: TaxEscrowMonitorConfig | None = None) -> None:
        self.config = config or TaxEscrowMonitorConfig()

    def target_from_underwriting(self, prop: PropertyInput, metrics: UnderwritingMetrics) -> float:
        if "occupancy" in self.name:
            return max(0.0, 1.0 - prop.vacancy_rate)
        if "dscr" in self.name.lower() or "covenant" in self.name:
            return max(1.20, min(metrics.dscr if metrics.dscr != float("inf") else 2.0, 1.65))
        if "expense" in self.name or "capex" in self.name or "reserve" in self.name:
            return max(1.0, metrics.operating_expenses / max(metrics.gross_potential_income, 1.0))
        if "noi" in self.name.lower():
            return metrics.noi
        if "rent" in self.name or "leasing" in self.name:
            return prop.monthly_rent
        return self.config.target

    def actual_from_snapshot(self, prop: PropertyInput, metrics: UnderwritingMetrics, snapshot: dict[str, float] | None = None) -> float:
        if snapshot and self.name in snapshot:
            return snapshot[self.name]
        target = self.target_from_underwriting(prop, metrics)
        if "delinquency" in self.name or "turn time" in self.name or "incident" in self.name:
            return target * 1.08
        if "collections" in self.name or "renewal" in self.name or "satisfaction" in self.name:
            return target * 0.96
        return target * 0.99

    def build_kpi(self, prop: PropertyInput, metrics: UnderwritingMetrics, snapshot: dict[str, float] | None = None) -> MonitoringKPI:
        target = self.target_from_underwriting(prop, metrics)
        actual = self.actual_from_snapshot(prop, metrics, snapshot)
        return MonitoringKPI(
            name=self.name,
            actual=round(actual, 4),
            target=round(target, 4),
            tolerance=self.config.tolerance,
            unit=self.config.unit,
            owner=self.config.owner,
            notes=self.description,
        )

    def watch_items(self, kpi: MonitoringKPI) -> list[str]:
        items: list[str] = []
        if not kpi.in_tolerance():
            items.append(f"{kpi.name} is outside tolerance by {kpi.variance_pct():.1%}.")
        if abs(kpi.variance_pct()) > self.config.tolerance * 2:
            items.append("Variance is severe enough for asset-management escalation.")
        return items

    def action_items(self, kpi: MonitoringKPI) -> list[str]:
        if kpi.in_tolerance():
            return [f"Continue monitoring {kpi.name} on the standard reporting cadence."]
        return [
            f"Assign {kpi.owner} to explain {kpi.name} variance.",
            "Update forecast, reserves, and business-plan milestones if the variance persists.",
        ]

    def report(self, prop: PropertyInput, metrics: UnderwritingMetrics, snapshot: dict[str, float] | None = None, period: str = "Month 1") -> MonitoringReport:
        kpi = self.build_kpi(prop, metrics, snapshot)
        return MonitoringReport(
            period=period,
            asset_name=prop.name,
            kpis=[kpi],
            watch_items=self.watch_items(kpi),
            action_items=self.action_items(kpi),
        )

