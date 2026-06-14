from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


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
    total_equity_budget: float = Field(ge=0)
    candidates: list[dict[str, Any]] = Field(default_factory=list)


class WatchlistPayload(BaseModel):
    name: str
    market: str
    reason: str = "manual"
    target_price: float = 0


class OptimizeRunsPayload(BaseModel):
    total_equity_budget: float = Field(gt=0)
    run_ids: list[str] | None = None
    max_single_asset_pct: float = 0.20
    max_market_pct: float = 0.35
    min_score: float = 60
    min_risk_score: float = 55
    reserve_rate: float = 0.05


class BacktestPayload(BaseModel):
    min_score: float = 65
    starting_equity: float = 1_000_000
    max_positions: int = 10
    allocation_per_deal: float = 0.10
