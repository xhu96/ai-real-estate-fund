from __future__ import annotations

import hashlib
import json
import sqlite3
from contextlib import closing
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS audit_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    actor TEXT NOT NULL,
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    request_id TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    previous_hash TEXT NOT NULL,
    event_hash TEXT NOT NULL UNIQUE
);
CREATE INDEX IF NOT EXISTS idx_audit_created_at ON audit_events(created_at);
CREATE INDEX IF NOT EXISTS idx_audit_actor ON audit_events(actor);
CREATE INDEX IF NOT EXISTS idx_audit_resource ON audit_events(resource_type, resource_id);
"""


@dataclass(frozen=True, slots=True)
class AuditEvent:
    actor: str
    action: str
    resource_type: str
    resource_id: str
    payload: dict[str, Any] = field(default_factory=dict)
    request_id: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    previous_hash: str = ""
    event_hash: str = ""

    def canonical_payload_json(self) -> str:
        return json.dumps(self.payload, sort_keys=True, separators=(",", ":"), default=str)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def event_digest(event: AuditEvent) -> str:
    parts = [
        event.created_at,
        event.actor,
        event.action,
        event.resource_type,
        event.resource_id,
        event.request_id,
        event.canonical_payload_json(),
        event.previous_hash,
    ]
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


class SQLiteAuditLog:
    """Append-only audit log with hash-chain verification."""

    def __init__(self, path: str | Path = "data/audit.db") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.migrate()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def migrate(self) -> None:
        with closing(self._connect()) as conn:
            conn.executescript(SCHEMA_SQL)
            conn.commit()

    def latest_hash(self) -> str:
        with closing(self._connect()) as conn:
            row = conn.execute("SELECT event_hash FROM audit_events ORDER BY id DESC LIMIT 1").fetchone()
        return "GENESIS" if row is None else str(row["event_hash"])

    def append(self, event: AuditEvent) -> AuditEvent:
        previous_hash = self.latest_hash()
        prepared = AuditEvent(
            actor=event.actor,
            action=event.action,
            resource_type=event.resource_type,
            resource_id=event.resource_id,
            payload=event.payload,
            request_id=event.request_id,
            created_at=event.created_at,
            previous_hash=previous_hash,
        )
        signed = AuditEvent(
            actor=prepared.actor,
            action=prepared.action,
            resource_type=prepared.resource_type,
            resource_id=prepared.resource_id,
            payload=prepared.payload,
            request_id=prepared.request_id,
            created_at=prepared.created_at,
            previous_hash=prepared.previous_hash,
            event_hash=event_digest(prepared),
        )
        with closing(self._connect()) as conn:
            conn.execute(
                """
                INSERT INTO audit_events
                (created_at, actor, action, resource_type, resource_id, request_id, payload_json, previous_hash, event_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    signed.created_at,
                    signed.actor,
                    signed.action,
                    signed.resource_type,
                    signed.resource_id,
                    signed.request_id,
                    signed.canonical_payload_json(),
                    signed.previous_hash,
                    signed.event_hash,
                ),
            )
            conn.commit()
        return signed

    def list_events(self, *, limit: int = 100) -> list[AuditEvent]:
        limit = max(1, min(limit, 1000))
        with closing(self._connect()) as conn:
            rows = conn.execute("SELECT * FROM audit_events ORDER BY id ASC LIMIT ?", (limit,)).fetchall()
        events: list[AuditEvent] = []
        for row in rows:
            events.append(
                AuditEvent(
                    actor=row["actor"],
                    action=row["action"],
                    resource_type=row["resource_type"],
                    resource_id=row["resource_id"],
                    payload=json.loads(row["payload_json"]),
                    request_id=row["request_id"],
                    created_at=row["created_at"],
                    previous_hash=row["previous_hash"],
                    event_hash=row["event_hash"],
                )
            )
        return events

    def verify_chain(self) -> tuple[bool, list[str]]:
        errors: list[str] = []
        expected_previous = "GENESIS"
        for idx, event in enumerate(self.list_events(limit=1000), start=1):
            if event.previous_hash != expected_previous:
                errors.append(f"event {idx} previous_hash mismatch")
            expected_hash = event_digest(AuditEvent(
                actor=event.actor,
                action=event.action,
                resource_type=event.resource_type,
                resource_id=event.resource_id,
                payload=event.payload,
                request_id=event.request_id,
                created_at=event.created_at,
                previous_hash=event.previous_hash,
            ))
            if event.event_hash != expected_hash:
                errors.append(f"event {idx} event_hash mismatch")
            expected_previous = event.event_hash
        return (not errors, errors)
