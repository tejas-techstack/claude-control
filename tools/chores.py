#!/usr/bin/env python3
"""chores: detect and run the repetitive tasks (format, lint, test, typecheck,
audit) that scripts should do instead of an AI doing them token-by-token.
Stdlib only. Usage: chores.py list | chores.py run <name|all>"""
import subprocess, sys, shutil, json
from pathlib import Path


def has(f):
    return Path(f).exists()


def cmd_exists(c):
    return shutil.which(c) is not None


def detect():
    chores = {}
    py = has("pyproject.toml") or has("setup.py") or any(Path(".").glob("*.py"))
    js = has("package.json")
    if py:
        if cmd_exists("ruff"):
            chores["format"] = "ruff format ."
            chores["lint"] = "ruff check . --fix"
        elif cmd_exists("black"):
            chores["format"] = "black ."
        if cmd_exists("pytest") and (has("tests") or list(Path(".").rglob("test_*.py"))):
            chores["test"] = "pytest -q"
        if cmd_exists("mypy") and has("pyproject.toml"):
            chores["typecheck"] = "mypy ."
        if cmd_exists("pip-audit"):
            chores["audit"] = "pip-audit"
    if js:
        try:
            scripts = json.loads(Path("package.json").read_text()).get("scripts", {})
        except Exception:
            scripts = {}
        for key in ("format", "lint", "test", "typecheck", "build"):
            if key in scripts:
                chores[key] = "npm run " + key
        if "format" not in chores and cmd_exists("npx"):
            chores["format"] = "npx --yes prettier -w ."
        chores.setdefault("audit", "npm audit --audit-level=high")
    if has("go.mod"):
        chores["format"] = "gofmt -w ."
        chores["test"] = "go test ./..."
        chores["vet"] = "go vet ./..."
    if has("Cargo.toml"):
        chores["format"] = "cargo fmt"
        chores["lint"] = "cargo clippy"
        chores["test"] = "cargo test"
    if has("Makefile"):
        chores.setdefault("make-test", "make test")
    return chores


def main():
    chores = detect()
    args = sys.argv[1:]
    if not args or args[0] == "list":
        if not chores:
            print("No chores detected (no known project files/tools found).")
            return
        print("Detected chores (run: chores.py run <name|all>):")
        for k, v in chores.items():
            print(f"  {k:10} -> {v}")
        print("")
        print("Rule of thumb: if a script can do it, the AI should not do it by hand.")
        return
    if args[0] == "run":
        targets = list(chores) if args[1:] == ["all"] else args[1:]
        failed = []
        for t in targets:
            if t not in chores:
                print("unknown chore: " + t)
                failed.append(t)
                continue
            print(f"\n== {t}: {chores[t]}")
            r = subprocess.run(chores[t], shell=True)
            if r.returncode != 0:
                failed.append(t)
        if failed:
            print("\nSummary: FAILED: " + ", ".join(failed))
            sys.exit(1)
        print("\nSummary: all chores passed")
        return
    print(__doc__)


if __name__ == "__main__":
    main()
