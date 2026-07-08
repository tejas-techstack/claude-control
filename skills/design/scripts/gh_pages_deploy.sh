#!/usr/bin/env bash
# Deploy ./docs on the current branch to GitHub Pages. REQUIRES prior user consent.
# Usage: gh_pages_deploy.sh --yes   (the flag exists so Claude cannot run it "by accident")
set -euo pipefail
[ "${1:-}" = "--yes" ] || { echo "Refusing: run with --yes only after the user explicitly approved the push."; exit 1; }
git rev-parse --is-inside-work-tree >/dev/null || { echo "Not a git repo"; exit 1; }
[ -f docs/index.html ] || { echo "docs/index.html not found"; exit 1; }
BRANCH=$(git rev-parse --abbrev-ref HEAD)
git add docs && git commit -m "site: add/update GitHub Pages site" || true
git push origin "$BRANCH"
if command -v gh >/dev/null 2>&1; then
  gh api -X POST "repos/{owner}/{repo}/pages" -f "source[branch]=$BRANCH" -f "source[path]=/docs" 2>/dev/null \
    || gh api -X PUT "repos/{owner}/{repo}/pages" -f "source[branch]=$BRANCH" -f "source[path]=/docs" 2>/dev/null \
    || echo "Enable Pages manually: repo Settings -> Pages -> Deploy from branch -> $BRANCH /docs"
  gh api "repos/{owner}/{repo}/pages" --jq .html_url 2>/dev/null || true
else
  echo "gh CLI not found. Enable Pages manually: Settings -> Pages -> Deploy from branch -> $BRANCH /docs"
fi
