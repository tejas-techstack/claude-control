#!/usr/bin/env python3
"""skillsource: load EXTERNAL Claude skill collections (gstack, anthropics/skills,
your own team repos) alongside the 25 skills in this repo — WITHOUT modifying the
upstream skills. One source of truth shared by install.sh, install.ps1, and the
skill manager, so "load a skill repo" means the same thing everywhere.

Commands
  list                       configured sources + how many skills each installed
  sync [NAME|all]            git clone/pull each source, (re)install its SKILL.md dirs
  remove [NAME|all]          uninstall the skills a source installed (upstream clone kept)
  add NAME URL [--subdir S] [--ref R] [--prefix P]   append a source to the manifest
  status                     machine-readable JSON (the skill manager calls this)

  Global flags: --manifest FILE  --skills-dir DIR  --ctrl-dir DIR
                --mode copy|symlink  --json

How it works
  * Manifest ............ skill-sources.txt next to this file (or --manifest).
  * Clones cached in .... <ctrl>/external/<name>/           (re-pull, never edited)
  * Skills installed to . ~/.claude/skills/<prefix><skill>/ (symlink or copy)
  * Provenance tracked in <ctrl>/external/installed.json    (so re-sync/remove is exact)

Every folder containing a SKILL.md under a source's subdir becomes a skill. On a
name clash with an existing folder we disambiguate (never clobber) and warn.
Stdlib only; needs `git` on PATH for sync.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")


# ---------- locations ----------

def default_ctrl_dir():
    return Path(os.environ.get("CLAUDE_CTRL_DIR",
                               Path.home() / ".claude" / "claude-control"))


def default_skills_dir():
    return Path(os.environ.get("CLAUDE_SKILLS_DIR",
                               Path.home() / ".claude" / "skills"))


def default_manifest():
    # Prefer a manifest sitting next to the installed tools; fall back to the repo copy.
    for cand in (HERE / "skill-sources.txt", HERE.parent / "skill-sources.txt"):
        if cand.exists():
            return cand
    return HERE / "skill-sources.txt"


# ---------- manifest ----------

def parse_manifest(path):
    """Return [{name,url,subdir,ref,prefix,raw,lineno}]. Tolerant of blanks/comments."""
    sources = []
    if not Path(path).exists():
        return sources
    for lineno, raw in enumerate(Path(path).read_text(errors="replace").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        toks = line.split()
        name, url = toks[0], (toks[1] if len(toks) > 1 else "")
        entry = {"name": name, "url": url, "subdir": ".", "ref": "",
                 "prefix": name + "-", "raw": raw, "lineno": lineno}
        for tok in toks[2:]:
            if "=" in tok:
                k, v = tok.split("=", 1)
                if k in ("subdir", "ref", "prefix"):
                    entry[k] = v
        if not NAME_RE.match(name) or not url:
            entry["error"] = "bad source line (need: <name> <git-url> [k=v...])"
        sources.append(entry)
    return sources


def find_source(sources, name):
    for s in sources:
        if s["name"] == name:
            return s
    return None


# ---------- lockfile (provenance) ----------

def lock_path(ctrl):
    return Path(ctrl) / "external" / "installed.json"


def read_lock(ctrl):
    p = lock_path(ctrl)
    if p.exists():
        try:
            return json.loads(p.read_text())
        except (ValueError, OSError):
            pass
    return {"installed": []}   # each: {source, dir, upstream, mode}


def write_lock(ctrl, data):
    p = lock_path(ctrl)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2))


# ---------- git ----------

def git_available():
    return shutil.which("git") is not None


def clone_or_pull(src, ctrl):
    """Clone the source (or pull if already cloned). Returns (ok, message)."""
    if not git_available():
        return False, "git not found on PATH"
    dest = Path(ctrl) / "external" / src["name"]
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        if (dest / ".git").exists():
            subprocess.run(["git", "-C", str(dest), "fetch", "--depth", "1", "origin"],
                           check=True, capture_output=True, text=True, timeout=300)
            ref = src["ref"] or _default_branch(dest)
            subprocess.run(["git", "-C", str(dest), "checkout", "-q", ref],
                           check=True, capture_output=True, text=True, timeout=120)
            subprocess.run(["git", "-C", str(dest), "reset", "--hard", "-q",
                            "origin/" + ref if _is_branch(dest, ref) else ref],
                           check=True, capture_output=True, text=True, timeout=120)
            return True, "pulled " + ref
        cmd = ["git", "clone", "--depth", "1"]
        if src["ref"]:
            cmd += ["--branch", src["ref"]]
        cmd += [src["url"], str(dest)]
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=600)
        return True, "cloned"
    except subprocess.CalledProcessError as e:
        return False, (e.stderr or e.stdout or str(e)).strip().splitlines()[-1][:200]
    except subprocess.TimeoutExpired:
        return False, "git timed out"


def _default_branch(dest):
    try:
        r = subprocess.run(["git", "-C", str(dest), "symbolic-ref", "--short", "-q",
                            "refs/remotes/origin/HEAD"], capture_output=True, text=True)
        head = r.stdout.strip().rsplit("/", 1)[-1]
        return head or "main"
    except Exception:
        return "main"


def _is_branch(dest, ref):
    r = subprocess.run(["git", "-C", str(dest), "rev-parse", "--verify", "-q",
                        "origin/" + ref], capture_output=True, text=True)
    return r.returncode == 0


# ---------- discovery + install ----------

def discover_skills(repo_root, subdir):
    """Every *subdirectory* holding a SKILL.md under subdir.

    We never install the discovery root itself as a skill (installing a whole
    repo as one "skill" is never what you want): a repo like gstack ships a
    root-level umbrella SKILL.md plus dozens of real skills in subfolders, so we
    take the subfolders and skip the umbrella. The lone exception: if the root
    has a SKILL.md and there are NO subfolder skills, the repo *is* one skill.
    Among subfolder skills, an outer skill wins over one nested inside it.
    """
    base = (Path(repo_root) / subdir).resolve()
    if not base.exists():
        return []
    found = []
    for md in sorted(base.rglob("SKILL.md")):
        d = md.parent.resolve()
        if any(part in (".git", "node_modules", ".disabled", ".trash", "__pycache__")
               for part in d.parts):
            continue
        found.append(d)
    subfolder = [d for d in found if d != base]
    if not subfolder:
        return [base] if base in found else []
    subfolder.sort(key=lambda p: len(p.parts))
    kept = []
    for d in subfolder:
        if not any(str(d).startswith(str(k) + os.sep) for k in kept):
            kept.append(d)
    return kept


def frontmatter_name(skill_dir):
    try:
        text = (Path(skill_dir) / "SKILL.md").read_text(errors="replace")
    except OSError:
        return ""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        body = text[3:end] if end != -1 else text[3:]
        for line in body.splitlines():
            if line.strip().startswith("name:"):
                return line.split(":", 1)[1].strip()
    return ""


def _rm(p):
    if p.is_symlink():
        p.unlink()
    elif p.is_dir():
        shutil.rmtree(p, ignore_errors=True)
    elif p.exists():
        p.unlink()


def install_one(skill_dir, skills_dir, prefix, taken, mode):
    """Install a single skill folder; returns (dir_name, action). Never clobbers a
    folder we don't own — `taken` already holds every dir currently on disk plus the
    ones installed earlier this run, so a clash just bumps to <name>-2, <name>-3..."""
    skills_dir = Path(skills_dir)
    skills_dir.mkdir(parents=True, exist_ok=True)
    base = prefix + skill_dir.name
    dir_name, i = base, 2
    while dir_name in taken:
        dir_name = "%s-%d" % (base, i)
        i += 1
    target = skills_dir / dir_name
    if target.is_symlink() and Path(os.path.realpath(target)) == skill_dir.resolve():
        taken.add(dir_name)
        return dir_name, "unchanged"
    _rm(target)
    # Symlink is the right default for external skills: the clone stays whole under
    # external/, so a skill that references sibling paths (../bin, shared assets) still
    # resolves. Copy mode is the fallback when symlinks aren't permitted (e.g. Windows).
    try:
        if mode == "symlink":
            target.symlink_to(skill_dir.resolve(), target_is_directory=True)
            action = "linked"
        else:
            shutil.copytree(skill_dir, target)
            action = "copied"
    except (OSError, NotImplementedError):
        _rm(target)
        shutil.copytree(skill_dir, target, dirs_exist_ok=True)
        action = "copied (symlink unavailable)"
    taken.add(dir_name)
    return dir_name, action


def existing_taken(skills_dir):
    s = set()
    for base in (Path(skills_dir), Path(skills_dir) / ".disabled"):
        if base.exists():
            s.update(p.name for p in base.iterdir() if p.is_dir())
    return s


# ---------- commands ----------

def cmd_sync(args, cfg):
    sources = parse_manifest(cfg["manifest"])
    if not sources:
        print("No sources in " + str(cfg["manifest"]))
        return 0
    which = [s for s in sources if args.name in ("all", s["name"])]
    if not which:
        print("no source named '%s' (see: skillsource.py list)" % args.name)
        return 1
    if not git_available():
        print("git is required to sync external skills — install git and retry.")
        return 1
    lock = read_lock(cfg["ctrl"])
    run_names = {s["name"] for s in which}
    # Records for sources we're not touching survive as-is; rebuild the rest.
    kept_records = [r for r in lock["installed"] if r["source"] not in run_names]
    warned = 0
    for src in which:
        if src.get("error"):
            print("  [WARN] %s: %s" % (src["name"], src["error"]))
            warned += 1
            kept_records += [r for r in lock["installed"] if r["source"] == src["name"]]
            continue
        ok, msg = clone_or_pull(src, cfg["ctrl"])
        if not ok:
            print("  [FAIL] %s: %s" % (src["name"], msg))
            warned += 1
            kept_records += [r for r in lock["installed"] if r["source"] == src["name"]]
            continue
        repo = Path(cfg["ctrl"]) / "external" / src["name"]
        # Free this source's own folders, THEN read what's on disk, so a fresh sync
        # reuses its own names but can never overwrite another source or a hand-made skill.
        for r in [x for x in lock["installed"] if x["source"] == src["name"]]:
            _uninstall_dir(cfg["skills"], r["dir"])
        taken = existing_taken(cfg["skills"])
        skills = discover_skills(repo, src["subdir"])
        installed, seen_fm = 0, {}
        for sd in skills:
            dir_name, action = install_one(sd, cfg["skills"], src["prefix"], taken, cfg["mode"])
            fm = frontmatter_name(sd)
            if fm and fm in seen_fm:
                print("  [WARN] %s: two skills both answer to '/%s' (%s, %s) — Claude will "
                      "see a name clash; disable one in the manager" % (src["name"], fm, seen_fm[fm], dir_name))
                warned += 1
            elif fm:
                seen_fm[fm] = dir_name
            kept_records.append({"source": src["name"], "dir": dir_name,
                                 "upstream": str(sd), "mode": cfg["mode"], "invoke": fm})
            installed += 1
        print("  [ OK ] %s: %s, %d skill%s installed"
              % (src["name"], msg, installed, "" if installed == 1 else "s"))
    write_lock(cfg["ctrl"], {"installed": kept_records})
    print("Synced. External skills now live in %s (prefix per source)." % cfg["skills"])
    if warned:
        print("%d warning(s) above." % warned)
    return 0


def _uninstall_dir(skills_dir, dir_name):
    for base in (Path(skills_dir), Path(skills_dir) / ".disabled"):
        t = base / dir_name
        if t.is_symlink():
            t.unlink()
            return True
        if t.exists():
            shutil.rmtree(t, ignore_errors=True)
            return True
    return False


def cmd_remove(args, cfg):
    lock = read_lock(cfg["ctrl"])
    keep, removed = [], 0
    for rec in lock["installed"]:
        if args.name in ("all", rec["source"]):
            if _uninstall_dir(cfg["skills"], rec["dir"]):
                removed += 1
        else:
            keep.append(rec)
    write_lock(cfg["ctrl"], {"installed": keep})
    print("Removed %d external skill folder(s). Upstream clones under %s/external kept."
          % (removed, cfg["ctrl"]))
    return 0


def _status(cfg):
    sources = parse_manifest(cfg["manifest"])
    lock = read_lock(cfg["ctrl"])
    by_src = {}
    for rec in lock["installed"]:
        by_src.setdefault(rec["source"], []).append(rec)
    out = []
    for s in sources:
        recs = by_src.get(s["name"], [])
        cloned = (Path(cfg["ctrl"]) / "external" / s["name"] / ".git").exists()
        out.append({"name": s["name"], "url": s["url"], "subdir": s["subdir"],
                    "ref": s["ref"], "prefix": s["prefix"], "cloned": cloned,
                    "installed": len(recs),
                    "skills": [{"dir": r["dir"], "invoke": r.get("invoke", "")} for r in recs],
                    "error": s.get("error", "")})
    return {"manifest": str(cfg["manifest"]), "skills_dir": str(cfg["skills"]),
            "git": git_available(), "sources": out}


def cmd_status(args, cfg):
    print(json.dumps(_status(cfg), indent=2))
    return 0


def cmd_list(args, cfg):
    st = _status(cfg)
    if args.json:
        print(json.dumps(st, indent=2))
        return 0
    print("External skill sources  (manifest: %s)" % st["manifest"])
    print("  git on PATH: %s   install target: %s" % (st["git"], st["skills_dir"]))
    if not st["sources"]:
        print("  (none configured — add one with: skillsource.py add NAME URL)")
        return 0
    for s in st["sources"]:
        flag = "cloned" if s["cloned"] else "not fetched"
        extra = (" err:" + s["error"]) if s["error"] else ""
        print("  * %-16s %-45s [%s, %d installed]%s"
              % (s["name"], s["url"], flag, s["installed"], extra))
        for sk in s["skills"][:60]:
            print("      - %s%s" % (sk["dir"], ("  -> /" + sk["invoke"]) if sk["invoke"] else ""))
    print("\nsync one:  skillsource.py sync <name>    sync all: skillsource.py sync all")
    return 0


def cmd_add(args, cfg):
    if not NAME_RE.match(args.name):
        print("name must be lowercase letters/digits/-/_")
        return 1
    sources = parse_manifest(cfg["manifest"])
    if find_source(sources, args.name):
        print("a source named '%s' already exists in the manifest" % args.name)
        return 1
    line = "%s  %s" % (args.name, args.url)
    if args.subdir and args.subdir != ".":
        line += "  subdir=" + args.subdir
    if args.ref:
        line += "  ref=" + args.ref
    if args.prefix is not None:
        line += "  prefix=" + args.prefix
    with open(cfg["manifest"], "a") as f:
        f.write(("" if Path(cfg["manifest"]).read_text().endswith("\n") else "\n") + line + "\n")
    print("added source '%s' -> %s\nrun: skillsource.py sync %s" % (args.name, args.url, args.name))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", default=str(default_manifest()))
    ap.add_argument("--skills-dir", default=str(default_skills_dir()))
    ap.add_argument("--ctrl-dir", default=str(default_ctrl_dir()))
    ap.add_argument("--mode", choices=["copy", "symlink"], default="symlink",
                    help="how to install external skills (symlink keeps the clone whole; "
                         "copy is the Windows-safe fallback)")
    ap.add_argument("--json", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("list")
    sub.add_parser("status")
    p_sync = sub.add_parser("sync"); p_sync.add_argument("name", nargs="?", default="all")
    p_rm = sub.add_parser("remove"); p_rm.add_argument("name", nargs="?", default="all")
    p_add = sub.add_parser("add")
    p_add.add_argument("name"); p_add.add_argument("url")
    p_add.add_argument("--subdir", default="."); p_add.add_argument("--ref", default="")
    p_add.add_argument("--prefix", default=None)
    a = ap.parse_args(argv)
    cfg = {"manifest": Path(a.manifest).expanduser(), "skills": Path(a.skills_dir).expanduser(),
           "ctrl": Path(a.ctrl_dir).expanduser(), "mode": a.mode}
    fns = {"list": cmd_list, "status": cmd_status, "sync": cmd_sync,
           "remove": cmd_remove, "add": cmd_add}
    if not a.cmd:
        a.cmd, a.json = "list", a.json
    return fns[a.cmd](a, cfg)


if __name__ == "__main__":
    sys.exit(main())
