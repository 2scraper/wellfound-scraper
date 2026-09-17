# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/) as
closely as a CLI toolkit can. **A patch release means "fixes", not "no flag
moved"** — a default that changes behaviour can ship in a patch, and when one
does it leads the release notes rather than being discovered from a bill.

## [Unreleased]

## [0.1.0] — 2026-09-17

First release. Everything below was measured on 2026-09-17 unless a different
date is given.

### Added

- **Three modes.** `--mode role` reads a `/role/{r}`, `/role/r/{r}` or
  `/role/l/{r}/{loc}` landing page and paginates; `--mode jobs` reads the
  `/jobs` discovery feed; `--mode job` reads one `/jobs/{id}-{slug}` page.
  `--role`, `--location` and `--remote` build a landing URL so a run needs no
  hand-assembled address.
- **Four fetchers.** `playwright_scraper.py` (primary, with `--concurrency`),
  `selenium_scraper.py`, `puppeteer_scraper.py`, and `scraper_api_client.py`
  for the 2Captcha Scraper API. All three browser engines were run live
  against the same listing and returned **byte-identical rows** — the same 52
  skus, the same 38 columns, the same `position` on every row, and identical
  sidecars.
- **38-column `JobPosting` row**, carrying the family prefix (`source`,
  `scraped_at`, `url`, `sku`, `title`) unchanged, plus the company's size,
  badges and tagline, the salary AND equity ranges, the remote configuration
  and the full job description.
- **Compensation parsing** for the nine shapes measured across 312 non-null
  values, including `₹30L – ₹80L` (the Indian lakh, 1e5 — not 30 to 80),
  `0.5% – 1.0%` with no salary at all, and `No equity` as a statement rather
  than a missing value.
- **`data_source` provenance column** (`apollo` / `jsonld`), because a
  landing page and a job page publish through different mechanisms and
  neither is a subset of the other. `diff_runs.py` reports a difference that
  comes with a source difference as `source_changed`.
- **349 offline checks**, with fixtures cut from real captures and verified
  to parse identically to their untrimmed originals.

### Notes on the site, which decide how this repo is built

- **Gating is per ROUTE.** From a residential US exit, three requests each:
  `/`, `/jobs`, every `/role/…` shape and `/jobs/{id}-{slug}` answered 200
  every time; `/company/{slug}` answered 403 every time, to plain HTTP and to
  a real Chromium on that same exit. There is no `--mode company`, because
  there is nothing this repo can honestly offer for it.
- **A datacenter address gets nothing.** Every route was refused from a
  Hetzner VPS, `robots.txt` included, to plain HTTP and to headless and
  headful Chromium alike (0 of 1 each). A residential exit is not optional.
- **The obvious challenge marker is inverted on this site.**
  `challenges.cloudflare.com` appears once on every page Wellfound SERVES —
  the site loads Cloudflare Turnstile as part of its own application, with
  its sitekey in its own page config — and zero times on either refusal.
  `cf-turnstile` appears nowhere at all. This repo uses `_cf_chl_opt` and
  its siblings instead, and the offline suite fails the build if the
  inverted marker is reintroduced.
- **Walking past the last page does not fail — it repeats.** `?page=48` of a
  47-page listing answers HTTP 200 carrying page 1's rows again. Runs plan
  against the `pageCount` the site states, and the response's own echoed page
  number stops a run that gets past that.
- **A "page" is twenty COMPANIES, not twenty jobs.**
  `/role/r/software-engineer` reported `perPage: 20`, `pageCount: 47`,
  `totalStartupCount: 923` and `totalJobCount: 1881`, and its pages carried
  between 32 and 45 job rows each.
- **`/jobs` has no addressable pages.** `?page=2` returns the identical 46
  job ids as page 1, so that mode reports `single_page_listing` rather than a
  complete multi-page run holding one page several times.
- **The two structured sources agree about pay.** Job 4697947 is
  `$100k – $180k` on the listing and 100000–180000 USD in the detail page's
  `baseSalary`.

[Unreleased]: https://github.com/2scraper/wellfound-scraper/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/2scraper/wellfound-scraper/releases/tag/v0.1.0
