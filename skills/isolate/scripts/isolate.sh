#!/usr/bin/env bash
# Build and enter the claude-control sandbox. Mounts ONLY the current directory, so
# `claude --dangerously-skip-permissions` inside can't touch your real system.
# See references/hardening.md for why each flag is here.
#
# Usage:   bash isolate.sh [up|build|down|clean]
# Env:     SANDBOX_NETWORK=none   fully offline run (strongest containment)
#          SANDBOX_MEMORY=4g      memory cap (default 4g)
#          SANDBOX_CPUS=2         cpu cap  (default 2)
#          SANDBOX_READONLY=1     immutable root fs (only /work + tmpfs writable)
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMG=claude-control-sandbox
VOL=claude-sandbox-home
NET="${SANDBOX_NETWORK:-bridge}"
MEM="${SANDBOX_MEMORY:-4g}"
CPUS="${SANDBOX_CPUS:-2}"

# docker or podman
if command -v docker >/dev/null 2>&1; then ENGINE=docker
elif command -v podman >/dev/null 2>&1; then ENGINE=podman
else echo "Need Docker or Podman. Run /setup first." >&2; exit 1; fi

# SAFETY: never sandbox your whole home dir (that would mount everything sensitive).
if [ "$(pwd)" = "$HOME" ]; then
  echo "Refusing to sandbox \$HOME — cd into the specific PROJECT directory first." >&2
  exit 1
fi

build() {
  echo ">> building $IMG with $ENGINE (base is pinned; non-root user inside)"
  "$ENGINE" build -t "$IMG" -f "$DIR/Dockerfile" "$DIR"
}

up() {
  "$ENGINE" image inspect "$IMG" >/dev/null 2>&1 || build
  echo ">> project: $(pwd)  ->  /work    network: $NET    limits: mem $MEM, cpus $CPUS"
  echo ">> host is protected. inside, run:  claude --dangerously-skip-permissions"
  local args=(--rm -it
    --network "$NET"
    --cap-drop ALL
    --security-opt no-new-privileges
    --pids-limit 512
    --memory "$MEM" --cpus "$CPUS"
    -v "$(pwd)":/work
    -v "$VOL":/home/sandbox
    --name "claude-control-sandbox-$$")
  if [ "${SANDBOX_READONLY:-0}" = "1" ]; then
    args+=(--read-only --tmpfs /tmp --tmpfs /run)
    echo ">> read-only root fs: only /work and tmpfs are writable"
  fi
  exec "$ENGINE" run "${args[@]}" "$IMG"
}

case "${1:-up}" in
  up)    up ;;
  build) build ;;
  down)  ids=$("$ENGINE" ps -aq --filter name=claude-control-sandbox); [ -n "$ids" ] && "$ENGINE" rm -f $ids; echo "stopped." ;;
  clean) "$ENGINE" volume rm "$VOL" 2>/dev/null || true
         "$ENGINE" image rm "$IMG" 2>/dev/null || true
         echo "removed sandbox volume + image (project files untouched)." ;;
  *) echo "usage: $0 {up|build|down|clean}"; exit 2 ;;
esac
