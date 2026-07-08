---
name: research
description: Scour free, open-access academic sources (arXiv, OpenReview, Semantic Scholar, ACL Anthology, PubMed, DOAJ) for papers, surveys, and prior art. Use whenever the user wants a literature review, asks "what papers exist on X", wants to find related work, state of the art, benchmarks, citations, or mentions arXiv/ACM/IEEE/research. Also use before building anything novel to check what already exists.
---

# Research

Find, filter, and synthesize academic work using only free and open-access sources. Read `../_shared/GUARDRAILS.md` first if you have not this session.

## Fast start — run the search tool
`python3 scripts/paper_search.py "your topic" --limit 15 --since 2021` queries arXiv + Semantic Scholar, deduplicates, and prints a ranked shortlist with free-PDF links (it degrades to arXiv-only if S2 rate-limits). Use `--json` to pipe the results. Then read abstracts and synthesize. Full source list, APIs, query operators, and integrity rules are in `references/sources.md`.

## Sources (in priority order — all free)
1. **arXiv** and **Semantic Scholar** — covered by the script above; both free, no key.
2. **OpenAlex / Crossref / Unpaywall** — huge coverage and DOI→free-PDF resolution when S2 is throttled (see `references/sources.md`).
3. **OpenReview, ACL Anthology, PubMed Central, DOAJ, Papers with Code, dblp** — via web search or `/firecrawl` restricted to those domains.
4. ACM/IEEE pages may be browsed for metadata (title/abstract/citations) but NEVER attempt to access paywalled PDFs. When a paper is paywalled, check arXiv, `openAccessPdf`, and Unpaywall for the free version and say plainly when none exists.

## Workflow
1. Clarify scope in one question if the topic is broad: subfield, years, application vs theory, how many papers.
2. Run `paper_search.py` (or query ≥2 sources by hand). Deduplicate by DOI then normalized title.
3. Rank by relevance first, then citation count and recency. Include 1-2 recent (last 2 years) items even if lightly cited.
4. For the top 5-10: read abstracts (fetch the abstract page or API, not full PDFs unless asked). Never cite a paper you did not open.
5. Synthesize — do not just list.

## Output format
ALWAYS use this exact template:
# Research brief: [topic]
## Landscape (3-6 sentences: schools of thought, where the field is moving)
## Key papers
For each: **Title** (year, venue) — 2-3 sentence contribution summary — why it matters for the user — [free link] — BibTeX on request
## Gaps and open problems
## Suggested next reads

## Chaining
- Input: a topic or a repo (pair with /humanize to research the ideas behind a codebase).
- Output: research brief; feeds /cross-check (requirements), /creative-spin (novelty check), /prompt-suggest.
