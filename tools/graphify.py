#!/usr/bin/env python3
"""graphify: build an import/dependency graph of a repo so the model can see
structure without reading everything. Stdlib only.
Usage: graphify.py [ROOT] [--out docs/GRAPH.md] [--json graph.json] [--top 12]
Outputs: Mermaid graph of the most central files + centrality ranking."""
import ast, re, json, argparse
from pathlib import Path
from collections import defaultdict

IGNORE = {".git", "node_modules", "venv", ".venv", "env", "dist", "build", "__pycache__",
          ".next", "target", "vendor", ".tox", ".mypy_cache", "coverage", ".idea", ".vscode"}
JS_EXT = {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}
JS_IMPORT = re.compile(r"""(?:import\s+(?:[\w*{}\s,]+\s+from\s+)?|require\s*\(\s*|import\s*\(\s*)["']([^"']+)["']""")


def walk(root):
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root)
        if any(part in IGNORE or (part.startswith(".") and part != ".github") for part in rel.parts):
            continue
        if p.is_file() and (p.suffix == ".py" or p.suffix in JS_EXT):
            yield p


def py_imports(path):
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


def js_imports(path):
    try:
        return JS_IMPORT.findall(path.read_text(errors="replace"))
    except Exception:
        return []


def build(root):
    files = list(walk(root))
    rel = {f: f.relative_to(root) for f in files}
    pymap = {}
    for f in files:
        if f.suffix == ".py":
            dotted = ".".join(rel[f].with_suffix("").parts)
            pymap[dotted] = f
            if f.name == "__init__.py":
                pymap[".".join(rel[f].parent.parts)] = f
    edges = defaultdict(set)
    for f in files:
        if f.suffix == ".py":
            for m in py_imports(f):
                cands = [m]
                if "." in m:
                    cands.append(m.rsplit(".", 1)[0])
                for cand in cands:
                    if cand in pymap and pymap[cand] != f:
                        edges[str(rel[f])].add(str(rel[pymap[cand]]))
                        break
        else:
            for spec in js_imports(f):
                if not spec.startswith("."):
                    continue
                base = (f.parent / spec)
                candidates = [base] + [base.with_suffix(e) for e in JS_EXT] + [base / ("index" + e) for e in JS_EXT]
                for cand in candidates:
                    try:
                        c = cand.resolve().relative_to(root.resolve())
                    except ValueError:
                        continue
                    if (root / c).is_file():
                        edges[str(rel[f])].add(str(c))
                        break
    return files, edges


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--out", default="")
    ap.add_argument("--json", default="")
    ap.add_argument("--top", type=int, default=12)
    a = ap.parse_args()
    root = Path(a.root).resolve()
    files, edges = build(root)
    indeg = defaultdict(int)
    for src, dsts in edges.items():
        for d in dsts:
            indeg[d] += 1
    nodes = sorted(set(list(indeg) + list(edges)), key=lambda n: (-indeg[n], n))
    top = nodes[: a.top]
    lines = ["# Dependency graph: " + root.name, "",
             f"{len(files)} source files scanned, {sum(len(v) for v in edges.values())} internal imports.",
             "", "## Most central files (import in-degree)"]
    for n in top:
        lines.append(f"- `{n}` <- imported by {indeg[n]}")
    lines += ["", "## Graph (top nodes)", "```mermaid", "graph LR"]
    ids = {n: f"n{i}" for i, n in enumerate(top)}
    for n in top:
        lines.append(f'  {ids[n]}["{n}"]')
    for src, dsts in edges.items():
        for d in dsts:
            if src in ids and d in ids:
                lines.append(f"  {ids[src]} --> {ids[d]}")
    lines += ["```", "", "Tip: read the central files first; they explain the most per token."]
    out = "\n".join(lines) + "\n"
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(out)
        print("wrote " + a.out)
    else:
        print(out)
    if a.json:
        Path(a.json).write_text(json.dumps(
            {"edges": {k: sorted(v) for k, v in edges.items()}, "in_degree": dict(indeg)}, indent=1))
        print("wrote " + a.json)


if __name__ == "__main__":
    main()
