# Self-hosting the real Firecrawl (free)

Read this when Tier 0 (`crawl.py`) can't handle a page and you're standing up the actual Firecrawl engine. Firecrawl is open source under **AGPL-3.0** ([github.com/firecrawl/firecrawl](https://github.com/firecrawl/firecrawl)); self-hosting is fully free and needs no API key. The authoritative guide is the repo's `SELF_HOST.md` — always defer to it if these notes drift from the current release.

## What you get vs. the stdlib crawler

| | `crawl.py` (Tier 0) | self-hosted Firecrawl (Tier 1) |
|---|---|---|
| Dependencies | none (Python stdlib) | Docker + ~8GB RAM |
| JS rendering | no | yes (headless browser) |
| PDF / structured extraction | no | yes |
| Speed to first result | instant | minutes on first `up` |
| Cost | free | free |

Rule: only climb to Tier 1 when Tier 0's markdown comes back empty or mangled, or the user needs Firecrawl-grade extraction. Don't spin up containers for a page `curl` could read.

## Prerequisites

- **Docker** (or Podman + podman-compose). No Docker? Route to `/setup` first, or use the Playwright alternative in SKILL.md.
- **~8GB RAM free** and a few GB of disk for images. The stack is several services (API, worker, Redis, a headless browser).
- **Ports**: the API binds `3002` on the host by default. Change with `FIRECRAWL_PORT` before `up` if it's taken.

## Bring it up (managed by `scripts/firecrawl_selfhost.sh`)

```bash
bash scripts/firecrawl_selfhost.sh up       # clone/pull + docker compose up -d + health wait
bash scripts/firecrawl_selfhost.sh status   # is the API answering?
bash scripts/firecrawl_selfhost.sh logs     # tail compose logs while it builds
bash scripts/firecrawl_selfhost.sh down     # stop the stack (images/data kept)
```

The script clones into `~/.claude/claude-control/services/firecrawl`, seeds a `.env` from the example, and ensures `USE_DB_AUTHENTICATION=false` so **no API key is required**.

### Fast path — skip the ~8GB source build

The repo's `docker-compose.yaml` defaults to *building* every service from source. It also ships commented `image:` lines pointing at prebuilt images on GitHub Container Registry (GHCR). To avoid the long build, edit the compose file once and uncomment those `image:` directives (and comment the matching `build:` blocks), then re-run `up`. This pulls ready-made images instead of compiling. See `SELF_HOST.md` → "Using pre-built images" for the exact lines in the current release.

## Drive it (no SDK, no key) — `scripts/fc_api.py`

```bash
export FIRECRAWL_API_URL=http://localhost:3002
python3 scripts/fc_api.py scrape https://example.com -o page.md
python3 scripts/fc_api.py map    https://docs.example.com --limit 200
python3 scripts/fc_api.py crawl  https://docs.example.com --limit 40 -d .crawl
```

Endpoints it uses (Firecrawl v1):

- `POST /v1/scrape` — `{ "url", "formats": ["markdown"] }` → `{ data: { markdown } }`
- `POST /v1/map` — `{ "url", "limit" }` → `{ links: [...] }`
- `POST /v1/crawl` — `{ "url", "limit", "scrapeOptions": {"formats":["markdown"]} }` → `{ id }`; poll `GET /v1/crawl/{id}` for `{ status, data: [...] }`

`fc_api.py` sends `Authorization: Bearer local`; with DB auth off the token is ignored, so self-host works with no real key.

## Troubleshooting

- **API never comes up**: `... logs` — first build is slow; a browser/Redis service may still be starting. Give it a few minutes.
- **Port 3002 in use**: `FIRECRAWL_PORT=3010 bash scripts/firecrawl_selfhost.sh up`, then point `FIRECRAWL_API_URL` at the new port.
- **Out of memory / OOM-killed containers**: free RAM or use the prebuilt-image fast path; the headless browser is the hungry part.
- **Scrape returns empty on a specific site**: some sites block automated browsers; respect that (guardrails) rather than evading it.

## Remove it entirely

```bash
bash scripts/firecrawl_selfhost.sh down
rm -rf ~/.claude/claude-control/services/firecrawl     # clone + its .env
docker image prune                                     # optional: reclaim image space
```

## Licensing note

Firecrawl is AGPL-3.0. Running it locally for your own crawling is fine. If you build a *service* on top of a modified Firecrawl and expose it over a network, AGPL's network-copyleft obligations apply — mention this if the user talks about redistributing or hosting it for others.
