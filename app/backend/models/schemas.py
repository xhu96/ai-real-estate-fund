from __future__ import annotations
from typing import Any

try:
    from pydantic import BaseModel, Field
except ImportError:  # pragma: no cover
    class BaseModel:  # type: ignore
        pass
    def Field(default=None, **kwargs):  # type: ignore
        return default

class PropertyPayload(BaseModel):
    name: str
    address: str
    market: str
    purchase_price: float
    estimated_arv: float = 0
    monthly_rent: float
    property_type: str = "single_family"
    unit_count: int = 1
    square_feet: float = 0
    bedrooms: int = 0
    bathrooms: float = 0
    year_built: int | None = None
    assumptions: dict[str, Any] = Field(default_factory=dict)

class AnalysisResponse(BaseModel):
    run_id: str
    recommendation: str
    overall_score: float
    memo: dict[str, Any]

class PortfolioPayload(BaseModel):
    total_equity_budget: float
    candidates: list[dict[str, Any]] = Field(default_factory=list)
