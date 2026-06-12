from __future__ import annotations
from fastapi import APIRouter
from ..repositories.property_repository import PropertyRepository
router = APIRouter(prefix="/properties", tags=["properties"])
@router.get("")
def list_properties(limit: int = 50):
    return PropertyRepository().list(limit)
@router.post("")
def create_property(payload: dict):
    property_id = PropertyRepository().save(payload)
    return {"id": property_id, "status": "saved"}
