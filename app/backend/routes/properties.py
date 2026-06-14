from __future__ import annotations
from fastapi import APIRouter, Depends
from ..dependencies import require_scope
from ..repositories.property_repository import PropertyRepository
router = APIRouter(prefix="/properties", tags=["properties"])
@router.get("")
def list_properties(limit: int = 50, _: dict = Depends(require_scope("read"))):
    return PropertyRepository().list(limit)
@router.post("")
def create_property(payload: dict, _: dict = Depends(require_scope("write"))):
    property_id = PropertyRepository().save(payload)
    return {"id": property_id, "status": "saved"}
