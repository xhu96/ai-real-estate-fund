from __future__ import annotations
from fastapi import APIRouter, Depends
from ..dependencies import require_scope
from ..models.schemas import BacktestPayload
from ..services.backtest_service import BacktestService
router = APIRouter(prefix="/research", tags=["research"])
@router.post("/backtest")
def backtest(body: BacktestPayload, _: dict = Depends(require_scope("analyze"))):
    return BacktestService().run(body)
