from __future__ import annotations


def normalize_market_name(value: str) -> str:
    parts = [part.strip() for part in value.replace("/", ",").split(",") if part.strip()]
    if len(parts) >= 2:
        return f"{parts[0].title()}, {parts[1].upper()}"
    return value.strip().title()


def parse_money(value: str | float | int | None) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    return float(value.replace("$", "").replace(",", "").strip() or 0)
