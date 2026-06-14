from __future__ import annotations

import hashlib
import hmac
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Iterable

DEFAULT_SCOPES = frozenset({"read", "write", "analyze", "export"})
ADMIN_SCOPES = frozenset({"read", "write", "analyze", "export", "admin"})


def hash_api_key(raw_key: str) -> str:
    if not raw_key:
        raise ValueError("raw_key cannot be empty")
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class APIKeyPrincipal:
    name: str
    key_hash: str
    scopes: frozenset[str] = field(default_factory=lambda: DEFAULT_SCOPES)
    disabled: bool = False

    def allows(self, required_scope: str) -> bool:
        return not self.disabled and (required_scope in self.scopes or "admin" in self.scopes)

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["key_hash"] = self.key_hash[:12] + "..."
        payload["scopes"] = sorted(self.scopes)
        return payload


@dataclass(frozen=True, slots=True)
class AuthResult:
    ok: bool
    principal: APIKeyPrincipal | None = None
    reason: str = ""
    checked_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, object]:
        return {
            "ok": self.ok,
            "principal": None if self.principal is None else self.principal.to_dict(),
            "reason": self.reason,
            "checked_at": self.checked_at,
        }


class APIKeyStore:
    """Constant-time API key verifier with named principals and scopes.

    Accepted raw env formats:
    - API_KEYS="operator:raw-key:read|analyze,admin:other-key:admin"
    - API_KEYS="raw-key-1,raw-key-2" where names become key-1, key-2
    """

    def __init__(self, principals: Iterable[APIKeyPrincipal] = ()) -> None:
        self._principals = tuple(principals)

    @classmethod
    def from_raw_keys(cls, raw_values: Iterable[str]) -> "APIKeyStore":
        principals: list[APIKeyPrincipal] = []
        for idx, raw_value in enumerate(raw_values, start=1):
            raw_value = raw_value.strip()
            if not raw_value:
                continue
            parts = raw_value.split(":")
            if len(parts) >= 2:
                name = parts[0] or f"key-{idx}"
                key = parts[1]
                scopes = frozenset(parts[2].split("|")) if len(parts) >= 3 and parts[2] else DEFAULT_SCOPES
            else:
                name = f"key-{idx}"
                key = raw_value
                scopes = DEFAULT_SCOPES
            principals.append(APIKeyPrincipal(name=name, key_hash=hash_api_key(key), scopes=scopes))
        return cls(principals)

    @classmethod
    def from_hashes(cls, hashes: Iterable[str], *, scopes: Iterable[str] = ADMIN_SCOPES) -> "APIKeyStore":
        principals = [APIKeyPrincipal(name=f"hashed-key-{idx}", key_hash=value.strip(), scopes=frozenset(scopes)) for idx, value in enumerate(hashes, start=1) if value.strip()]
        return cls(principals)

    @property
    def principals(self) -> tuple[APIKeyPrincipal, ...]:
        return self._principals

    def verify(self, provided_key: str | None, *, required_scope: str = "read") -> AuthResult:
        if not provided_key:
            return AuthResult(ok=False, reason="missing_api_key")
        provided_hash = hash_api_key(provided_key)
        for principal in self._principals:
            if hmac.compare_digest(provided_hash, principal.key_hash):
                if principal.allows(required_scope):
                    return AuthResult(ok=True, principal=principal)
                return AuthResult(ok=False, principal=principal, reason="insufficient_scope")
        return AuthResult(ok=False, reason="invalid_api_key")


def build_store(raw_keys: Iterable[str] = (), key_hashes: Iterable[str] = ()) -> APIKeyStore:
    stores = [APIKeyStore.from_raw_keys(raw_keys), APIKeyStore.from_hashes(key_hashes)]
    principals: list[APIKeyPrincipal] = []
    for store in stores:
        principals.extend(store.principals)
    return APIKeyStore(principals)
