#!/usr/bin/env python3
"""claude-control skill manager - a local, dependency-free web UI to view, edit,
create, enable/disable, and delete Claude skills, with built-in Claude chat.

Usage:  python3 server.py [--root ~/.claude/skills] [--port 8765]

Security model: binds to 127.0.0.1 only; skill names are strictly validated;
all file access is confined to the skills root. No external dependencies.

Claude chat backend order:
  1. `claude` CLI if installed (uses your existing Claude Code login)
  2. Anthropic API via ANTHROPIC_API_KEY env var
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")
FILE_RE = re.compile(r"^[A-Za-z0-9._/-]{1,120}$")
STATIC = Path(__file__).parent / "static"
DEFAULT_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")

ROOT = Path.home() / ".claude" / "skills"  # overridden by --root


# ---------- skill helpers ----------

def disabled_dir():
    d = ROOT / ".disabled"
    d.mkdir(parents=True, exist_ok=True)
    return d


def parse_frontmatter(text):
    """Tiny YAML-frontmatter reader: returns (name, description)."""
    name, desc = "", ""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            for line in text[3:end].splitlines():
                if line.strip().startswith("name:") and not name:
                    name = line.split(":", 1)[1].strip()
                if line.strip().startswith("description:") and not desc:
                    desc = line.split(":", 1)[1].strip()
    return name, desc


def skill_dirs():
    out = []
    if ROOT.exists():
        for p in sorted(ROOT.iterdir()):
            if p.is_dir() and not p.name.startswith(".") and (p / "SKILL.md").exists():
                out.append((p, True))
    dd = ROOT / ".disabled"
    if dd.exists():
        for p in sorted(dd.iterdir()):
            if p.is_dir() and (p / "SKILL.md").exists():
                out.append((p, False))
    return out


def list_skills():
    skills = []
    for path, enabled in skill_dirs():
        try:
            text = (path / "SKILL.md").read_text(errors="replace")
        except OSError:
            text = ""
        _, desc = parse_frontmatter(text)
        files = sorted(str(f.relative_to(path)) for f in path.rglob("*")
                       if f.is_file() and not f.name.startswith("."))
        skills.append({"name": path.name, "description": desc[:300],
                       "enabled": enabled, "files": files[:100],
                       "path": str(path)})
    return skills


def resolve_skill(name):
    if not NAME_RE.match(name or ""):
        raise ValueError("invalid skill name")
    for base in (ROOT, ROOT / ".disabled"):
        cand = base / name
        if cand.is_dir():
            return cand
    raise FileNotFoundError("skill not found: " + name)


def safe_file(skill_path, rel):
    if not FILE_RE.match(rel or "") or ".." in rel.split("/"):
        raise ValueError("invalid file path")
    p = (skill_path / rel).resolve()
    if not str(p).startswith(str(skill_path.resolve())):
        raise ValueError("path escapes skill directory")
    return p


# ---------- claude chat backends ----------

def claude_cli_available():
    return shutil.which("claude") is not None


def ask_claude(messages):
    """messages: [{role, content}] -> (reply, backend) or raises RuntimeError."""
    if claude_cli_available():
        transcript = "\n\n".join(
            ("User: " if m["role"] == "user" else "Assistant: ") + m["content"]
            for m in messages)
        prompt = transcript + "\n\nAssistant:"
        try:
            r = subprocess.run(["claude", "-p", prompt, "--output-format", "text"],
                               capture_output=True, text=True, timeout=180)
            if r.returncode == 0 and r.stdout.strip():
                return r.stdout.strip(), "claude CLI"
        except (subprocess.TimeoutExpired, OSError):
            pass  # fall through to API
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        raise RuntimeError(
            "No Claude backend available. Install Claude Code (claude CLI) "
            "or set ANTHROPIC_API_KEY, then restart the skill manager.")
    body = json.dumps({"model": DEFAULT_MODEL, "max_tokens": 2000,
                       "messages": messages}).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages", data=body,
        headers={"content-type": "application/json", "x-api-key": key,
                 "anthropic-version": "2023-06-01"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode())
    reply = "".join(b.get("text", "") for b in data.get("content", []))
    return reply or "(empty response)", "Anthropic API (" + DEFAULT_MODEL + ")"


# ---------- http handler ----------

SKILL_TEMPLATE = """---
name: {name}
description: {description}
---

# {title}

Describe the workflow here. Read `../_shared/GUARDRAILS.md` first if installed.

## Workflow
1. ...

## Chaining
- Input: ...
- Output: ...
"""


class Handler(BaseHTTPRequestHandler):
    server_version = "claude-control-skill-manager/0.1"

    # -- plumbing --
    def _send(self, code, payload, ctype="application/json"):
        data = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _json_body(self):
        n = int(self.headers.get("Content-Length") or 0)
        if n > 5_000_000:
            raise ValueError("body too large")
        return json.loads(self.rfile.read(n).decode() or "{}")

    def log_message(self, fmt, *args):
        pass  # keep the terminal quiet

    # -- routes --
    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        try:
            if u.path in ("/", "/index.html"):
                html = (STATIC / "index.html").read_bytes()
                return self._send(200, html, "text/html; charset=utf-8")
            if u.path == "/api/skills":
                return self._send(200, {"root": str(ROOT), "skills": list_skills(),
                                        "cli": claude_cli_available(),
                                        "api_key": bool(os.environ.get("ANTHROPIC_API_KEY"))})
            if u.path == "/api/skill":
                skill = resolve_skill(q.get("name", [""])[0])
                rel = q.get("file", ["SKILL.md"])[0]
                p = safe_file(skill, rel)
                return self._send(200, {"name": skill.name, "file": rel,
                                        "content": p.read_text(errors="replace")})
            return self._send(404, {"error": "not found"})
        except (ValueError, FileNotFoundError) as e:
            return self._send(400, {"error": str(e)})
        except Exception as e:  # noqa: BLE001 - surface to UI
            return self._send(500, {"error": repr(e)})

    def do_POST(self):
        u = urlparse(self.path)
        try:
            body = self._json_body()
            if u.path == "/api/skill":          # save a file
                skill = resolve_skill(body["name"])
                p = safe_file(skill, body.get("file", "SKILL.md"))
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(body.get("content", ""))
                return self._send(200, {"ok": True, "saved": str(p)})
            if u.path == "/api/skill/new":      # scaffold a new skill
                name = body.get("name", "").strip()
                if not NAME_RE.match(name):
                    raise ValueError("name must be lowercase letters, digits, - or _")
                target = ROOT / name
                if target.exists() or (ROOT / ".disabled" / name).exists():
                    raise ValueError("skill already exists")
                target.mkdir(parents=True)
                desc = body.get("description", "Describe when to use this skill.")
                title = name.replace("-", " ").replace("_", " ").title()
                (target / "SKILL.md").write_text(
                    SKILL_TEMPLATE.format(name=name, description=desc, title=title))
                return self._send(200, {"ok": True, "name": name})
            if u.path == "/api/toggle":         # enable <-> disable
                skill = resolve_skill(body["name"])
                if skill.parent.name == ".disabled":
                    dest = ROOT / skill.name
                else:
                    dest = disabled_dir() / skill.name
                shutil.move(str(skill), str(dest))
                return self._send(200, {"ok": True,
                                        "enabled": dest.parent == ROOT})
            if u.path == "/api/delete":         # soft delete to .trash
                skill = resolve_skill(body["name"])
                trash = ROOT / ".trash"
                trash.mkdir(parents=True, exist_ok=True)
                dest = trash / (skill.name + "-" + str(int(time.time())))
                shutil.move(str(skill), str(dest))
                return self._send(200, {"ok": True, "trashed_to": str(dest)})
            if u.path == "/api/claude":         # chat
                messages = body.get("messages", [])
                if not messages:
                    raise ValueError("no messages")
                reply, backend = ask_claude(messages)
                return self._send(200, {"reply": reply, "backend": backend})
            return self._send(404, {"error": "not found"})
        except (ValueError, FileNotFoundError, KeyError) as e:
            return self._send(400, {"error": str(e)})
        except RuntimeError as e:
            return self._send(503, {"error": str(e)})
        except Exception as e:  # noqa: BLE001
            return self._send(500, {"error": repr(e)})


def main():
    global ROOT
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=str(ROOT), help="skills directory")
    ap.add_argument("--port", type=int, default=8765)
    a = ap.parse_args()
    ROOT = Path(a.root).expanduser()
    ROOT.mkdir(parents=True, exist_ok=True)
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), Handler)
    print("claude-control skill manager")
    print("  skills root : " + str(ROOT))
    print("  claude CLI  : " + ("found" if claude_cli_available() else "not found"))
    print("  API key     : " + ("set" if os.environ.get("ANTHROPIC_API_KEY") else "not set"))
    print("  open        : http://127.0.0.1:%d  (Ctrl+C to stop)" % a.port)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")


if __name__ == "__main__":
    main()
