from __future__ import annotations
from fastapi import APIRouter, Depends
from ..dependencies import require_scope
from ..models.schemas import OptimizeRunsPayload, PortfolioPayload
from ..services.portfolio_service import PortfolioService
router = APIRouter(prefix="/portfolio", tags=["portfolio"])
@router.post("/optimize")
def optimize(body: PortfolioPayload, _: dict = Depends(require_scope("analyze"))):
    return PortfolioService().optimize(body)
@router.post("/optimize-runs")
def optimize_runs(body: OptimizeRunsPayload, _: dict = Depends(require_scope("analyze"))):
    return PortfolioService().optimize_from_runs(body)
