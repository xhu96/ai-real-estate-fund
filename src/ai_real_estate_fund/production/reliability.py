from __future__ import annotations

from dataclasses import dataclass, field
from time import monotonic, sleep
from typing import Callable, Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    attempts: int = 3
    base_delay_seconds: float = 0.1
    max_delay_seconds: float = 2.0

    def delays(self) -> list[float]:
        values: list[float] = []
        for idx in range(max(self.attempts - 1, 0)):
            values.append(min(self.max_delay_seconds, self.base_delay_seconds * (2 ** idx)))
        return values


def retry_call(func: Callable[[], T], *, policy: RetryPolicy = RetryPolicy(), retry_on: tuple[type[BaseException], ...] = (Exception,)) -> T:
    errors: list[BaseException] = []
    for delay in [0.0, *policy.delays()]:
        if delay:
            sleep(delay)
        try:
            return func()
        except retry_on as exc:  # pragma: no cover - simple branch but important for runtime
            errors.append(exc)
    raise errors[-1]


@dataclass(slots=True)
class CircuitBreaker:
    failure_threshold: int = 5
    recovery_seconds: float = 30.0
    failure_count: int = 0
    opened_at: float | None = None

    def allow(self) -> bool:
        if self.opened_at is None:
            return True
        if monotonic() - self.opened_at >= self.recovery_seconds:
            self.failure_count = 0
            self.opened_at = None
            return True
        return False

    def record_success(self) -> None:
        self.failure_count = 0
        self.opened_at = None

    def record_failure(self) -> None:
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.opened_at = monotonic()


@dataclass(slots=True)
class IdempotencyStore:
    ttl_seconds: float = 3600.0
    _items: dict[str, tuple[float, object]] = field(default_factory=dict)

    def get(self, key: str) -> object | None:
        item = self._items.get(key)
        if item is None:
            return None
        created_at, value = item
        if monotonic() - created_at > self.ttl_seconds:
            self._items.pop(key, None)
            return None
        return value

    def set(self, key: str, value: object) -> None:
        self._items[key] = (monotonic(), value)

    def clear_expired(self) -> int:
        before = len(self._items)
        for key in list(self._items):
            self.get(key)
        return before - len(self._items)
