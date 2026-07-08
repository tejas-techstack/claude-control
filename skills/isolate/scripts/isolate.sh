#!/usr/bin/env bash
# Build and enter the claude-control sandbox. Mounts ONLY the current directory.
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMG=claude-control-sandbox
NET="${SANDBOX_NETWORK:-bridge}"   # set SANDBOX_NETWORK=none for offline
docker build -t "$IMG" -f "$DIR/Dockerfile" "$DIR"
echo ">> Entering sandbox. Project mounted at /work. Host is protected."
echo ">> Inside, run:  claude --dangerously-skip-permissions"
exec docker run --rm -it \
  --network "$NET" \
  -v "$(pwd)":/work \
  -v claude-sandbox-home:/home/sandbox \
  --name claude-control-sandbox-$$ \
  "$IMG"
