from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any

@dataclass(slots=True)
class DomainEvent:
    event_type: str
    payload: dict[str, Any]
    created_at: str = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
