# claude-control tools — spend 20% of the tokens on 80% of the work

Stdlib-only Python scripts. No pip installs, no network. Point Claude at these before it reads a repo raw.

| Tool | What it does | Typical call |
|---|---|---|
| `repo_map.py` | Token-cheap overview: layout, languages, entry points, symbols, TODOs | `python3 tools/repo_map.py . --out REPO_MAP.md` |
| `graphify.py` | Import/dependency graph + centrality ranking (Mermaid + JSON) | `python3 tools/graphify.py . --out docs/GRAPH.md` |
| `context_pack.py` | Budgeted context pack: README + most central files, truncated smartly | `python3 tools/context_pack.py . --budget 8000` |
| `chores.py` | Detects and runs mechanical work (format/lint/test/typecheck/audit) so the AI doesn't burn tokens on it | `python3 tools/chores.py list` |

The installer copies these to `~/.claude/claude-control/tools/`, and `templates/CLAUDE.md` wires them into any project so Claude uses them automatically.
