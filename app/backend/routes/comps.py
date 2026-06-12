from __future__ import annotations
from fastapi import APIRouter
from ..services.comp_service import CompService
router = APIRouter(prefix="/comps", tags=["comps"])
@router.get("/{market}")
def comps(market: str):
    return CompService().comps_for_market(market)
