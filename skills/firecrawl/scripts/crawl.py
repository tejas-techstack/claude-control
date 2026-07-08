#!/usr/bin/env python3
"""claude-control local crawler: fetch/crawl/map -> markdown-ish text. Stdlib only.
Usage:
  crawl.py fetch URL [-o out.md]
  crawl.py crawl URL [--limit N] [--same-host] [--prefix PATH] [-d OUTDIR]
  crawl.py map URL
Respects robots.txt; 1 request/second; honest User-Agent."""
import sys, re, time, argparse, urllib.request, urllib.parse, urllib.robotparser
from html.parser import HTMLParser
from pathlib import Path

UA = "claude-control-crawler (+https://github.com/; local, respectful)"
SKIP_TAGS = {"script", "style", "nav", "header", "footer", "aside", "noscript", "svg", "form"}
BLOCK_TAGS = {"p", "div", "section", "article", "li", "br", "tr", "pre", "blockquote"}

class Extract(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts, self.links, self.skip, self.title = [], [], 0, ""
        self._in_title = False; self._h = 0
    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS: self.skip += 1
        if tag == "title": self._in_title = True
        if tag == "a":
            for k, v in attrs:
                if k == "href" and v: self.links.append(v)
        if re.fullmatch(r"h[1-6]", tag): self._h = int(tag[1]); self.parts.append("\n\n" + "#" * self._h + " ")
        elif tag in BLOCK_TAGS: self.parts.append("\n")
        elif tag == "code" and self.skip == 0: self.parts.append("`")
    def handle_endtag(self, tag):
        if tag in SKIP_TAGS and self.skip: self.skip -= 1
        if tag == "title": self._in_title = False
        if re.fullmatch(r"h[1-6]", tag): self._h = 0; self.parts.append("\n")
        if tag == "code" and self.skip == 0: self.parts.append("`")
    def handle_data(self, data):
        if self._in_title: self.title += data.strip()
        if self.skip == 0 and data.strip(): self.parts.append(data)

def clean(text):
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()

def allowed(url):
    p = urllib.parse.urlparse(url)
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(f"{p.scheme}://{p.netloc}/robots.txt")
    try: rp.read()
    except Exception: return True
    return rp.can_fetch(UA, url)

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        ct = r.headers.get("Content-Type", "")
        if "html" not in ct and "text" not in ct: return None, []
        html = r.read().decode(r.headers.get_content_charset() or "utf-8", "replace")
    ex = Extract(); ex.feed(html)
    body = f"# {ex.title}\n\nSource: {url}\n\n" + clean("".join(ex.parts))
    return body, [urllib.parse.urljoin(url, l) for l in ex.links]

def slug(url):
    p = urllib.parse.urlparse(url)
    s = re.sub(r"[^a-zA-Z0-9]+", "-", (p.netloc + p.path)).strip("-")[:80]
    return s or "index"

def cmd_fetch(a):
    if not allowed(a.url): sys.exit(f"robots.txt disallows fetching {a.url}; not proceeding.")
    body, _ = get(a.url)
    if body is None: sys.exit("Not an HTML/text page.")
    if a.out: Path(a.out).write_text(body); print(f"saved {a.out} ({len(body)//4} approx tokens)")
    else: print(body)

def cmd_crawl(a):
    start = a.url; host = urllib.parse.urlparse(start).netloc
    outdir = Path(a.dir); outdir.mkdir(exist_ok=True)
    seen, queue, saved = set(), [start], 0
    while queue and saved < a.limit:
        url = queue.pop(0).split("#")[0]
        if url in seen or not url.startswith("http"): continue
        seen.add(url)
        p = urllib.parse.urlparse(url)
        if a.same_host and p.netloc != host: continue
        if a.prefix and not p.path.startswith(a.prefix): continue
        if not allowed(url): print(f"skip (robots): {url}"); continue
        try: body, links = get(url)
        except Exception as e: print(f"skip ({e.__class__.__name__}): {url}"); continue
        if body is None: continue
        f = outdir / f"{slug(url)}.md"; f.write_text(body); saved += 1
        print(f"[{saved}/{a.limit}] {url} -> {f}")
        queue.extend(l for l in links if l not in seen)
        time.sleep(1.0)
    print(f"done: {saved} pages in {outdir}/")

def cmd_map(a):
    p = urllib.parse.urlparse(a.url)
    for path in ("/sitemap.xml", "/sitemap_index.xml"):
        sm = f"{p.scheme}://{p.netloc}{path}"
        try:
            req = urllib.request.Request(sm, headers={"User-Agent": UA})
            xml = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "replace")
        except Exception: continue
        urls = re.findall(r"<loc>\s*(.*?)\s*</loc>", xml)
        if urls:
            print(f"# sitemap: {sm} ({len(urls)} urls)"); print("\n".join(urls[:500])); return
    print("No sitemap found; use: crawl.py crawl URL --same-host")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch"); f.add_argument("url"); f.add_argument("-o", "--out"); f.set_defaults(fn=cmd_fetch)
    c = sub.add_parser("crawl"); c.add_argument("url"); c.add_argument("--limit", type=int, default=30)
    c.add_argument("--same-host", action="store_true"); c.add_argument("--prefix", default="")
    c.add_argument("-d", "--dir", default=".crawl"); c.set_defaults(fn=cmd_crawl)
    m = sub.add_parser("map"); m.add_argument("url"); m.set_defaults(fn=cmd_map)
    a = ap.parse_args(); a.fn(a)
