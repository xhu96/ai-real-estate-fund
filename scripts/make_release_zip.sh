#!/usr/bin/env bash
# Assemble a curated, turnkey release zip of the current working tree.
#
# What this produces (and why it differs from GitHub's auto "Source code" zip):
#   - a clean source tree (junk, caches, secrets and runtime DBs stripped), PLUS
#   - the PRE-BUILT frontend (app/frontend/dist) so `app/run.sh` serves the SPA
#     same-origin with no npm step — a runnable single-server bundle.
# The Python wheel/sdist (python -m build) only ship the src/ package, so this
# curated zip is a separate artifact, attached alongside them on the GitHub Release.
#
# Usage:   scripts/make_release_zip.sh [VERSION]
#   VERSION defaults to the installed/pyproject version (single source of truth).
#   Set SKIP_FRONTEND_BUILD=1 to reuse an existing app/frontend/dist (the release
#   workflow does this because it builds the frontend in its own step).
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$(pwd)"

# --- Resolve version: arg > installed/pyproject metadata > pyproject grep ---
VERSION="${1:-}"
if [ -z "$VERSION" ]; then
  VERSION="$(python -c 'from ai_real_estate_fund.production.release import resolve_version; print(resolve_version())' 2>/dev/null || true)"
fi
if [ -z "$VERSION" ]; then
  VERSION="$(grep -m1 '^version' pyproject.toml | sed 's/.*=//; s/[" ]//g' || true)"
fi
if [ -z "$VERSION" ]; then
  echo "error: could not resolve version (pass it explicitly: make_release_zip.sh 0.7.0)" >&2
  exit 1
fi
NAME="ai-real-estate-fund-$VERSION"

# --- Build the SPA so the zip runs single-server out of the box ---
if [ -z "${SKIP_FRONTEND_BUILD:-}" ]; then
  echo "Building frontend (set SKIP_FRONTEND_BUILD=1 to reuse an existing build)..."
  ( cd app/frontend && { [ -d node_modules ] || npm ci; } && npm run build )
fi
if [ ! -d app/frontend/dist ]; then
  echo "warning: app/frontend/dist missing — the zip will not run single-server until 'npm run build'." >&2
fi

# --- Stage a clean tree under a top-level dir, then zip ---
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
DEST="$STAGE/$NAME"
mkdir -p "$DEST"

# Excludes mirror .gitignore/.dockerignore. Leading-slash patterns are anchored to
# the repo root, so '/dist/' drops the Python build output but KEEPS app/frontend/dist,
# and '/venv/' '/env/' drop only a root-level virtualenv. '.env' matches only the real
# secret, never '.env.example' / '.env.production.example'. '._*' and '__MACOSX/' strip
# macOS resource-fork junk so the zip is clean on macOS too (the Linux CI never makes them).
rsync -a \
  --exclude='.git/' \
  --exclude='/dist/' \
  --exclude='/build/' \
  --exclude='node_modules/' \
  --exclude='__pycache__/' \
  --exclude='*.py[cod]' \
  --exclude='*.egg-info/' \
  --exclude='.pytest_cache/' \
  --exclude='.ruff_cache/' \
  --exclude='.mypy_cache/' \
  --exclude='.cache/' \
  --exclude='.venv/' \
  --exclude='/venv/' \
  --exclude='/env/' \
  --exclude='.env' \
  --exclude='.env.production' \
  --exclude='*.db' \
  --exclude='.DS_Store' \
  --exclude='._*' \
  --exclude='__MACOSX/' \
  --exclude='*.zip' \
  --exclude='/reports/*.md' \
  ./ "$DEST/"

mkdir -p dist
OUT="dist/$NAME.zip"
rm -f "$ROOT/$OUT"
( cd "$STAGE" && zip -r -q -X "$ROOT/$OUT" "$NAME" -x '*/.DS_Store' '*/._*' '__MACOSX*' )

SIZE="$(du -h "$ROOT/$OUT" | cut -f1 | tr -d '[:space:]')"
echo "Wrote $OUT ($SIZE) — top-level dir: $NAME/"
