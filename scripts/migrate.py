#!/usr/bin/env python
from __future__ import annotations

from app.backend.database.migrations import migrate

if __name__ == "__main__":
    migrate()
    print("Database migration complete")
