from __future__ import annotations
from fastapi import APIRouter, Depends
from ai_real_estate_fund.scenarios import build_scenarios
from ..dependencies import require_scope
from ..utils.parsing import parse_property_input
router = APIRouter(prefix="/scenarios", tags=["scenarios"])
@router.post("")
def scenarios(payload: dict, _: dict = Depends(require_scope("analyze"))):
    prop = parse_property_input(payload)
    return [s.to_dict() for s in build_scenarios(prop)]
