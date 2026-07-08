# Free & FOSS alternatives — starting catalog

A launch point, not gospel: **verify the current license and free-tier terms before recommending** (they change, and "free" sometimes quietly grows a card requirement). Prefer FOSS/self-hostable → genuinely free tier (no card) → open standards. Disqualify: trials, open-core where the needed feature is paid, and "free" tools that monetize by selling user data (check telemetry/privacy reputation). Compare against the user's *actual* 3-5 used features, not the paid tool's brochure.

## Creative & media

| Paid | Free alternatives |
|---|---|
| Photoshop | GIMP, Krita, Photopea (browser, free) |
| Illustrator | Inkscape |
| Figma | Penpot (self-hostable, FOSS) |
| Premiere / Final Cut | DaVinci Resolve (free tier), Shotcut, Kdenlive |
| After Effects | Blender, Natron |
| Audition | Audacity, Ocenaudio |
| Lightroom | darktable, RawTherapee |

## Productivity & docs

| Paid | Free alternatives |
|---|---|
| Notion | AppFlowy, Anytype, Obsidian (local md), Logseq |
| Office 365 | LibreOffice, OnlyOffice (self-host) |
| Google Docs (collab) | CryptPad, Etherpad, OnlyOffice |
| Airtable | NocoDB, Baserow (self-host) |
| Todoist | Vikunja, Super Productivity |
| Miro | Excalidraw, tldraw |

## Dev & infra

| Paid | Free alternatives |
|---|---|
| Postman | Bruno (FOSS, local), Hoppscotch, `curl`/`httpie` |
| GitHub Copilot | Continue + a local model (Ollama), Tabby (self-host) |
| Vercel/Netlify (beyond free tier) | GitHub Pages, Cloudflare Pages free tier, self-host + Caddy |
| Datadog | Grafana + Prometheus + Loki (self-host) |
| Sentry (hosted) | self-hosted Sentry, GlitchTip |
| Auth0 | Keycloak, Authentik, Ory (self-host) |
| Algolia | Meilisearch, Typesense (self-host) |
| Firebase | Supabase (FOSS, self-host), PocketBase, Appwrite |
| Zapier | n8n (self-host), Node-RED, plain cron + scripts |
| Heroku | Fly.io free-ish, Render free tier, Dokku (self-host) |
| ngrok (paid) | Cloudflare Tunnel (free), localtunnel |

## Data & AI

| Paid | Free alternatives |
|---|---|
| OpenAI API (for local-ok tasks) | Ollama / llama.cpp with open-weight models (Llama, Qwen, Mistral) |
| Pinecone/Weaviate cloud | Qdrant, Chroma, pgvector (self-host) |
| Firecrawl hosted | self-hosted Firecrawl (see `/firecrawl`), or the bundled `crawl.py` |
| Snowflake (small scale) | DuckDB, Postgres, ClickHouse (self-host) |

## Communication & sync

| Paid | Free alternatives |
|---|---|
| Slack (history limits) | Mattermost, Rocket.Chat, Zulip (self-host) |
| Dropbox | Nextcloud, Syncthing (P2P, no server) |
| Zoom (limits) | Jitsi Meet (FOSS, free) |
| 1Password | Bitwarden / Vaultwarden (self-host), KeePassXC |

## Where to hunt when it's not listed

- **alternativeto.net** — filter by "Open Source" / "Free" / "Self-Hosted".
- **awesome-selfhosted** (GitHub) — the canonical self-hostable index.
- **european-alternatives.eu** — privacy-focused SaaS alternatives.
- GitHub topic pages + `/github-explore` to vet a candidate's health.

## Deliver honestly

Table: Alternative | License/model | Covers your features? | Privacy | Platforms | Migration path. Then one recommendation with the single biggest tradeoff stated out loud. If the free option genuinely loses for the user's use, say so: "for your workflow the paid tool wins; the nearest free option is X minus feature Y." Include an install one-liner (`/setup` takes it from there).
