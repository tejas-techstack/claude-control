#!/usr/bin/env python3
"""inventory: list every installed skill with its trigger description, cheaply — so
the router can match intent to skills without reading 25+ files. Marks which are
local (this repo / hand-made) vs external (gstack, anthropic-skills, ...).

Usage:
  inventory.py                      # human table, enabled skills
  inventory.py --all                # include disabled
  inventory.py --grep auth deploy   # only skills whose name/desc match any term
  inventory.py --json               # machine-readable

Reads ~/.claude/skills (override with CLAUDE_SKILLS_DIR) plus the project-local
.claude/skills if present, and the external lockfile so sources are labeled.
"""
import argparse, json, os, re
from pathlib import Path

CTRL = Path(os.environ.get("CLAUDE_CTRL_DIR", Path.home() / ".claude" / "claude-control"))
LOCK = CTRL / "external" / "installed.json"


def roots():
    out = []
    env = os.environ.get("CLAUDE_SKILLS_DIR")
    out.append(Path(env) if env else Path.home() / ".claude" / "skills")
    proj = Path(".claude") / "skills"
    if proj.exists():
        out.append(proj)
    return [r for r in out if r.exists()]


def frontmatter(md):
    name = desc = ""
    text = md.read_text(errors="replace")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        body = text[3:end] if end != -1 else ""
        for ln in body.splitlines():
            s = ln.strip()
            if s.startswith("name:") and not name:
                name = s.split(":", 1)[1].strip()
            elif s.startswith("description:") and not desc:
                desc = s.split(":", 1)[1].strip()
    return name or md.parent.name, desc


def external_map():
    if LOCK.exists():
        try:
            return {r["dir"]: r["source"] for r in json.loads(LOCK.read_text()).get("installed", [])}
        except Exception:
            return {}
    return {}


def collect(include_disabled):
    ext = external_map()
    seen, rows = set(), []
    for root in roots():
        bases = [(root, True)]
        if include_disabled and (root / ".disabled").exists():
            bases.append((root / ".disabled", False))
        for base, enabled in bases:
            for d in sorted(base.iterdir()):
                md = d / "SKILL.md"
                if not (d.is_dir() and md.exists()) or d.name.startswith("."):
                    continue
                if d.name in seen:
                    continue
                seen.add(d.name)
                name, desc = frontmatter(md)
                rows.append({"dir": d.name, "invoke": name, "description": desc,
                             "enabled": enabled, "source": ext.get(d.name, "local")})
    rows.sort(key=lambda r: (r["source"] != "local", r["invoke"]))
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--all", action="store_true", help="include disabled skills")
    ap.add_argument("--grep", nargs="*", default=[], help="filter by name/description terms")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    rows = collect(a.all)
    if a.grep:
        terms = [t.lower() for t in a.grep]
        rows = [r for r in rows if any(t in (r["invoke"] + " " + r["description"]).lower() for t in terms)]
    if a.json:
        print(json.dumps(rows, indent=2)); return
    local = [r for r in rows if r["source"] == "local"]
    ext = [r for r in rows if r["source"] != "local"]
    print("Installed skills: %d local, %d external\n" % (len(local), len(ext)))
    for r in rows:
        tag = "" if r["source"] == "local" else "  <" + r["source"] + ">"
        state = "" if r["enabled"] else "  (disabled)"
        print("/%s%s%s" % (r["invoke"], tag, state))
        if r["description"]:
            print("   " + re.sub(r"\s+", " ", r["description"])[:200])
    print("\nRoute: pick ≤5 task-specific + 1-2 generic; give the literal /invocation for each.")


if __name__ == "__main__":
    main()
