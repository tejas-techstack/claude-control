#!/usr/bin/env python3
"""fc_api: a tiny stdlib client for a Firecrawl API — your self-hosted instance by
default (free, no SDK, no pip). Talks the v1 endpoints scrape/map/crawl and prints
clean markdown, so /firecrawl can use the strong engine started by firecrawl_selfhost.sh.

Usage:
  fc_api.py scrape URL [-o out.md]
  fc_api.py map URL [--limit N]
  fc_api.py crawl URL [--limit N] [-d OUTDIR] [--timeout SEC]

Config (env):
  FIRECRAWL_API_URL   base URL, default http://localhost:3002
  FIRECRAWL_API_KEY   bearer token; self-host with auth off ignores it (default "local")

Self-host has no key and no usage cap — the free path. Point FIRECRAWL_API_URL at the
hosted service only if the user has their own key and explicitly opts in.
"""
import argparse, json, os, re, sys, time, urllib.request, urllib.error
from pathlib import Path

BASE = os.environ.get("FIRECRAWL_API_URL", "http://localhost:3002").rstrip("/")
KEY = os.environ.get("FIRECRAWL_API_KEY", "local")


def call(path, payload=None, method="POST"):
    url = BASE + path
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json",
                                          "Authorization": "Bearer " + KEY})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:300]
        sys.exit("Firecrawl API %s on %s — %s\nIs it running? Start it with "
                 "firecrawl_selfhost.sh up" % (e.code, url, body))
    except urllib.error.URLError as e:
        sys.exit("Cannot reach Firecrawl at %s (%s). Start it with firecrawl_selfhost.sh up, "
                 "or set FIRECRAWL_API_URL." % (BASE, e.reason))


def slug(url):
    return re.sub(r"[^a-zA-Z0-9]+", "-", url).strip("-")[:80] or "page"


def cmd_scrape(a):
    d = call("/v1/scrape", {"url": a.url, "formats": ["markdown"]})
    md = (d.get("data") or {}).get("markdown") or d.get("markdown") or ""
    if not md:
        sys.exit("no markdown returned: " + json.dumps(d)[:300])
    if a.out:
        Path(a.out).write_text(md); print("saved %s (~%d tokens)" % (a.out, len(md) // 4))
    else:
        print(md)


def cmd_map(a):
    d = call("/v1/map", {"url": a.url, "limit": a.limit})
    links = d.get("links") or d.get("data") or []
    links = [l.get("url") if isinstance(l, dict) else l for l in links]
    print("# map: %s (%d urls)" % (a.url, len(links)))
    print("\n".join(links[:a.limit]))


def cmd_crawl(a):
    d = call("/v1/crawl", {"url": a.url, "limit": a.limit,
                           "scrapeOptions": {"formats": ["markdown"]}})
    cid = d.get("id") or d.get("jobId")
    if not cid:
        sys.exit("crawl did not start: " + json.dumps(d)[:300])
    out = Path(a.dir); out.mkdir(exist_ok=True)
    print("crawl %s started (id %s); polling…" % (a.url, cid))
    deadline = time.time() + a.timeout
    while time.time() < deadline:
        s = call("/v1/crawl/" + cid, method="GET")
        status, docs = s.get("status"), s.get("data") or []
        if status in ("completed", "failed") or (status == "scraping" and len(docs) >= a.limit):
            saved = 0
            for doc in docs:
                md = doc.get("markdown") or ""
                url = (doc.get("metadata") or {}).get("sourceURL") or doc.get("url") or ("doc%d" % saved)
                if md:
                    (out / (slug(url) + ".md")).write_text(md); saved += 1
            print("done: status=%s, %d pages saved in %s/" % (status, saved, out)); return
        print("  … %s (%d pages so far)" % (status, len(docs))); time.sleep(3)
    print("timed out after %ss; the job may still be running (id %s)." % (a.timeout, cid))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scrape"); s.add_argument("url"); s.add_argument("-o", "--out"); s.set_defaults(fn=cmd_scrape)
    m = sub.add_parser("map"); m.add_argument("url"); m.add_argument("--limit", type=int, default=200); m.set_defaults(fn=cmd_map)
    c = sub.add_parser("crawl"); c.add_argument("url"); c.add_argument("--limit", type=int, default=30)
    c.add_argument("-d", "--dir", default=".crawl"); c.add_argument("--timeout", type=int, default=300); c.set_defaults(fn=cmd_crawl)
    args = ap.parse_args(); args.fn(args)
