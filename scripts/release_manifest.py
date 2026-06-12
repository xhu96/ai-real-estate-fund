#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path

from ai_real_estate_fund.production.release import build_release_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Build release manifest.")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--version", default="0.6.0")
    parser.add_argument("--out", type=Path, default=Path("dist/release-manifest.json"))
    args = parser.parse_args()
    manifest = build_release_manifest(args.root, version=args.version)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(manifest.to_json(), encoding="utf-8")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()
