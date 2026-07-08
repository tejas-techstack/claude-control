# claude-control tools — spend 20% of the tokens on 80% of the work

Stdlib-only Python scripts. No pip installs, no network. Point Claude at these before it reads a repo raw.

| Tool | What it does | Typical call |
|---|---|---|
| `repo_map.py` | Token-cheap overview: layout, languages, entry points, symbols, TODOs | `python3 tools/repo_map.py . --out REPO_MAP.md` |
| `graphify.py` | Import/dependency graph + centrality ranking (Mermaid + JSON) | `python3 tools/graphify.py . --out docs/GRAPH.md` |
| `context_pack.py` | Budgeted context pack: README + most central files, truncated smartly | `python3 tools/context_pack.py . --budget 8000` |
| `chores.py` | Detects and runs mechanical work (format/lint/test/typecheck/audit) so the AI doesn't burn tokens on it | `python3 tools/chores.py list` |
| `skillsource.py` | Loads **external** skill repos (gstack, anthropic-skills, your own) into `~/.claude/skills/` without editing them — shared by the installers and the skill manager | `python3 tools/skillsource.py sync all` |

The installer copies these to `~/.claude/claude-control/tools/`, and `templates/CLAUDE.md` wires the token tools into any project so Claude uses them automatically. `skillsource.py` is the odd one out — it's not a token tool, it's the engine behind the external-skills loader (see the main README's "Loading external skills" section).
