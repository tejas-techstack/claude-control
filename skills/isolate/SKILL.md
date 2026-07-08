---
name: isolate
description: Dockerize/sandbox the current project so Claude Code can run inside the container with --dangerously-skip-permissions (danger mode) without ever touching the host userspace. Use whenever the user says isolate, sandbox, dockerize, container, "run Claude in danger mode safely", "YOLO mode", or wants risky/autonomous runs contained.
---

# Isolate (sandboxed danger mode)

Danger mode belongs ONLY inside a container. Read `../_shared/GUARDRAILS.md` first.

## Hard rules
- NEVER run `claude --dangerously-skip-permissions` on the host. If the user asks for that, this skill exists precisely to say "yes — inside a container" and set it up.
- Mount ONLY the project directory into the container. Never mount $HOME, credentials directories, or the docker socket.
- Default network inside the sandbox: enabled but explain the tradeoff; offer `--network none` for fully offline runs.

## Workflow
1. Check Docker (or Podman) exists: `docker version`. If missing, route to /setup first.
2. Copy `assets/Dockerfile` and `scripts/isolate.sh` from this skill folder into the project as `.sandbox/` (adjust base image to the project stack: node/python/go layers as needed). The Dockerfile creates a non-root user and installs Claude Code inside the image.
3. Explain auth simply: first run inside the container triggers Claude login; credentials persist in a named docker volume (`claude-sandbox-home`), never on the host project.
4. Build and run: `bash .sandbox/isolate.sh` — it builds the image, mounts ONLY `$(pwd)` at /work, and drops into the container. Danger mode inside: `claude --dangerously-skip-permissions`.
5. State the escape hatches: `exit` leaves the sandbox; `docker volume rm claude-sandbox-home` wipes sandbox credentials; deleting `.sandbox/` removes everything.

## Chaining
- Input: any project (pairs with /setup for the image recipe).
- Output: .sandbox/ with Dockerfile + isolate.sh; feeds /agent-automation (run agents contained).
