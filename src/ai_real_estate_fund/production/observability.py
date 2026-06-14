from __future__ import annotations

import json
import logging
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from threading import Lock
from typing import Any, Iterator


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # pragma: no cover - exercised through integration use
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in ("request_id", "actor", "route", "status_code", "duration_ms"):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(*, level: str = "INFO", json_logs: bool = True) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter() if json_logs else logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(getattr(logging, level.upper(), logging.INFO))


@dataclass(slots=True)
class MetricSeries:
    name: str
    help: str
    value: float = 0.0
    labels: dict[str, str] = field(default_factory=dict)

    def line(self) -> str:
        if self.labels:
            labels = ",".join(f'{key}="{value}"' for key, value in sorted(self.labels.items()))
            return f"{self.name}{{{labels}}} {self.value}"
        return f"{self.name} {self.value}"


class MetricsRegistry:
    """Tiny Prometheus-text registry for dependency-light deployments."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._metrics: dict[tuple[str, tuple[tuple[str, str], ...]], MetricSeries] = {}

    def _key(self, name: str, labels: dict[str, str] | None) -> tuple[str, tuple[tuple[str, str], ...]]:
        return (name, tuple(sorted((labels or {}).items())))

    def inc(self, name: str, *, amount: float = 1.0, help_text: str = "", labels: dict[str, str] | None = None) -> None:
        with self._lock:
            key = self._key(name, labels)
            metric = self._metrics.get(key) or MetricSeries(name=name, help=help_text or name, labels=labels or {})
            metric.value += amount
            self._metrics[key] = metric

    def set(self, name: str, value: float, *, help_text: str = "", labels: dict[str, str] | None = None) -> None:
        with self._lock:
            self._metrics[self._key(name, labels)] = MetricSeries(name=name, help=help_text or name, value=value, labels=labels or {})

    def to_prometheus(self) -> str:
        with self._lock:
            metrics = list(self._metrics.values())
        lines: list[str] = []
        emitted_help: set[str] = set()
        for metric in sorted(metrics, key=lambda item: (item.name, sorted(item.labels.items()))):
            if metric.name not in emitted_help:
                lines.append(f"# HELP {metric.name} {metric.help}")
                lines.append(f"# TYPE {metric.name} gauge")
                emitted_help.add(metric.name)
            lines.append(metric.line())
        return "\n".join(lines) + ("\n" if lines else "")

    def snapshot(self) -> list[dict[str, Any]]:
        with self._lock:
            return [asdict(metric) for metric in self._metrics.values()]


metrics = MetricsRegistry()


@contextmanager
def track_timing(metric_name: str, *, labels: dict[str, str] | None = None) -> Iterator[None]:
    start = time.perf_counter()
    try:
        yield
        metrics.inc(f"{metric_name}_success_total", labels=labels)
    except Exception:
        metrics.inc(f"{metric_name}_error_total", labels=labels)
        raise
    finally:
        metrics.set(f"{metric_name}_last_duration_ms", (time.perf_counter() - start) * 1000.0, labels=labels)
