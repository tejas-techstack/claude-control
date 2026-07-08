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
