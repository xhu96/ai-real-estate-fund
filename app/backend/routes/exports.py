from __future__ import annotations
from fastapi import APIRouter, Response
from ai_real_estate_fund.models import PropertyInput
from ai_real_estate_fund.investment_committee import run_property_committee
from ai_real_estate_fund.report import render_diligence_memo
router = APIRouter(prefix="/exports", tags=["exports"])
@router.post("/memo.md")
def export_memo(payload: dict):
    decision = run_property_committee(PropertyInput.from_dict(payload))
    return Response(render_diligence_memo(decision), media_type="text/markdown")
