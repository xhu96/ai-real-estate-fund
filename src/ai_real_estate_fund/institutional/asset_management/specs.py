"""Spec list + registry for the asset-management monitor family.

One short ``MonitorSpec`` entry per original ``*_monitor.py`` clone, with the
name/description/owner extracted verbatim from each original file. The registry
generates one configured ``Monitor`` subclass per spec, preserving the exact
original class name so that ``from ...asset_management import <ClassName>``
works and ``<ClassName>()`` constructs the correctly configured instance.
"""

from __future__ import annotations

from .base import Monitor, MonitorSpec

SPECS: list[MonitorSpec] = [
    MonitorSpec("BusinessPlanMilestoneMonitor", "business-plan milestones", "completed milestones versus approved plan", "asset_manager"),
    MonitorSpec("CapexBudgetMonitor", "capex budget", "capex spend versus approved budget", "construction_manager"),
    MonitorSpec("CollectionsMonitor", "collections", "cash collected against tenant ledger", "property_manager"),
    MonitorSpec("ComplianceCalendarMonitor", "compliance calendar", "licenses, inspections, and filings", "compliance_lead"),
    MonitorSpec("CovenantComplianceMonitor", "covenant compliance", "lender covenant headroom", "debt_asset_manager"),
    MonitorSpec("DelinquencyMonitor", "delinquency", "past-due balance as a share of monthly rent", "property_manager"),
    MonitorSpec("DscrMonitor", "DSCR", "NOI divided by debt service", "debt_asset_manager"),
    MonitorSpec("EconomicOccupancyMonitor", "economic occupancy", "collected rent divided by scheduled rent", "asset_manager"),
    MonitorSpec("ExitReadinessMonitor", "exit readiness", "materials required for sale/refi process", "portfolio_manager"),
    MonitorSpec("ExpenseVarianceMonitor", "expense variance", "actual controllable expenses versus budget", "controller"),
    MonitorSpec("InsuranceClaimMonitor", "insurance claims", "claim frequency and retained losses", "risk_manager"),
    MonitorSpec("InvestorReportingMonitor", "investor reporting", "investor package timeliness and quality", "investor_relations"),
    MonitorSpec("LeasingVelocityMonitor", "leasing velocity", "new leases signed per available unit", "leasing_manager"),
    MonitorSpec("LenderReportingMonitor", "lender reporting", "reporting package timeliness", "controller"),
    MonitorSpec("MaintenanceSlaMonitor", "maintenance SLA", "work orders completed within SLA", "maintenance_lead"),
    MonitorSpec("ManagerScorecardMonitor", "manager scorecard", "operator KPI scorecard", "portfolio_manager"),
    MonitorSpec("NoiVarianceMonitor", "NOI variance", "actual NOI versus budget", "asset_manager"),
    MonitorSpec("OccupancyMonitor", "occupancy", "occupied units divided by rentable units", "leasing_manager"),
    MonitorSpec("OnlineReputationMonitor", "online reputation", "reviews and response cadence", "property_manager"),
    MonitorSpec("RenewalMonitor", "renewals", "expiring leases converted to renewals", "leasing_manager"),
    MonitorSpec("RenovationDrawMonitor", "renovation draws", "draws funded versus completion milestones", "construction_manager"),
    MonitorSpec("RentCompRefreshMonitor", "rent comp refresh", "freshness of rent comp evidence", "research_lead"),
    MonitorSpec("RentGrowthMonitor", "rent growth", "achieved rents versus underwritten rents", "asset_manager"),
    MonitorSpec("ReserveBalanceMonitor", "reserve balance", "available reserves versus policy minimum", "controller"),
    MonitorSpec("ResidentSatisfactionMonitor", "resident satisfaction", "survey and work-order quality signals", "property_manager"),
    MonitorSpec("SafetyIncidentMonitor", "safety incidents", "incidents per occupied unit", "risk_manager"),
    MonitorSpec("SaleCompRefreshMonitor", "sale comp refresh", "freshness of sale comp evidence", "research_lead"),
    MonitorSpec("TaxEscrowMonitor", "tax escrow", "escrow balance versus projected tax bill", "controller"),
    MonitorSpec("TurnTimeMonitor", "turn time", "days from move-out to rent-ready", "maintenance_lead"),
    MonitorSpec("UtilityRecoveryMonitor", "utility recovery", "tenant reimbursements against utility expense", "asset_manager"),
]


def _build_monitor_class(spec: MonitorSpec) -> type[Monitor]:
    """Generate a configured ``Monitor`` subclass for ``spec``.

    Binds the per-instance constants as class attributes (mirroring the
    original clone's class body) and sets ``__name__`` to the original class
    name so the generated type is indistinguishable from the hand-written one.
    """

    cls = type(
        spec.class_name,
        (Monitor,),
        {
            "name": spec.name,
            "description": spec.description,
            "owner": spec.owner,
            "spec": spec,
            "__module__": __name__,
            "__qualname__": spec.class_name,
            "__doc__": f"Asset-management monitor for {spec.name}.",
        },
    )
    return cls


REGISTRY: dict[str, type[Monitor]] = {
    spec.class_name: _build_monitor_class(spec) for spec in SPECS
}
"""Mapping of original class name -> generated configured Monitor subclass."""


def get_monitor_class(class_name: str) -> type[Monitor]:
    """Return the configured Monitor subclass for an original class name."""

    return REGISTRY[class_name]
