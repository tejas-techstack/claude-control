---
name: improve-prompt
description: Read, understand, and rewrite a user prompt to be clearer, more specific, and verifiable — diagnosing what was underspecified. Use whenever the user shares a prompt to improve, says "why does the AI keep misunderstanding me", gets repeatedly wrong outputs, or asks how to phrase a request.
---

# Improve Prompt

Diagnose, rewrite, explain — keep the users intent sacred. Read `../_shared/GUARDRAILS.md` first.

## Diagnosis checklist (run the prompt through all of these)
- **Goal**: is the desired end state explicit, or implied? What would the model have to guess?
- **Context**: does the model know the stack/audience/constraints it needs? Anything it must NOT do?
- **Success criteria**: could two people disagree on whether an output satisfies it? Then it is underspecified.
- **Format**: is the output shape (length, structure, code vs prose, file vs inline) stated?
- **Verification**: does the prompt ask the model to check its own work against anything?
- **Scope creep / conflation**: is it 3 tasks in a trenchcoat? Split it.

## Rewrite rules
Keep the users intent and vocabulary; add structure only where it pays: [Role if it changes behavior] + Context + Task + Constraints + Output format + Verify-step. Concrete beats abstract ("under 200 words" not "concise"). Include one example if the format is unusual. Do not bloat a working prompt — sometimes the fix is deleting contradictions. `references/diagnosis.md` has the full checklist, the rewrite skeleton, and several before/after worked examples.

## Output format
1. **Diagnosis** — bullet list of what was underspecified/ambiguous (quote the offending phrase).
2. **Improved prompt** — in a copy-paste block. If the task warranted splitting, give the sequence.
3. **Minimal variant** — the shortest version that still fixes the main failure, for users who hate long prompts.
4. One sentence: what difference to expect.

## Chaining
- Input: any prompt (often from /prompt-suggest templates being adapted). Output: improved prompt; test it, then bake recurring ones into /control-skill.
