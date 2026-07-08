---
name: isolate
description: Dockerize/sandbox the current project so Claude Code can run inside the container with --dangerously-skip-permissions (danger mode) without ever touching the host userspace. Use whenever the user says isolate, sandbox, dockerize, container, "run Claude in danger mode safely", "YOLO mode", or wants risky/autonomous runs contained.
---

# Isolate (sandboxed danger mode)

Danger mode belongs ONLY inside a container. Read `../_shared/GUARDRAILS.md` first.

## Hard rules
- NEVER run `claude --dangerously-skip-permissions` on the host. If the user asks for that, this skill exists precisely to say "yes — inside a container" and set it up.
- Mount ONLY the project directory into the container. Never mount $HOME, credentials directories, or the docker socket. (`isolate.sh` refuses to launch from `$HOME` and drops all Linux capabilities.)
- Default network inside the sandbox: enabled but explain the tradeoff; offer `SANDBOX_NETWORK=none` for fully offline runs. Why each flag exists is documented in `references/hardening.md`.

## Workflow
1. Check Docker (or Podman) exists: `docker version`. If missing, route to /setup first.
2. Copy `assets/Dockerfile` and `scripts/isolate.sh` from this skill folder into the project as `.sandbox/`. The Dockerfile pins a base, runs as a non-root `sandbox` user, and has commented optional layers (Go/Rust/Java/build-essential) — uncomment only what the project needs.
3. Explain auth simply: first run inside the container triggers Claude login; credentials persist in a named docker volume (`claude-sandbox-home`), never on the host project.
4. Build and run: `bash .sandbox/isolate.sh` (`up` builds if needed, mounts ONLY `$(pwd)` at /work with `--cap-drop ALL`, `--no-new-privileges`, pid/mem/cpu limits, and drops you in). Danger mode inside: `claude --dangerously-skip-permissions`. Harden further with `SANDBOX_NETWORK=none` or `SANDBOX_READONLY=1`.
5. State the escape hatches: `exit` leaves the sandbox; `isolate.sh clean` wipes the credential volume + image; deleting `.sandbox/` removes everything. Full list in `references/hardening.md`.

## Chaining
- Input: any project (pairs with /setup for the image recipe).
- Output: .sandbox/ with Dockerfile + isolate.sh; feeds /agent-automation (run agents contained).
