# claude-control

One repo that upgrades Claude Code four ways: **25 composable skills**, a **loader for external skill collections** (gstack, Anthropic's official skills, your own repos), **token-saving repo tools**, and a **local skill-manager UI** with Claude built in. One-shot install on Linux, macOS, and Windows. Everything is free-only, privacy-respecting, and consent-gated — no skill will push, publish, or install system-wide without asking you first.

```
claude-control/
├── install.sh / install.ps1     one-shot installers (idempotent, back up conflicts)
├── skills/                      25 skills + _shared/GUARDRAILS.md
├── skill-sources.txt            external skill repos to load (gstack, anthropic-skills, …)
├── tools/                       repo_map, context_pack, chores, skillsource (stdlib)
├── skill-manager/               local web UI: edit skills, manage sources, chat with Claude
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

## Operating it from Claude Code (CLI **and** the VS Code extension)

Everything here runs *inside* Claude Code — the terminal CLI and the VS Code / Cursor / JetBrains extension behave the same, because they share the one skills directory (`~/.claude/skills/`). This is the day-to-day driver's guide.

**1 — Load the skills into your session.** Skills are read once when a session starts, so after installing (or syncing new ones) start a fresh Claude Code session: in the CLI just relaunch `claude`; in the VS Code extension open a new chat (or run *Developer: Reload Window*). Then type `/` and you'll see `research`, `guide`, `humanize`, … in the slash menu. Sanity check: ask *"which skills do you have available?"* and Claude will list them.

**2 — Two ways to fire a skill.**

- **Explicitly** — type the slash command with your ask: `/research diffusion model watermarking`, `/guide where is auth handled?`, `/humanize this repo`. In VS Code, start the message with `/` and pick from the popup.
- **Automatically** — you don't have to name skills. Each `SKILL.md` has a trigger-rich `description`, so a plain request like *"find me a well-tested rate-limiter library"* makes Claude reach for `/github-explore` on its own. Not sure which to use? Run **`/skill-suggestions`** and it routes you; run **`/skills-interleave`** to chain several into a pipeline.

**3 — Let the tools save you tokens.** Drop `templates/CLAUDE.md` into a project as `CLAUDE.md` and Claude will, on its own, run `repo_map.py` / `context_pack.py` before reading a big repo and hand mechanical work (format, lint, test) to `chores.py`. You can also just ask: *"map this repo first"* or *"run the chores."* Nothing is auto-run without that wiring or your say-so.

**4 — Open the skill manager next to your editor.** Launch `~/.claude/claude-control/bin/skill-manager` (Windows: `skill-manager.cmd`) from any terminal — in VS Code use the **integrated terminal**, then open `http://127.0.0.1:8765` in the built-in **Simple Browser** (`Cmd/Ctrl-Shift-P → Simple Browser: Show`) so it sits beside your code. Edit skills, toggle them, add external sources, and chat with Claude — it reuses your existing Claude Code login, no API key needed.

**5 — Make skills stick to a project.** After a good session, run **`/control-skill`** — it writes `.claude/skills/control-<project>/SKILL.md` into the repo so the commands, conventions, and gotchas you just established load automatically for you (and your teammates) next time.

**6 — Run risky/autonomous work safely.** `/isolate` builds a Docker sandbox so `claude --dangerously-skip-permissions` only ever touches one mounted folder — never your host. Use it for long unattended runs from either the CLI or the extension.

> **Reload rule of thumb:** installed or synced something and don't see it? Start a new Claude Code session (CLI relaunch, or *Reload Window* in VS Code). Skills are enumerated at session start.

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
| `/prompt-suggest` | 40 fill-in prompt templates (build, modify, test, debug, review, migrate, data/SQL, devops, frontend, concurrency, automate, meta) |
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

## Loading external skills (gstack, anthropic-skills, your own repos)

The 25 skills above are the ones *this* repo maintains. But the ecosystem is bigger — so claude-control can also pull in whole skill collections from any public git repo and install them right next to the built-ins, **without editing a single upstream file**. Two collections ship enabled in `skill-sources.txt`:

| Source | Repo | What you get |
|---|---|---|
| `gstack` | [garrytan/gstack](https://github.com/garrytan/gstack) | Garry Tan's ~50-skill "virtual eng team": CEO product review, eng-manager, designer, reviewer, QA, security, release. |
| `anthropic-skills` | [anthropics/skills](https://github.com/anthropics/skills) | Anthropic's official Agent Skills — document (pdf/docx/pptx/xlsx), creative, and technical. |

Nothing is fetched on a plain install. You opt in, three interchangeable ways:

```bash
./install.sh --with-external                     # every enabled source (needs git)
./install.sh --external gstack                    # just one
python3 ~/.claude/claude-control/tools/skillsource.py sync all   # anytime, after install
```

…or open the skill manager and use the **sources** panel (sync / update / remove / add) with buttons.

**Add your own** — one line in `skill-sources.txt` (`<name> <git-url> [subdir=…] [ref=…] [prefix=…]`), or `skillsource.py add my-skills https://github.com/you/repo`. The loader clones the repo under `~/.claude/claude-control/external/`, finds every folder containing a `SKILL.md`, and installs each — prefixing folders per-source (`gstack-review`, …) so they never collide with your own. In the manager, external skills carry a source badge and a 🔒: they're **read-only** so re-syncing always matches upstream cleanly. `skillsource.py list` shows what's installed; `remove <name>` / `--uninstall` takes them back out. It's the same `tools/skillsource.py` under the installers *and* the UI, so the two can't drift.

> Free-only still applies: only genuinely free, public, reputable repos belong in `skill-sources.txt`. Two collections can both define, say, `/review`; the loader warns on the clash and you disable one in the manager.

## The tools (spend 20% of the tokens for 80% of the work)

Stdlib-only Python, installed to `~/.claude/claude-control/tools/`, wired in via `templates/CLAUDE.md`:

| Tool | Purpose |
|---|---|
| `repo_map.py` | Token-cheap repo overview: layout, languages, entry points, symbols, TODOs (`--budget`, default ~3k tokens) |
| `context_pack.py` | Budgeted CONTEXT_PACK.md: README + most central files (by import in-degree), smart head+tail truncation |
| `chores.py` | Detects and runs mechanical work (format/lint/test/typecheck/audit) so the model never does it token-by-token |

For a **deep dependency/knowledge graph** (interactive `graph.html`, `GRAPH_REPORT.md`, "god node" detection), claude-control now uses **[graphify](https://github.com/safishamsi/graphify)** by [@safishamsi](https://github.com/safishamsi) instead of a hand-rolled script. It's a Claude Code skill that runs fully locally — the installer offers to set it up (`pip install graphifyy && graphify install`), after which you invoke it in any repo with `/graphify .`. See **Acknowledgments** below.

## The skill manager

```bash
~/.claude/claude-control/bin/skill-manager        # Windows: skill-manager.cmd
# → http://127.0.0.1:8765
```

Browse and edit every skill, create new ones from a template, enable/disable (moves folders to `.disabled/`), soft-delete (to `.trash/`), and chat with Claude in a side panel that can include the skill you're editing as context. Localhost-only, path-traversal-guarded, zero dependencies. Details in `skill-manager/README.md`.


## FAQ

**Why free-only?** House rule, enforced in `GUARDRAILS.md`: every skill must work with no subscription, no paywall, no trial-that-expires. Where an official paid integration exists, the skill ships a free equivalent. `/firecrawl` is the model: it starts with a stdlib crawler, and when a page needs a real browser it **pulls and runs the actual open-source Firecrawl engine on your machine** (`firecrawl_selfhost.sh`) — same engine as the hosted API, no key, no bill. The paid hosted option is only ever *mentioned*.

**Is `--dangerously-skip-permissions` ever used on my machine?** No. Only `/isolate` mentions it, and only inside the Docker container it builds, which mounts a single project folder and nothing else.

**Where does everything live?** Skills: `~/.claude/skills/`. Tools, templates, manager, external clones: `~/.claude/claude-control/`. Project wiring: the `CLAUDE.md` you copy in.

**Do external skills (gstack, etc.) get modified?** Never. They're cloned under `claude-control/external/` and installed by symlink (or copy on Windows); the loader only reads them. The skill manager marks them read-only and refuses to write. Their invocation names come from their own `SKILL.md` frontmatter, so `/review` etc. work exactly as their authors intended.

**How do I update?** For claude-control itself: `git pull` then re-run the installer (or use `--symlink` mode once and never think about it again). For external skills: `skillsource.py sync all`, or the **sync / update** button in the manager's sources panel.

**How do I remove it?** `./install.sh --uninstall` or `install.ps1 -Uninstall`. Backups made at install time are left untouched.

## Acknowledgments

claude-control stands on other people's work. Credit where it's due — please keep these intact if you fork:

| Project | Author | Used for | License |
|---|---|---|---|
| [graphify](https://github.com/safishamsi/graphify) | [@safishamsi](https://github.com/safishamsi) | Deep dependency/knowledge-graph tool (`/graphify .`), replacing our old stdlib `graphify.py` | see upstream repo |
| [gstack](https://github.com/garrytan/gstack) | [Garry Tan (@garrytan)](https://github.com/garrytan) | Optional external skill collection ("virtual eng team": product/eng/design/QA/security) | see upstream repo |
| [anthropics/skills](https://github.com/anthropics/skills) | [Anthropic](https://github.com/anthropics) | Optional external skill collection (official document/creative/technical Agent Skills) | see upstream repo |

External collections are cloned unmodified under `~/.claude/claude-control/external/` and installed read-only, so upstream is never altered. graphify is installed from its own PyPI package / repo and invoked as its authors intend. If you add sources to `skill-sources.txt`, credit them here too.

MIT licensed. Built to be forked.
