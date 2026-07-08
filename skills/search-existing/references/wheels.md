# Reinvented-wheel catalog — hand-rolled → battle-tested

When you spot one of these hand-rolled in a repo, a well-tested library almost always does it better. Verify the library still meets the `/github-explore` bar (alive, adopted, permissively licensed, free) before recommending — versions and maintenance change. **Crypto and auth are top priority: home-rolled versions are a finding by themselves.**

## The usual suspects (what to grep for)

Retry/backoff loops, date math, cron parsing, arg parsing, config loading, HTTP clients, caching/memoization, rate limiting, state machines, CSV/JSON/YAML parsing, schema validation, templating, UUID/ID generation, password hashing, JWT handling, pagination, connection pooling, task queues, file watching, diffing.

## Python

| Reinvented | Reach for | Note |
|---|---|---|
| retry loops | `tenacity` | backoff, jitter, conditions |
| date math / parsing | `python-dateutil`, stdlib `zoneinfo` | stop hand-parsing dates |
| arg parsing | stdlib `argparse`, `click`, `typer` | argparse is usually enough |
| settings | `pydantic-settings`, stdlib `configparser` | validation + env |
| HTTP | `httpx`, `requests` | don't hand-roll `urllib` retries |
| schema validation | `pydantic`, `jsonschema` | |
| password hashing | `argon2-cffi`, `bcrypt` (via `passlib`) | never hashlib for passwords |
| JWT | `pyjwt`, `authlib` | never hand-roll signing |
| retry+cache | `cachetools`, stdlib `functools.lru_cache` | |
| CLI tables/progress | `rich` | |
| data validation/frames | `pandas`/`polars` only if the problem is real tabular work | don't pull pandas to sum a list |

## JavaScript / TypeScript

| Reinvented | Reach for | Note |
|---|---|---|
| date math | `date-fns`, `Temporal` (as it lands), `Luxon` | avoid moment (legacy) |
| validation | `zod`, `valibot` | runtime + types |
| HTTP | `undici`/`fetch`, `ky`, `axios` | native fetch first |
| retry | `p-retry` | |
| cron parse | `cron-parser` | |
| CLI | `commander`, `yargs` | |
| env/config | `dotenv` + `zod` | |
| uuid | `crypto.randomUUID()` (built-in) | no dep needed |
| deep utils | native + a few `lodash-es` fns | don't import all of lodash |

## Go

| Reinvented | Reach for | Note |
|---|---|---|
| CLI | stdlib `flag`, `cobra` | |
| config | `viper`, stdlib `encoding/json` | |
| retry | `cenkalti/backoff` | |
| HTTP router | stdlib `net/http` (1.22+ patterns), `chi` | stdlib is strong now |
| structured logging | stdlib `log/slog` | |
| UUID | `google/uuid` | |

## Rust

| Reinvented | Reach for | Note |
|---|---|---|
| CLI | `clap` | |
| async runtime | `tokio` | |
| serialization | `serde` + `serde_json` | |
| errors | `thiserror` (libs), `anyhow` (apps) | |
| HTTP | `reqwest` | |
| time | `chrono`, `time` | |

## Cross-language / infra

- **Rate limiting, queues, locks**: Redis + a maintained client beats a hand-rolled in-memory scheme once you have >1 process.
- **Full-text search**: SQLite FTS5, Meilisearch, Typesense — not a `LIKE '%x%'` scan.
- **Background jobs**: a real queue (Celery/RQ, BullMQ, Sidekiq, asynq) beats a homemade DB-polling loop.
- **Feature flags, migrations, i18n**: mature tools exist; hand-rolled versions rot.

## Judge honestly per candidate

- **REPLACE** — the library is strictly better and the dep cost is proportionate.
- **KEEP** — the custom code carries real domain logic, or the dep is heavier than the problem (don't add pandas to sum 3 numbers). Custom is sometimes correct — say so.
- **WRAP** — keep the current interface, swap the internals behind an adapter.

Dependencies have costs too: supply-chain risk, bundle size, learning curve, transitive bloat. Name them. Migration plan for each REPLACE: adapter-first → pin current behavior with tests → swap → remove. Estimate effort S/M/L.
