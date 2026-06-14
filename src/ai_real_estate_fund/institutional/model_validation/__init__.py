"""Model validation and governance checks for the institutional workflow.

The 20 validators in this package were structurally identical clones differing
only by a label and class names. They are now generated from a single
``BaseValidator`` plus a list of specs (see :mod:`.base` and :mod:`.specs`).
The original class names are re-exported here so that
``from ai_real_estate_fund.institutional.model_validation import <ClassName>``
keeps working and ``<ClassName>()`` constructs the right configured instance.
"""

from .base import BaseValidator, DictLikeDecision, ValidatorResult, ValidatorSpec
from .specs import REGISTRY, SPECS, VALIDATOR_NAMES, build_registry

# Re-export every generated validator + result class at the package level.
globals().update(REGISTRY)

__all__ = [
    "BaseValidator",
    "DictLikeDecision",
    "ValidatorResult",
    "ValidatorSpec",
    "REGISTRY",
    "SPECS",
    "VALIDATOR_NAMES",
    "build_registry",
    *sorted(REGISTRY),
]
