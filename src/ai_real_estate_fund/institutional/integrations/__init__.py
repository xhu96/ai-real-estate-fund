"""Adapter interfaces and offline stubs for future real-estate data integrations.

The 25 provider adapters were collapsed into one generic base
(:mod:`.base`) plus a list of specs (:mod:`.specs`). The original class
names (``<Provider>Adapter`` / ``<Provider>AdapterQuery`` /
``<Provider>AdapterRecord``) are preserved and re-exported here so
``from ai_real_estate_fund.institutional.integrations import <Name>``
keeps working and ``<Name>()`` constructs the right configured instance.
"""

from .base import Adapter, AdapterQuery, AdapterRecord, AdapterSpec
from .specs import REGISTRY, SPECS

# Bind every preserved class name into this module's namespace.
globals().update(REGISTRY)

__all__ = [
    "Adapter",
    "AdapterQuery",
    "AdapterRecord",
    "AdapterSpec",
    "SPECS",
    "REGISTRY",
    *sorted(REGISTRY),
]
