---
name: improvements
description: Generate a curated, prioritized list of improvements for the current project — correctness, security, architecture, performance, DX — each with impact and effort. Use whenever the user asks "what should I improve", "what is missing", "make this better", "roadmap", or after finishing a milestone.
---

# Improvements

A short list that changes the project, not a dump of nitpicks. Read `../_shared/GUARDRAILS.md` first.

## Workflow
1. Map the repo with `repo_map.py`/`context_pack.py` (or the `/graphify .` skill for a deep graph); skim only central files, tests, CI, and README.
2. Collect candidates across: correctness bugs, security holes, missing tests on critical paths, architecture debt that blocks change, performance with real user impact, developer experience (setup pain, docs), and missing table-stakes features.
3. **Curate hard**: max 10 items. Cut anything that is a micro-optimization or pure style. Every item needs evidence (file:line or a reproduced behavior).
4. Score each: Impact (H/M/L) x Effort (H/M/L). Order by Impact desc, Effort asc. `references/rubric.md` has the candidate categories, the impact×effort matrix, the evidence standard, and an explicit "what NOT to include" list.

## Output format
ALWAYS use this exact template per item:
**N. Title** — [Impact: H|M|L, Effort: H|M|L]
Evidence: file/behavior. Why it matters: 1-2 sentences. First step: one concrete action.
End with: "Top 3 I would do first and why", and offer to implement #1.

## Chaining
- Input: repo; richer after /humanize or /critical-review.
- Output: prioritized list; feeds /focus-review (verify fixes), /search-existing (replace instead of improve), /create-test-suite.
