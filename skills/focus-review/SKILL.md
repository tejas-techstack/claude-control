---
name: focus-review
description: Review only what is important — bugs, security, data loss, and order-of-magnitude improvements — explicitly skipping style nits and micro-optimizations. Use whenever the user wants a quick review of a diff/PR/file, says "just tell me if anything is actually wrong", or is about to merge/ship.
---

# Focus Review

High signal, zero noise. Read `../_shared/GUARDRAILS.md` first.

## The filter (apply to every candidate finding)
Report ONLY if at least one is true:
- It is a correctness bug (wrong output, crash, race, unhandled failure path).
- It is a security or data-loss risk.
- It changes complexity class or architecture in a way worth >=2x (perf, cost, or future change-speed) — exponential/structural wins are in scope.
- It will silently corrupt state or mislead users.
FORBIDDEN: formatting, naming taste, "this works but could be slightly nicer", speculative abstraction, micro-optimizations, tool preferences.

## Workflow
1. Get the diff (`git diff`, PR, or file). For context, read only the functions the diff touches plus their direct callers.
2. Hunt in order: broken invariants -> unchecked inputs/errors -> concurrency and lifetime -> security surfaces -> quadratic-or-worse patterns on real data sizes.
3. If NOTHING passes the filter, the correct output is: "No blocking issues found. Checked: [list]." — resist inventing findings to seem thorough.

## Output format
Per finding: **[BLOCKER|WARN] title** — evidence (file:line) — impact in one sentence — minimal fix (diff-sized). Max 7 findings; if more exist, give the top 7 and say how many were cut.

## Chaining
- Input: diff/PR/file; the pre-merge companion to /create-test-suite.
- Output: blockers list; escalate to /critical-review for a full audit.
