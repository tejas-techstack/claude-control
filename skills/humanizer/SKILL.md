---
name: humanizer
description: Rewrite AI-flavored writing and code artifacts (comments, docstrings, README, commit messages, UI copy) so they read like a competent human wrote them — removing AI tells while preserving meaning. Use whenever the user says humanize, "sounds like AI", "make this natural", de-slop, or before publishing generated text/docs. Do NOT use for explaining a codebase — that is the humanize skill.
---

# Humanizer (de-AI text and code artifacts)

Remove the tells, keep the substance, do not gut legitimate prose. Read `../_shared/GUARDRAILS.md` first. The full catalog of prose + code tells (each with a fix, plus before/after guidance and the "do not overcorrect" rules) is in `references/ai-tells.md` — open it when doing a thorough pass; the summary below is the quick version.

## Tells to hunt (prose)
- Significance inflation ("pivotal", "testament to", "in todays fast-paced world"), promotional adjectives ("seamless", "robust", "vibrant"), AI vocabulary ("delve", "leverage", "tapestry", "landscape", "crucial").
- Structure tells: rule-of-three everywhere, "Its not just X, its Y", bullet lists where a sentence would do, every paragraph the same length, em-dash overuse, bold-word-per-line.
- Hedging and filler ("Its worth noting"), vague attributions ("experts believe" -> cite or cut), chatbot artifacts ("Great question!", "I hope this helps"), tidy moral-of-the-story conclusions.

## Tells to hunt (code artifacts)
- Comments that narrate the obvious (`i += 1  # increment i`) — delete; keep only WHY comments.
- Docstrings that restate the signature; READMEs with badge walls, empty "Features" hype, or emoji-section headers; commit messages like "Enhanced functionality and improved robustness" -> rewrite to what actually changed and why.
- Over-generic names (data2, ManagerHelper) where a domain word exists.

## Workflow
1. If the user has a voice sample (their own writing), ask for 2-3 paragraphs and match its rhythm and vocabulary instead of a generic "clean" voice.
2. Rewrite, then self-audit: read the result asking "what still smells generated?" and do a second pass.
3. Do not overcorrect: real humans write plainly too; polish is not proof of AI. Keep technical precision — never trade correctness for flavor. This skill is for making honest writing better, not for disguising authorship where AI disclosure is required (e.g., academic integrity policies) — if that is the situation, say so instead.

## Output format
The rewrite, then a short "Changes" list grouped by tell (so the user learns the patterns).

## Chaining
- Input: any text/README/comments (e.g., a /design pages copy). Output: humanized version; pair with /critical-review for substance, this skill for voice.
