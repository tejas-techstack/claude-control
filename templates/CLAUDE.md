# Project instructions (claude-control)

## Token thrift — the 80/20 rule
- BEFORE exploring this repo, run `python3 ~/.claude/claude-control/tools/repo_map.py . --out REPO_MAP.md` and read the map, not the raw tree.
- For structure questions, run `python3 ~/.claude/claude-control/tools/graphify.py .`; read the central files it names first.
- Never read generated, vendored, or lock files.

## Delegate mechanical work to scripts
- Run `python3 ~/.claude/claude-control/tools/chores.py list` once per session; use `chores.py run <name>` for formatting, linting, tests, and audits instead of doing them by hand.
- If you repeat any manual sequence twice, write a script for it (see /automation-how).

## Skills
- claude-control skills are installed in `~/.claude/skills/`. Route with /skill-suggestions, compose with /skills-interleave, persist project learnings with /control-skill.

## Consent
- Never push, publish, or install system-wide without asking. Full rules: `~/.claude/skills/_shared/GUARDRAILS.md`.
