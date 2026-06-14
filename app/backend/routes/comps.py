from __future__ import annotations
from fastapi import APIRouter, Depends
from ..dependencies import require_scope
from ..services.comp_service import CompService
router = APIRouter(prefix="/comps", tags=["comps"])
@router.get("/{market}")
def comps(market: str, _: dict = Depends(require_scope("read"))):
    return CompService().comps_for_market(market)
