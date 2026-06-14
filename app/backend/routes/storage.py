from __future__ import annotations
from fastapi import APIRouter, Depends
from ..dependencies import require_scope
router = APIRouter(prefix="/storage", tags=["storage"])
@router.get("/status")
def status(_: dict = Depends(require_scope("read"))):
    return {"storage": "sqlite", "status": "configured"}
