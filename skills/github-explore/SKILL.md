---
name: github-explore
description: Explore GitHub for well-tested, actively maintained repositories that do what the user (or another skill) needs, judged by real quality signals rather than stars alone. Use whenever the user asks to find a library/tool/repo for a task, compare GitHub projects, "is there something that already does X", or another skill needs candidate repos.
---

# GitHub Explore (quality-filtered)

Stars are marketing; maintenance is truth. Read `../_shared/GUARDRAILS.md` first.

## Workflow
1. Sharpen the need into capabilities ("parse cron expressions in Go, stdlib-style API") — search capabilities, not vibes.
2. Search: GitHub search (web or `https://api.github.com/search/repositories?q=...` — no key needed for light use), plus awesome-lists and topic pages for the domain. Collect 5-10 candidates.
   - Shortcut: `python3 scripts/repo_health.py --search "cron parser language:go"` (or pass explicit `owner/repo` names) fetches and **scores** candidates on the signals below, then ranks them. Set `GITHUB_TOKEN` to raise the rate limit; `--json` to pipe into a comparison.
3. Score each candidate on the quality bar (`repo_health.py` automates most of this):
   - **Alive**: last commit / release recency; issues get responses; not "looking for maintainers".
   - **Tested**: real test directory, CI badge that passes.
   - **Adopted**: downloads (npm/PyPI/crates), dependents, who uses it in production.
   - **Governed**: license (must be permissive-compatible and FREE — no open-core traps for the needed features), more than one contributor (bus factor).
   - **Fits**: API shape, size, and deps proportionate to the problem.
4. Read the README and skim the code of the top 2-3 — enough to confirm the docs are not lying. Never recommend from the description alone.

## Output format
Comparison table: Repo | What it is | Alive | Tested | Adopted | License | Fit note. Then: "Recommendation: X, because... Runner-up: Y if [condition]." Include clone/install one-liners. If nothing meets the bar, say so — that IS the answer, and it feeds /creative-spin or a build decision.

## Chaining
- Input: a capability need (often from /search-existing, /free-alternatives, /research).
- Output: vetted repo shortlist; feeds /humanize (understand the winner), /setup (install it).
