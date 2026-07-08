---
name: free-alternatives
description: Find free, subscription-less, privacy-respecting alternatives to any paid tool or service the user mentions, with an honest feature-gap comparison. Use whenever the user asks for a free alternative/replacement to X, complains about pricing or subscriptions, or a workflow depends on a paid service.
---

# Free Alternatives

Free, no card, privacy-respecting — with honest tradeoffs. Read `../_shared/GUARDRAILS.md` first.

## What qualifies
FOSS first; self-hostable a plus. "Free tier" only if it needs no card and the users actual usage fits inside it — say the limit out loud. Disqualify: trials, open-core where the needed feature is paid, and "free" tools funded by selling user data (check the privacy policy/telemetry reputation).

## Workflow
1. Pin the need: which 3-5 features of the paid tool does the user ACTUALLY use? (People replace "Photoshop", but they need "crop, layers, export webp".)
2. Hunt: web search "open source X alternative", AlternativeTo (free to browse), awesome-X lists on GitHub, european-alternatives.eu for services. Vet the top candidates via /github-explore quality bar (alive, adopted, licensed).
3. Compare against the users features, not the paid tools brochure. Note platform support and migration path (can it import the old tools files?).
4. Be honest when the free option loses: name the gap and the workaround, or say "for your use, the paid tool is genuinely better; nearest free is X minus Y".

## Output format
Table: Alternative | License/Model | Covers your features? | Privacy | Platforms | Migration. Then a recommendation with the single biggest tradeoff stated, plus install one-liner (/setup can take it from there).

## Chaining
- Input: a paid tool + the users real feature list. Output: vetted free pick; feeds /setup (install), /automation-how (wire it in).
