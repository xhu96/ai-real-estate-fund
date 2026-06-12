from __future__ import annotations
from fastapi import APIRouter
from ..services.portfolio_service import PortfolioService
router = APIRouter(prefix="/portfolio", tags=["portfolio"])
@router.post("/optimize")
def optimize(payload: dict):
    return PortfolioService().optimize(payload)
