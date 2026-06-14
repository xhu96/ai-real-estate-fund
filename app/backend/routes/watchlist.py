from __future__ import annotations
from fastapi import APIRouter, Depends
from ..dependencies import require_scope
from ..models.schemas import WatchlistPayload
from ..services.watchlist_service import WatchlistService
router = APIRouter(prefix="/watchlist", tags=["watchlist"])
_service = WatchlistService()
@router.post("")
def add(body: WatchlistPayload, _: dict = Depends(require_scope("write"))):
    return _service.add(body)
