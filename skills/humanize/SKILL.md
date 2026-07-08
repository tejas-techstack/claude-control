---
name: humanize
description: Explain a codebase or repository in human terms so the user truly understands it — what it does, what makes it special, similar systems, prerequisite concepts — then quiz the user and verify their understanding. Use whenever the user says "explain this repo/codebase", "help me understand this project", "walk me through this code", "what is special about X repo", or wants to learn a system deeply. Do NOT use for rewriting text to sound human — that is the humanizer skill.
---

# Humanize (understand any codebase)

Two phases: teach, then verify. Read `../_shared/GUARDRAILS.md` first.

## Phase A — Teach
Run `python3 <claude-control>/tools/repo_map.py` and `graphify.py` first; read maps, then only the central files (token thrift). Then produce, in this order:
1. **Plain-language explanation** — what the system does, for whom, and how data flows through it, in words a smart newcomer gets. Analogies encouraged; jargon defined on first use.
2. **What makes THIS one special** — the specific design decisions, tricks, or constraints that distinguish it (with file/line pointers as evidence, never vibes).
3. **Similar systems** — 2-4 comparable projects (search the web if needed) and a one-line "same/different" per project, so specialness has context.
4. **Prerequisite concepts** — the 3-6 ideas you must know first (e.g., event loops, CRDTs, B-trees), each with a 2-sentence primer and one free resource.

## Phase B — Verify (ask first: "Want me to check your understanding?")
- Ask 3-5 questions from concrete to conceptual ("What happens when a request hits X?" → "Why did they choose Y over Z?"). One question at a time.
- Diagnose answers honestly: confirm what is right, correct what is wrong with a pointer back to the code, and re-explain differently — never just repeat.
- Offer a final "teach it back" prompt: user explains the system in 5 sentences; you review.

## Chaining
- Input: any repo; use /guide for navigation afterwards, /research for the papers behind the ideas.
- Output: understanding doc (offer to save as UNDERSTANDING.md); feeds /improvements, /search-existing.
