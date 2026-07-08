# Sandbox hardening — why each flag is there

`/isolate` exists so `claude --dangerously-skip-permissions` can run **only** inside a container that can't touch your real system. This is the reasoning behind `scripts/isolate.sh`, so you can adjust it knowingly.

## The non-negotiables

- **Mount ONLY the project.** `-v "$(pwd)":/work` and nothing else. Never mount `$HOME`, `~/.ssh`, `~/.aws`, `~/.config`, cloud credential dirs, or the Docker socket (`/var/run/docker.sock` = full host takeover). The runner refuses to launch from `$HOME` for exactly this reason.
- **Non-root user in the image.** Claude runs as `sandbox`, not root, so even in-container mistakes have limited reach.
- **Credentials live in a named volume** (`claude-sandbox-home`), never in the project and never on the host filesystem — so the login persists between runs without leaking onto disk.

## Defense-in-depth flags (in the runner)

| Flag | What it buys |
|---|---|
| `--cap-drop ALL` | drops all Linux capabilities; the container can't do privileged operations |
| `--security-opt no-new-privileges` | processes can't gain privileges via setuid binaries |
| `--pids-limit 512` | a fork bomb can't exhaust host PIDs |
| `--memory`, `--cpus` | a runaway process can't starve the host (tune via env) |
| `--network none` (opt-in) | fully offline run — nothing leaves the box; the strongest containment |
| `--read-only` + tmpfs (opt-in) | immutable root filesystem; only `/work` and tmpfs are writable |

## Network: the real tradeoff

Default is `bridge` (network on) because Claude Code needs to reach the API to work, and most tasks need to install deps or hit the internet. But **network-on means an autonomous agent can exfiltrate or fetch anything**. For a run that only needs local files, `SANDBOX_NETWORK=none bash isolate.sh` is meaningfully safer. State this tradeoff to the user and let them choose.

## What the sandbox does NOT protect against

- Anything you explicitly mount in beyond `/work`.
- Secrets you paste into the session or bake into the project files.
- Malicious images: build from the provided Dockerfile (pinned base) rather than pulling a random one.
- Kernel exploits (containers share the host kernel) — for a truly hostile workload, a VM is stronger than a container. Say so if the threat model warrants it.

## Escape hatches (tell the user these)

- `exit` — leave the sandbox.
- `docker volume rm claude-sandbox-home` — wipe the sandbox's stored credentials.
- `rm -rf .sandbox/` — remove the sandbox setup from the project entirely.
- `docker image rm claude-control-sandbox` — reclaim the image.

## Podman note

Rootless Podman is an even stronger default (no root daemon). `isolate.sh` uses `docker` if present, else `podman`; the flags above are compatible with both.
