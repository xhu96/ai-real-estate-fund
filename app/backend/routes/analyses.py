from __future__ import annotations
from fastapi import APIRouter
from ..services.analysis_service import AnalysisService
from ..repositories.analysis_repository import AnalysisRepository
router = APIRouter(prefix="/analyses", tags=["analyses"])
@router.post("")
def analyze(payload: dict):
    return AnalysisService().analyze(payload)
@router.get("")
def recent(limit: int = 25):
    return AnalysisRepository().list_recent(limit)
