#!/usr/bin/env bash
set -euo pipefail
python -m pip install -e ".[api,dev]" -q
python -m pytest -q
python -m build
