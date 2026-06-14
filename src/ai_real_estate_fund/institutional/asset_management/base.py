"""Generic asset-management monitor base.

These modules are designed to make the repository feel like a real fund
system after acquisition: the diligence thesis is converted into KPIs,
tolerances, watch items, and action ownership. The calculations are
deterministic and intentionally simple, but the interfaces mirror the
components a production system would connect to accounting, property
management, construction, lender reporting, and investor reporting data.

The 30 monitors in this family were byte-identical clones differing only in
a handful of per-instance constants (name/description/owner and the Config
defaults). They are consolidated here into one generic ``Monitor`` whose
method bodies are copied verbatim from the original clones, plus a frozen
``MonitorConfig`` dataclass and a ``MonitorSpec`` carrying the per-instance
constants. See ``specs.py`` for the spec list and the registry that rebuilds
each original class name.

Note: this family is an illustrative, uncalibrated deterministic heuristic
that demonstrates the *shape* of a production fund system. Its KPI
coefficients, tolerances, and labels are placeholders, not validated models.
It is standalone and not wired into the committee decision (only sampled by a
couple of tests).
"""

from __future__ import annotations

from dataclasses import dataclass

from ...models import PropertyInput, UnderwritingMetrics
from .models import MonitoringKPI, MonitoringReport


@dataclass(slots=True)
class MonitorConfig:
    target: float = 1.0
    tolerance: float = 0.10
    unit: str = "ratio"
    owner: str = "asset_manager"
    enabled: bool = True


@dataclass(frozen=True)
class MonitorSpec:
    """Per-instance constants extracted verbatim from each original clone.

    In every original clone the class-level ``owner`` and the ``Config.owner``
    default were the same string, and ``target``/``tolerance``/``unit``/
    ``enabled`` were uniform; a single ``owner`` field therefore reproduces
    both the class attribute and the config default identically.
    """

    class_name: str
    name: str
    description: str
    owner: str
    target: float = 1.0
    tolerance: float = 0.10
    unit: str = "ratio"
    enabled: bool = True

    def build_config(self) -> MonitorConfig:
        return MonitorConfig(
            target=self.target,
            tolerance=self.tolerance,
            unit=self.unit,
            owner=self.owner,
            enabled=self.enabled,
        )


class Monitor:
    # Per-instance constants are supplied by the bound spec on each generated
    # subclass; these class-level defaults mirror the original clone shape.
    name = "asset_manager"
    description = ""
    owner = "asset_manager"
    spec: MonitorSpec | None = None

    def __init__(self, config: MonitorConfig | None = None) -> None:
        if config is None and self.spec is not None:
            config = self.spec.build_config()
        self.config = config or MonitorConfig()

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
