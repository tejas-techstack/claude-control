# Prompt diagnosis & rewrite — checklist and worked examples

Diagnose, rewrite, explain — keep the user's intent and vocabulary sacred. Add structure only where it pays; sometimes the fix is *deleting* a contradiction, not adding words.

## Diagnosis checklist (run the prompt through all of these)

- **Goal** — is the desired end state explicit, or must the model guess it?
- **Context** — does the model know the stack/audience/constraints it needs? Anything it must NOT do?
- **Success criteria** — could two people disagree on whether an output satisfies it? Then it's underspecified.
- **Format** — is the output shape stated (length, structure, code vs prose, file vs inline)?
- **Verification** — does the prompt ask the model to check its own work against anything?
- **Scope/conflation** — is it three tasks in a trenchcoat? Split it.
- **Contradictions** — "make it detailed but under 50 words" — resolve before sending.

## Rewrite skeleton (use only the parts that earn their place)

```
[Role — only if it changes behavior]
Context: <stack, audience, constraints, what exists already>
Task: <the specific thing, one goal>
Constraints: <must / must-not, concrete: "under 200 words", "stdlib only">
Output format: <exact shape; give an example if unusual>
Verify: <how the model should self-check before finishing>
```

Concrete beats abstract: "under 200 words" not "concise"; "return a JSON array of {id,score}" not "structured output".

## Worked examples

**Before:** "Write some tests for my code."
**Diagnosis:** no target (which code?), no framework, no idea what "done" means, no failure cases implied.
**After:** "For `payments.py`'s `refund()` (pytest), write 3 tests: a normal refund, a refund exceeding the original charge (must raise `ValueError`), and a double-refund (must be idempotent). Runnable with `pytest -q`. Show the file."

**Before:** "Make this faster and also add features and clean it up."
**Diagnosis:** three tasks conflated; no metric for "faster"; "features" unspecified.
**After (split):** "1) Profile `ingest()` and cut its runtime on a 1M-row file — report before/after. [then] 2) List the top 3 features worth adding with effort estimates; don't build yet. [then] 3) Only after I pick, refactor."

**Before:** "Explain this in a good way."
**After:** "Explain what `scheduler.py` does to a backend dev who's new to this repo: one paragraph on the data flow, then the one non-obvious design decision and why. Under 150 words, no bullet lists."

## Output format

1. **Diagnosis** — bullets of what was underspecified/ambiguous (quote the offending phrase).
2. **Improved prompt** — copy-paste block; if it warranted splitting, give the sequence.
3. **Minimal variant** — the shortest version that still fixes the main failure.
4. One sentence: what difference to expect.

Bake recurring good prompts into `/control-skill`; adapt library templates via `/prompt-suggest`.
