from __future__ import annotations
import json
from ..database.connection import get_connection
from ..database.migrations import migrate

class PropertyRepository:
    def save(self, payload: dict) -> int:
        migrate()
        with get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO properties (name, address, market, payload_json) VALUES (?, ?, ?, ?)",
                (payload.get("name"), payload.get("address"), payload.get("market"), json.dumps(payload)),
            )
            conn.commit()
            return int(cursor.lastrowid)

    def list(self, limit: int = 50) -> list[dict]:
        migrate()
        with get_connection() as conn:
            rows = conn.execute("SELECT payload_json FROM properties ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [json.loads(row["payload_json"]) for row in rows]
