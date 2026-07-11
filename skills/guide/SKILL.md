---
name: guide
description: Navigate a complex repository like a human tour guide — entry points, "if you want X look in Y", guided walks with checkpoints. Use whenever the user asks "where is X handled", "where do I start reading", "how is this repo organized", "give me a tour", or is clearly lost in a codebase.
---

# Guide (repo navigation)

Turn a maze into a map. Read `../_shared/GUARDRAILS.md` first.

## Workflow
1. Build the map cheaply: `python3 <claude-control>/tools/repo_map.py` + `context_pack.py` (which ranks files by import in-degree). Read the outputs, not the whole repo. For a deep dependency/knowledge graph, use the `/graphify .` skill.
2. Identify: entry points (main/index/cli/server), the 5-8 load-bearing files (graph centrality), config surface, test layout, and where generated/vendored code lives (mark as "do not read"). `references/navigation.md` has the "if you want X, look in Y" lookup table (routes, models, auth, jobs, config…) and a flow-tracing method.
3. Deliver the tour in this order:
   - **You are here** — one paragraph: what kind of codebase, how big, how it is layered.
   - **Doors** — the entry points and what walking through each shows you.
   - **If you want X, look in Y** — a lookup table for the 6-10 most likely intents (change the API, add a model, fix styling, find the DB schema...).
   - **Guided walk** — offer to trace ONE real flow end-to-end (e.g., "a request comes in") with checkpoints; at each checkpoint ask "clear so far?" before continuing.
4. Offer to save the tour as `TOUR.md` in the repo.

## Chaining
- Input: repo; pairs with /humanize (guide = where, humanize = why/how).
- Output: TOUR.md; feeds /improvements, /focus-review.
