from __future__ import annotations

import re
from typing import Any

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}(?!\d)")
API_KEY_RE = re.compile(r"(?i)(api[_-]?key|token|secret|password)['\"\s:=]+[A-Za-z0-9_\-\.]{8,}")

SENSITIVE_KEYS = {"email", "phone", "ssn", "api_key", "token", "secret", "password", "authorization"}


def redact_text(value: str) -> str:
    value = EMAIL_RE.sub("[redacted-email]", value)
    value = PHONE_RE.sub("[redacted-phone]", value)
    value = API_KEY_RE.sub(lambda match: match.group(1) + "=[redacted-secret]", value)
    return value


def redact_payload(payload: Any) -> Any:
    if isinstance(payload, dict):
        redacted: dict[str, Any] = {}
        for key, value in payload.items():
            if key.lower() in SENSITIVE_KEYS or any(marker in key.lower() for marker in ("secret", "token", "password", "api_key")):
                redacted[key] = "[redacted]"
            else:
                redacted[key] = redact_payload(value)
        return redacted
    if isinstance(payload, list):
        return [redact_payload(item) for item in payload]
    if isinstance(payload, tuple):
        return tuple(redact_payload(item) for item in payload)
    if isinstance(payload, str):
        return redact_text(payload)
    return payload
