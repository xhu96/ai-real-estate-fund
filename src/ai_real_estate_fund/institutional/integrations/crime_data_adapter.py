from __future__ import annotations

"""Offline adapter stub for crime data.

The adapter exposes the contract a production integration would follow:
connection metadata, query planning, response normalization, quality
checks, and provenance. It deliberately returns deterministic fixture
data so tests can run without network access or paid data licenses.
"""

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class CrimeDataAdapterRecord:
    source: str
    external_id: str
    fields: dict[str, Any]
    confidence: float = 0.70
    as_of: str = ""
    provenance: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class CrimeDataAdapterQuery:
    address: str
    market: str = ""
    parcel_id: str = ""
    limit: int = 25
    include_raw: bool = False

    def cache_key(self) -> str:
        return "|".join([self.address.lower().strip(), self.market.lower().strip(), self.parcel_id.lower().strip(), str(self.limit)])


class CrimeDataAdapter:
    provider_name = 'crime data'
    expected_fields = ['incident_type', 'date', 'location', 'severity']

    def __init__(self, enabled: bool = False, base_url: str = "", api_key_env: str = "") -> None:
        self.enabled = enabled
        self.base_url = base_url
        self.api_key_env = api_key_env

    def describe(self) -> dict[str, Any]:
        return {
            "provider_name": self.provider_name,
            "enabled": self.enabled,
            "base_url": self.base_url,
            "api_key_env": self.api_key_env,
            "expected_fields": list(self.expected_fields),
            "mode": "offline_fixture" if not self.enabled else "external",
        }

    def plan_query(self, query: CrimeDataAdapterQuery) -> dict[str, Any]:
        return {
            "cache_key": query.cache_key(),
            "address": query.address,
            "market": query.market,
            "parcel_id": query.parcel_id,
            "limit": query.limit,
            "provider": self.provider_name,
        }

    def fetch(self, query: CrimeDataAdapterQuery) -> list[CrimeDataAdapterRecord]:
        planned = self.plan_query(query)
        return [
            CrimeDataAdapterRecord(
                source=self.provider_name,
                external_id=f"{planned['cache_key']}::{index}",
                fields={field_name: self.fixture_value(field_name, index) for field_name in self.expected_fields},
                confidence=max(0.45, 0.82 - index * 0.03),
                as_of="fixture",
                provenance={"mode": "offline", "cache_key": planned["cache_key"]},
            )
            for index in range(min(query.limit, 3))
        ]

    def fixture_value(self, field_name: str, index: int) -> Any:
        if "date" in field_name or "year" in field_name:
            return "2026-01-01"
        if "rate" in field_name or "cap" in field_name or "confidence" in field_name:
            return round(0.05 + index * 0.01, 4)
        if "price" in field_name or "value" in field_name or "rent" in field_name or "premium" in field_name:
            return 100000 + index * 12500
        if "latitude" in field_name:
            return 29.7604
        if "longitude" in field_name:
            return -95.3698
        if "score" in field_name or "rating" in field_name:
            return 6 + index
        return f"{field_name}_fixture_{index}"

    def normalize(self, records: list[CrimeDataAdapterRecord]) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for record in records:
            payload = record.to_dict()
            payload["quality_warnings"] = self.quality_warnings(record)
            normalized.append(payload)
        return normalized

    def quality_warnings(self, record: CrimeDataAdapterRecord) -> list[str]:
        warnings: list[str] = []
        missing = [field for field in self.expected_fields if field not in record.fields]
        if missing:
            warnings.append(f"Missing expected fields: {', '.join(missing)}")
        if record.confidence < 0.60:
            warnings.append("Low-confidence provider response.")
        if not record.as_of:
            warnings.append("Provider record lacks as_of date.")
        return warnings

