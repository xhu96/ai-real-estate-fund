from __future__ import annotations

import sqlite3
from contextlib import closing
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from .settings import ProductionSettings


@dataclass(frozen=True, slots=True)
class HealthCheck:
    name: str
    status: str
    message: str
    latency_ms: float = 0.0

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class HealthReport:
    status: str
    generated_at: str
    checks: list[HealthCheck] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {"status": self.status, "generated_at": self.generated_at, "checks": [check.to_dict() for check in self.checks]}


def _sqlite_path(url: str) -> Path | None:
    if not url.startswith("sqlite:///"):
        return None
    return Path(url.replace("sqlite:///", ""))


def check_sqlite(url: str, *, name: str) -> HealthCheck:
    path = _sqlite_path(url)
    if path is None:
        return HealthCheck(name=name, status="unknown", message="Non-SQLite database configured; use external DB health checks.")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(path)) as conn:
            conn.execute("SELECT 1").fetchone()
        return HealthCheck(name=name, status="ok", message=f"SQLite database reachable at {path}")
    except Exception as exc:
        return HealthCheck(name=name, status="fail", message=str(exc))


def check_writable_directory(path: Path, *, name: str) -> HealthCheck:
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe = path / ".healthcheck"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return HealthCheck(name=name, status="ok", message=f"{path} is writable")
    except Exception as exc:
        return HealthCheck(name=name, status="fail", message=str(exc))


def run_health_checks(settings: ProductionSettings | None = None) -> HealthReport:
    settings = settings or ProductionSettings.from_env()
    checks = [
        check_sqlite(settings.database_url, name="database"),
        check_sqlite(settings.audit_database_url, name="audit_database"),
        check_writable_directory(settings.artifact_root, name="artifact_root"),
        check_writable_directory(settings.data_root, name="data_root"),
    ]
    status = "ok" if all(check.status in {"ok", "unknown"} for check in checks) else "fail"
    return HealthReport(status=status, generated_at=datetime.now(timezone.utc).isoformat(), checks=checks)
