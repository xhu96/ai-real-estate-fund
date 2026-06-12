from __future__ import annotations
import json
from ..database.connection import get_connection
from ..database.migrations import migrate

class CompRepository:
    def save_set(self, market: str, comp_type: str, payload: list[dict]) -> None:
        migrate()
        with get_connection() as conn:
            conn.execute("INSERT INTO comp_sets (market, comp_type, payload_json) VALUES (?, ?, ?)", (market, comp_type, json.dumps(payload)))
            conn.commit()

    def list_sets(self, market: str | None = None) -> list[dict]:
        migrate()
        sql = "SELECT market, comp_type, payload_json FROM comp_sets"
        params = ()
        if market:
            sql += " WHERE market = ?"
            params = (market,)
        with get_connection() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [{"market": r["market"], "comp_type": r["comp_type"], "items": json.loads(r["payload_json"])} for r in rows]
