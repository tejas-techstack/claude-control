#!/usr/bin/env python3
"""chores: detect and run the repetitive tasks (format, lint, test, typecheck,
audit) that scripts should do instead of an AI doing them token-by-token.
Detects Python, Node/Deno, Go, Rust, Ruby, PHP, .NET, Java (gradle/maven), Make.
Stdlib only. Usage: chores.py list | chores.py run <name|all> [--dry-run]"""
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
        if "typecheck" not in chores and has("tsconfig.json") and cmd_exists("npx"):
            chores["typecheck"] = "npx --yes tsc --noEmit"
        chores.setdefault("audit", "npm audit --audit-level=high")
    if has("deno.json") or has("deno.jsonc"):
        chores.setdefault("format", "deno fmt")
        chores.setdefault("lint", "deno lint")
        chores.setdefault("test", "deno test -A")
    if has("go.mod"):
        chores["format"] = "gofmt -w ."
        chores["test"] = "go test ./..."
        chores["vet"] = "go vet ./..."
    if has("Cargo.toml"):
        chores["format"] = "cargo fmt"
        chores["lint"] = "cargo clippy"
        chores["test"] = "cargo test"
    if has("Gemfile") or any(Path(".").glob("*.gemspec")):
        if cmd_exists("rubocop"):
            chores["format"] = "rubocop -A"
            chores["lint"] = "rubocop"
        if cmd_exists("rspec") and has("spec"):
            chores["test"] = "rspec"
        elif cmd_exists("rake"):
            chores.setdefault("test", "rake test")
    if has("composer.json"):
        if cmd_exists("php-cs-fixer"):
            chores["format"] = "php-cs-fixer fix"
        if has("vendor/bin/phpunit"):
            chores["test"] = "vendor/bin/phpunit"
        elif cmd_exists("phpunit"):
            chores["test"] = "phpunit"
    if (any(Path(".").glob("*.csproj")) or any(Path(".").glob("*.sln")) or has("global.json")) and cmd_exists("dotnet"):
        chores["format"] = "dotnet format"
        chores["test"] = "dotnet test"
        chores["build"] = "dotnet build"
    if has("gradlew"):
        chores.setdefault("build", "./gradlew build")
        chores.setdefault("test", "./gradlew test")
    elif has("pom.xml") and cmd_exists("mvn"):
        chores.setdefault("test", "mvn -q test")
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
        rest = [a for a in args[1:] if a != "--dry-run"]
        dry = "--dry-run" in args
        targets = list(chores) if rest in ([], ["all"]) else rest
        failed = []
        for t in targets:
            if t not in chores:
                print("unknown chore: " + t)
                failed.append(t)
                continue
            print(f"\n== {t}: {chores[t]}")
            if dry:
                continue
            r = subprocess.run(chores[t], shell=True)
            if r.returncode != 0:
                failed.append(t)
        if dry:
            print("\n(dry-run: nothing executed)")
            return
        if failed:
            print("\nSummary: FAILED: " + ", ".join(failed))
            sys.exit(1)
        print("\nSummary: all chores passed")
        return
    print(__doc__)


if __name__ == "__main__":
    main()
