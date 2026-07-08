# Improvements rubric — curate hard, score honestly

A short list that changes the project, not a dump of nitpicks. Max 10 items. Every item needs **evidence** (file:line or reproduced behavior) and a **first concrete step**. Cut anything that's a micro-optimization or pure style.

## Candidate categories (mine each, then cut ruthlessly)

- **Correctness bugs** — wrong output, crashes, unhandled failure paths, races.
- **Security holes** — injection, secrets in repo/logs, missing authz, home-rolled crypto. (Cross-ref `/critical-review` rubric.)
- **Missing tests on critical paths** — money/auth/data-mutation with no coverage.
- **Architecture debt that blocks change** — the coupling that makes every feature slow; "to change X I must edit 7 files."
- **Performance with real user impact** — quadratic on real data, N+1 queries, unbounded memory. Not micro-opts.
- **Developer experience** — can't run from the README; flaky setup; no one-command test; slow feedback loop.
- **Missing table-stakes** — no error handling, no logging, no CI, no input validation at the boundary.

## Scoring

Score each surviving item **Impact (H/M/L) × Effort (H/M/L)**. Order by Impact desc, then Effort asc — so high-impact/low-effort rises to the top.

| | Impact H | Impact M | Impact L |
|---|---|---|---|
| **Effort L** | do first | do | maybe |
| **Effort M** | do | consider | skip |
| **Effort H** | plan it | skip | skip |

Impact = what breaks / what it unblocks / how many users or how much money. Effort = realistic hours including tests and review, not a guess of the happy-path change.

## Evidence standard

- Point to `file:line` or paste the reproduced behavior. "This could be better" without evidence doesn't ship.
- Prefer things you can demonstrate over things you suspect. A repro beats an opinion.

## What NOT to include

Formatting, naming taste, "works but could be nicer", speculative abstraction for a future that may not come, tool-preference swaps, and anything you can't tie to impact. Those belong in a linter, not a roadmap.

## Output (per item)

```
N. <Title>  — [Impact: H|M|L, Effort: H|M|L]
   Evidence: <file:line or behavior>
   Why it matters: <1-2 sentences>
   First step: <one concrete action>
```

End with **"Top 3 I'd do first and why"** and an offer to implement #1. For "replace instead of improve" candidates, hand to `/search-existing`; to verify fixes, `/focus-review` or `/create-test-suite`.
