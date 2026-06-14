from __future__ import annotations
import json
from ..database.connection import get_connection
from ..database.migrations import migrate

class AnalysisRepository:
    def save(self, decision: dict) -> None:
        migrate()
        with get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO analysis_runs (run_id, property_name, recommendation, overall_score, payload_json) VALUES (?, ?, ?, ?, ?)",
                (decision["run_id"], decision["property"]["name"], decision["recommendation"], decision["overall_score"], json.dumps(decision)),
            )
            conn.commit()

    def list_recent(self, limit: int = 25) -> list[dict]:
        migrate()
        with get_connection() as conn:
            rows = conn.execute("SELECT payload_json FROM analysis_runs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [json.loads(row["payload_json"]) for row in rows]

    def get(self, run_id: str) -> dict | None:
        migrate()
        with get_connection() as conn:
            row = conn.execute("SELECT payload_json FROM analysis_runs WHERE run_id = ?", (run_id,)).fetchone()
        return json.loads(row["payload_json"]) if row else None
