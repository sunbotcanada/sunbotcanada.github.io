#!/usr/bin/env python3
"""Submit the canonical URLs listed in sitemap.xml to IndexNow.

IndexNow notifies Bing, Yandex, Seznam and Naver that content changed.
The key is public by design because it must be readable at the site root.

Usage:
    python3 .github/scripts/indexnow_submit.py            # submit
    python3 .github/scripts/indexnow_submit.py --dry-run  # print payload only
"""

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

INDEXNOW_ENDPOINT = "https://api.indexnow.org/IndexNow"
SITE_HOST = "sunbotcanada.github.io"
INDEXNOW_KEY = "2755c0b1c44be636c12e0ef6010a75e0"


def read_sitemap_urls(sitemap_path: Path) -> list[str]:
    """Return the <loc> values from the sitemap, preserving document order."""
    urls = re.findall(r"<loc>\s*(.*?)\s*</loc>", sitemap_path.read_text(encoding="utf-8"))
    if not urls:
        raise SystemExit(f"No <loc> entries found in {sitemap_path}")
    return urls


def build_payload(urls: list[str]) -> dict:
    return {
        "host": SITE_HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": f"https://{SITE_HOST}/{INDEXNOW_KEY}.txt",
        "urlList": urls,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sitemap", default="sitemap.xml", help="Path to sitemap.xml")
    parser.add_argument("--dry-run", action="store_true", help="Print the payload without submitting")
    args = parser.parse_args()

    urls = read_sitemap_urls(Path(args.sitemap))
    payload = build_payload(urls)

    if args.dry_run:
        print(json.dumps(payload, indent=2))
        return 0

    request = urllib.request.Request(
        INDEXNOW_ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        print(f"IndexNow responded {response.status} for {len(urls)} URLs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
