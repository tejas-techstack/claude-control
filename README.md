# claude-control

One repo that upgrades Claude Code three ways: **25 composable skills**, **token-saving repo tools**, and a **local skill-manager UI** with Claude built in. One-shot install on Linux, macOS, and Windows. Everything is free-only, privacy-respecting, and consent-gated — no skill will push, publish, or install system-wide without asking you first.

```
claude-control/
├── install.sh / install.ps1     one-shot installers (idempotent, back up conflicts)
├── skills/                      25 skills + _shared/GUARDRAILS.md
├── tools/                       repo_map, graphify, context_pack, chores (stdlib-only)
├── skill-manager/               local web UI: edit skills + chat with Claude
├── templates/CLAUDE.md          drop into any project to wire it all up
└── README.md · LICENSE (MIT) · VERSION
```

## Requirements

| | Required | Strongly recommended | Optional |
|---|---|---|---|
| **Linux** | bash | Python 3.9+, git, Node 18+ + Claude Code | Docker (for /isolate), gh |
| **macOS** | bash/zsh | Python 3.9+, git, Node 18+ + Claude Code | Docker, gh |
| **Windows** | PowerShell 5.1+ | Python 3.9+ ("Add to PATH"), git, Node 18+ + Claude Code | Docker Desktop, gh, Git Bash/WSL for bash-based skill scripts |

Nothing blocks the install — missing pieces are reported as warnings with links, and the installer still finishes.

## Install (one shot)

**Linux / macOS**

```bash
git clone <your-fork-or-this-repo-url> claude-control && cd claude-control
./install.sh              # copy mode (stable)
./install.sh --symlink    # live mode: git pull updates skills instantly
```

**Windows (PowerShell)**

```powershell
git clone <your-fork-or-this-repo-url> claude-control ; cd claude-control
powershell -ExecutionPolicy Bypass -File install.ps1          # add -Symlink for live mode
```

What it does: copies every folder in `skills/` into `~/.claude/skills/` (existing skills with the same name are **backed up** to `~/.claude/skills-backup-<timestamp>/`, never clobbered), installs the tools and skill-manager to `~/.claude/claude-control/`, creates a `skill-manager` launcher, and prints a dependency report. Re-running is safe. `--uninstall` / `-Uninstall` reverses it.

Then restart Claude Code and type `/` — the skills are live. For any project, copy `templates/CLAUDE.md` in as `CLAUDE.md` so Claude automatically uses the token-saving tools and consent rules there.

## The 25 skills

Every skill obeys `skills/_shared/GUARDRAILS.md`: free-only (no paid APIs, subscriptions, or paywalls), safe well-known sites only, privacy-first, explicit consent before any side effect, and token-thrift via the bundled tools. Each SKILL.md ends with a **Chaining** section so skills can call each other.

| Skill | What it does |
|---|---|
| `/research` | Searches arXiv, ACM DL, IEEE Xplore, Semantic Scholar for relevant papers; returns ranked, cited findings |
| `/design` | Builds a fast static site and (with your consent) deploys it to GitHub Pages **inside the existing repo** — never creates a new one |
| `/create-test-suite` | Stands up tests + CI/CD (GitHub Actions) for a new or existing project, matched to the stack |
| `/humanize` | Teaches you a codebase like a colleague would: plain-language tour, what's special, similar systems, prerequisites — then quizzes you and verifies your answers |
| `/cross-check` | Interrogates your request *before* generating code; you pick deep or shallow questioning first |
| `/improvements` | Curated, prioritized improvement list for the current repo — impact over nitpicks |
| `/skill-suggestions` | Reads your coarse prompt, infers intent, proposes the top ≤5 installed skills (plus generic ones), and can search online for better ones |
| `/guide` | Human-style guided tour of a repo: where things live, how data flows, where to make your change |
| `/setup` | Gets a project running, aggressively: install → run → read error → fix → repeat until it works or is provably impossible (with evidence) |
| `/isolate` | Dockerizes the workspace so `claude --dangerously-skip-permissions` runs **only inside the sandbox** — your real system is never touched |
| `/prompt-suggest` | 24 fill-in prompt templates (build, modify, test, debug, review, migrate, automate, meta) |
| `/i-have-no-idea` | Interactive discovery for when you're lost — narrows from "no idea" to a concrete next step |
| `/critical-review` | Brutal but fair review: correctness, security, design — with severity and evidence |
| `/focus-review` | Reviews only what matters; explicitly skips micro-optimizations, allows exponential wins |
| `/agent-automation` | Designs, builds, and tests agentic automations using **free** models/tools only |
| `/search-existing` | Finds hand-rolled code in your repo that a well-tested library already does better |
| `/github-explore` | Finds healthy, well-tested repos for a need (stars ≠ health; checks tests, activity, license) |
| `/skills-interleave` | The conductor: composes other skills into pipelines (e.g. search-existing → github-explore) |
| `/firecrawl` | Local-first web fetch/crawl/map via bundled `crawl.py` (robots.txt-respecting, rate-limited, free) |
| `/humanizer` | De-AI-ifies prose: removes tells, varies rhythm, keeps meaning |
| `/automation-how` | Answers "how do I automate X?" with free, local-first workflows |
| `/free-alternatives` | Free, subscription-less, privacy-respecting alternatives to any paid tool |
| `/improve-prompt` | Rewrites your prompt for better results and explains each change |
| `/control-skill` | Meta-skill: improves your other skills per repo/task and persists learnings across sessions |
| `/creative-spin` | Generates ideas and *verifies* uniqueness by searching before claiming novelty |

Naming note: `/humanize` (codebase teacher) and `/humanizer` (prose de-AI-ifier) are intentionally distinct and their descriptions are collision-proof, but rename either if you prefer — the skill-manager makes that a 10-second edit.

## The tools (spend 20% of the tokens for 80% of the work)

Stdlib-only Python, installed to `~/.claude/claude-control/tools/`, wired in via `templates/CLAUDE.md`:

| Tool | Purpose |
|---|---|
| `repo_map.py` | Token-cheap repo overview: layout, languages, entry points, symbols, TODOs (`--budget`, default ~3k tokens) |
| `graphify.py` | Import/dependency graph as Mermaid + centrality ranking — find the files that matter |
| `context_pack.py` | Budgeted CONTEXT_PACK.md: README + most central files, smart head+tail truncation |
| `chores.py` | Detects and runs mechanical work (format/lint/test/typecheck/audit) so the model never does it token-by-token |

## The skill manager

```bash
~/.claude/claude-control/bin/skill-manager        # Windows: skill-manager.cmd
# → http://127.0.0.1:8765
```

Browse and edit every skill, create new ones from a template, enable/disable (moves folders to `.disabled/`), soft-delete (to `.trash/`), and chat with Claude in a side panel that can include the skill you're editing as context. Localhost-only, path-traversal-guarded, zero dependencies. Details in `skill-manager/README.md`.

## Publishing this to your GitHub (you do it — nothing is pushed for you)

```bash
cd claude-control
git init -b main
git add -A
git commit -m "claude-control v0.1.0"
gh repo create claude-control --private --source . --push 
```

## FAQ

**Why free-only?** House rule, enforced in `GUARDRAILS.md`: every skill must work with no subscription, no paywall, no trial-that-expires. Where an official paid integration exists (e.g. Firecrawl's hosted API), the skill ships a local free equivalent instead and only *mentions* the paid option.

**Is `--dangerously-skip-permissions` ever used on my machine?** No. Only `/isolate` mentions it, and only inside the Docker container it builds, which mounts a single project folder and nothing else.

**Where does everything live?** Skills: `~/.claude/skills/`. Tools, templates, manager: `~/.claude/claude-control/`. Project wiring: the `CLAUDE.md` you copy in.

**How do I update?** `git pull` then re-run the installer (or use `--symlink` mode once and never think about it again).

**How do I remove it?** `./install.sh --uninstall` or `install.ps1 -Uninstall`. Backups made at install time are left untouched.

MIT licensed. Built to be forked.
