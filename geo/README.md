# GEO monitoring

Tracks two separate things:

1. **Is the site technically retrievable** by search and AI crawlers. Automated.
2. **Is SunBot actually recommended** when parents ask AI assistants. Manual.

The second part is manual on purpose. There is no dependable API for observing what
ChatGPT, Gemini, Perplexity, Copilot, Claude or Grok say to a given parent, and answers
differ by user, session, account history and region. Anything claiming to automate it
produces numbers that cannot be reproduced. Recording a small number of honest
observations by hand is more useful than a large table of unreliable ones.

## Layout

```text
geo/
├── queries.csv          the parent question bank being monitored
├── results.csv          observations, created on first use
├── README.md
├── scripts/
│   ├── validate_site.py     technical checks on the site itself
│   ├── record_results.py    enter what an assistant answered
│   ├── analyze_results.py   visibility rates by platform, category and query
│   └── generate_report.py   dated Markdown report combining both
└── reports/             generated reports
```

## Usage

Everything is Python 3 standard library, run from the repository root. No installs.

Check the site is sound, before and after content changes:

```bash
python3 geo/scripts/validate_site.py
python3 geo/scripts/validate_site.py --live    # also check the deployed URLs
```

This verifies that every JSON-LD block parses, the organization entity is defined exactly
once and referenced by `@id` elsewhere, canonicals are correct and no page carries
`noindex`, the FAQ schema matches the visible text one-to-one, internal links resolve,
images have dimensions and alt text, and `sitemap.xml` and `robots.txt` agree with the
pages that exist. It exits non-zero on failure, so it can gate a commit.

Record observations after running queries on a platform:

```bash
python3 geo/scripts/record_results.py --platform chatgpt
python3 geo/scripts/record_results.py --platform gemini --priority high
```

It walks through `queries.csv` and asks what you saw. Press Enter to skip a query.
For one-off entries, pass `--query-id` and `--outcome` directly.

Review and report:

```bash
python3 geo/scripts/analyze_results.py
python3 geo/scripts/generate_report.py
```

## Reading the numbers

`outcome` is one of:

- `mentioned` — SunBot named in the answer
- `not_mentioned` — a local answer was given, SunBot absent
- `refused` — the assistant declined or gave no local recommendation
- `error` — platform unavailable

Visibility rate counts `mentioned` against `mentioned + not_mentioned` only. A refusal
is not a loss to a competitor, so folding it into the denominator would understate
performance.

A single observation means little. Look for a query that is consistently missed across
several dates and platforms: that usually points at a real content gap, which is
something the site can fix.

## Suggested cadence

Monthly is enough; these systems change slowly. Worth an extra run after a significant
content change, and after any update to the Google Business Profile or Nextdoor page.
Start with the `high` priority queries if time is short.

## What actually moves the needle

On-site work is necessary but not sufficient. For geographic queries such as "robotics
classes in southwest Edmonton", assistants lean heavily on off-site signals they can
cross-reference, so consistency matters more than volume:

- The business name, service area and website URL should read identically on the site,
  the Google Business Profile listing (`SunBot Kids Robotics & STEM Education`) and
  Nextdoor. The `sameAs` array in the homepage schema links these together.
- Genuine Google reviews are the strongest local trust signal. Do not script, buy or
  template them.
- Answer questions in the words parents use, directly, in visible HTML. An assistant can
  only quote text it can retrieve.

Do not attempt to manipulate assistant output through hidden text, prompt injection,
cloaking, doorway pages or fabricated facts. Beyond being against platform policies,
inconsistent claims make an entity harder to verify and so less likely to be cited.
