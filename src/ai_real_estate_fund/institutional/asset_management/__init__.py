"""Asset-management monitoring modules for the institutional workflow.

The 30 monitors in this family were near-identical clones, each in its own
``*_monitor.py`` module. They are consolidated into a single generic
``Monitor`` base (``base.py``) plus a list of specs and a registry
(``specs.py``). Each original class name is preserved and re-exported here so
``from ai_real_estate_fund.institutional.asset_management import <ClassName>``
keeps working and ``<ClassName>()`` constructs the correctly configured
instance.
"""

from __future__ import annotations

from .base import Monitor, MonitorConfig, MonitorSpec
from .models import MonitoringKPI, MonitoringReport
from .specs import REGISTRY, SPECS, get_monitor_class

# Re-export every preserved class name at the package level.
globals().update(REGISTRY)

__all__ = [
    "Monitor",
    "MonitorConfig",
    "MonitorSpec",
    "MonitoringKPI",
    "MonitoringReport",
    "REGISTRY",
    "SPECS",
    "get_monitor_class",
    *REGISTRY.keys(),
]
