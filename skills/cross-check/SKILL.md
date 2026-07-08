---
name: cross-check
description: Thoroughly interrogate the user about expectations BEFORE any code or docs get generated, producing a signed-off spec. Use whenever the user is about to start building something non-trivial, gives vague or large requirements, says "build me X", or asks to plan a feature/system — proactively suggest it before generating significant code. First ask whether they want a deep or shallow cross-check.
---

# Cross-Check (requirements interrogation)

No code until the spec is agreed. Read `../_shared/GUARDRAILS.md` first.

## Step 0 — always ask first
"Deep cross-check (multi-round, ~15 questions, produces a full spec) or shallow (one round, 5-7 questions, produces a one-page brief)?" Respect the answer.

## Shallow mode — one round, then brief
Ask the 5-7 highest-leverage questions in a single message: goal in one sentence; primary user; must-have vs nice-to-have; hard constraints (stack, platform, deadline, free-only?); what does DONE look like (acceptance criteria); what is explicitly OUT of scope. Then write a one-page brief and get a yes/no.

## Deep mode — rounds, max ~3 questions each
1. **Intent** — problem behind the request, who feels the pain, what happens if nothing is built.
2. **Shape** — inputs/outputs, interfaces (CLI/API/UI), data lifetime, scale honestly expected.
3. **Constraints** — stack, environment, budget (default: free), security/privacy needs, existing code it must fit.
4. **Edges** — the 3 worst inputs, failure behavior, concurrency, migration.
5. **Done** — measurable acceptance criteria, non-goals, how the user will verify.
6. **Hidden assumptions** — surface and challenge anything the request takes for granted.
Draw the exact questions (plus domain add-ons for web/data/CLI/API/ML/automation) from `references/question-bank.md`. Challenge contradictions politely and immediately. Offer defaults so answering is cheap ("Default X — object?").

## Output format
Write `SPEC.md` from `assets/SPEC-template.md`: Goal / Users / Requirements (MoSCoW) / Non-goals / Constraints / Interfaces & data / Edge cases / Acceptance criteria / How the user verifies / Open questions. End with: "Reply APPROVE to lock this spec; building starts only after approval."

## Chaining
- Input: a raw idea; pairs with /i-have-no-idea when even the idea is unclear.
- Output: SPEC.md; feeds /create-test-suite (tests from acceptance criteria), /prompt-suggest, /improve-prompt.
