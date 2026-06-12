from __future__ import annotations

def require_demo_key(api_key: str | None) -> bool:
    return api_key in {None, "", "demo"}
