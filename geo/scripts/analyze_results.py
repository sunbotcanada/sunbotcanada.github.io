#!/usr/bin/env python3
"""Summarise recorded GEO observations.

Reads geo/results.csv and reports how often SunBot appears, broken down by
platform, by query category and by individual query. Platforms are taken from
the data rather than a fixed list, so new ones need no code change.

Usage:
    python3 geo/scripts/analyze_results.py
    python3 geo/scripts/analyze_results.py --since 2026-11-01
"""

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

GEO = Path(__file__).resolve().parents[1]
QUERIES = GEO / "queries.csv"
RESULTS = GEO / "results.csv"


def load():
    if not RESULTS.exists():
        return [], {}
    with RESULTS.open(newline="", encoding="utf-8") as handle:
        results = list(csv.DictReader(handle))
    with QUERIES.open(newline="", encoding="utf-8") as handle:
        queries = {row["id"]: row for row in csv.DictReader(handle)}
    return results, queries


def rate(rows):
    """Share of answered observations where SunBot was mentioned.

    'refused' and 'error' are excluded: they mean the platform gave no local
    recommendation at all, which is not the same as recommending a competitor.
    """
    answered = [r for r in rows if r["outcome"] in ("mentioned", "not_mentioned")]
    if not answered:
        return None, 0, len(rows)
    hits = sum(1 for r in answered if r["outcome"] == "mentioned")
    return hits / len(answered), hits, len(answered)


def group(rows, key):
    buckets = defaultdict(list)
    for row in rows:
        buckets[key(row)].append(row)
    return buckets


def format_rate(value, hits, total):
    if value is None:
        return "no answered observations"
    return "%3.0f%%  (%d of %d)" % (value * 100, hits, total)


def summarise(results, queries, since=None):
    """Build the report body as a list of lines, shared with generate_report.py."""
    if since:
        results = [r for r in results if r["checked_on"] >= since]

    lines = []
    if not results:
        lines.append("No observations recorded yet.")
        lines.append("")
        lines.append("Run: python3 geo/scripts/record_results.py --platform chatgpt")
        return lines

    dates = sorted({r["checked_on"] for r in results})
    overall, hits, total = rate(results)

    lines.append("Observations: %d across %d dates (%s to %s)"
                 % (len(results), len(dates), dates[0], dates[-1]))
    lines.append("Overall visibility: %s" % format_rate(overall, hits, total))
    lines.append("")

    lines.append("By platform")
    for platform, rows in sorted(group(results, lambda r: r["platform"]).items()):
        lines.append("  %-14s %s" % (platform, format_rate(*rate(rows))))
    lines.append("")

    lines.append("By category")
    by_category = group(results,
                        lambda r: queries.get(r["query_id"], {}).get("category", "unknown"))
    for category, rows in sorted(by_category.items()):
        lines.append("  %-26s %s" % (category, format_rate(*rate(rows))))
    lines.append("")

    lines.append("Queries where SunBot was never mentioned")
    gaps = []
    for query_id, rows in sorted(group(results, lambda r: r["query_id"]).items()):
        value, _, answered = rate(rows)
        if value == 0 and answered:
            text = queries.get(query_id, {}).get("query", query_id)
            gaps.append("  [%s] %s" % (query_id, text))
    lines.extend(gaps or ["  none"])
    lines.append("")

    cited = [r["cited_url"] for r in results if r.get("cited_url")]
    if cited:
        lines.append("Most cited pages")
        counts = defaultdict(int)
        for url in cited:
            counts[url] += 1
        for url, count in sorted(counts.items(), key=lambda kv: -kv[1]):
            lines.append("  %2d  %s" % (count, url))
        lines.append("")

    return lines


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--since", help="only include observations on or after this date")
    args = parser.parse_args()

    results, queries = load()
    for line in summarise(results, queries, args.since):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
