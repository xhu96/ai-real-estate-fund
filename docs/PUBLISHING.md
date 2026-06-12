# Publishing to GitHub

This repository is configured for the default GitHub location:

```text
https://github.com/xhu96/ai-real-estate-fund
```

## Option A: GitHub CLI

```bash
git init
git add .
git commit -m "Initial production-oriented AI Real Estate Fund"
git branch -M main
gh repo create xhu96/ai-real-estate-fund --private --source=. --remote=origin --push
```

Use `--public` instead of `--private` when you are ready to publish publicly.

## Option B: existing empty GitHub repository

Create the repository on GitHub first, then run:

```bash
git init
git add .
git commit -m "Initial production-oriented AI Real Estate Fund"
git branch -M main
git remote add origin https://github.com/xhu96/ai-real-estate-fund.git
git push -u origin main
```

## Option C: SSH remote

```bash
git init
git add .
git commit -m "Initial production-oriented AI Real Estate Fund"
git branch -M main
git remote add origin git@github.com:xhu96/ai-real-estate-fund.git
git push -u origin main
```
