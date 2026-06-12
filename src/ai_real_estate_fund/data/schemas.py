from __future__ import annotations
from dataclasses import asdict, dataclass

@dataclass(slots=True)
class ListingRecord:
    source_id: str
    address: str
    market: str
    price: float
    rent_estimate: float
    beds: int
    baths: float
    sqft: float
    url: str = ""

    def to_dict(self) -> dict[str, object]:
        return asdict(self)

@dataclass(slots=True)
class MarketRecord:
    market: str
    population_growth_yoy: float
    job_growth_yoy: float
    vacancy_rate: float
    rent_growth_yoy: float
    source: str = "fixture"

@dataclass(slots=True)
class PropertyRecord:
    parcel_id: str
    address: str
    year_built: int | None
    assessed_value: float
    annual_tax: float
    owner_name: str = ""
