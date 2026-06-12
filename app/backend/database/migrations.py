from __future__ import annotations

from .connection import get_connection
from .models import SCHEMA_SQL, SCHEMA_VERSION


def migrate() -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA_SQL)
        conn.execute("INSERT OR IGNORE INTO schema_migrations (version) VALUES (?)", (SCHEMA_VERSION,))
        conn.commit()
