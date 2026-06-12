from __future__ import annotations
from fastapi import APIRouter
router = APIRouter(prefix="/storage", tags=["storage"])
@router.get("/status")
def status():
    return {"storage": "sqlite", "status": "configured"}
