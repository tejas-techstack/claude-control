# Testing playbook

Test what breaks and what costs money — not getters. Aim for meaningful coverage of critical paths, a green suite runnable with one command, and free CI. Ready-to-copy workflows are in `assets/ci/`.

## What to test first (the 3-7 critical paths)

Rank by blast radius: money movement, auth/authorization, data mutation/migration, the core algorithm, anything users hit constantly. For each critical path write **one happy path, one edge case, one failure case**. Skip exhaustive coverage of trivial code.

- **Happy path** — normal input → expected output/state.
- **Edge** — empty, max, boundary, unicode, duplicate, zero, negative, concurrent.
- **Failure** — bad input rejected cleanly; downstream error handled; no partial writes.

Good test qualities: fast, deterministic (no real clock/network/random — inject them), isolated (no shared state between tests), and named so a failure reads like a bug report (`test_refund_fails_when_amount_exceeds_charge`).

## Per-stack defaults

| Stack | Runner | One-command | Notes |
|---|---|---|---|
| Python | pytest | `pytest -q` | fixtures for setup; `pytest.raises` for failures; `freezegun`/`monkeypatch` for time/env; `-p no:cacheprovider` in CI |
| JS/TS | vitest or jest | `npm test` | `vi.mock`/`jest.mock`; `@testing-library` for UI; msw for HTTP |
| Go | go test | `go test ./...` | table-driven tests; `-race` in CI |
| Rust | cargo test | `cargo test` | `#[cfg(test)]` modules; `assert_cmd` for CLIs |
| Java | JUnit 5 | `mvn -q test` / `gradle test` | AssertJ for readable asserts |

## Test doubles — pick the lightest that works

- **Stub** a return value; **fake** a working in-memory version (e.g., a dict-backed repo); **mock** only to assert an interaction happened. Don't mock what you don't own — wrap it and fake the wrapper.
- Inject dependencies (clock, HTTP client, DB) so tests can substitute them. Untestable code usually means hidden globals — that's a design finding for `/improvements`.

## Pinning legacy behavior before a refactor

Characterization tests: capture current output for real inputs, assert it stays equal, then refactor under the green suite. This is how `/search-existing` migrations stay safe.

## CI (GitHub Actions — free for public repos, monthly free minutes for private)

Minimum pipeline: trigger on push + PR → checkout → set up runtime **with dependency cache** → install → lint → test. Matrix only when it earns its cost (multiple runtimes/OSes you actually support). Copy the matching file from `assets/ci/` into `.github/workflows/ci.yml` and adjust the versions.

Optional, offer don't force: coverage upload, a release workflow on tags, pre-commit (format + lint) so bad commits never land.

## Prove it before handing over

Run the suite locally; a red suite is never "done." If CI can only be verified after push, say so — pushing needs the user's consent (guardrails). Report: files created, the one command to run tests, what CI does on which events, and 2-3 next tests worth adding.
