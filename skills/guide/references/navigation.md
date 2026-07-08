# Repo navigation patterns

Turn a maze into a map cheaply. Build the map with `repo_map.py` + `graphify.py` and read the outputs, not the whole repo. The load-bearing files are the ones with high import in-degree (graphify centrality) — read those first; they explain the most per token.

## "If you want X, look in Y" — where things usually live

| Intent | Look for |
|---|---|
| Entry point / how it starts | `main`, `index`, `cli`, `app`, `server`, `__main__`, `bin/`, `cmd/`; `package.json` "scripts"/"bin", `pyproject` `[project.scripts]` |
| HTTP routes / API surface | `routes`, `controllers`, `handlers`, `api/`, `urls.py`, `router`, framework decorators |
| Data model / schema | `models`, `schema`, `entities`, `migrations/`, `*.sql`, ORM classes |
| Business logic | `services`, `core`, `domain`, `lib`, `usecases` (not the controller) |
| Config / settings | `config`, `settings`, `.env(.example)`, `*.toml/yaml/ini`, `constants` |
| Auth | `auth`, `middleware`, `guards`, `permissions`, `session`, `login` |
| Background work | `jobs`, `tasks`, `workers`, `queue`, `cron`, `schedule` |
| Tests | `tests/`, `test/`, `spec/`, `__tests__/`, `*_test.go`, `*.test.ts` |
| Build / deploy | `Makefile`, `Dockerfile`, `.github/workflows`, `justfile`, `scripts/` |
| Generated / vendored (do NOT read) | `dist`, `build`, `node_modules`, `vendor`, `*.min.*`, `*.generated.*`, lockfiles |

## The tour, in order

1. **You are here** — one paragraph: what kind of codebase, how big, how it's layered (from `repo_map.py`).
2. **Doors** — the entry points, and what walking through each one shows you.
3. **If you want X, look in Y** — a lookup table of the 6-10 most likely intents for *this* repo.
4. **Guided walk** — offer to trace ONE real flow end-to-end (e.g., "a request comes in → route → service → model → response") with checkpoints; at each, ask "clear so far?" before continuing.

## Tracing a flow

Start at the entry (route/CLI command/event handler), follow the call graph one hop at a time, and name the artifact that moves between layers (request → DTO → domain object → row). Stop at the first external boundary (DB, network, filesystem) and note it. Don't read every function — read the one the flow actually calls.

## Marking dead weight

Explicitly tell the user which directories are generated/vendored/build output so they don't waste attention (or tokens) there. That negative information is as useful as the positive map.

Offer to save the tour as `TOUR.md`. `/guide` answers *where*; pair with `/humanize` for *why/how*.
