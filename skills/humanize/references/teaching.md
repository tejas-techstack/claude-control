# Teaching a codebase — frameworks & question bank

Two phases: teach, then verify. Goal is real understanding, not a wall of facts. Use `repo_map.py`/`context_pack.py` first and read only the central files (token thrift), then teach from evidence (file/line pointers), never vibes.

## Phase A — teach (in this order)

1. **Plain-language explanation** — what the system does, for whom, and how data flows through it, in words a smart newcomer gets. Analogies encouraged; define jargon on first use.
2. **What makes THIS one special** — the specific design decisions, tricks, or constraints that distinguish it, each with a file/line pointer as evidence.
3. **Similar systems** — 2-4 comparable projects (search the web if needed) with a one-line "same/different" each, so "special" has context.
4. **Prerequisite concepts** — the 3-6 ideas you must know first (event loop, B-tree, CRDT, backpressure…), each a 2-sentence primer + one free resource.

### Explanation techniques

- **Analogy then precision**: "It's like a post office — messages go in labeled boxes… concretely, it's a bounded channel with per-key partitions."
- **Data-flow narrative**: follow one real input from entry to output; understanding a system = understanding what moves through it.
- **Why-before-what**: the constraint that forced a design ("must survive a crash mid-write → they use a WAL") sticks better than the mechanism alone.
- **Concept scaffolding**: name the prerequisite, give the 2-sentence version, link one good free resource; don't send the learner off to read a textbook mid-tour.

## Phase B — verify (ask first: "Want me to check your understanding?")

Ask 3-5 questions, one at a time, concrete → conceptual. Diagnose honestly: confirm what's right, correct what's wrong with a pointer back to the code, and re-explain *differently* — never just repeat.

### Question ladder (adapt to the repo)

1. **Recall**: "Where does a request first enter the system?"
2. **Trace**: "What happens, step by step, when X occurs?"
3. **Why**: "Why did they choose Y over the obvious Z?"
4. **Predict**: "If input W were malformed, what would happen and where?"
5. **Transfer**: "Where else in the code does this same pattern appear?"

Finish with a **teach-it-back**: the user explains the system in 5 sentences; you review for the one thing they got subtly wrong. Offer to save the tour as `UNDERSTANDING.md`.

## Don't

- Don't dump all four teach-sections as walls of bullets — narrate.
- Don't quiz before teaching, or ask two questions at once.
- Don't assert specialness without a file/line to back it.
