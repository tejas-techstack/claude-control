---
name: skills-interleave
description: Combine multiple installed skills into one pipeline so their outputs feed each other, and let skills invoke other skills (e.g., search-existing uses github-explore, research uses firecrawl). Use whenever a task spans several skills, the user asks to "combine skills", "chain skills", or a single skill hits a step another skill does better.
---

# Skills Interleave (composition layer)

Skills are files; composing them means reading the right SKILL.md at the right step. Read `../_shared/GUARDRAILS.md` first.

## How skills call skills
Every claude-control skill ends with a **Chaining** section declaring its inputs and outputs. To have skill A use skill B mid-task: pause A, read `~/.claude/skills/B/SKILL.md` (or the project-local copy), execute B with As intermediate artifact as input, then resume A with Bs output. Announce each hop in one line ("-> using /github-explore to vet candidates").

## Workflow
1. Decompose the user goal into stages; for each stage pick the best installed skill (use /skill-suggestions if unsure). Read only the SKILL.md files you will actually use.
2. Draw the pipeline BEFORE executing and show it:
   `/research (brief) -> /cross-check (SPEC.md) -> build -> /create-test-suite (CI) -> /focus-review`
   Name the artifact passed across each arrow.
3. Resolve conflicts by specificity: a skills own rules > this skill > general habits. Guardrails always win.
4. Execute stage by stage. After each stage, confirm the artifact exists and is sane before feeding it forward; on failure, fix the stage — do not push garbage downstream.
5. Offer to save a working pipeline as a new composite skill via /control-skill.

## Known-good pipelines (starters)
- Ship a feature: /cross-check -> /prompt-suggest -> build -> /create-test-suite -> /focus-review
- Adopt a repo: /github-explore -> /humanize -> /setup -> /guide
- De-bloat a codebase: /improvements -> /search-existing -> /github-explore -> migrate -> /focus-review
- Research to prototype: /research -> /creative-spin -> /cross-check -> build in /isolate

`references/pipelines.md` has the full catalog (8+ pipelines with the artifact named on each arrow) plus the composition rules and a recipe for building your own.

## Chaining
- Input: any multi-stage goal. Output: an executed pipeline + its artifacts; persist good pipelines with /control-skill.
