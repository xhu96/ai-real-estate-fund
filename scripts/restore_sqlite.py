#!/usr/bin/env python
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Restore a SQLite database from backup.")
    parser.add_argument("backup", type=Path)
    parser.add_argument("--dest", type=Path, default=Path("data/app.db"))
    parser.add_argument("--yes", action="store_true")
    args = parser.parse_args()
    if not args.yes:
        raise SystemExit("Refusing to restore without --yes")
    args.dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(args.backup, args.dest)
    print(f"Restored {args.backup} -> {args.dest}")


if __name__ == "__main__":
    main()
