#!/usr/bin/env python3
"""context_pack: assemble a budgeted CONTEXT_PACK.md - README + the most central
files (by import in-degree) truncated head+tail - the cheapest useful context for a model.
Stdlib only, self-contained. Usage: context_pack.py [ROOT] [--budget 8000] [--out CONTEXT_PACK.md]

Centrality is computed inline here (a lightweight Python/JS import scan) so this tool
has no external dependencies. For a deep dependency/knowledge graph, use the `/graphify .`
skill (pip install graphifyy && graphify install) instead."""
import ast, re, argparse
from pathlib import Path
from collections import defaultdict

IGNORE = {".git", "node_modules", "venv", ".venv", "env", "dist", "build", "__pycache__",
          ".next", "target", "vendor", ".tox", ".mypy_cache", "coverage", ".idea", ".vscode"}
JS_EXT = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}
JS_IMPORT = re.compile(r"""(?:import\s+(?:[\w*{}\s,]+\s+from\s+)?|require\s*\(\s*|import\s*\(\s*)["']([^"']+)["']""")


def tokens(s):
    return len(s) // 4


def head_tail(text, tok_budget):
    if tokens(text) <= tok_budget:
        return text
    chars = tok_budget * 4
    return text[: chars * 2 // 3] + "\n\n[... truncated by context_pack ...]\n\n" + text[-chars // 3:]


def _walk(root):
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root)
        if any(part in IGNORE or (part.startswith(".") and part != ".github") for part in rel.parts):
            continue
        if p.is_file() and (p.suffix == ".py" or p.suffix in JS_EXT):
            yield p


def _py_imports(path):
    try:
        tree = ast.parse(path.read_text(errors="replace"))
    except SyntaxError:
        return []
    mods = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods += [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.module:
            mods.append(node.module)
    return mods


def _js_imports(path):
    try:
        return JS_IMPORT.findall(path.read_text(errors="replace"))
    except Exception:
        return []


def central_files(root, top=8):
    """Return up to `top` repo-relative paths ranked by internal import in-degree."""
    files = list(_walk(root))
    rel = {f: f.relative_to(root) for f in files}
    pymap = {}
    for f in files:
        if f.suffix == ".py":
            pymap[".".join(rel[f].with_suffix("").parts)] = f
            if f.name == "__init__.py":
                pymap[".".join(rel[f].parent.parts)] = f
    indeg = defaultdict(int)
    for f in files:
        if f.suffix == ".py":
            for m in _py_imports(f):
                cands = [m] + ([m.rsplit(".", 1)[0]] if "." in m else [])
                for cand in cands:
                    if cand in pymap and pymap[cand] != f:
                        indeg[str(rel[pymap[cand]])] += 1
                        break
        else:
            for spec in _js_imports(f):
                if not spec.startswith("."):
                    continue
                base = f.parent / spec
                candidates = [base] + [base.with_suffix(e) for e in JS_EXT] + [base / ("index" + e) for e in JS_EXT]
                for cand in candidates:
                    try:
                        c = cand.resolve().relative_to(root.resolve())
                    except ValueError:
                        continue
                    if (root / c).is_file():
                        indeg[str(c)] += 1
                        break
    return sorted(indeg, key=lambda k: -indeg[k])[:top]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--budget", type=int, default=8000)
    ap.add_argument("--out", default="CONTEXT_PACK.md")
    a = ap.parse_args()
    root = Path(a.root).resolve()
    central = central_files(root, top=8)
    picks = []
    for name in ("README.md", "readme.md", "README.rst", "pyproject.toml", "package.json"):
        if (root / name).exists():
            picks.append(root / name)
    picks += [root / c for c in central if (root / c).exists()]
    seen = set()
    parts = [f"# Context pack: {root.name} (budget {a.budget} tokens)\n"]
    used = 0
    per_file = max(400, a.budget // max(len(picks), 1))
    for p in picks:
        if p in seen:
            continue
        seen.add(p)
        try:
            txt = p.read_text(errors="replace")
        except Exception:
            continue
        chunk = head_tail(txt, per_file)
        block = (f"\n---\n## FILE: {p.relative_to(root)} (~{tokens(chunk)} tok of {tokens(txt)})\n\n"
                 "```\n" + chunk + "\n```\n")
        if used + tokens(block) > a.budget:
            break
        parts.append(block)
        used += tokens(block)
    out = "".join(parts)
    Path(a.out).write_text(out)
    print(f"wrote {a.out}: {len(seen)} files, ~{tokens(out):,} tokens (raw repo would be far larger)")


if __name__ == "__main__":
    main()
