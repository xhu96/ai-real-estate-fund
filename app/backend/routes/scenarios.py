from __future__ import annotations
from fastapi import APIRouter
from ai_real_estate_fund.models import PropertyInput
from ai_real_estate_fund.scenarios import build_scenarios
router = APIRouter(prefix="/scenarios", tags=["scenarios"])
@router.post("")
def scenarios(payload: dict):
    prop = PropertyInput.from_dict(payload)
    return [s.to_dict() for s in build_scenarios(prop)]
