from __future__ import annotations
from fastapi import APIRouter
from ..services.watchlist_service import WatchlistService
router = APIRouter(prefix="/watchlist", tags=["watchlist"])
_service = WatchlistService()
@router.post("")
def add(payload: dict):
    return _service.add(payload)
