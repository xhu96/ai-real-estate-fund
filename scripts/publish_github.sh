#!/usr/bin/env bash
set -euo pipefail

REPO_FULL_NAME="${1:-xhu96/ai-real-estate-fund}"
VISIBILITY="${2:-private}"

if ! command -v git >/dev/null 2>&1; then
  echo "git is required" >&2
  exit 1
fi

if [ ! -d .git ]; then
  git init
fi

git add .
if ! git diff --cached --quiet; then
  git commit -m "Initial production-oriented AI Real Estate Fund"
fi

git branch -M main

if command -v gh >/dev/null 2>&1; then
  if ! gh repo view "$REPO_FULL_NAME" >/dev/null 2>&1; then
    gh repo create "$REPO_FULL_NAME" "--$VISIBILITY" --source=. --remote=origin --push
  else
    git remote remove origin >/dev/null 2>&1 || true
    git remote add origin "https://github.com/$REPO_FULL_NAME.git"
    git push -u origin main
  fi
else
  echo "GitHub CLI not found. Create https://github.com/$REPO_FULL_NAME first, then run:" >&2
  echo "  git remote add origin https://github.com/$REPO_FULL_NAME.git" >&2
  echo "  git push -u origin main" >&2
fi
