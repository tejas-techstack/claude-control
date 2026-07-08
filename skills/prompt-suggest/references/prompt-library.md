# Prompt Library (fill the {PLACEHOLDERS})
Each template: Role / Context / Task / Constraints / Output / Verify. Copy, fill, send.

## Build
1. **Greenfield feature** — You are a senior {STACK} engineer. Context: {ONE_PARA_PRODUCT}, repo conventions: {CONVENTIONS_OR_"read CLAUDE.md"}. Task: implement {FEATURE} end to end. Constraints: follow existing patterns, no new deps without asking, keep functions under 40 lines. Output: code + a short design note. Verify: write and run tests for {ACCEPTANCE_CRITERIA} before declaring done.
2. **CLI tool from scratch** — Build a {LANG} CLI named {NAME} that {DOES_WHAT}. Subcommands: {LIST}. Constraints: stdlib only, --help for everything, exit codes documented. Output: single file + README section. Verify: run each subcommand on {SAMPLE_INPUT} and show output.
3. **API endpoint** — Add {METHOD} {PATH} to {FRAMEWORK} app. Request/response schema: {SCHEMA}. Constraints: validate input, auth via existing {AUTH}, no breaking changes. Verify: curl examples for success + 2 failure cases, run them.
4. **UI component** — Build {COMPONENT} for {FRAMEWORK}. Props: {PROPS}. States: loading/empty/error/success. Constraints: match existing design tokens, keyboard accessible. Verify: render all four states.
5. **Data pipeline** — Ingest {SOURCE} -> transform ({RULES}) -> write {SINK}. Constraints: idempotent, resumable, logs row counts. Verify: run on a 100-row sample, show counts in vs out.

## Modify / refactor
6. **Safe refactor** — Refactor {FILE_OR_MODULE} to {GOAL} WITHOUT changing behavior. First list current behaviors as a checklist, then refactor, then prove each checklist item still holds (tests or manual runs). Never mix refactor and feature commits.
7. **Behavior change** — Change {CURRENT_BEHAVIOR} to {NEW_BEHAVIOR}. First show every call site affected, propose the smallest diff, wait for my OK, then implement + update tests.
8. **Dependency upgrade** — Upgrade {DEP} from {V1} to {V2}. List breaking changes from the changelog, grep our usage of each, patch, run full test suite, summarize risk.
9. **Kill the Ctrl-file** — {FILE} is too big. Propose a split into modules by responsibility (show the mapping table first), then execute after my approval, keeping imports backward compatible.

## Test / debug
10. **Characterization tests** — Before touching {LEGACY_MODULE}, write tests that pin its CURRENT behavior, including the weird parts. Do not fix bugs yet; document them as "pinned" cases.
11. **Bug hunt** — Symptom: {SYMPTOM}. Repro: {STEPS_OR_UNKNOWN}. Form 3 hypotheses ranked by likelihood, design the cheapest experiment to kill each, run them in order, fix the confirmed cause, add a regression test.
12. **Flaky test** — {TEST} fails intermittently. Run it {N} times to measure the failure rate, instrument for timing/order/state dependence, identify the race or shared state, fix, re-run {N} times to prove stability.
13. **Test suite for spec** — Here is SPEC.md acceptance criteria: {PASTE}. Write one test per criterion, name tests after criteria, then a coverage note on what the spec does NOT cover.

## Review / understand
14. **Focused review** — Review {DIFF_OR_PR} ONLY for: correctness bugs, security, data loss, and order-of-magnitude perf issues. Skip style and micro-optimizations entirely. For each finding: severity, evidence, minimal fix.
15. **Explain like I maintain it** — Explain {FILE/FLOW} as if I take over maintenance tomorrow: invariants, gotchas, what breaks if I change X, where the bodies are buried.
16. **Architecture decision** — Compare {OPTION_A} vs {OPTION_B} for {DECISION} in our context ({CONSTRAINTS}). Give a recommendation with the 2 strongest points against it.

## Migrate / document / optimize
17. **Migration plan** — Migrate {FROM} to {TO}. Produce: inventory of touchpoints, phased plan where every phase leaves the system shippable, rollback per phase, and the first phase implemented.
18. **Docs from code** — Generate {README|API docs|onboarding doc} for {SCOPE} strictly from the code — mark anything you inferred with (inferred). Include a quickstart that you actually ran.
19. **Perf pass** — Profile {WORKLOAD} first (show numbers), optimize only the top 2 hotspots, measure again, report before/after. No speculative optimization.
20. **Security sweep** — Audit {SCOPE} for: injection, authz gaps, secrets in code, unsafe deserialization, SSRF, path traversal. Evidence per finding, fix or mitigation, ranked by exploitability.

## Automate / meta
21. **Scriptify a chore** — I keep doing {REPETITIVE_TASK} manually. Write a script that does it, handles the 2 most likely error cases, and prints what it did. Then show me the one-liner to run it.
22. **CI pipeline** — Create GitHub Actions CI for this repo: lint, test, build on push+PR, with caching. Free tier only. Show the file, explain each job in one line each.
23. **Agent task brief** — You are an autonomous agent. Goal: {GOAL}. You may: {ALLOWED_ACTIONS}. You may not: {FORBIDDEN}. Definition of done: {CHECKS}. Work in small verified steps; after each step state what you verified. Stop and ask if you hit {STOP_CONDITIONS}.
24. **Prompt improver** — Rewrite this prompt to be unambiguous and verifiable, keeping my intent: {PROMPT}. Return improved prompt + a bullet list of what was underspecified.

## Data / SQL
25. **Query author** — Write a {DIALECT} query: from {TABLES_WITH_KEYS}, return {RESULT}. Constraints: no full scans on {BIG_TABLE} (use {INDEXED_COL}), parametrized (no string interpolation). Verify: show the query plan and run on sample data.
26. **Schema design** — Design tables for {DOMAIN}. Give DDL, the key relationships, the indexes each frequent query needs, and one migration to get there from {CURRENT_STATE}. Call out any denormalization and why.
27. **Data cleanup** — {DATASET} has {PROBLEMS}. Write a reproducible, idempotent transform (script, not manual edits) that fixes each, logs how many rows each rule touched, and leaves the original untouched. Verify on a sample.

## DevOps / deploy
28. **Dockerize** — Write a Dockerfile for this {STACK} app: multi-stage, non-root user, pinned base, minimal final image, healthcheck. Then a compose file for local dev. Verify: `docker build` + one run command that works.
29. **Deploy plan (free tier)** — Deploy {APP} on {FREE_HOST}. Steps from zero, secrets handling, the exact commands, and how to roll back. Free tier only — state any limit that bites at {EXPECTED_SCALE}.
30. **Observability starter** — Add structured logging + a health endpoint + the 3 metrics that matter for {APP} ({SUGGEST_IF_UNSURE}). No paid SaaS; keep it to what {FREE_STACK} gives.

## Frontend
31. **Responsive layout** — Build {LAYOUT} that works at 360/768/1440px. Constraints: no CSS framework unless already present, logical properties, respects prefers-reduced-motion + prefers-color-scheme. Verify: describe behavior at each breakpoint.
32. **Accessibility fix** — Audit {COMPONENT/PAGE} for WCAG AA: contrast, focus order, labels, keyboard traps, ARIA misuse. Per issue: what/why/the fix. Then apply the fixes.

## Concurrency / performance
33. **Make it concurrent (safely)** — {SEQUENTIAL_CODE} is slow because {REASON}. Parallelize with {PRIMITIVE}, but first name every shared resource and how you'll protect it. Cap concurrency; handle partial failure. Verify: correctness on repeated runs, then timing.
34. **Find the hotspot** — {WORKLOAD} is slow. Profile first and show the top 3 costs by time. Optimize only #1, measure again, report before/after. Stop if the win is under {THRESHOLD}.

## Explain / learn
35. **Teach me this concept** — Explain {CONCEPT} using an analogy, then precisely, then one worked example from {MY_CONTEXT}. End with a question that checks I understood the tricky part.
36. **Compare & choose** — I'm choosing between {A}, {B}, {C} for {USE_CASE} ({CONSTRAINTS}). Table them on the 4 axes that matter here, recommend one, and give the strongest argument against your pick.

## Meta / workflow
37. **Plan before code** — Before writing anything for {TASK}, produce a short plan: the approach, the files you'll touch, the risks, and the first checkpoint. Wait for my OK.
38. **Constrain the blast radius** — Do {TASK}, but touch only {ALLOWED_PATHS}. If you think you need to change anything else, stop and tell me why first.
39. **Small reversible steps** — Implement {FEATURE} as a sequence of commits, each independently revertible and green. After each, state what changed and what you verified. Don't batch it into one giant diff.
40. **Rubber-duck / red-team my plan** — Here's my plan: {PLAN}. Poke the 3 biggest holes, name one thing I'm assuming that might be false, and suggest the cheapest way to de-risk it before I start.
