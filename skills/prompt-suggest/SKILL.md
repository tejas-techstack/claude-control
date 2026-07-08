---
name: prompt-suggest
description: Suggest ready-to-fill prompt templates for what the user is doing — building from scratch, modifying, testing, debugging, reviewing, migrating, documenting and more. Use whenever the user asks "how should I prompt this", "give me a prompt for X", seems to be getting poor results from vague prompts, or is starting a common task type where a strong template exists.
---

# Prompt Suggest

Give the user prompts that work, not lectures about prompting. Read `../_shared/GUARDRAILS.md` first.

## Workflow
1. Classify the task (build / modify / test / debug / review / understand / migrate / document / optimize / automate / data / SQL / devops / frontend / concurrency / meta).
2. Open `references/prompt-library.md` in this skill folder (40 templates across those categories) and pick the 2-4 best matches — never dump the whole library.
3. **Pre-fill every variable you can** from the current context (repo name, stack, file paths). Leave the rest as `{PLACEHOLDERS}` with a one-line note on what to put there.
4. For each suggestion: template name, when it beats winging it, the filled prompt in a copy-paste block, and one common mistake it prevents.
5. If no template fits, write a new one on the spot in the same structure (role / context / task / constraints / output format / verification) and offer to append it to the library.

## Chaining
- Input: any task; strongest right after /cross-check (spec becomes context) or /i-have-no-idea.
- Output: filled prompts; pair with /improve-prompt to refine a prompt the user already wrote.
