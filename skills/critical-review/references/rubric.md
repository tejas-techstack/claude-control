# Critical-review rubric — per-domain checklists

Every finding carries: **evidence** (file:line, quote, or reproduced behavior) → **severity** → **a way forward**. Criticism without a path forward is forbidden. Classify: CRITICAL (will cause damage) / MAJOR (will cause pain) / MINOR (worth fixing, not urgent; cap at 5).

## Correctness

- Off-by-one, boundary, and empty-collection handling.
- Error paths: are failures caught, or swallowed? Does the happy path assume success?
- Null/None/undefined propagation; optional values dereferenced.
- Floating-point money, integer overflow, timezone/DST, locale-dependent parsing.
- Concurrency: shared mutable state, races, deadlocks, non-atomic read-modify-write, missing locks/transactions.
- Idempotency: does a retry double-charge / double-insert?
- Resource lifetime: files/sockets/connections closed on every path (including exceptions)?

## Security

- Input trust: SQL/command/template injection, path traversal, SSRF, deserialization of untrusted data.
- AuthN/AuthZ: is every sensitive path actually checked, or just the UI hidden? IDOR (object IDs not scoped to the user).
- Secrets: hardcoded keys, secrets in logs, secrets in the repo, tokens not redacted.
- Crypto: home-rolled crypto (a finding by itself), weak hashing for passwords (use argon2/bcrypt/scrypt), predictable randomness for tokens.
- Transport: TLS verification disabled, mixed content, missing auth on internal endpoints.
- Dependencies: known-vuln versions (see `chores.py audit`), typosquat-prone installs.

## Data integrity

- Migrations: reversible? tested on a copy? destructive without backup?
- Transaction boundaries: partial writes on failure; missing rollback.
- Validation at the boundary vs. deep inside; trusting client-provided invariants.
- Backups and the actual restore path (an untested backup is not a backup).

## Architecture & coupling

- One module that knows about everything (god object); circular deps (check `graphify.py`).
- Leaky abstractions; business logic in the controller/UI; DB schema leaking into the API.
- Hidden global state; singletons that make testing impossible.
- Change amplification: "to add a field I must edit 7 files."
- Premature abstraction vs. missing seam where change is certain.

## Error handling & observability

- Errors that vanish (bare except, empty catch, `.catch(() => {})`).
- No logs at failure points, or logs with no context (which user? which request?).
- User-facing errors that leak internals or say nothing actionable.
- No timeouts/retries on network calls; retries without backoff or a cap.

## Tests

- Critical paths (money, auth, data mutation) untested.
- Tests that assert nothing, or only test the mock.
- No failure-case or edge-case tests; 100% coverage of getters, 0% of the hard logic.
- Flaky tests (time/order/network dependent) treated as normal.

## Performance (only where it matters on real sizes)

- Quadratic-or-worse loops on user-scale data; N+1 queries.
- Unbounded memory (loading a whole file/result set); missing pagination/streaming.
- Repeated work that should be cached; cache with no invalidation story.
- Note: don't flag micro-opts. Flag complexity-class and real-user-impact issues only.

## Docs & onboarding

- Can a new dev run it from the README alone? (If not, that's a MAJOR for a shared repo.)
- Setup steps that don't match reality; undocumented required env vars.
- Public API without usage examples or error semantics.

## For plans/designs (not code)

- Feasibility with the stated resources/time; the honest hard part named or hidden?
- Hidden assumptions (scale, data availability, team skills).
- What happens at 10x load / 10x data? Failure and rollback story?
- Cheaper alternative considered and rejected for a stated reason?

## Output template

```
# Critical review: <subject>
## Verdict            (2-3 blunt sentences + score /10 with one-line justification)
## What is genuinely good   (one honest section — no participation trophies)
## CRITICAL           (each: evidence → why it matters → minimal fix)
## MAJOR
## MINOR              (≤5)
## If you fix only three things
## What I did NOT review
```
