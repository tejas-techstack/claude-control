#!/usr/bin/env python3
"""Build a self-contained, read-only static site of the claude-control skills & tools.

Walks the repo's skills/ and tools/ (and a couple of top-level docs), bakes every
text file's contents into a single index.html, and writes it to the output dir.
No dependencies, no build tooling — just the standard library.

Usage:  python3 skill-manager/build_static.py [--out site] [--root <repo>]

The output dir is what GitHub Pages serves. The GitHub Actions workflow runs this
on every push so the published index is always current; nothing is committed.
"""
import argparse
import datetime
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
TEMPLATE = HERE / "static" / "viewer.html"

# Which files are worth showing. Binaries and generated junk are skipped.
TEXT_SUFFIXES = {".md", ".py", ".sh", ".ps1", ".txt", ".json", ".toml",
                 ".yml", ".yaml", ".cfg", ".ini", ".js", ".css", ".html"}
SKIP_DIRS = {"__pycache__", ".git", "node_modules", "external", ".disabled", ".trash"}
MAX_BYTES = 400_000  # per file; anything bigger is almost certainly not meant to be read


def read_text(p: Path):
    """Return decoded text, or None if the file looks binary / too big / unreadable."""
    try:
        if p.stat().st_size > MAX_BYTES:
            return None
        raw = p.read_bytes()
    except OSError:
        return None
    if b"\x00" in raw:
        return None
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1", errors="replace")


def parse_frontmatter(text: str):
    """Tiny YAML-frontmatter reader: returns (name, description)."""
    name = desc = ""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            for line in text[3:end].splitlines():
                s = line.strip()
                if s.startswith("name:") and not name:
                    name = s.split(":", 1)[1].strip()
                if s.startswith("description:") and not desc:
                    desc = s.split(":", 1)[1].strip()
    return name, desc


def collect_files(base: Path, root: Path):
    """All readable text files under `base`, as [{path, content}] relative to `base`."""
    out = []
    for p in sorted(base.rglob("*")):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.relative_to(base).parts):
            continue
        if p.name.startswith("."):
            continue
        if p.suffix.lower() not in TEXT_SUFFIXES:
            continue
        content = read_text(p)
        if content is None:
            continue
        out.append({"path": str(p.relative_to(base)), "content": content})
    # SKILL.md / README.md first, then alphabetical
    out.sort(key=lambda f: (0 if re.search(r"(^|/)SKILL\.md$", f["path"], re.I)
                            else 1 if re.search(r"README\.md$", f["path"], re.I)
                            else 2, f["path"].lower()))
    return out


def first_heading(text: str):
    for line in text.splitlines():
        m = re.match(r"^#\s+(.*)", line.strip())
        if m:
            return m.group(1).strip()
    return ""


def _skill_item(d: Path, path_label: str, source=""):
    files = collect_files(d, d)
    if not files:
        return None
    skill_md = next((f for f in files if re.search(r"(^|/)SKILL\.md$", f["path"], re.I)), None)
    desc = ""
    if skill_md:
        _, desc = parse_frontmatter(skill_md["content"])
    if not desc:
        # _shared and the like: fall back to a README or first heading
        readme = next((f for f in files if re.search(r"README\.md$", f["path"], re.I)), None)
        src = (skill_md or readme or files[0])["content"]
        desc = first_heading(src)
    return {
        "id": "skill/" + d.name,
        "name": d.name,
        "display": "/" + d.name,
        "description": desc[:300],
        "path": path_label,
        "files": files,
        "source": source,          # "" = shipped in this repo; else the external source
    }


def external_map(root: Path):
    """{installed_dir_name: source_name} for skills installed via claude-control.

    Same lockfile the skill-manager server reads (tools/skillsource.py writes it),
    plus graphify, which ships its own skill via `graphify install`.
    """
    out = {}
    lock = root / "external" / "installed.json"
    if lock.exists():
        try:
            for rec in json.loads(lock.read_text()).get("installed", []):
                out[rec["dir"]] = rec.get("source", "external")
        except (ValueError, OSError, KeyError):
            pass
    return out


def build_skills(root: Path, extra_dir: Path):
    skills_dir = root / "skills"
    items, seen = [], set()
    if skills_dir.exists():
        for d in sorted(skills_dir.iterdir()):
            if not d.is_dir() or d.name.startswith("."):
                continue
            it = _skill_item(d, "skills/" + d.name)
            if it:
                items.append(it)
                seen.add(d.name)
    # Track every external skill installed via claude-control — the skillsource
    # lockfile's entries plus graphify — reading them from the live skills dir.
    if extra_dir and extra_dir.exists():
        externals = dict(external_map(root))
        if "graphify" not in externals and (extra_dir / "graphify" / "SKILL.md").exists():
            externals["graphify"] = "graphify (pip: graphifyy)"
        for name, source in sorted(externals.items()):
            if name in seen:
                continue
            d = extra_dir / name
            if d.is_dir() and (d / "SKILL.md").exists():
                it = _skill_item(d, "external · " + name, source=source)
                if it:
                    items.append(it)
                    seen.add(name)
    return items


def build_tools(root: Path):
    """Each tool file (and templates/) is its own readable entry."""
    items = []
    tools_dir = root / "tools"
    if tools_dir.exists():
        readme = tools_dir / "README.md"
        readme_txt = read_text(readme) if readme.exists() else ""
        blurbs = {}
        if readme_txt:
            # rows like: | `repo_map.py` | does X | -> map filename -> blurb
            for m in re.finditer(r"`([\w./-]+\.py)`[^\n|]*\|([^\n|]+)", readme_txt):
                blurbs[m.group(1)] = m.group(2).strip()
        for p in sorted(tools_dir.iterdir()):
            if not p.is_file() or p.suffix.lower() not in TEXT_SUFFIXES or p.name.startswith("."):
                continue
            content = read_text(p)
            if content is None:
                continue
            desc = blurbs.get(p.name, "")
            if not desc:
                doc = re.search(r'^\s*(?:#\s*)?(?:"""|\'\'\')(.+?)(?:"""|\'\'\'|\n)', content, re.S)
                if doc:
                    desc = " ".join(doc.group(1).split())[:200]
                elif p.suffix.lower() == ".md":
                    desc = first_heading(content)
            items.append({
                "id": "tool/" + p.name,
                "name": p.name,
                "display": "tools/" + p.name,
                "description": desc[:300],
                "path": "tools/" + p.name,
                "files": [{"path": p.name, "content": content}],
            })
    return items


def build_docs(root: Path):
    """A few top-level docs worth reading from the index."""
    items = []
    for fname, disp in (("README.md", "README"), ("skill-manager/README.md", "skill-manager")):
        p = root / fname
        content = read_text(p) if p.exists() else None
        if content is None:
            continue
        items.append({
            "id": "doc/" + fname.replace("/", "-"),
            "name": disp,
            "display": fname,
            "description": first_heading(content) or fname,
            "path": fname,
            "files": [{"path": fname, "content": content}],
        })
    return items


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(REPO / "site"), help="output directory")
    ap.add_argument("--root", default=str(REPO), help="repo root to index")
    ap.add_argument("--extra-skills", default=str(Path.home() / ".claude" / "skills"),
                    help="live skills dir to pull claude-control-installed externals (graphify, synced sources) from")
    ap.add_argument("--repo-name", default="tejas-techstack/claude-control")
    a = ap.parse_args()

    root = Path(a.root).resolve()
    extra = Path(a.extra_skills).expanduser() if a.extra_skills else None
    all_skills = build_skills(root, extra)
    local = [s for s in all_skills if not s.get("source")]
    external = [s for s in all_skills if s.get("source")]
    tools = build_tools(root)
    docs = build_docs(root)

    collections = [{"label": "skills", "kind": "skill", "items": local}]
    if external:
        collections.append({"label": "external skills", "kind": "skill", "items": external})
    collections.append({"label": "tools", "kind": "tool", "items": tools})
    if docs:
        collections.append({"label": "docs", "kind": "doc", "items": docs})

    summary = "%d skills · %d tools" % (len(all_skills), len(tools))
    if external:
        summary = "%d skills (+%d external) · %d tools" % (len(local), len(external), len(tools))
    data = {
        "generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "repo": a.repo_name,
        "summary": summary,
        "collections": collections,
    }

    template = TEMPLATE.read_text()
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = template.replace("__DATA__", payload)

    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / "index.html").write_text(html, encoding="utf-8")
    # A .nojekyll file keeps GitHub Pages from touching our output.
    (out / ".nojekyll").write_text("")

    total_files = sum(len(it["files"]) for c in collections for it in c["items"])
    print("built %s" % (out / "index.html"))
    print("  %d local + %d external skills, %d tools, %d docs — %d files, %.0f KB html"
          % (len(local), len(external), len(tools), len(docs), total_files, len(html) / 1024))
    for s in external:
        print("  external: %s (%s)" % (s["name"], s["source"]))


if __name__ == "__main__":
    main()
