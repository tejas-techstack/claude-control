---
name: control-<project>
description: Use for ANY task in <project> — read this BEFORE other skills. Encodes this repo's proven commands, conventions, gotchas, and best skill-pipelines so Claude is instantly effective here. Use whenever working in <project>, when the user repeats a correction, or at the end of a productive session to capture what was learned.
---

# control-<project>

Project-specific knowledge for <project>. Only VERIFIED, project-specific facts live here —
no generic advice. Keep under ~150 lines; merge new learnings, delete invalidated ones.

## Commands that work here
<!-- exact invocations PROVEN this session — source from setup.log / chores.py, not guesses -->
- build:      `...`
- test:       `...`   (e.g. "needs the fake-S3 container up first: `docker compose up -d minio`")
- run/dev:    `...`
- lint/format:`...`
- deploy:     `...`   (consent-gated — never run without an explicit yes)

## Conventions (quote the correction that established each)
<!-- naming, structure, patterns the user corrected you toward -->
- <"we always X, never Y" — quoted from the session>

## Gotchas / traps hit this session
- <"tests fail unless TZ=UTC" — the specific trap and its fix>

## Architecture in one breath
<!-- 3-5 lines: entry points, the load-bearing files (graphify centrality), where NOT to look -->
- Entry: `...` · Core: `...` · Generated/vendored (don't read): `...`

## Best pipelines for this repo's recurring tasks
<!-- which claude-control skills, in which order, worked here (from /skills-interleave) -->
- Add a feature: `/cross-check → build → /create-test-suite (use `make test`) → /focus-review`
- <recurring task>: `<pipeline>`

## Skill adaptations (adapt-by-reference — never fork whole skills)
<!-- where a generic installed skill needed tweaking for this repo -->
- `/create-test-suite` here: use `make test`, not pytest directly.
- <skill>: <the delta>

---
_Changelog:_
- <YYYY-MM-DD> — created from session learnings.
