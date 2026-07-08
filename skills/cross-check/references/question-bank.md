# Cross-check question bank

Pull from these; never dump the whole list. Pick the highest-leverage questions for *this* request and always offer a default so answering is cheap ("Default: SQLite — object?").

## The 6 dimensions (deep mode walks all; shallow mode picks ~6 total)

### 1. Intent — why this exists

- What problem does this solve, and for whom? What happens if we build nothing?
- What does the user do *today* instead? What's painful about it?
- Is this a throwaway, a prototype, or something that must live for years? (Changes everything.)
- What would make you consider this a waste of time in hindsight?

### 2. Shape — inputs, outputs, interface

- Inputs: format, source, volume, trust level (user-supplied? untrusted?).
- Outputs: exact shape (file, API response, UI, stream), and who/what consumes them.
- Interface: CLI, library, HTTP API, GUI, batch job, cron? One or several?
- State: what persists between runs, and where (memory, file, DB, external)?
- Scale honestly expected: 10 items or 10M? 1 user or 10k concurrent? Don't over-engineer for imaginary scale, don't under-build for real scale.

### 3. Constraints — the box it lives in

- Language / framework / runtime already mandated? Existing code it must fit into?
- Environment: where does it run (laptop, server, serverless, browser, edge, air-gapped)?
- Budget: default **free** unless told otherwise — any paid service allowed?
- Security/privacy: PII? secrets? auth needed? compliance (GDPR/HIPAA/SOC2)?
- Dependencies: allowed to add libraries, or keep it stdlib? License limits?
- Deadline and "good enough" bar for v1.

### 4. Edges — where it breaks

- The 3 worst realistic inputs (empty, huge, malformed, hostile, duplicate).
- Failure behavior: crash loud, retry, degrade, queue, alert? Idempotent on retry?
- Concurrency: can two of these run at once? Shared resource contention?
- Migration/compat: existing data to preserve? Backward-compatible API?
- Time & ordering: timezones, clock skew, out-of-order events?

### 5. Done — how we'll know

- Acceptance criteria a third party could check objectively (not "works well").
- What's explicitly **out of scope** for this version? (Write non-goals down.)
- How will the user verify it themselves? What's the demo?
- What's the rollback plan if it ships broken?

### 6. Hidden assumptions — surface and challenge

- Any place the request assumes a fact not yet confirmed ("users have accounts", "data fits in RAM", "it's English-only").
- Contradictions between requirements — name them immediately and make the user choose.
- The unstated "obviously it should also…" that will appear after delivery.

## Domain add-ons (ask only if relevant)

- **Web app**: auth model, session vs token, SSR/SPA, SEO, browser support, mobile.
- **Data pipeline**: source of truth, schema evolution, backfill, exactly-once vs at-least-once, late data.
- **CLI tool**: install method, config precedence (flags > env > file), stdout vs stderr contract, exit codes, piping.
- **Library/API**: public surface, semver policy, error types, sync vs async, thread-safety.
- **ML/agent**: eval set, success metric, human-in-the-loop, cost per call, fallback when the model is wrong.
- **Automation**: trigger, schedule, kill switch, observability, what happens on partial failure.

## Anti-patterns to catch in the answers

- "It should just work" → push for the specific behavior on the specific input.
- Three tasks in one request → split into a sequence, spec each.
- Success criteria two people could disagree on → it's underspecified; rewrite it measurably.
- Scope that grew mid-conversation → re-confirm the whole spec before building.
