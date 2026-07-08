#!/usr/bin/env bash
# Deploy a static site dir on the current branch to GitHub Pages. REQUIRES prior consent.
# The --yes flag exists so Claude cannot run this "by accident" — only pass it after the
# user has explicitly approved the exact push.
#
# Usage: gh_pages_deploy.sh --yes [--dir docs|site]     (default dir: docs)
set -euo pipefail

DIR="docs"; OK="no"
while [ $# -gt 0 ]; do
  case "$1" in
    --yes) OK="yes" ;;
    --dir) shift; DIR="$1" ;;
    *) echo "unknown arg: $1"; exit 2 ;;
  esac; shift
done

[ "$OK" = "yes" ] || { echo "Refusing: run with --yes only after the user explicitly approved the push."; exit 1; }
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "Not a git repo."; exit 1; }
[ -f "$DIR/index.html" ] || { echo "$DIR/index.html not found (use --dir to point at your site folder)."; exit 1; }

BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo ">> deploying ./$DIR on branch '$BRANCH' to GitHub Pages"

git add "$DIR"
git commit -m "site: add/update GitHub Pages site" || echo "   (nothing new to commit)"
git push origin "$BRANCH"

if command -v gh >/dev/null 2>&1; then
  # Try to enable Pages via the API (create, then update if it already exists).
  gh api -X POST "repos/{owner}/{repo}/pages" -f "source[branch]=$BRANCH" -f "source[path]=/$DIR" 2>/dev/null \
    || gh api -X PUT "repos/{owner}/{repo}/pages" -f "source[branch]=$BRANCH" -f "source[path]=/$DIR" 2>/dev/null \
    || echo "   (couldn't toggle Pages via API — enable it manually below)"
  URL=$(gh api "repos/{owner}/{repo}/pages" --jq .html_url 2>/dev/null || true)
  [ -n "${URL:-}" ] && echo ">> live (allow ~1 min for first build): $URL"
fi

if [ -z "${URL:-}" ]; then
  echo ">> Enable Pages manually: repo Settings -> Pages -> Deploy from branch -> $BRANCH  /$DIR"
  echo "   URL will be: https://<owner>.github.io/<repo>/   (project pages)"
fi
