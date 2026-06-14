"""Specs + registry for the offline data-integration adapters.

Each original ``*_adapter.py`` clone collapsed to one :class:`AdapterSpec`
entry (values extracted verbatim from the original file). The registry
generates, per spec, three classes whose names match the originals
exactly:

* ``<Prefix>Adapter``       — configured :class:`~.base.Adapter` subclass
* ``<Prefix>AdapterQuery``  — :class:`~.base.AdapterQuery` subclass
* ``<Prefix>AdapterRecord`` — :class:`~.base.AdapterRecord` subclass

so ``from ai_real_estate_fund.institutional.integrations import <Name>``
works and ``<Name>()`` constructs the right configured instance.
"""

from __future__ import annotations

from .base import Adapter, AdapterQuery, AdapterRecord, AdapterSpec

# One short entry per original class. provider_name + expected_fields are
# copied verbatim from each original *_adapter.py file.
SPECS: list[AdapterSpec] = [
    AdapterSpec("Accounting", "accounting system", ("trial_balance", "general_ledger", "cash_receipts", "payables")),
    AdapterSpec("Appraisal", "appraisal reports", ("value", "approach", "cap_rate", "comps")),
    AdapterSpec("Avm", "automated valuation", ("value", "confidence", "range_low", "range_high")),
    AdapterSpec("BankStatement", "bank statements", ("deposit", "withdrawal", "date", "counterparty")),
    AdapterSpec("BrokerOpinion", "broker opinions", ("value_range", "cap_rate", "buyer_pool", "marketing_time")),
    AdapterSpec("BuildingPermit", "building permits", ("permit_type", "units", "value", "issued_date")),
    AdapterSpec("Census", "census data", ("population", "households", "income", "renter_share")),
    AdapterSpec("ClimateRisk", "climate risk", ("flood", "wildfire", "wind", "heat")),
    AdapterSpec("ContractorBid", "contractor bids", ("trade", "scope", "cost", "duration")),
    AdapterSpec("CountyAssessor", "county assessor", ("parcel_id", "assessed_value", "tax_year", "owner_name")),
    AdapterSpec("CountyRecorder", "county recorder", ("deed_date", "grantor", "grantee", "recording_number")),
    AdapterSpec("CrimeData", "crime data", ("incident_type", "date", "location", "severity")),
    AdapterSpec("DocumentStorage", "document storage", ("document_id", "category", "uploaded_at", "checksum")),
    AdapterSpec("Employment", "employment data", ("jobs", "unemployment", "wages", "industry")),
    AdapterSpec("FloodMap", "flood maps", ("fema_zone", "base_flood_elevation", "panel", "effective_date")),
    AdapterSpec("Geocoder", "geocoding", ("latitude", "longitude", "confidence", "match_type")),
    AdapterSpec("Inspection", "inspection reports", ("system", "condition", "severity", "cost")),
    AdapterSpec("InsuranceQuote", "insurance quotes", ("premium", "deductible", "coverage", "exclusions")),
    AdapterSpec("LenderQuote", "lender quotes", ("interest_rate", "term", "amortization", "fees")),
    AdapterSpec("PropertyManagement", "property management", ("rent_roll", "ledger", "work_orders", "leases")),
    AdapterSpec("RentListing", "rent listings", ("asking_rent", "bedrooms", "bathrooms", "days_on_market")),
    AdapterSpec("SaleListing", "sale listings", ("asking_price", "sale_price", "close_date", "days_on_market")),
    AdapterSpec("SchoolData", "school data", ("school_name", "rating", "assignment", "distance")),
    AdapterSpec("Title", "title commitment", ("exceptions", "easements", "liens", "vesting")),
    AdapterSpec("Zoning", "zoning data", ("district", "use", "density", "parking")),
]


def _build(spec: AdapterSpec) -> tuple[type, type, type]:
    """Generate the three preserved-name classes for one spec."""
    record_cls = type(f"{spec.prefix}AdapterRecord", (AdapterRecord,), {})
    query_cls = type(f"{spec.prefix}AdapterQuery", (AdapterQuery,), {})
    adapter_cls = type(
        f"{spec.prefix}Adapter",
        (Adapter,),
        {
            "provider_name": spec.provider_name,
            "expected_fields": list(spec.expected_fields),
            "_record_cls": record_cls,
        },
    )
    return adapter_cls, query_cls, record_cls


# Registry: original class name -> generated class.
REGISTRY: dict[str, type] = {}
for _spec in SPECS:
    _adapter_cls, _query_cls, _record_cls = _build(_spec)
    REGISTRY[_adapter_cls.__name__] = _adapter_cls
    REGISTRY[_query_cls.__name__] = _query_cls
    REGISTRY[_record_cls.__name__] = _record_cls

__all__ = ["SPECS", "REGISTRY"]
