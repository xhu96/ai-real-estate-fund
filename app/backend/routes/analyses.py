from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from ..dependencies import require_scope
from ..services.analysis_service import AnalysisService
from ..repositories.analysis_repository import AnalysisRepository
router = APIRouter(prefix="/analyses", tags=["analyses"])
@router.post("")
def analyze(payload: dict, _: dict = Depends(require_scope("analyze"))):
    return AnalysisService().analyze(payload)
@router.get("")
def recent(limit: int = 25, _: dict = Depends(require_scope("read"))):
    return AnalysisRepository().list_recent(limit)
@router.get("/{run_id}")
def get_analysis(run_id: str, _: dict = Depends(require_scope("read"))):
    decision = AnalysisRepository().get(run_id)
    if decision is None:
        raise HTTPException(status_code=404, detail=f"analysis run not found: {run_id}")
    return decision
