# Pipeline catalog & composition rules

Skills are files; composing them means reading the right SKILL.md at the right step and passing a named artifact across each arrow. Announce each hop in one line ("→ using /github-explore to vet candidates").

## How A calls B

Pause A → read `~/.claude/skills/B/SKILL.md` (or the project-local copy) → run B with A's intermediate artifact as input → resume A with B's output. Only read the SKILL.md files you'll actually use (token thrift). Use `/skill-suggestions` (or its `inventory.py`) if unsure which B fits.

## Known-good pipelines

| Goal | Pipeline | Artifact passed across arrows |
|---|---|---|
| Ship a feature | `/cross-check → /prompt-suggest → build → /create-test-suite → /focus-review` | SPEC.md → prompt → code → tests → blocker list |
| Adopt an unfamiliar repo | `/github-explore → /humanize → /setup → /guide` | repo pick → understanding → running env → TOUR.md |
| De-bloat a codebase | `/improvements → /search-existing → /github-explore → migrate → /focus-review` | issue list → wheel matches → vetted libs → diff → review |
| Research → prototype | `/research → /creative-spin → /cross-check → build in /isolate` | brief → differentiated idea → SPEC.md → sandboxed build |
| Learn a framework | `/firecrawl (docs) → /humanize → /prompt-suggest` | .crawl/*.md → understanding → practice prompts |
| Free up a paid dependency | `/free-alternatives → /github-explore → /setup → /automation-how` | candidate → vetted repo → installed → wired in |
| Pre-launch hardening | `/critical-review → /improvements → /create-test-suite → /focus-review` | findings → roadmap → tests → final gate |
| Automate a chore | `/improvements (spot it) → /automation-how → /agent-automation (if AI-shaped) → /isolate` | routine → scheduler → agent → sandbox |

## Composition rules

1. **Draw the pipeline before executing** and show it, naming the artifact on each arrow.
2. **Confirm each artifact exists and is sane before feeding it forward.** On failure, fix that stage — never push garbage downstream.
3. **Resolve conflicts by specificity**: a skill's own rules > this skill > general habits. Guardrails always win.
4. **Stop early if a stage says stop** (e.g., `/cross-check` not APPROVED, `/critical-review` finds a CRITICAL). Don't bulldoze past a gate.
5. **Offer to persist** a pipeline that worked as a project composite skill via `/control-skill`.

## Building your own

Decompose the goal into stages → pick the best skill per stage → identify the artifact each produces and the next consumes → check the producing skill's **Chaining** section lists that output. If two stages want the same artifact shaped differently, insert a transform step rather than hoping it fits.
