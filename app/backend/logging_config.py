from __future__ import annotations

import json
import logging
from threading import Lock

from .settings import settings

_CONFIGURED = False
_LOCK = Lock()

_EXTRA_KEYS = ("request_id", "actor", "route", "status_code", "duration_ms")


class _JsonFormatter(logging.Formatter):
    """Minimal stdlib-only JSON-lines formatter for structured logs."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in _EXTRA_KEYS:
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging() -> None:
    """Configure the root logger once from ProductionSettings.

    Idempotent: repeated calls (e.g. when ``create_app`` runs more than once
    in tests) reuse the existing handler instead of stacking duplicates.
    Level comes from ``log_level`` (default INFO); emits JSON lines when
    ``json_logs`` is true, otherwise a concise plain format. Stdlib only.
    """
    global _CONFIGURED
    with _LOCK:
        if _CONFIGURED:
            return

        production = settings.production
        level_name = (getattr(production, "log_level", None) or "INFO").upper()
        level = getattr(logging, level_name, logging.INFO)
        json_logs = bool(getattr(production, "json_logs", False))

        handler = logging.StreamHandler()
        if json_logs:
            handler.setFormatter(_JsonFormatter())
        else:
            handler.setFormatter(
                logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
            )

        root = logging.getLogger()
        root.handlers.clear()
        root.addHandler(handler)
        root.setLevel(level)

        _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a logger by name, ensuring logging is configured first."""
    configure_logging()
    return logging.getLogger(name)
