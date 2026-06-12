from __future__ import annotations
from fastapi import APIRouter
from ..services.validation_service import ValidationService
router = APIRouter(prefix="/validation", tags=["validation"])
@router.post("/calibration")
def calibration(payload: dict):
    return ValidationService().calibration(payload.get("scores", []), payload.get("outcomes", []))
@router.post("/drift")
def drift(payload: dict):
    return ValidationService().drift(payload.get("expected", []), payload.get("actual", []))
