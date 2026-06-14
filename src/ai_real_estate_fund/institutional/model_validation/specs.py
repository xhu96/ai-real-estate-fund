"""Per-validator specs + registry for the model_validation clone family.

Each entry holds the constants extracted verbatim from one original clone file.
The registry generates one ``BaseValidator`` subclass and one ``ValidatorResult``
subclass per spec, naming them exactly as the originals so that
``from ...model_validation import <ClassName>`` keeps working and
``<ClassName>()`` constructs the right configured instance.
"""

from __future__ import annotations

from .base import BaseValidator, ValidatorResult, ValidatorSpec

# Values below are extracted VERBATIM from each original <module>.py file:
#   description  <- the module docstring  ("""Model-validation check for ...""")
#   name         <- the `name = '...'` class constant
#   class_name / result_class_name <- the original public class names
SPECS: list[ValidatorSpec] = [
    ValidatorSpec("agent_score_drift", "AgentScoreDriftValidator", "AgentScoreDriftValidatorResult", "agent score drift", "Model-validation check for agent score drift."),
    ValidatorSpec("allocation_reasonableness", "AllocationReasonablenessValidator", "AllocationReasonablenessValidatorResult", "allocation reasonableness", "Model-validation check for allocation reasonableness."),
    ValidatorSpec("assumption_staleness", "AssumptionStalenessValidator", "AssumptionStalenessValidatorResult", "assumption staleness", "Model-validation check for assumption staleness."),
    ValidatorSpec("calibration_curve", "CalibrationCurveValidator", "CalibrationCurveValidatorResult", "calibration curve", "Model-validation check for calibration curve."),
    ValidatorSpec("capital_stack_consistency", "CapitalStackConsistencyValidator", "CapitalStackConsistencyValidatorResult", "capital-stack consistency", "Model-validation check for capital-stack consistency."),
    ValidatorSpec("committee_dissent", "CommitteeDissentValidator", "CommitteeDissentValidatorResult", "committee dissent", "Model-validation check for committee dissent."),
    ValidatorSpec("data_room_traceability", "DataRoomTraceabilityValidator", "DataRoomTraceabilityValidatorResult", "data-room traceability", "Model-validation check for data-room traceability."),
    ValidatorSpec("formula_reconciliation", "FormulaReconciliationValidator", "FormulaReconciliationValidatorResult", "formula reconciliation", "Model-validation check for formula reconciliation."),
    ValidatorSpec("hard_stop_enforcement", "HardStopEnforcementValidator", "HardStopEnforcementValidatorResult", "hard-stop enforcement", "Model-validation check for hard-stop enforcement."),
    ValidatorSpec("memo_consistency", "MemoConsistencyValidator", "MemoConsistencyValidatorResult", "memo consistency", "Model-validation check for memo consistency."),
    ValidatorSpec("outcome_backtest", "OutcomeBacktestValidator", "OutcomeBacktestValidatorResult", "outcome backtest", "Model-validation check for outcome backtest."),
    ValidatorSpec("override_audit", "OverrideAuditValidator", "OverrideAuditValidatorResult", "override audit", "Model-validation check for override audit."),
    ValidatorSpec("policy_gate_audit", "PolicyGateAuditValidator", "PolicyGateAuditValidatorResult", "policy gate audit", "Model-validation check for policy gate audit."),
    ValidatorSpec("production_readiness", "ProductionReadinessValidator", "ProductionReadinessValidatorResult", "production-readiness controls", "Model-validation check for production-readiness controls."),
    ValidatorSpec("risk_register_coverage", "RiskRegisterCoverageValidator", "RiskRegisterCoverageValidatorResult", "risk-register coverage", "Model-validation check for risk-register coverage."),
    ValidatorSpec("scenario_coverage", "ScenarioCoverageValidator", "ScenarioCoverageValidatorResult", "scenario coverage", "Model-validation check for scenario coverage."),
    ValidatorSpec("sensitivity_direction", "SensitivityDirectionValidator", "SensitivityDirectionValidatorResult", "sensitivity direction", "Model-validation check for sensitivity direction."),
    ValidatorSpec("source_concentration", "SourceConcentrationValidator", "SourceConcentrationValidatorResult", "source concentration", "Model-validation check for source concentration."),
    ValidatorSpec("stress_coverage", "StressCoverageValidator", "StressCoverageValidatorResult", "stress coverage", "Model-validation check for stress coverage."),
    ValidatorSpec("version_control", "VersionControlValidator", "VersionControlValidatorResult", "version-control evidence", "Model-validation check for version-control evidence."),
]


def _build_result_class(spec: ValidatorSpec) -> type[ValidatorResult]:
    """Generate the per-validator ``*ValidatorResult`` subclass with its name."""
    return type(spec.result_class_name, (ValidatorResult,), {"__doc__": spec.description})


def _build_validator_class(spec: ValidatorSpec, result_cls: type[ValidatorResult]) -> type[BaseValidator]:
    """Generate the per-validator ``*Validator`` subclass bound to its spec."""
    return type(
        spec.class_name,
        (BaseValidator,),
        {
            "name": spec.name,
            "spec": spec,
            "result_class": result_cls,
            "__doc__": spec.description,
        },
    )


def build_registry() -> dict[str, type]:
    """Return {class_name: class} for every validator and result class."""
    registry: dict[str, type] = {}
    for spec in SPECS:
        result_cls = _build_result_class(spec)
        validator_cls = _build_validator_class(spec, result_cls)
        registry[spec.result_class_name] = result_cls
        registry[spec.class_name] = validator_cls
    return registry


REGISTRY: dict[str, type] = build_registry()
VALIDATOR_NAMES: list[str] = [spec.class_name for spec in SPECS]
