"""Registry of underwriting model specs.

One short entry per original ``*_model.py`` clone. Values (class name,
``subject``, ``lens``) are extracted verbatim from the original files. The
registry generates a concrete subclass of :class:`~.base.Model` per spec so
that the original class names remain importable and constructable.
"""

from __future__ import annotations

from .base import Model, ModelSpec

# One entry per original clone. subject/lens copied verbatim from each file.
SPECS: list[ModelSpec] = [
    ModelSpec("BadDebtModel", "bad debt", "collection losses"),
    ModelSpec("CapitalReplacementModel", "capital replacements", "component useful life"),
    ModelSpec("ConcessionModel", "concessions", "effective rent"),
    ModelSpec("ConstructionDrawModel", "construction draws", "rehab cash timing"),
    ModelSpec("DebtServiceModel", "debt service", "amortization burden"),
    ModelSpec("ExitCapRateModel", "exit cap rate", "terminal value"),
    ModelSpec("InsuranceDeductibleModel", "insurance deductibles", "loss retention"),
    ModelSpec("InsuranceEscalationModel", "insurance escalation", "premium shock"),
    ModelSpec("LeaseExpirationModel", "lease expirations", "rollover risk"),
    ModelSpec("OperatingKpiModel", "operating KPIs", "asset-management monitoring"),
    ModelSpec("PropertyTaxAppealModel", "tax appeal", "assessment mitigation"),
    ModelSpec("RefinanceProceedsModel", "refinance proceeds", "takeout financing"),
    ModelSpec("RentRollModel", "rent roll", "income durability"),
    ModelSpec("RepairReserveModel", "repair reserves", "maintenance normalization"),
    ModelSpec("ReserveSizingModel", "reserve sizing", "liquidity buffer"),
    ModelSpec("SaleCostModel", "sale costs", "exit leakage"),
    ModelSpec("ScenarioNarrativeModel", "scenario narrative", "decision framing"),
    ModelSpec("SensitivityCubeModel", "sensitivity cube", "multi-variable stress"),
    ModelSpec("TaxReassessmentModel", "tax reassessment", "post-sale tax reset"),
    ModelSpec("TenantImprovementModel", "tenant improvements", "lease-up cost"),
    ModelSpec("UnitTurnModel", "unit turns", "turn cost and downtime"),
    ModelSpec("UtilityReimbursementModel", "utility reimbursements", "expense leakage"),
    ModelSpec("ValuationReconciliationModel", "valuation reconciliation", "income/comps/cost"),
    ModelSpec("WaterfallModel", "equity waterfall", "distribution priority"),
    ModelSpec("WorkingCapitalModel", "working capital", "escrows and timing"),
]


def _build(spec: ModelSpec) -> type[Model]:
    """Generate a concrete Model subclass bound to ``spec``."""
    cls = type(
        spec.name,
        (Model,),
        {"subject": spec.subject, "lens": spec.lens, "__doc__": f"Detailed underwriting model for {spec.subject}."},
    )
    cls.__module__ = __name__
    return cls


# Map of original class name -> generated configured class.
REGISTRY: dict[str, type[Model]] = {spec.name: _build(spec) for spec in SPECS}
