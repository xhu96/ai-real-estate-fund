from __future__ import annotations

from fastapi import HTTPException

from ai_real_estate_fund.models import PropertyInput


def parse_property_input(payload: dict) -> PropertyInput:
    """Parse a request payload into a PropertyInput, converting bad input to 422.

    PropertyInput.from_dict raises ValueError on unknown fields / failed validation
    and TypeError on missing required fields. Both indicate a malformed *request*,
    not a server bug, so they map to HTTP 422 at the parse boundary.
    """
    try:
        return PropertyInput.from_dict(payload)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=f"invalid property payload: {exc}") from exc
