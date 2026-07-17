# claude-control skill manager

A local web UI to browse, edit, create, enable/disable, and delete your Claude skills — with a built-in Claude chat panel that can see the skill you're editing.

Zero dependencies beyond Python 3.9+. No pip installs, no build step, no telemetry.

## Run it

```bash
python3 skill-manager/server.py            # manages ~/.claude/skills on port 8765
# or, after ./install.sh:
~/.claude/claude-control/bin/skill-manager
```

Open http://127.0.0.1:8765

Options: `--root <dir>` to manage a project's `.claude/skills`, `--port <n>` to change the port.

## What the buttons actually do (no surprises)

| Action | Effect on disk |
|---|---|
| enable / disable | Moves the folder between `<root>/` and `<root>/.disabled/`. Claude Code only loads enabled ones. |
| delete | Soft delete — moves the folder to `<root>/.trash/<name>-<timestamp>`. Recover it by moving it back. |
| + new | Scaffolds `<root>/<name>/SKILL.md` from a minimal template. |
| save file | Writes exactly the file shown in the active tab. |
| **sources** | Opens the external-source panel (below). |

## External sources (gstack, anthropic-skills, your own repos)

The **sources** button manages the git repos listed in `skill-sources.txt`. For each one you can:

- **sync / update** — `git clone` (or pull) the repo and install every `SKILL.md` folder it ships, without touching the upstream files.
- **remove skills** — uninstall what a source installed (the clone under `claude-control/external/` is kept, so a re-sync is instant).
- **add a source** — append a repo to the manifest by name + URL.

Synced skills show a **source badge** and a 🔒 in the list, and open **read-only** — the manager refuses to write to them (HTTP 403) so your upstream copies stay pristine. Use the **filter dropdown** to view `all`, `local only`, or one source at a time (handy once gstack adds ~50 skills). Everything here just shells out to the same `tools/skillsource.py` the installers use, so the CLI and the UI can never drift apart.

## Read-only web index (GitHub Pages)

The server above is for *managing* skills locally. To *publish* a read-only, always-current
index of every skill and tool — no editing, no backend — build the static site:

```bash
python3 skill-manager/build_static.py          # writes ./site/index.html (self-contained)
python3 -m http.server -d site 8123            # preview at http://127.0.0.1:8123
```

It walks this repo's `skills/` and `tools/`, plus every **external** skill installed via
claude-control (the `external/installed.json` sources **and** graphify), and bakes each file's
contents into one self-contained `index.html` — markdown rendered, code shown as-is, nothing
editable. `site/` is a build artifact (git-ignored); the viewer template lives in
`static/viewer.html`.

`.github/workflows/pages.yml` runs this on every push to `main` and deploys to GitHub Pages,
so the published index auto-updates. Enable it once under **Settings → Pages → Source:
GitHub Actions**. Live URL: `https://<owner>.github.io/<repo>/`.

## Claude chat backends

1. **`claude` CLI** (preferred) — uses your existing Claude Code login. Nothing to configure.
2. **Anthropic API** — used only if the CLI is absent; needs `ANTHROPIC_API_KEY` in the environment. Model defaults to `claude-sonnet-4-6`; override with `CLAUDE_MODEL`.

Tick "include selected SKILL.md as context" and Claude sees the file you're editing — handy for "tighten this description" or "add a chaining section".

## Security

- Binds to **127.0.0.1 only** — nothing is exposed to your network.
- Skill names are validated (`[a-z0-9_-]`), and every file path is resolved and confined to the skills root (no `..` traversal).
- The server never runs skill scripts; it only reads and writes text.
