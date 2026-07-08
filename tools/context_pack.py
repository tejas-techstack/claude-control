#!/usr/bin/env python3
"""context_pack: assemble a budgeted CONTEXT_PACK.md - README + the most central
files (from graphify) truncated head+tail - the cheapest useful context for a model.
Stdlib only. Usage: context_pack.py [ROOT] [--budget 8000] [--out CONTEXT_PACK.md]"""
import json, argparse, subprocess, sys
from pathlib import Path


def tokens(s):
    return len(s) // 4


def head_tail(text, tok_budget):
    if tokens(text) <= tok_budget:
        return text
    chars = tok_budget * 4
    return text[: chars * 2 // 3] + "\n\n[... truncated by context_pack ...]\n\n" + text[-chars // 3:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", nargs="?", default=".")
    ap.add_argument("--budget", type=int, default=8000)
    ap.add_argument("--out", default="CONTEXT_PACK.md")
    a = ap.parse_args()
    root = Path(a.root).resolve()
    gjson = root / ".graphify.json"
    subprocess.run([sys.executable, str(Path(__file__).parent / "graphify.py"), str(root),
                    "--json", str(gjson)], capture_output=True)
    central = []
    if gjson.exists():
        data = json.loads(gjson.read_text())
        central = sorted(data.get("in_degree", {}), key=lambda k: -data["in_degree"][k])[:8]
        gjson.unlink()
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
