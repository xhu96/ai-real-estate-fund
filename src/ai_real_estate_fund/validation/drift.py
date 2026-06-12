from __future__ import annotations
from math import log

def population_stability_index(expected: list[float], actual: list[float], buckets: int = 10) -> float:
    if not expected or not actual:
        return 0.0
    lo, hi = min(expected + actual), max(expected + actual)
    if hi == lo:
        return 0.0
    width = (hi - lo) / buckets
    psi = 0.0
    for idx in range(buckets):
        left, right = lo + idx * width, lo + (idx + 1) * width
        e = sum(1 for v in expected if left <= v < right) / len(expected)
        a = sum(1 for v in actual if left <= v < right) / len(actual)
        e = max(e, 0.0001); a = max(a, 0.0001)
        psi += (a - e) * log(a / e)
    return psi
