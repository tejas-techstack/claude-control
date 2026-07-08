---
name: firecrawl
description: Fetch, crawl, and convert web pages and documentation sites into clean LLM-ready markdown — locally and free, no API key or subscription. Use whenever the user wants to scrape a page, crawl docs, "get this site as markdown", pull web content into context, or another skill (research, free-alternatives, github-explore) needs page content. Escalates from a stdlib crawler to a self-hosted copy of the real Firecrawl engine for JS-heavy sites.
---

# Firecrawl (local, free)

Web → clean markdown, using only free and local tools. The paid hosted Firecrawl API is never required: for hard pages we run the **real Firecrawl engine on your own machine** (it's open source, AGPL-3.0). Read `../_shared/GUARDRAILS.md` first — robots.txt and rate limits are mandatory.

## Strategy ladder — climb only as far as the page forces you

**Tier 0 · stdlib crawler (`scripts/crawl.py`)** — default; zero dependencies, instant.

- Single page → `python3 scripts/crawl.py fetch URL` (strips nav/scripts, emits markdown + links).
- Docs site / many pages → `python3 scripts/crawl.py crawl URL --limit 30 --same-host` (BFS, robots-respecting, 1 req/s, one `.md` per page into `.crawl/`).
- Sitemap first → `python3 scripts/crawl.py map URL` lists `sitemap.xml` URLs so the user picks scope before a crawl.

**Tier 1 · self-hosted Firecrawl (the real engine, pulled from GitHub)** — when Tier 0's output is empty/broken because the page renders client-side (React/Vue/Next), or you need Firecrawl-grade extraction, PDFs, or structured crawls. Free, runs entirely local.

- Bring it up (needs Docker; **ask first** — it clones a repo and starts containers): `bash scripts/firecrawl_selfhost.sh up`. Clones `github.com/firecrawl/firecrawl`, runs `docker compose up -d`, waits for `http://localhost:3002`. First run builds/pulls images (~minutes, wants ~8GB RAM free); `references/firecrawl.md` has the fast prebuilt-image path and troubleshooting.
- Use it (no API key — self-host disables auth): `FIRECRAWL_API_URL=http://localhost:3002 python3 scripts/fc_api.py scrape URL` / `map URL` / `crawl URL --limit N`.
- Stop it when done: `bash scripts/firecrawl_selfhost.sh down`.

**Lighter tier-1 alternative** — if the user won't run Docker, a single JS page can be rendered with Playwright (`pip install playwright && playwright install chromium`, free/local); offer this install via `/setup` rather than assuming it. Docker-based self-host is preferred for anything beyond one page.

## Rules (all tiers)

- Check robots.txt (Tier 0 does automatically) and never work around a disallow. Honest User-Agent.
- Public, reputable pages only; nothing behind logins/paywalls; never scrape personal data.
- Big crawls or standing up containers: confirm scope/consent first ("~120 pages under /docs, and I'll start 3 Docker containers — proceed?").
- Keep context clean: write pages to `.crawl/`, read selectively; `.crawl/` is already git-ignored here.
- Never point `fc_api.py` at the paid hosted API unless the user supplies their own key and explicitly opts in — self-host is the free default.

## Output format
Report: which tier you used and why, pages fetched, where saved, total approx tokens, and a 5-line content inventory. Then answer the user's actual question from the content.

## Chaining
- Input: URLs/topics from `/research`, `/free-alternatives`, `/github-explore`.
- Output: `.crawl/*.md` corpus; feeds `/humanize` (learn a framework from its docs), `/research`. Deep self-host details live in `references/firecrawl.md`.
