from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True, slots=True)
class FileDigest:
    path: str
    sha256: str
    bytes: int

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ReleaseManifest:
    project: str
    version: str
    generated_at: str
    root_hash: str
    files: list[FileDigest] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "project": self.project,
            "version": self.version,
            "generated_at": self.generated_at,
            "root_hash": self.root_hash,
            "files": [item.to_dict() for item in self.files],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True) + "\n"


def digest_file(path: Path, root: Path) -> FileDigest:
    data = path.read_bytes()
    return FileDigest(path=str(path.relative_to(root).as_posix()), sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))


def iter_release_files(root: Path, patterns: Iterable[str] = ("*.py", "*.toml", "*.md", "*.yml", "*.yaml", "Dockerfile", "*.json")) -> list[Path]:
    paths: set[Path] = set()
    excluded_parts = {".git", "__pycache__", ".mypy_cache", ".pytest_cache", "node_modules", "dist", "build"}
    for pattern in patterns:
        for path in root.rglob(pattern):
            if path.is_file() and not excluded_parts.intersection(path.parts):
                paths.add(path)
    return sorted(paths)


def build_release_manifest(root: str | Path, *, project: str = "ai-real-estate-fund", version: str = "0.6.0") -> ReleaseManifest:
    root_path = Path(root)
    files = [digest_file(path, root_path) for path in iter_release_files(root_path)]
    root_hash_input = "".join(f"{item.path}:{item.sha256}:{item.bytes}\n" for item in files).encode("utf-8")
    return ReleaseManifest(
        project=project,
        version=version,
        generated_at=datetime.now(timezone.utc).isoformat(),
        root_hash=hashlib.sha256(root_hash_input).hexdigest(),
        files=files,
    )
