#!/usr/bin/env python
from __future__ import annotations

import argparse
import secrets

from ai_real_estate_fund.production.auth import hash_api_key


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an API key and SHA-256 hash for API_KEY_HASHES.")
    parser.add_argument("--bytes", type=int, default=32)
    args = parser.parse_args()
    raw = secrets.token_urlsafe(args.bytes)
    print("Raw API key; store this in your secret manager and show it only once:")
    print(raw)
    print("\nAPI_KEY_HASHES value:")
    print(hash_api_key(raw))


if __name__ == "__main__":
    main()
