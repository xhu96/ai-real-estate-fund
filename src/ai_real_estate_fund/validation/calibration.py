from __future__ import annotations

def calibration_table(scores: list[float], outcomes: list[bool], buckets: int = 5) -> list[dict[str, float]]:
    if len(scores) != len(outcomes):
        raise ValueError("scores and outcomes must have same length")
    if not scores:
        return []
    rows = []
    for idx in range(buckets):
        low = idx * 100 / buckets
        high = (idx + 1) * 100 / buckets
        selected = [(s, o) for s, o in zip(scores, outcomes) if low <= s < high or (idx == buckets - 1 and s == 100)]
        if not selected:
            rows.append({"low": low, "high": high, "count": 0, "success_rate": 0.0})
            continue
        rows.append({"low": low, "high": high, "count": len(selected), "success_rate": sum(1 for _, o in selected if o) / len(selected)})
    return rows
