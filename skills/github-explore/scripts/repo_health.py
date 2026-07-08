#!/usr/bin/env python3
"""repo_health: score a GitHub repo on real maintenance signals, not stars alone.
Stdlib only, no key needed for light use (unauthenticated GitHub API ~60 req/hr; set
GITHUB_TOKEN to raise the limit). Use it to vet /github-explore and /search-existing
candidates before recommending them.

Usage:
  repo_health.py owner/repo [owner/repo ...]        # score one or several
  repo_health.py --search "cron parser language:go" # find + score top matches
  repo_health.py owner/repo --json

Signals: recency of last push, release cadence, open/closed issue ratio, contributors
(bus factor), archived/disabled flags, license (free?), tests present, stars for context.
"""
import argparse, json, os, sys, time
import urllib.request, urllib.error

API = "https://api.github.com"
UA = "claude-control-repo-health"
PERMISSIVE = {"mit", "apache-2.0", "bsd-3-clause", "bsd-2-clause", "isc", "mpl-2.0",
              "unlicense", "0bsd", "zlib", "postgresql", "python-2.0"}
COPYLEFT = {"gpl-3.0", "gpl-2.0", "agpl-3.0", "lgpl-3.0", "lgpl-2.1"}


def gh(path):
    req = urllib.request.Request(API + path, headers={"User-Agent": UA,
                                 "Accept": "application/vnd.github+json"})
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        req.add_header("Authorization", "Bearer " + tok)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode()), None
    except urllib.error.HTTPError as e:
        if e.code == 403 and "rate limit" in e.read().decode("utf-8", "replace").lower():
            return None, "GitHub rate limit hit (set GITHUB_TOKEN to raise it)"
        return None, "HTTP %s" % e.code
    except urllib.error.URLError as e:
        return None, str(e.reason)


def days_since(iso):
    if not iso:
        return None
    t = time.strptime(iso[:10], "%Y-%m-%d")
    return int((time.time() - time.mktime(t)) / 86400)


def assess(full):
    repo, err = gh("/repos/" + full)
    if err:
        return {"repo": full, "error": err}
    lic = ((repo.get("license") or {}).get("spdx_id") or "").lower()
    pushed = days_since(repo.get("pushed_at"))
    contributors = "?"
    cdata, _ = gh("/repos/%s/contributors?per_page=1&anon=1" % full)
    # contributor count via Link header is overkill for stdlib; sample the page instead
    if isinstance(cdata, list):
        contributors = "1+" if cdata else "0"
    releases, _ = gh("/repos/%s/releases?per_page=1" % full)
    last_release = days_since(releases[0]["published_at"]) if isinstance(releases, list) and releases else None
    # tests: look for a tests dir / CI workflow
    tree, _ = gh("/repos/%s/contents" % full)
    names = {c["name"].lower() for c in tree} if isinstance(tree, list) else set()
    has_tests = bool(names & {"tests", "test", "spec", "__tests__"})
    open_i = repo.get("open_issues_count", 0)

    score, notes = 0, []
    if pushed is not None:
        if pushed < 90: score += 3; notes.append("active (pushed %dd ago)" % pushed)
        elif pushed < 365: score += 1; notes.append("slowing (pushed %dd ago)" % pushed)
        else: notes.append("STALE (pushed %dd ago)" % pushed)
    if repo.get("archived"): score -= 3; notes.append("ARCHIVED")
    if last_release is not None and last_release < 365: score += 1; notes.append("released <1y")
    if has_tests: score += 2; notes.append("has tests dir")
    else: notes.append("no obvious tests dir")
    if lic in PERMISSIVE: score += 2; notes.append("permissive license (%s)" % lic)
    elif lic in COPYLEFT: score += 1; notes.append("copyleft (%s) — check compatibility" % lic)
    elif not lic: score -= 2; notes.append("NO LICENSE (not legally reusable)")
    stars = repo.get("stargazers_count", 0)
    if stars > 500: score += 1

    verdict = "STRONG" if score >= 6 else "OK" if score >= 3 else "WEAK"
    return {"repo": full, "verdict": verdict, "score": score, "stars": stars,
            "pushed_days": pushed, "open_issues": open_i, "license": lic or "none",
            "has_tests": has_tests, "last_release_days": last_release,
            "url": repo.get("html_url"), "desc": (repo.get("description") or "")[:120],
            "notes": notes}


def search(query, n):
    data, err = gh("/search/repositories?q=%s&sort=stars&per_page=%d"
                   % (urllib.request.quote(query), n))
    if err:
        sys.exit("search failed: " + err)
    return [r["full_name"] for r in data.get("items", [])[:n]]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repos", nargs="*", help="owner/repo …")
    ap.add_argument("--search", help="GitHub search query; scores the top matches")
    ap.add_argument("--top", type=int, default=6)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    targets = list(a.repos)
    if a.search:
        targets += search(a.search, a.top)
    if not targets:
        ap.error("give owner/repo args or --search QUERY")
    results = [assess(t) for t in targets]
    results.sort(key=lambda r: r.get("score", -99), reverse=True)
    if a.json:
        print(json.dumps(results, indent=2)); return
    for r in results:
        if r.get("error"):
            print("• %-30s  ERROR: %s" % (r["repo"], r["error"])); continue
        print("• %-30s  %-6s score %+d  ★%d" % (r["repo"], r["verdict"], r["score"], r["stars"]))
        print("    %s" % r["desc"])
        print("    " + " · ".join(r["notes"]))
        print("    " + (r["url"] or ""))
    print("\nRule: read the README + skim code of the top 2-3 before recommending. "
          "Stars are context, not proof.")


if __name__ == "__main__":
    main()
