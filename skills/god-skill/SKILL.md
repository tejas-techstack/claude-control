---
name: control-skill
description: Inspect the current repo/task plus all installed skills, then synthesize and maintain a project-specific composite skill (the control-skill) that bakes in this projects conventions, commands, gotchas, and best skill-pipelines for the session and future sessions. Use whenever the user says control-skill, "remember this for the project", "make Claude better at THIS repo", repeats the same corrections, or at the end of a productive session.
---

# Ctrl Skill (per-project meta-skill)

Turn session learnings into a permanent project skill. Read `../_shared/GUARDRAILS.md` first.

## What it produces
`.claude/skills/control-<project>/SKILL.md` inside the project (so it ships with the repo and loads for anyone) containing ONLY verified, project-specific knowledge:
- **Commands that work here**: build, test, run, lint — the exact invocations proven this session (source them from setup.log / chores.py detection, not guesses).
- **Conventions**: naming, structure, patterns the user corrected you toward (quote the correction).
- **Gotchas**: the traps hit this session ("tests need the fake S3 container up first").
- **Pipelines**: which claude-control skills, in which order, worked for this repos recurring tasks (from /skills-interleave).
- **Improved fragments**: where a generic installed skill needed adaptation here, record the delta ("when /create-test-suite runs here, use `make test` not pytest directly") — adapt-by-reference, never fork whole skills into the control-skill.

## Workflow
1. First run: scan installed skills names/descriptions, run repo_map.py, and mine THIS conversation for corrections, discovered commands, and decisions. Draft the control-skill; show it; write only on approval.
2. Frontmatter description must be project-pushy: "Use for ANY task in <project> — read this before other skills."
3. Subsequent runs: update, do not append-forever — merge new learnings, delete invalidated ones, keep under ~150 lines. Date-stamp a changelog line at the bottom.
4. Session scope option: if the user wants it session-only, keep it in memory/scratch instead of writing the file.

## Chaining
- Input: a sessions worth of learnings + installed skills. Output: .claude/skills/control-<project>/; consumes /skills-interleave pipelines and /setup logs; every other skill benefits next session.
