from __future__ import annotations
from dataclasses import dataclass

@dataclass(slots=True)
class ValidationFinding:
    name: str
    status: str
    metric: float
    message: str
