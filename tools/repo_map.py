#!/usr/bin/env python3
"""repo_map: a token-cheap overview of a repository - tree, languages, sizes,
entry points, symbols, TODOs - so the model reads a map instead of the territory.
Stdlib only. Usage: repo_map.py [ROOT] [--out REPO_MAP.md] [--budget 3000]"""
import ast, re, argparse
from pathlib import Path
from collections import Counter

IGNORE = {".git", "node_modules", "venv", ".venv", "env", "dist", "build", "__pycache__",
          ".next", "target", "vendor", ".tox", ".mypy_cache", "coverage"}
LANG = {".py": "Python", ".js": "JavaScript", ".ts": "TypeScript", ".tsx": "TSX", ".jsx": "JSX",
        ".go": "Go", ".rs": "Rust", ".java": "Java", ".rb": "Ruby", ".c": "C", ".h": "C header",
        ".cpp": "C++", ".cs": "C#", ".php": "PHP", ".sh": "Shell", ".md": "Markdown",
        ".html": "HTML", ".css": "CSS", ".sql": "SQL", ".yml": "YAML", ".yaml": "YAML", ".json": "JSON"}
ENTRY_HINTS = ("main", "index", "app", "cli", "server", "manage", "__main__")
JS_SYM = re.compile(r"^\s*export\s+(?:default\s+)?(?:async\s+)?(?:function|class|const)\s+([A-Za-z_$][\w$]*)", re.M)


def keep(rel):
    return not any(part in IGNORE or (part.startswith(".") and part != ".github") for part in rel.parts)


def list_files(root):
    return [p for p in sorted(root.rglob("*")) if p.is_file() and keep(p.relative_to(root))]


def tokens(n_chars):
    return n_chars // 4


def py_symbols(p):
    try:
        tree = ast.parse(p.read_text(errors="replace"))
    except SyntaxError:
        return []
    out = []
    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.append("def " + n.name + "()")
        elif isinstance(n, ast.ClassDef):
            methods = [m.name for m in n.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))][:6]
            out.append("class " + n.name + " [" + ", ".join(methods) + "]")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--out", default="")
    ap.add_argument("--budget", type=int, default=3000)
    a = ap.parse_args()
    root = Path(a.root).resolve()
    fs = list_files(root)
    lang = Counter()
    size = {}
    for p in fs:
        lang[LANG.get(p.suffix, p.suffix or "other")] += 1
        try:
            size[p] = p.stat().st_size
        except OSError:
            size[p] = 0
    total_tok = tokens(sum(size.values()))
    lines = ["# Repo map: " + root.name, "",
             f"{len(fs)} files, ~{total_tok:,} tokens if read raw. Read THIS map instead.", "",
             "## Languages: " + ", ".join(f"{k} x{v}" for k, v in lang.most_common(8)), ""]
    lines.append("## Layout")
    dirs = Counter(p.relative_to(root).parts[0] if len(p.relative_to(root).parts) > 1 else "." for p in fs)
    for d, c in dirs.most_common(20):
        lines.append(f"- {d}/ ({c} files)" if d != "." else f"- ./ ({c} top-level files)")
    entries = [p for p in fs if p.stem.lower() in ENTRY_HINTS or
               p.name in ("Makefile", "Dockerfile", "package.json", "pyproject.toml", "go.mod", "Cargo.toml")]
    lines += ["", "## Entry points and manifests"] + [f"- {p.relative_to(root)}" for p in entries[:15]]
    big = sorted(fs, key=lambda p: -size[p])[:8]
    lines += ["", "## Largest files (skim, do not read blindly)"]
    lines += [f"- {p.relative_to(root)} (~{tokens(size[p]):,} tok)" for p in big]
    lines += ["", "## Symbols (top-level, per source file)"]
    used = tokens(len("\n".join(lines)))
    src = sorted([f for f in fs if f.suffix in (".py", ".js", ".ts", ".tsx", ".jsx")], key=lambda p: -size[p])
    for p in src:
        if p.suffix == ".py":
            syms = py_symbols(p)
        else:
            syms = JS_SYM.findall(p.read_text(errors="replace"))[:12]
        if not syms:
            continue
        chunk = f"- **{p.relative_to(root)}**: " + "; ".join(str(s) for s in syms[:10])
        if used + tokens(len(chunk)) > a.budget:
            lines.append("- ...budget reached; run with --budget N for more.")
            break
        lines.append(chunk)
        used += tokens(len(chunk))
    todos = []
    for p in fs:
        if p.suffix in LANG and size[p] < 300_000:
            try:
                txt = p.read_text(errors="replace")
            except Exception:
                continue
            for i, line in enumerate(txt.splitlines(), 1):
                if "TODO" in line or "FIXME" in line:
                    todos.append(f"- {p.relative_to(root)}:{i} {line.strip()[:90]}")
    if todos:
        lines += ["", f"## TODO/FIXME ({len(todos)} found, first 10)"] + todos[:10]
    out = "\n".join(lines) + "\n"
    if a.out:
        Path(a.out).write_text(out)
        print(f"wrote {a.out} (~{tokens(len(out))} tokens)")
    else:
        print(out)


if __name__ == "__main__":
    main()
