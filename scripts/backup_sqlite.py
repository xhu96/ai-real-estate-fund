#!/usr/bin/env python
from __future__ import annotations

import argparse
import shutil
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a timestamped SQLite backup.")
    parser.add_argument("--source", type=Path, default=Path("data/app.db"))
    parser.add_argument("--dest-dir", type=Path, default=Path("backups"))
    args = parser.parse_args()
    args.dest_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dest = args.dest_dir / f"{args.source.stem}-{stamp}{args.source.suffix}"
    shutil.copy2(args.source, dest)
    print(dest)


if __name__ == "__main__":
    main()
