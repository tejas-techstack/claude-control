# Free scholarly sources — cheatsheet

All free, all no-login. `scripts/paper_search.py` already queries the first two; use the rest by web search restricted to their domains. Never touch paywalled PDFs — find the open version instead.

## Programmable APIs (no key)

| Source | Endpoint | Notes |
|---|---|---|
| **arXiv** | `http://export.arxiv.org/api/query?search_query=all:TERMS&max_results=20` | Atom XML. Preprints in CS/math/physics/stat/econ/q-bio. `sortBy=relevance|submittedDate`. |
| **Semantic Scholar** | `https://api.semanticscholar.org/graph/v1/paper/search?query=TERMS&fields=title,abstract,year,citationCount,openAccessPdf,externalIds` | JSON. Free tier is rate-limited without a key (HTTP 429) — `paper_search.py` degrades to arXiv-only when that happens. `openAccessPdf` often gives a free copy of an otherwise-paywalled paper. |
| **OpenAlex** | `https://api.openalex.org/works?search=TERMS` | JSON, generous free tier. Huge coverage; good for citation counts and concepts when S2 is throttled. Add `&mailto=you@example.com` to get the polite pool. |
| **Crossref** | `https://api.crossref.org/works?query=TERMS` | JSON. Best for DOIs, metadata, and resolving a citation to a canonical record. |
| **PubMed / E-utilities** | `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=TERMS` | Biomed. Follow with `efetch` for abstracts; PMC has free full text. |
| **Unpaywall** | `https://api.unpaywall.org/v2/DOI?email=you@example.com` | Given a DOI, returns a legal free full-text location if one exists. The right tool when a paper looks paywalled. |

## Search-by-domain (use the web / `/firecrawl`)

- **arXiv listing** `arxiv.org/list/<cat>/recent` — browse a subfield's newest.
- **ACL Anthology** `aclanthology.org` — NLP; every paper free.
- **OpenReview** `openreview.net` — ICLR/NeurIPS reviews + PDFs, free.
- **PMC** `ncbi.nlm.nih.gov/pmc` — free biomed full text.
- **DOAJ** `doaj.org` — directory of open-access journals.
- **Papers with Code** `paperswithcode.com` — links papers to code + benchmark leaderboards (great for SOTA claims).
- **dblp** `dblp.org` — authoritative CS bibliography; disambiguate authors/venues.

## Query craft

- Search **capabilities and methods**, not vibes: `"contrastive" "pretraining" "graph"` beats `"good graph model"`.
- Use each engine's operators: arXiv `au:`, `ti:`, `abs:`, `cat:cs.LG`; Crossref/OpenAlex filters for year/type.
- Start narrow, widen if <5 hits. Always include 1–2 recent (≤2y) items even if lightly cited — the field moves.
- Deduplicate by DOI first, then normalized title (preprint vs. published version are the same work).

## Integrity rules

- A paywalled paper is not a dead end: check arXiv + `openAccessPdf` + Unpaywall for the free version, and say plainly when none exists.
- Never invent a title, author, year, venue, DOI, or citation count. If a number is unknown, write "n/a".
- Citation counts differ across engines (S2 vs OpenAlex vs Google Scholar) — cite the source of the number.
- Quote the abstract's actual claim; don't infer results you didn't read.
