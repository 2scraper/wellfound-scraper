# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/) as
closely as a CLI toolkit can. **A patch release means "fixes", not "no flag
moved"** — a default that changes behaviour can ship in a patch, and when one
does it leads the release notes rather than being discovered from a bill.

## [Unreleased]

## [0.1.1] — 2026-09-17

An audit against this family's own checklist, section by section, executing
each claim rather than re-reading it. Three defects, all found by running a
path that had never been run, and none of them visible to the 356 green
offline checks v0.1.0 shipped with.

> **Correction to v0.1.0's documentation.** v0.1.0 described the captcha
> path as wired in and bounded, and did not say what buying a solve
> actually achieves here. Measured now: on this site, from a datacenter
> address, a paid Turnstile token is **refused** — the challenge is
> captured and solved correctly and Cloudflare does not accept it. If you
> read v0.1.0's README and bought solving to get past the block, that is
> not what will get you in; a residential exit is, and it costs less. The
> table under "About the captcha, precisely" now carries the numbers,
> including the control that makes them mean something: the block does
> not expire on its own — 0 of 8 reloads in the same session cleared it.

### Fixed

- **`SOLVES_PER_PAGE` was not enforced, and it is a money limit.** Every
  engine calls `handle_captcha_if_present` twice per attempt — once before
  the page is classified, once after — and only the second was counted.
  Measured from a datacenter address, where a real Cloudflare challenge
  renders on every fetch: **one page bought three Turnstile solves**. Both
  call sites now go through `_solve_budget()`, and the same run buys one.
- **A dead proxy was reported as a plain "gave up loading".** The reason was
  computed and logged on rotation with a pool, then dropped without one —
  the single-`--proxy` case, which is the common one. All three engines now
  name it, and pyppeteer gained the `exit_failed` binding its twins already
  had so the three are structurally identical.
- **Two inherited claims that were false about this site.**
  `scraper_api_client.py` printed a sibling repo's measurement as this
  repo's; replaced with what was measured here — the Scraper API's own exits
  get upstream 403 and 11,825 bytes, while the same task through a Scraping
  Browser session returns 200, 610,897 bytes and 37 job rows.
  `captcha_solver.py`'s docstring described another site's PerimeterX
  defence and called itself load-bearing here; rewritten, with the sibling
  figures kept and labelled as such.
- **The README said `angel.co`'s old routes no longer exist.** Measured,
  `angel.co/role/r/software-engineer` returns the same page as the
  wellfound.com URL. The host is still refused — one job must not appear
  under two spellings — but the stated reason is now the true one.

### Added

- Regression checks for both fixes, each controlled in both directions:
  planting the fault makes them fail with the expected message, reverting
  makes them green. 373 checks total.
- `years_experience_max` documented as almost always null — 1 of 1,216 rows
  pooled across every live run.

### Verified, by running it

The fingerprint path applies its user agent, locale (`en-US`, not
`en-{country}`) and timezone to the real browser; a failing API call does not
leak the key; credentials never reach the browser's argv (`--proxy-server`
carries host and port only); the engine flag set covers all 28 of the
family's contract flags with none missing; `pip check` passes in each
engine's own venv; the Scraping Browser path serves this site; `--dump-html`
writes on success; exit 3 and exit 4 are distinct; no column is null on every
row of every run; and all three engines return 52 identical rows after the
edits.

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
- **355 offline checks**, with fixtures cut from real captures and verified
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

[Unreleased]: https://github.com/2scraper/wellfound-scraper/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/2scraper/wellfound-scraper/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/2scraper/wellfound-scraper/releases/tag/v0.1.0
