from __future__ import annotations

from fastapi import APIRouter, Depends

from ai_real_estate_fund.institutional.agents import AGENT_SPECS
from ..dependencies import require_scope

router = APIRouter(prefix="/committee", tags=["committee"])

# Canonical category order with display labels.
_CATEGORY_LABELS: tuple[tuple[str, str], ...] = (
    ("acquisition", "Acquisition"),
    ("income", "Income"),
    ("expenses", "Expenses"),
    ("debt", "Debt"),
    ("physical", "Physical condition"),
    ("market", "Market"),
    ("portfolio", "Portfolio & returns"),
    ("governance", "Governance"),
)


def _serialize_agent(spec) -> dict:
    return {
        "name": spec.name,
        "weight": spec.weight,
        "role": spec.role,
        "focus_components": list(spec.focus_components),
        "positive": spec.positive,
        "concern": spec.concern,
        "action": spec.action,
        "sources": list(spec.sources),
    }


@router.get("/roster")
def roster(_: dict = Depends(require_scope("read"))) -> dict:
    grouped: dict[str, list[dict]] = {key: [] for key, _label in _CATEGORY_LABELS}
    for spec in AGENT_SPECS:
        grouped[spec.category].append(_serialize_agent(spec))
    categories = [
        {
            "key": key,
            "label": label,
            "count": len(grouped[key]),
            "agents": grouped[key],
        }
        for key, label in _CATEGORY_LABELS
    ]
    return {"total": len(AGENT_SPECS), "categories": categories}
