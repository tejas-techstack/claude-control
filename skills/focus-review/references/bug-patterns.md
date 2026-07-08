# High-signal bug patterns

Where real bugs hide. Use this as a hunting checklist on the diff and the functions it touches. Report only what passes the filter: a correctness bug, a security/data-loss risk, or a ≥2x structural win. Everything else is forbidden noise.

## Language-agnostic

- **Boundaries**: off-by-one, empty collection, single-element, max/overflow, negative, zero.
- **Error paths**: exceptions swallowed; the happy path assumes success; partial writes on failure; no cleanup on the error branch.
- **Null/optional**: dereferenced without a check; `Optional`/`nil`/`undefined` flowing into code that assumes present.
- **Concurrency**: shared mutable state without a lock; check-then-act races (TOCTOU); non-atomic read-modify-write; deadlock ordering.
- **Idempotency**: retried operation double-charges / double-inserts; no dedupe key.
- **Resource leaks**: file/socket/connection/lock not released on every path (esp. exceptions).
- **Trust**: untrusted input reaching SQL/shell/path/template/deserializer.
- **Time & money**: float for currency; naive datetimes across timezones/DST; clock used for ordering.

## Python

- Mutable default args (`def f(x=[])`), `except:` bare, `== None`, late-binding closures in loops, iterating a dict while mutating it, `assert` for validation in prod code (stripped under `-O`).

## JavaScript / TypeScript

- `==` vs `===`; `async` function whose rejection is unhandled (missing `await`/`.catch`); floating promises; `for..in` over arrays; `JSON.parse` without try/catch; `as any` hiding a real type hole; unbounded `Promise.all` over user data.

## Go

- Ignored `err`; `defer` in a loop (accumulates); goroutine leak (no ctx/cancel); loop-variable capture (pre-1.22); nil map write; slice aliasing after `append`.

## SQL / data

- Missing `WHERE` on `UPDATE`/`DELETE`; N+1 queries; no transaction around multi-write; string-built queries (injection); migration with no rollback; unindexed lookup on a growing table.

## Security surfaces (always escalate)

- Secrets in code/logs; authz checked in UI only (IDOR); `verify=False` / TLS off; weak password hashing; predictable token randomness; open redirect; SSRF via user-supplied URL.

## The filter (before reporting anything)

Report ONLY if at least one holds: it's a correctness bug (wrong output/crash/race/unhandled failure), a security or data-loss risk, or it changes complexity class/architecture for a ≥2x win. FORBIDDEN: formatting, naming, "could be nicer", speculative abstraction, micro-opts, tool preference. If nothing passes: *"No blocking issues found. Checked: [list]."* — don't invent findings.

Per finding: `[BLOCKER|WARN] title — evidence (file:line) — impact in one sentence — minimal fix`. Max 7; if more, give the top 7 and say how many were cut.
