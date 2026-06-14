from __future__ import annotations

from dataclasses import dataclass
from time import monotonic


@dataclass(frozen=True, slots=True)
class RateLimitDecision:
    allowed: bool
    remaining: int
    retry_after_seconds: float = 0.0

    def to_dict(self) -> dict[str, float | int | bool]:
        return {
            "allowed": self.allowed,
            "remaining": self.remaining,
            "retry_after_seconds": round(self.retry_after_seconds, 3),
        }


class InMemoryRateLimiter:
    """Token-bucket limiter suitable for one API process.

    Multi-instance production deployments should replace this with Redis or the
    platform load balancer's quota controls. Keeping this implementation in the
    repo makes the failure mode explicit and testable.
    """

    def __init__(self, *, limit: int = 120, window_seconds: int = 60) -> None:
        if limit <= 0 or window_seconds <= 0:
            raise ValueError("limit and window_seconds must be positive")
        self.limit = limit
        self.window_seconds = window_seconds
        self._buckets: dict[str, tuple[int, float]] = {}

    def check(self, key: str) -> RateLimitDecision:
        now = monotonic()
        count, reset_at = self._buckets.get(key, (0, now + self.window_seconds))
        if now >= reset_at:
            count, reset_at = 0, now + self.window_seconds
        if count >= self.limit:
            return RateLimitDecision(False, 0, max(0.0, reset_at - now))
        count += 1
        self._buckets[key] = (count, reset_at)
        return RateLimitDecision(True, self.limit - count, 0.0)

    def reset(self) -> None:
        self._buckets.clear()
