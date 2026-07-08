#!/usr/bin/env python3
"""paper_search: query free, open-access paper sources and return a ranked,
deduplicated shortlist ready to drop into a research brief. Stdlib only, no keys.

Sources: arXiv (Atom API) + Semantic Scholar (Graph API, free tier). Both are free
and need no login. Semantic Scholar also yields free openAccessPdf links for many
papers that are paywalled at the publisher.

Usage:
  paper_search.py "graph neural network sampling" [--limit 15] [--since 2021] [--json]

Ranking = query-term overlap in title/abstract  +  log(citations)  +  recency bonus.
Never fabricate: if a source errors or returns nothing, it says so and uses the rest.
"""
import argparse, json, math, re, sys, time
import urllib.parse, urllib.request
from xml.etree import ElementTree as ET

UA = "claude-control-research (+local; respectful)"
ARXIV = "http://export.arxiv.org/api/query"
S2 = "https://api.semanticscholar.org/graph/v1/paper/search"


def _get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def norm_title(t):
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


def search_arxiv(query, limit):
    q = urllib.parse.urlencode({"search_query": "all:" + query, "start": 0,
                                "max_results": limit, "sortBy": "relevance"})
    out = []
    try:
        xml = _get(ARXIV + "?" + q)
    except Exception as e:
        print("  (arXiv unavailable: %s)" % e.__class__.__name__, file=sys.stderr)
        return out
    ns = {"a": "http://www.w3.org/2005/Atom"}
    for e in ET.fromstring(xml).findall("a:entry", ns):
        title = (e.findtext("a:title", "", ns) or "").strip().replace("\n", " ")
        summ = (e.findtext("a:summary", "", ns) or "").strip().replace("\n", " ")
        published = e.findtext("a:published", "", ns) or ""
        year = int(published[:4]) if published[:4].isdigit() else 0
        authors = [a.findtext("a:name", "", ns) for a in e.findall("a:author", ns)]
        pdf = ""
        for link in e.findall("a:link", ns):
            if link.get("title") == "pdf" or link.get("type") == "application/pdf":
                pdf = link.get("href", "")
        out.append({"title": title, "abstract": summ, "year": year, "citations": None,
                    "authors": authors[:6], "url": e.findtext("a:id", "", ns), "pdf": pdf,
                    "venue": "arXiv", "source": "arXiv"})
    return out


def search_s2(query, limit):
    fields = "title,abstract,year,citationCount,venue,authors,externalIds,openAccessPdf,url"
    q = urllib.parse.urlencode({"query": query, "limit": limit, "fields": fields})
    out = []
    try:
        data = json.loads(_get(S2 + "?" + q))
    except Exception as e:
        print("  (Semantic Scholar unavailable: %s — arXiv only)" % e.__class__.__name__, file=sys.stderr)
        return out
    for p in data.get("data", []) or []:
        pdf = (p.get("openAccessPdf") or {}).get("url", "") or ""
        out.append({"title": p.get("title") or "", "abstract": p.get("abstract") or "",
                    "year": p.get("year") or 0, "citations": p.get("citationCount"),
                    "authors": [a.get("name") for a in (p.get("authors") or [])][:6],
                    "url": p.get("url") or "", "pdf": pdf,
                    "venue": p.get("venue") or "", "source": "Semantic Scholar"})
    return out


def merge(lists):
    by_title = {}
    for lst in lists:
        for p in lst:
            k = norm_title(p["title"])
            if not k:
                continue
            if k in by_title:
                cur = by_title[k]
                cur["citations"] = cur["citations"] if cur["citations"] is not None else p["citations"]
                if not cur["pdf"]:
                    cur["pdf"] = p["pdf"]
                if cur["source"] != p["source"]:
                    cur["source"] = cur["source"] + " + " + p["source"]
                if not cur["abstract"]:
                    cur["abstract"] = p["abstract"]
            else:
                by_title[k] = dict(p)
    return list(by_title.values())


def score(p, terms, this_year):
    hay = (p["title"] + " " + (p["abstract"] or "")).lower()
    overlap = sum(1 for t in terms if t in hay) / max(len(terms), 1)
    cites = p["citations"] or 0
    cite_bonus = math.log10(cites + 1)
    recency = 0.5 if p["year"] and p["year"] >= this_year - 2 else 0.0
    return overlap * 3 + cite_bonus + recency


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query")
    ap.add_argument("--limit", type=int, default=15, help="results to fetch per source")
    ap.add_argument("--since", type=int, default=0, help="drop papers older than this year")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    terms = [t for t in norm_title(a.query).split() if len(t) > 2]
    this_year = time.gmtime().tm_year
    papers = merge([search_s2(a.query, a.limit), search_arxiv(a.query, a.limit)])
    if a.since:
        papers = [p for p in papers if not p["year"] or p["year"] >= a.since]
    papers.sort(key=lambda p: -score(p, terms, this_year))
    if not papers:
        print("No results. Try broader terms, or search ACL Anthology / PubMed via the web.")
        return
    if a.json:
        print(json.dumps(papers, indent=2))
        return
    print("# Ranked candidates for: %s   (%d found, free sources)\n" % (a.query, len(papers)))
    for i, p in enumerate(papers[:a.limit], 1):
        cites = "n/a" if p["citations"] is None else str(p["citations"])
        line = "%2d. %s (%s%s) — cites %s [%s]" % (
            i, p["title"], p["year"] or "?",
            ", " + p["venue"] if p["venue"] and p["venue"] != "arXiv" else "", cites, p["source"])
        print(line)
        if p["authors"]:
            print("    " + ", ".join(a2 for a2 in p["authors"] if a2))
        if p["pdf"]:
            print("    free PDF: " + p["pdf"])
        elif p["url"]:
            print("    " + p["url"])
    print("\nNext: read the top abstracts, then synthesize into the brief template in SKILL.md "
          "(never cite a paper you haven't opened).")


if __name__ == "__main__":
    main()
