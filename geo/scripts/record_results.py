#!/usr/bin/env python3
"""Record whether SunBot appeared in an AI assistant's answer to a parent query.

There is no reliable API for observing assistant answers across platforms, so
observations are entered by hand. Run a query on a platform, read the answer,
then record what you saw. Results append to geo/results.csv.

Usage:
    # walk through every query for one platform
    python3 geo/scripts/record_results.py --platform chatgpt

    # only the high priority queries
    python3 geo/scripts/record_results.py --platform gemini --priority high

    # record a single observation without prompts
    python3 geo/scripts/record_results.py --platform perplexity --query-id L01 \
        --outcome mentioned --rank 2 --cited-url https://sunbotcanada.github.io/
"""

import argparse
import csv
import datetime
import sys
from pathlib import Path

GEO = Path(__file__).resolve().parents[1]
QUERIES = GEO / "queries.csv"
RESULTS = GEO / "results.csv"

FIELDS = ["checked_on", "query_id", "platform", "outcome", "rank", "cited_url", "notes"]

PLATFORMS = [
    "chatgpt",     # ChatGPT Search, OpenAI
    "gemini",      # Google Gemini
    "ai_overview", # Google AI Overviews / AI Mode
    "perplexity",  # Perplexity AI
    "copilot",     # Microsoft Copilot and Bing
    "claude",      # Claude, Anthropic
    "grok",        # Grok, xAI
]

OUTCOMES = [
    "mentioned",      # SunBot named in the answer
    "not_mentioned",  # answer given, SunBot absent
    "refused",        # assistant declined or gave no local recommendation
    "error",          # platform unavailable or query failed
]


def load_queries(priority=None, category=None):
    with QUERIES.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if priority:
        rows = [r for r in rows if r["priority"] == priority]
    if category:
        rows = [r for r in rows if r["category"].lower() == category.lower()]
    return rows


def append(rows):
    is_new = not RESULTS.exists()
    with RESULTS.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        if is_new:
            writer.writeheader()
        for row in rows:
            writer.writerow(row)


def ask(query, platform, today):
    """Prompt for one observation. Returns None if the user skips."""
    print("\n" + "-" * 72)
    print("[%s] %s" % (query["id"], query["query"]))
    print("category: %s | priority: %s" % (query["category"], query["priority"]))
    print("Run this on %s, then record the result." % platform)
    print("outcomes: " + ", ".join("%d=%s" % (i + 1, o) for i, o in enumerate(OUTCOMES)))

    choice = input("outcome (1-4, or Enter to skip): ").strip()
    if not choice:
        return None
    try:
        outcome = OUTCOMES[int(choice) - 1]
    except (ValueError, IndexError):
        print("  not a valid choice, skipping")
        return None

    rank, cited = "", ""
    if outcome == "mentioned":
        rank = input("position in the list of suggestions (Enter if unranked): ").strip()
        cited = input("URL the assistant cited (Enter if none): ").strip()
    notes = input("notes (optional): ").strip()

    return {
        "checked_on": today,
        "query_id": query["id"],
        "platform": platform,
        "outcome": outcome,
        "rank": rank,
        "cited_url": cited,
        "notes": notes,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--platform", required=True, choices=PLATFORMS)
    parser.add_argument("--query-id", help="record one query instead of walking all")
    parser.add_argument("--outcome", choices=OUTCOMES, help="non-interactive outcome")
    parser.add_argument("--rank", default="", help="position among suggestions")
    parser.add_argument("--cited-url", default="", help="URL the assistant cited")
    parser.add_argument("--notes", default="", help="free-text notes")
    parser.add_argument("--priority", choices=["high", "medium", "low"])
    parser.add_argument("--category", help="filter by category, for example Location")
    parser.add_argument("--date", help="observation date, defaults to today (YYYY-MM-DD)")
    args = parser.parse_args()

    today = args.date or datetime.date.today().isoformat()
    queries = load_queries(args.priority, args.category)
    if not queries:
        print("no queries matched the filters")
        return 1

    # Non-interactive single record.
    if args.outcome:
        if not args.query_id:
            print("--outcome also requires --query-id")
            return 2
        if args.query_id not in {q["id"] for q in queries}:
            print("unknown query id: %s" % args.query_id)
            return 2
        append([{
            "checked_on": today,
            "query_id": args.query_id,
            "platform": args.platform,
            "outcome": args.outcome,
            "rank": args.rank,
            "cited_url": args.cited_url,
            "notes": args.notes,
        }])
        print("recorded %s / %s / %s" % (args.query_id, args.platform, args.outcome))
        return 0

    if args.query_id:
        queries = [q for q in queries if q["id"] == args.query_id]
        if not queries:
            print("unknown query id: %s" % args.query_id)
            return 2

    print("Recording %d queries for %s on %s" % (len(queries), args.platform, today))
    collected = []
    for query in queries:
        try:
            row = ask(query, args.platform, today)
        except (KeyboardInterrupt, EOFError):
            print("\nstopped early")
            break
        if row:
            collected.append(row)

    if collected:
        append(collected)
        print("\nSaved %d observations to %s" % (len(collected), RESULTS))
    else:
        print("\nnothing recorded")
    return 0


if __name__ == "__main__":
    sys.exit(main())
