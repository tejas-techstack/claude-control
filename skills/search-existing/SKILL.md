---
name: search-existing
description: Scan the repo for hand-rolled components that could be replaced by existing, well-tested, better-optimized libraries or systems, and produce a migration plan. Use whenever the user asks "am I reinventing the wheel", "is there a library for this", wants to reduce maintenance burden, or a review reveals custom implementations of solved problems.
---

# Search Existing (stop reinventing wheels)

Find the hand-rolled, match it to battle-tested replacements, and be honest when custom is correct. Read `../_shared/GUARDRAILS.md` first.

## Workflow
1. **Scan** — repo_map.py + grep for classic wheel-reinventions: date/time math, retry/backoff, caching, argument parsing, HTTP clients, auth/JWT/crypto (highest priority — custom crypto is a finding by itself), state machines, schedulers, CSV/JSON parsing, validation, templating, queues. `references/wheels.md` is a per-language catalog (Python/JS/Go/Rust/infra) mapping each hand-rolled pattern to its battle-tested replacement.
2. **For each candidate**, capture: what it does, LOC, test coverage, and any custom behavior a replacement must preserve.
3. **Find replacements** via /github-explore quality bar: maintained (commits within ~a year), widely used (downloads/dependents), permissive license compatible with the project, no paid tier required for the needed features.
4. **Judge honestly per candidate**: REPLACE (lib is strictly better) / KEEP (custom carries real domain logic or the dep is heavier than the problem) / WRAP (keep interface, swap internals). Dependencies have costs too — supply chain, size, learning — say so.
5. **Migration plan** for each REPLACE: adapter-first strategy, test-pinning current behavior (prompt 10 in /prompt-suggest), swap, remove. Estimate effort S/M/L.

## Output format
Table: Component | Where | Verdict | Replacement (license) | Effort | Risk. Then the one migration with the best payoff, planned in steps. Offer to execute it.

## Chaining
- Input: repo; often triggered by /improvements or /critical-review findings.
- Output: replacement plan; uses /github-explore; verify with /create-test-suite.
