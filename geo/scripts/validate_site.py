#!/usr/bin/env python3
"""Validate the technical foundations that AI and search crawlers depend on.

Checks the local working copy by default. Pass --live to also verify that the
deployed pages, robots.txt, sitemap.xml and the IndexNow key file respond.

Standard library only, so it runs anywhere Python 3 is available.

Usage:
    python3 geo/scripts/validate_site.py
    python3 geo/scripts/validate_site.py --live
"""

import argparse
import html
import json
import re
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

REPO = Path(__file__).resolve().parents[2]
ORIGIN = "https://sunbotcanada.github.io"
ORG_ID = ORIGIN + "/#organization"

failures = []
notes = []


def fail(msg):
    failures.append(msg)


def jsonld_blocks(text):
    """Yield (attributes, raw_json) for every JSON-LD script in a page."""
    pattern = r'<script type="application/ld\+json"([^>]*)>(.*?)</script>'
    for attrs, raw in re.findall(pattern, text, re.S):
        yield attrs, raw


def plain_text(fragment):
    """Replicate the plainText() helper in assets/js/faq-schema.js."""
    stripped = re.sub(r"<[^>]+>", "", fragment)
    return re.sub(r"\s+", " ", html.unescape(stripped)).strip()


def check_structured_data(pages):
    """Every JSON-LD block must parse, carry no raw HTML entities, and use unique @id values."""
    seen_ids = {}
    for page in pages:
        text = page.read_text(encoding="utf-8")
        for _, raw in jsonld_blocks(text):
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as exc:
                fail("%s: JSON-LD does not parse: %s" % (page.name, exc))
                continue

            # Entities are not decoded inside a script block, so they would be
            # read literally by consumers.
            for entity in set(re.findall(r"&(?:amp|lt|gt|quot|#39|nbsp);", raw)):
                fail("%s: HTML entity %r inside JSON-LD" % (page.name, entity))

            for node in data.get("@graph", [data]):
                node_id = node.get("@id")
                if not node_id:
                    continue
                if node_id in seen_ids and seen_ids[node_id] != page.name:
                    fail("%s: @id %s already defined in %s"
                         % (page.name, node_id, seen_ids[node_id]))
                seen_ids.setdefault(node_id, page.name)

    if ORG_ID not in seen_ids:
        fail("the %s entity is not defined on any page" % ORG_ID)
    else:
        notes.append("organization entity defined once, in %s" % seen_ids[ORG_ID])


def check_org_references(pages):
    """Pages that point at the organization must use the canonical @id, not a copy."""
    for page in pages:
        text = page.read_text(encoding="utf-8")
        if page.name == "index.html":
            continue
        if '"@type": "EducationalOrganization"' in text or '"@type": "Organization"' in text:
            fail("%s: redefines the organization instead of referencing %s"
                 % (page.name, ORG_ID))


def check_canonicals(pages):
    for page in pages:
        text = page.read_text(encoding="utf-8")
        match = re.search(r'<link rel="canonical" href="([^"]+)"', text)
        if not match:
            fail("%s: no canonical link" % page.name)
            continue
        expected = ORIGIN + "/" if page.name == "index.html" else "%s/%s" % (ORIGIN, page.name)
        if match.group(1) != expected:
            fail("%s: canonical is %s, expected %s" % (page.name, match.group(1), expected))
        if "noindex" in text:
            fail("%s: contains a noindex directive" % page.name)


def check_faq_parity():
    """The static FAQPage block must match what faq-schema.js builds from the DOM."""
    page = REPO / "faq.html"
    text = page.read_text(encoding="utf-8")
    match = re.search(r'<script type="application/ld\+json" id="faq-jsonld">(.*?)</script>',
                      text, re.S)
    if not match:
        fail("faq.html: static faq-jsonld fallback block is missing")
        return
    schema = [(q["name"], q["acceptedAnswer"]["text"])
              for q in json.loads(match.group(1))["mainEntity"]]

    visible = []
    body = text.split("<main", 1)[-1]
    for item in re.findall(r'<article class="faq-item">(.*?)</article>', body, re.S):
        question = re.search(r'<h3 class="faq-question">(.*?)</h3>', item, re.S)
        answer = re.search(r'<div class="faq-answer">(.*?)</div>\s*$', item, re.S)
        if question and answer:
            visible.append((plain_text(question.group(1)), plain_text(answer.group(1))))

    if len(schema) != len(visible):
        fail("faq.html: %d schema questions but %d visible items"
             % (len(schema), len(visible)))
        return
    for index, (from_schema, from_dom) in enumerate(zip(schema, visible)):
        if from_schema != from_dom:
            fail("faq.html: item %d differs between schema and visible text (%r)"
                 % (index, from_schema[0][:60]))
    notes.append("faq.html: %d questions, schema matches visible text" % len(schema))


def check_internal_links(pages):
    for page in pages:
        text = page.read_text(encoding="utf-8")
        for ref in re.findall(r'(?:href|src)="([^"]+)"', text):
            if ref.startswith(("http", "mailto:", "tel:", "sms:", "#", "data:")):
                continue
            target = ref.split("#")[0].split("?")[0]
            if target and not (REPO / target).exists():
                fail("%s: broken reference %s" % (page.name, ref))


def check_images(pages):
    """Missing dimensions cause layout shift; missing alt text hurts accessibility."""
    for page in pages:
        for tag in re.findall(r"<img[^>]*>", page.read_text(encoding="utf-8")):
            if 'src=""' in tag:
                continue  # lightbox placeholder, filled in by main.js
            missing = [attr for attr in ("width=", "height=", "alt=") if attr not in tag]
            if missing:
                src = re.search(r'src="([^"]*)"', tag)
                fail("%s: image %s missing %s"
                     % (page.name, src.group(1) if src else "?", ", ".join(missing)))


def check_sitemap_and_robots(pages):
    sitemap = (REPO / "sitemap.xml").read_text(encoding="utf-8")
    listed = set(re.findall(r"<loc>(.*?)</loc>", sitemap))

    for url in sorted(listed):
        name = url[len(ORIGIN):].lstrip("/") or "index.html"
        if not (REPO / name).exists():
            fail("sitemap.xml: %s does not exist in the repository" % url)

    for page in pages:
        expected = ORIGIN + "/" if page.name == "index.html" else "%s/%s" % (ORIGIN, page.name)
        if expected not in listed:
            fail("sitemap.xml: %s is missing" % expected)

    robots = (REPO / "robots.txt").read_text(encoding="utf-8")
    if "Sitemap: %s/sitemap.xml" % ORIGIN not in robots:
        fail("robots.txt: does not reference the canonical sitemap")
    if re.search(r"^\s*Disallow:\s*/\s*$", robots, re.M):
        fail("robots.txt: a blanket Disallow would block all crawlers")

    for agent in ("Googlebot", "Bingbot", "OAI-SearchBot", "PerplexityBot",
                  "Claude-SearchBot", "Applebot"):
        if "User-agent: %s" % agent not in robots:
            notes.append("robots.txt: %s not listed explicitly (allowed by wildcard)" % agent)

    notes.append("sitemap.xml lists %d URLs" % len(listed))


def check_live():
    paths = ["/", "/robots.txt", "/sitemap.xml", "/llms.txt", "/faq.html",
             "/courses.html", "/2755c0b1c44be636c12e0ef6010a75e0.txt"]
    for path in paths:
        url = ORIGIN + path
        try:
            request = Request(url, headers={"User-Agent": "SunBot-GEO-Validator"})
            with urlopen(request, timeout=20) as response:
                if response.status != 200:
                    fail("live: %s returned HTTP %s" % (url, response.status))
                else:
                    notes.append("live: %s -> 200" % path)
        except (HTTPError, URLError) as exc:
            fail("live: %s unreachable (%s)" % (url, exc))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true",
                        help="also check that the deployed site responds")
    args = parser.parse_args()

    pages = sorted(REPO.glob("*.html"))
    if not pages:
        print("no HTML pages found; run this from inside the repository")
        return 2

    check_structured_data(pages)
    check_org_references(pages)
    check_canonicals(pages)
    check_faq_parity()
    check_internal_links(pages)
    check_images(pages)
    check_sitemap_and_robots(pages)
    if args.live:
        check_live()

    print("Checked %d pages\n" % len(pages))
    for note in notes:
        print("  note: %s" % note)
    print()
    if failures:
        print("FAILED (%d)" % len(failures))
        for item in failures:
            print("  - %s" % item)
        return 1
    print("All checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
