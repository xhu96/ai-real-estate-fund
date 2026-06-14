"""Market and model-research utilities for v5.

The per-signal ``*_signal.py`` clones were consolidated into a single
``BaseSignal`` (see :mod:`.base`) plus a registry of specs (see :mod:`.specs`).
Each original class name is re-exported here so that
``from ai_real_estate_fund.institutional.research import <ClassName>`` works and
``<ClassName>()`` constructs the original configured instance.
"""

from .base import BaseSignal, SignalObservation, SignalSpec
from .specs import SIGNAL_REGISTRY, SIGNAL_SPECS

# Re-export every original Signal class name at the package level.
globals().update(SIGNAL_REGISTRY)

__all__ = [
    "BaseSignal",
    "SignalObservation",
    "SignalSpec",
    "SIGNAL_SPECS",
    "SIGNAL_REGISTRY",
    *SIGNAL_REGISTRY,
]
