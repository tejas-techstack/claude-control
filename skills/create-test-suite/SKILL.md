---
name: create-test-suite
description: Create tests and a CI/CD pipeline (GitHub Actions) for a new or existing project. Use whenever the user mentions tests, testing, CI, CD, pipelines, GitHub Actions, coverage, "make sure this does not break", or pre-commit hooks — even if they only ask for one of these, offer the full suite.
---

# Create Test Suite (tests + CI/CD)

Stand up meaningful tests and a free CI pipeline. Read `../_shared/GUARDRAILS.md` first.

## Workflow
1. **Detect the stack** — look for pyproject.toml/package.json/go.mod/Cargo.toml/pom.xml. Run `python3 <claude-control>/tools/repo_map.py` on unfamiliar repos instead of reading everything.
2. **Find what matters** — identify the 3-7 critical paths (money, auth, data-mutation, core algorithm). Test those first; do NOT chase 100% coverage of getters.
3. **Scaffold tests** with the ecosystem default: pytest / vitest or jest / go test / cargo test. Include: one happy path, one edge case, one failure case per critical path. Make them runnable with a single command; document it.
4. **CI pipeline** — write `.github/workflows/ci.yml`: trigger on push+PR, matrix only if it earns its cost, steps = checkout, setup runtime with caching, install, lint, test. GitHub Actions is free for public repos and has a free monthly quota for private ones — state this.
5. **Optional (offer, do not force):** pre-commit hooks (format+lint), coverage report step, release workflow on tags.
6. **Prove it** — run the tests locally. A red suite must never be delivered as done. If CI can only be verified after push, say so; pushing requires user consent.

## Output format
Files created, the one command to run tests locally, what CI does on which events, and 2-3 next tests worth adding.

## Chaining
- Input: repo (any state); works well after /cross-check produced a SPEC.md (test the spec).
- Output: tests + .github/workflows/ci.yml; feeds /focus-review, /improvements.
