from __future__ import annotations

def pagination(limit: int = 25, offset: int = 0) -> tuple[int, int]:
    return max(1, min(limit, 250)), max(0, offset)
