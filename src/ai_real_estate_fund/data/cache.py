from __future__ import annotations
import json
from pathlib import Path
from time import time

class JsonFileCache:
    def __init__(self, directory: str | Path = ".cache/ai-real-estate-fund") -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        safe = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in key)
        return self.directory / f"{safe}.json"

    def get(self, key: str, ttl_seconds: int = 86400):
        path = self._path(key)
        if not path.exists():
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
        if time() - payload.get("created_at", 0) > ttl_seconds:
            return None
        return payload.get("value")

    def set(self, key: str, value) -> None:
        self._path(key).write_text(json.dumps({"created_at": time(), "value": value}, indent=2), encoding="utf-8")
