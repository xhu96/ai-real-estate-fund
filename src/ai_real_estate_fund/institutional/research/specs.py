"""Registry of research-signal specs.

One short entry per original ``*_signal.py`` clone. The values are extracted
verbatim from each original file (class name, ``name`` attribute, and the
description from the module docstring). The registry generates one configured
subclass of :class:`BaseSignal` per spec, with the original class ``__name__``
preserved so ``from ...research import <ClassName>`` works and ``<ClassName>()``
constructs the right configured instance.
"""

from __future__ import annotations

from .base import BaseSignal, SignalObservation, SignalSpec

SIGNAL_SPECS: list[SignalSpec] = [
    SignalSpec("AbsorptionVelocitySignal", "leasing absorption", "leasing absorption"),
    SignalSpec("AffordabilitySignal", "rent-to-income affordability", "rent-to-income affordability"),
    SignalSpec("CapRateSpreadSignal", "cap-rate spread to debt", "cap-rate spread to debt"),
    SignalSpec("ClimateExposureSignal", "physical climate exposure", "physical climate exposure"),
    SignalSpec("ConstructionCostSignal", "construction-cost pressure", "construction-cost pressure"),
    SignalSpec("CrimeTrendSignal", "safety trend", "safety trend"),
    SignalSpec("DistressSupplySignal", "distressed-sale inventory", "distressed-sale inventory"),
    SignalSpec("EmploymentDiversitySignal", "employer concentration", "employer concentration"),
    SignalSpec("EvictionTimelineSignal", "remedy timeline", "remedy timeline"),
    SignalSpec("ExitBidSignal", "exit bid support", "exit bid support"),
    SignalSpec("InsuranceAvailabilitySignal", "insurance market depth", "insurance market depth"),
    SignalSpec("LaborAvailabilitySignal", "contractor availability", "contractor availability"),
    SignalSpec("LiquiditySignal", "buyer depth", "buyer depth"),
    SignalSpec("MigrationSignal", "inbound household migration", "inbound household migration"),
    SignalSpec("NeighborhoodMomentumSignal", "neighborhood momentum", "neighborhood momentum"),
    SignalSpec("PermitSupplySignal", "new supply pipeline", "new supply pipeline"),
    SignalSpec("PropertyTaxSignal", "tax reassessment pressure", "tax reassessment pressure"),
    SignalSpec("RateSensitivitySignal", "interest-rate sensitivity", "interest-rate sensitivity"),
    SignalSpec("RentCompDepthSignal", "rent-comp breadth", "rent-comp breadth"),
    SignalSpec("RentControlSignal", "regulatory rent restrictions", "regulatory rent restrictions"),
    SignalSpec("SaleCompDepthSignal", "sale-comp breadth", "sale-comp breadth"),
    SignalSpec("SchoolDemandSignal", "school-driven demand", "school-driven demand"),
    SignalSpec("SubmarketVolatilitySignal", "submarket volatility", "submarket volatility"),
    SignalSpec("TenantIncomeSignal", "tenant income support", "tenant income support"),
    SignalSpec("TransitCommuteSignal", "commute accessibility", "commute accessibility"),
]


def _build_signal_class(spec: SignalSpec) -> type[BaseSignal]:
    """Build a configured ``BaseSignal`` subclass with the original class name."""
    cls = type(
        spec.class_name,
        (BaseSignal,),
        {
            "name": spec.name,
            "description": spec.description,
            "spec": spec,
            "__doc__": f"Research signal for {spec.description}.",
            "__module__": __name__,
        },
    )
    return cls


# {ClassName: configured BaseSignal subclass}
SIGNAL_REGISTRY: dict[str, type[BaseSignal]] = {
    spec.class_name: _build_signal_class(spec) for spec in SIGNAL_SPECS
}

# Bind each generated class as a module-level name so it is importable directly.
globals().update(SIGNAL_REGISTRY)

__all__ = ["BaseSignal", "SignalObservation", "SignalSpec", "SIGNAL_SPECS", "SIGNAL_REGISTRY", *SIGNAL_REGISTRY]
