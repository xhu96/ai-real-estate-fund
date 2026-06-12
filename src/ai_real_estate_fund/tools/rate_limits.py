from __future__ import annotations
from dataclasses import dataclass, field
from time import time

@dataclass(slots=True)
class TokenBucket:
    capacity: int
    refill_per_second: float
    tokens: float = field(init=False)
    last_refill: float = field(default_factory=time)

    def __post_init__(self) -> None:
        self.tokens = float(self.capacity)

    def allow(self) -> bool:
        now = time()
        self.tokens = min(self.capacity, self.tokens + (now - self.last_refill) * self.refill_per_second)
        self.last_refill = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False
