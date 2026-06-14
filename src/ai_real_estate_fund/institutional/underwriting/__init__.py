"""Detailed underwriting components.

The 25 underwriting models were near-identical clones. They are now generated
from a single :class:`~.base.Model` plus a list of specs in :mod:`.specs`. The
original class names are re-exported here so that
``from ai_real_estate_fund.institutional.underwriting import <ClassName>``
keeps working and ``<ClassName>()`` constructs the right configured instance.
"""

from __future__ import annotations

from .base import Model, ModelResult, ModelSpec
from .specs import REGISTRY, SPECS

# Re-export each generated class under its original name at package level.
globals().update(REGISTRY)

__all__ = [
    "Model",
    "ModelResult",
    "ModelSpec",
    "REGISTRY",
    "SPECS",
    *sorted(REGISTRY),
]
