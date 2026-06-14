from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from ..settings import settings


def sqlite_path() -> Path:
    url = settings.database_url
    if url.startswith("sqlite:///"):
        return Path(url.replace("sqlite:///", ""))
    return Path("data/app.db")


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    path = sqlite_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()
