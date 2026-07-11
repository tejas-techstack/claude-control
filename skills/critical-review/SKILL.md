---
name: critical-review
description: A brutal-but-fair full review of code, a design, a document, or a plan — hard-hitting, evidence-based criticism that never collapses into "all hope is lost". Use whenever the user asks for a harsh review, honest opinion, "tear this apart", "roast my code/plan", red-team, or pre-launch audit.
---

# Critical Review (brutal but fair)

Brutal means evidence and severity, not cruelty or doom. Read `../_shared/GUARDRAILS.md` first.

## Stance
- Every criticism must carry: evidence (file:line, quote, or reproduced behavior), severity, and a way forward. Criticism without a path forward is forbidden.
- "Fair" also means saying what is genuinely good — one section, honest, no participation trophies.
- Never inflate severity for drama; never soften a CRITICAL to be polite.

## Workflow
1. Scope with the user in one question: whole repo, a diff, a doc, or a plan? Depth: skim or deep?
2. Map first (repo_map.py/context_pack.py for code; `/graphify .` for a deep dependency graph), then examine against the rubric: correctness, security, data integrity, architecture and coupling, error handling, tests, performance where it matters, docs/onboarding, and (for plans) feasibility and hidden assumptions. `references/rubric.md` has the concrete per-domain checklists (what to actually look for in each) — work through the ones that fit the subject.
3. Classify findings: CRITICAL (will cause damage) / MAJOR (will cause pain) / MINOR (worth fixing, not urgent). Cap MINOR at 5 — this is a review, not a lint run.

## Output format
ALWAYS use this exact template:
# Critical review: [subject]
## Verdict (2-3 blunt sentences + a 1-10 score with one-line justification)
## What is genuinely good
## CRITICAL / ## MAJOR / ## MINOR — each finding: evidence -> why it matters -> minimal fix
## If you fix only three things
## What I did NOT review

## Chaining
- Input: repo/diff/doc; deeper after /humanize. Output: findings; feeds /improvements (roadmap-ify), /focus-review (the fast sibling for diffs).
