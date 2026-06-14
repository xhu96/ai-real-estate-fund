from __future__ import annotations

from ..models import DiligenceDataBundle, PropertyInput
from .models import DataRoomDocument, DataRoomManifest


DEFAULT_DOCUMENT_BLUEPRINTS: list[tuple[str, str, bool]] = [
    ("Purchase contract or LOI", "transaction", True),
    ("Seller disclosures", "transaction", True),
    ("Trailing 12-month operating statement", "financial", True),
    ("Current rent roll", "income", True),
    ("Lease files", "income", True),
    ("Bank deposit support", "income", False),
    ("Property tax bill", "expenses", True),
    ("Insurance quote or policy", "expenses", True),
    ("Utility bills", "expenses", False),
    ("Repair and maintenance ledger", "expenses", False),
    ("Inspection report", "physical", True),
    ("Roof/HVAC/plumbing/electrical specialist reports", "physical", False),
    ("Renovation scope of work", "capex", True),
    ("Contractor bids", "capex", False),
    ("ALTA title commitment", "legal", True),
    ("Survey", "legal", False),
    ("Zoning confirmation", "legal", True),
    ("Environmental screen", "legal", False),
    ("Rent comps", "market", True),
    ("Sale comps", "market", True),
    ("Lender term sheet", "debt", True),
    ("Appraisal", "debt", False),
    ("Property management proposal", "operations", True),
    ("Reserve budget", "operations", True),
    ("Exit broker opinion of value", "exit", False),
    ("Investment committee memo", "governance", True),
    ("Model version and assumption audit", "governance", True),
]


def _infer_received(name: str, prop: PropertyInput, data: DiligenceDataBundle) -> bool:
    lower = name.lower()
    if "rent comp" in lower:
        return bool(data.rent_comps)
    if "sale comp" in lower:
        return bool(data.sale_comps)
    if "market" in lower:
        return data.market_snapshot.market != "Unknown"
    if "rent roll" in lower or "lease" in lower:
        return prop.monthly_rent > 0 and prop.unit_count > 0
    if "tax" in lower:
        return prop.property_taxes_annual > 0
    if "insurance" in lower:
        return prop.insurance_annual > 0
    if "renovation" in lower or "scope" in lower:
        return prop.rehab_budget > 0
    if "lender" in lower:
        return prop.loan_amount > 0 and prop.annual_interest_rate > 0
    if "model" in lower or "memo" in lower:
        return True
    if "title" in lower or "zoning" in lower or "inspection" in lower or "contract" in lower:
        return False
    return False


def build_data_room_manifest(prop: PropertyInput, data: DiligenceDataBundle) -> DataRoomManifest:
    documents: list[DataRoomDocument] = []
    for name, category, required in DEFAULT_DOCUMENT_BLUEPRINTS:
        received = _infer_received(name, prop, data)
        freshness = 60 if received and category in {"financial", "income", "market", "expenses"} else None
        documents.append(
            DataRoomDocument(
                name=name,
                category=category,
                required=required,
                received=received,
                freshness_days=freshness,
                source="inferred_from_property_payload" if received else "missing",
                notes="Auto-inferred by the data-room review; replace with real document tracking in production.",
            )
        )
    return DataRoomManifest(documents=documents, generated_from=prop.source or "manual")


def diligence_readiness_label(manifest: DataRoomManifest) -> str:
    score = manifest.completeness_score()
    if score >= 85:
        return "committee-ready"
    if score >= 65:
        return "diligence-in-progress"
    return "screening-only"


def missing_document_actions(manifest: DataRoomManifest) -> list[str]:
    return [f"Upload or verify: {doc.name}" for doc in manifest.missing_required_documents()[:10]]

