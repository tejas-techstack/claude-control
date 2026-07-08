#!/usr/bin/env bash
# firecrawl_selfhost.sh — pull and run the REAL Firecrawl locally, for free.
#
# Firecrawl (github.com/firecrawl/firecrawl, AGPL-3.0) is open source and self-hostable:
# a full crawl-to-markdown engine with JS rendering that the hosted paid API also runs.
# This brings it up on your machine — no API key, no subscription — so /firecrawl can use
# the strong engine when the stdlib crawl.py isn't enough.
#
# Usage:
#   firecrawl_selfhost.sh up        # clone/pull + docker compose up -d + health check
#   firecrawl_selfhost.sh down      # stop the stack
#   firecrawl_selfhost.sh status    # is it answering on the API port?
#   firecrawl_selfhost.sh logs      # tail compose logs
#
# Env: FIRECRAWL_DIR  (clone location, default ~/.claude/claude-control/services/firecrawl)
#      FIRECRAWL_PORT (host API port, default 3002)
#      FIRECRAWL_REPO (default https://github.com/firecrawl/firecrawl)
set -euo pipefail

DIR="${FIRECRAWL_DIR:-$HOME/.claude/claude-control/services/firecrawl}"
PORT="${FIRECRAWL_PORT:-3002}"
REPO="${FIRECRAWL_REPO:-https://github.com/firecrawl/firecrawl}"
API="http://localhost:$PORT"

# docker or podman?
if command -v docker >/dev/null 2>&1; then DC="docker compose"; DKR="docker"
elif command -v podman >/dev/null 2>&1 && command -v podman-compose >/dev/null 2>&1; then DC="podman-compose"; DKR="podman"
else
  echo "Docker (or Podman + podman-compose) is required. Run /setup to install it, then retry." >&2
  exit 1
fi

health() { curl -fsS --max-time 5 "$API/" >/dev/null 2>&1 || curl -fsS --max-time 5 "$API/test" >/dev/null 2>&1; }

case "${1:-up}" in
  up)
    if ! command -v git >/dev/null 2>&1; then echo "git is required to fetch Firecrawl." >&2; exit 1; fi
    if [ -d "$DIR/.git" ]; then
      echo "==> updating Firecrawl clone in $DIR"
      git -C "$DIR" pull --ff-only || echo "    (pull skipped — using existing checkout)"
    else
      echo "==> cloning $REPO -> $DIR"
      mkdir -p "$(dirname "$DIR")"
      git clone --depth 1 "$REPO" "$DIR"
    fi
    cd "$DIR"
    # Self-host wants a .env; seed one from the example on first run (free, no-auth defaults).
    if [ ! -f .env ]; then
      if [ -f .env.example ]; then cp .env.example .env; echo "==> seeded .env from .env.example"
      elif [ -f apps/api/.env.example ]; then cp apps/api/.env.example .env; echo "==> seeded .env from apps/api/.env.example"
      fi
      # Ensure the free path: DB auth off = no API key needed. Append only if absent.
      grep -q '^USE_DB_AUTHENTICATION=' .env 2>/dev/null || echo 'USE_DB_AUTHENTICATION=false' >> .env
    fi
    echo "==> starting Firecrawl ($DC up -d).  First run builds/pulls images — can take several"
    echo "    minutes and wants ~8GB RAM free. Prebuilt GHCR images (see SELF_HOST.md) skip the build."
    $DC up -d
    echo "==> waiting for $API to answer (up to ~180s)…"
    for i in $(seq 1 60); do
      if health; then echo "READY: Firecrawl API is live at $API"; echo
      echo "Use it:  FIRECRAWL_API_URL=$API python3 $(dirname "$0")/fc_api.py scrape https://example.com"; exit 0; fi
      sleep 3
    done
    echo "Not answering yet. Check '$0 logs' — the API may still be building." >&2; exit 1
    ;;
  down)   cd "$DIR" && $DC down && echo "Firecrawl stopped. Data/images kept; delete $DIR to remove entirely." ;;
  status) if health; then echo "up: $API"; else echo "down (no response on $API)"; fi ;;
  logs)   cd "$DIR" && $DC logs --tail=80 -f ;;
  *) echo "usage: $0 {up|down|status|logs}"; exit 2 ;;
esac
