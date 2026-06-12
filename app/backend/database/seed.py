from __future__ import annotations
from .migrations import migrate


def seed_demo_data() -> None:
    migrate()
