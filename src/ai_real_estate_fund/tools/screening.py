from __future__ import annotations

def screen_property_payload(payload: dict) -> list[str]:
    warnings: list[str] = []
    if payload.get("purchase_price", 0) <= 0: warnings.append("purchase_price must be positive")
    if payload.get("monthly_rent", 0) <= 0: warnings.append("monthly_rent should be positive")
    if payload.get("market", "") == "": warnings.append("market is required")
    if payload.get("loan_amount", 0) > payload.get("purchase_price", 0): warnings.append("loan_amount exceeds purchase price")
    return warnings
