from __future__ import annotations
from dataclasses import dataclass

@dataclass(slots=True)
class ScheduledJob:
    name: str
    cron: str
    enabled: bool = True
