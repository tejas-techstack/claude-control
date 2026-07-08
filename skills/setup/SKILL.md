---
name: setup
description: Aggressively set up a requirement or list of requirements on the user machine, looping install-verify-fix until everything works or is proven impossible on this system. Use whenever the user says "set up X", "install X", "get my environment ready", gives a requirements list, or a project needs dependencies before work can start.
---

# Setup (relentless environment setup)

Loop until green or provably impossible. Read `../_shared/GUARDRAILS.md` first — consent rules still apply while being aggressive.

## Workflow
1. **Plan first**: expand the requirements into a checklist with a verification command per item (e.g., "docker" -> `docker --version` AND `docker run hello-world`). Show the checklist.
2. **Detect the system**: run `bash scripts/detect_env.sh` — it reports OS, arch, package managers, shells, and versions of common toolchains, and flags the right install route (sudo vs user-space, brew vs apt vs dnf). Never assume; probe first. (Windows: use the equivalent `Get-Command`/`winget`/`choco` checks.)
3. **Execute per item, in dependency order**:
   - Prefer user-space installs (pipx, npm prefix, ~/.local, official user installers) over system-wide. sudo/system-wide only with explicit consent per command.
   - Install -> **verify with the real command** -> on failure, read the actual error, fix (missing dep, PATH, version pin), retry. Up to 3 distinct strategies per item (e.g., apt -> official script -> build from source) before declaring it blocked.
   - Log every command run and its outcome to `setup.log` in the working directory.
4. **Impossibility is a finding, not a failure**: if an item cannot work here (wrong OS/arch, needs hardware, needs paid license), stop retrying, state exactly why, and offer the nearest free alternative or a container route (/isolate).
5. **Final report**: table of item | status (PASS/BLOCKED) | verify command | notes. Everything PASS must be re-verified in one final pass at the end.

## Chaining
- Input: requirements list or a repo README. Output: working environment + setup.log; feeds /isolate (containerize the now-known recipe), /control-skill (bake the recipe into a project skill).
