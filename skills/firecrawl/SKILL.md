---
name: firecrawl
description: Fetch, crawl, and convert web pages and documentation sites into clean LLM-ready markdown — locally and free, no API key or subscription. Use whenever the user wants to scrape a page, crawl docs, "get this site as markdown", pull web content into context, or another skill (research, free-alternatives, github-explore) needs page content.
---

# Firecrawl (local, free)

A free-first take on web crawling: local scripts first, the paid Firecrawl service never required. Read `../_shared/GUARDRAILS.md` first — robots.txt and rate limits are mandatory.

## Strategy ladder (climb only as far as needed)
1. **Single page** -> `python3 scripts/crawl.py fetch URL` (stdlib; strips nav/scripts, emits markdown-ish text + links).
2. **Docs site / many pages** -> `python3 scripts/crawl.py crawl URL --limit 30 --same-host` (BFS from the start page, respects robots.txt, 1 req/sec, saves one .md per page into `.crawl/`).
3. **JS-heavy page** (script output looks empty/broken) -> if Playwright is available (`pip install playwright && playwright install chromium` — free, local), render then extract; offer this install via /setup rather than assuming it.
4. **Site map first** -> `crawl.py map URL` lists sitemap.xml URLs so the user can pick before crawling.

## Rules
- Check robots.txt (the script does) and never work around a disallow. Honest User-Agent: `claude-control-crawler`.
- Public, reputable pages only; nothing behind logins/paywalls; no scraping of personal data.
- Big crawls: confirm scope with the user first ("~120 pages under /docs — proceed?").
- Keep context clean: write pages to `.crawl/`, read selectively; add `.crawl/` to .gitignore.

## Output format
Report: pages fetched, where saved, total approx tokens, and a 5-line content inventory. Then answer the users actual question from the content.

## Chaining
- Input: URLs/topics from /research, /free-alternatives, /github-explore.
- Output: .crawl/*.md corpus; feeds /humanize (learn a framework from its docs), /research.
