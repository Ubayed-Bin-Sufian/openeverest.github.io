#!/usr/bin/env python3
"""Post-process the MkDocs builds in assets/documentation/<version>/ for SEO.

MkDocs is built with an unversioned `site_url`, so every page ships with a
canonical such as /documentation/index.html (a 404) or, for builds that predate
the OpenEverest rename, https://docs.percona.com/everest/... This script
rewrites, in place and idempotently:

* <link rel="canonical"> and og:url -> the page's own versioned URL. Pages of
  the latest stable release (which `current/` is a copy of) point to their
  /documentation/current/ equivalent so ranking accrues on a URL that survives
  releases.
* <title>/og:title -> bare "<Brand>" home titles become "<Brand> Documentation";
  versions other than current get the version appended to keep them distinct.
* <meta name="description"> -> the page's first paragraph instead of the
  generic "Documentation".
* sitemap.xml(.gz) -> versioned URLs, so Hugo can merge them into /sitemap.xml.

Run after every docs import (hack/import_docs.sh does this automatically):

    hack/fix_docs_seo.py [assets/documentation]
"""

import gzip
import html
import os
import re
import sys
from urllib.parse import quote, unquote

SITE = "https://openeverest.io/documentation/"
BRANDS = ("OpenEverest", "Percona Everest")
DESC_MAX = 160

BRAND_RE = "|".join(re.escape(b) for b in BRANDS)
VERSION_RE = r"[0-9][0-9A-Za-z.\-]*"
CANONICAL_RE = re.compile(r'<link rel="canonical" href="[^"]*">')
OG_URL_RE = re.compile(r'<meta property="og:url" content="[^"]*"\s*/?>')
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)
OG_TITLE_RE = re.compile(r'(<meta property="og:title" content=")([^"]*)(")')
DESC_RE = re.compile(r'<meta name="description" content="[^"]*">')
ARTICLE_RE = re.compile(r'<article class="md-content__inner md-typeset">(.*?)</article>', re.S)
PARA_RE = re.compile(r"<p>(.*?)</p>", re.S)
TAG_RE = re.compile(r"<[^>]+>")
SUFFIX_RE = re.compile(rf"^(?:(.*) - )?({BRAND_RE})(?: {VERSION_RE})?(?: Documentation)?$")
LOC_RE = re.compile(r"<loc>([^<]*)</loc>")
OLD_PREFIXES = ("https://docs.percona.com/everest/", "https://openeverest.io/documentation/")


def version_key(v):
    return [int(p) for p in v.split(".")]


def latest_stable(versions):
    stable = [v for v in versions if re.fullmatch(r"\d+(\.\d+)*", v)]
    return max(stable, key=version_key) if stable else None


def page_url(base, rel):
    rel = rel.replace(os.sep, "/")
    if rel == "index.html":
        return base
    if rel.endswith("/index.html"):
        rel = rel[: -len("index.html")]
    return base + quote(rel, safe="/")


def fix_title(title, label):
    m = SUFFIX_RE.match(html.unescape(title).strip())
    if not m:
        return title
    page, brand = m.group(1), m.group(2)
    branded = f"{brand} {label}" if label else brand
    return html.escape(f"{page} - {branded}" if page else f"{branded} Documentation", quote=False)


def describe(content, fallback):
    article = ARTICLE_RE.search(content)
    if article:
        for p in PARA_RE.findall(article.group(1)):
            text = re.sub(r"\s+", " ", html.unescape(TAG_RE.sub("", p))).strip()
            if len(text) >= 40:
                if len(text) > DESC_MAX:
                    text = text[: DESC_MAX - 1].rsplit(" ", 1)[0].rstrip(",.;:") + "…"
                return text
    return fallback


def fix_html(path, url, label):
    with open(path, encoding="utf-8") as f:
        content = f.read()
    orig = content

    content = CANONICAL_RE.sub(f'<link rel="canonical" href="{url}">', content, count=1)
    content = OG_URL_RE.sub(f'<meta property="og:url" content="{url}">', content, count=1)

    title_m = TITLE_RE.search(content)
    if title_m:
        new_title = fix_title(title_m.group(1), label)
        content = content[: title_m.start(1)] + new_title + content[title_m.end(1) :]
        content = OG_TITLE_RE.sub(lambda m: m.group(1) + html.escape(html.unescape(new_title)) + m.group(3), content, count=1)
        page_title = html.unescape(new_title)
    else:
        page_title = "OpenEverest documentation"

    desc = describe(content, f"{page_title}.")
    content = DESC_RE.sub(lambda _: f'<meta name="description" content="{html.escape(desc)}">', content, count=1)

    if content != orig:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def fix_sitemap(vdir, self_base):
    path = os.path.join(vdir, "sitemap.xml")
    if not os.path.isfile(path):
        return

    def relocate(m):
        loc = m.group(1)
        rel = loc
        for prefix in (self_base, *OLD_PREFIXES):
            if loc.startswith(prefix):
                rel = loc[len(prefix) :]
                break
        return f"<loc>{page_url(self_base, unquote(rel) or 'index.html')}</loc>"

    with open(path, encoding="utf-8") as f:
        content = f.read()
    new = LOC_RE.sub(relocate, content)
    if new != content:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new)
    gz = path + ".gz"
    if os.path.isfile(gz):
        with gzip.open(gz, "rt", encoding="utf-8") as f:
            if f.read() == new:
                return
        with gzip.GzipFile(gz, "wb", mtime=0) as f:
            f.write(new.encode("utf-8"))


def main():
    root = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "assets", "documentation"))
    versions = sorted(d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d)))
    stable = latest_stable([v for v in versions if v != "current"])

    changed = 0
    for v in versions:
        vdir = os.path.join(root, v)
        self_base = f"{SITE}{v}/"
        is_current = v in ("current", stable)
        canonical_base = f"{SITE}current/" if is_current else self_base
        label = "" if is_current else v

        for dirpath, _, files in os.walk(vdir):
            for name in files:
                if not name.endswith(".html") or name == "404.html":
                    continue
                path = os.path.join(dirpath, name)
                url = page_url(canonical_base, os.path.relpath(path, vdir))
                changed += fix_html(path, url, label)
        fix_sitemap(vdir, self_base)

    print(f"fix_docs_seo: {len(versions)} versions, latest stable {stable}, {changed} HTML files updated")


if __name__ == "__main__":
    main()
