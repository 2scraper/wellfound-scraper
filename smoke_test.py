"""
smoke_test.py — the offline suite for wellfound-scraper.

One file of plain functions with inline fixtures. No pytest, no conftest, no
fixtures directory (CLAUDE.md §10); `tests/test_smoke.py` wraps this as a
single pytest test so `pytest` works as an entry point without a second copy
of the checks.

    python3 smoke_test.py            run everything
    python3 smoke_test.py -v         print every check as it passes

It must pass with NO engine library installed at all: every
`import playwright_scraper` / `selenium_scraper` / `puppeteer_scraper` is
guarded and the skip is RECORDED, because "skipped, engine absent" reads
identically to a real import error. CI installs each engine in its own venv
and fails if that engine's group reports a skip.

The fixtures below are cut from real captures taken 2026-09-17 and trimmed to
the companies and jobs the checks read. Every trimmed fixture was verified to
parse IDENTICALLY to its untrimmed original, field for field, before being
committed — the only deliberate difference is that each `description` is cut
to its first 200 characters, because a job description runs to six kilobytes
and forty of them would be most of this file.

Nothing here carries personal data: Wellfound's job and company objects name
companies, not people, and the parser reads no field that could hold an
individual's name. `check_fixtures_carry_no_personal_names` guards the SHAPE
so a future capture from a route that does is caught.
"""

import argparse
import ast
import csv
import inspect
import io
import json
import os
import re
import subprocess
import sys
import pathlib
import tempfile
from dataclasses import asdict, fields

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

FAILURES = []
PASSED = 0
SKIPS = []
VERBOSE = False


def check(name, condition, detail=""):
    global PASSED
    if condition:
        PASSED += 1
        if VERBOSE:
            print("  ok   %s" % name)
    else:
        FAILURES.append("%s%s" % (name, (" — " + detail) if detail else ""))
        print("  FAIL %s%s" % (name, (" — " + detail) if detail else ""))


def equal(name, got, want):
    check(name, got == want, "got %r, want %r" % (got, want))


def skip(group, reason):
    SKIPS.append("%s: %s" % (group, reason))
    print("  SKIP %s — %s" % (group, reason))
LISTING_NEXT_DATA = r'''<html><head><script>turnstileLoad = function () { turnstile.render('#turnstile_widget', {sitekey: k}); };</script><script src="https://challenges.cloudflare.com/turnstile/v0/api.js?onload=turnstileLoad" async="" defer=""></script><script>window.__ENV={"CLOUDFLARE_TURNSTILE_SITE_KEY":"0x4AAAAAAAgpA-Qx7SsJOW-g"};</script><script>var a=document.createElement('script');a.src='/cdn-cgi/challenge-platform/scripts/jsd/main.js';</script><link href="/_next/static/css/app.css"/></head><body><img src="https://photos.wellfound.com/startups/i/1-logo.jpg"/><script id="__NEXT_DATA__" type="application/json">{"props":{"pageProps":{"apolloState":{"data":{"ROOT_QUERY":{"__typename":"Query","talent":{"__typename":"Talent","seoLandingPageJobSearchResults({\"page\":1,\"remote\":true,\"role\":\"software-engineer\"})":{"__typename":"Results","totalJobCount":1881,"totalStartupCount":923,"perPage":20,"pageCount":47,"startups":[{"__ref":"StartupResult:829771"},{"__ref":"StartupResult:5268250"},{"__ref":"StartupResult:8667152"}]}}},"StartupResult:829771":{"__typename":"StartupResult","id":"829771","badges":[{"__ref":"Badge:ACTIVELY_HIRING"},{"__ref":"Badge:TOP_RESPONDER-829771"},{"__ref":"Badge:QUICK_RESPONDER-829771"},{"__ref":"Badge:B2B-829771"},{"__ref":"Badge:COMPANY_STAGE-829771"},{"__ref":"Badge:TOP_INVESTORS-829771"},{"__ref":"Badge:YC-829771"}],"companySize":"SIZE_11_50","highConcept":"The easiest way to test","highlightedJobListings":[{"__ref":"JobListingSearchResult:4697947"}],"logoUrl":"https://photos.wellfound.com/startups/i/829771-IMAGEHASHPLACEHOLDER0000000000ab-medium_jpg.jpg?buster=1742329133","name":"Confident LIMS","slug":"confidentlims"},"Badge:ACTIVELY_HIRING":{"__typename":"Badge","id":"ACTIVELY_HIRING","name":"ACTIVELY_HIRING_BADGE","label":"Actively Hiring","tooltip":"Actively processing applications","avatarUrl":null,"rating":null,"data":null},"Badge:TOP_RESPONDER-829771":{"__typename":"Badge","id":"TOP_RESPONDER-829771","name":"TOP_RESPONDER_BADGE","label":"Top 1% of responders","tooltip":"Confident LIMS is in the top 1% of companies in terms of response time to applications","avatarUrl":null,"rating":null,"data":null},"Badge:QUICK_RESPONDER-829771":{"__typename":"Badge","id":"QUICK_RESPONDER-829771","name":"QUICK_RESPONDER_BADGE","label":"Responds within a day","tooltip":"Based on past data, Confident LIMS usually responds to incoming applications within a day","avatarUrl":null,"rating":null,"data":null},"Badge:B2B-829771":{"__typename":"Badge","id":"B2B-829771","name":"B2B_BADGE","label":"B2B","tooltip":null,"avatarUrl":null,"rating":null,"data":null},"Badge:COMPANY_STAGE-829771":{"__typename":"Badge","id":"COMPANY_STAGE-829771","name":"COMPANY_STAGE_BADGE","label":"Early Stage","tooltip":"Startup in initial stages","avatarUrl":null,"rating":null,"data":"early_stage"},"Badge:TOP_INVESTORS-829771":{"__typename":"Badge","id":"TOP_INVESTORS-829771","name":"TOP_INVESTORS_BADGE","label":"Top Investors","tooltip":"This company has received a significant amount of investment from top investors","avatarUrl":null,"rating":null,"data":null},"Badge:YC-829771":{"__typename":"Badge","id":"YC-829771","name":"YC_BADGE","label":"YC Funded","tooltip":"Startup funded by Y Combinator","avatarUrl":null,"rating":null,"data":null},"StartupResult:5268250":{"__typename":"StartupResult","id":"5268250","badges":[{"__ref":"Badge:ACTIVELY_HIRING"},{"__ref":"Badge:B2B-5268250"},{"__ref":"Badge:COMPANY_STAGE-5268250"},{"__ref":"Badge:TOP_INVESTORS-5268250"},{"__ref":"Badge:YC-5268250"},{"__ref":"Badge:GROWING_FAST-5268250"}],"companySize":"SIZE_201_500","highConcept":"Making reactors people want","highlightedJobListings":[{"__ref":"JobListingSearchResult:4579450"},{"__ref":"JobListingSearchResult:3685218"},{"__ref":"JobListingSearchResult:4617952"}],"logoUrl":"https://photos.wellfound.com/startups/i/5268250-IMAGEHASHPLACEHOLDER0000000000ab-medium_jpg.jpg?buster=1621284628","name":"Oklo","slug":"oklo"},"Badge:B2B-5268250":{"__typename":"Badge","id":"B2B-5268250","name":"B2B_BADGE","label":"B2B","tooltip":null,"avatarUrl":null,"rating":null,"data":null},"Badge:COMPANY_STAGE-5268250":{"__typename":"Badge","id":"COMPANY_STAGE-5268250","name":"COMPANY_STAGE_BADGE","label":"Growth Stage","tooltip":"Expanding market presence","avatarUrl":null,"rating":null,"data":"growth_stage"},"Badge:TOP_INVESTORS-5268250":{"__typename":"Badge","id":"TOP_INVESTORS-5268250","name":"TOP_INVESTORS_BADGE","label":"Top Investors","tooltip":"This company has received a significant amount of investment from top investors","avatarUrl":null,"rating":null,"data":null},"Badge:YC-5268250":{"__typename":"Badge","id":"YC-5268250","name":"YC_BADGE","label":"YC Funded","tooltip":"Startup funded by Y Combinator","avatarUrl":null,"rating":null,"data":null},"Badge:GROWING_FAST-5268250":{"__typename":"Badge","id":"GROWING_FAST-5268250","name":"GROWING_FAST_BADGE","label":"Growing fast","tooltip":"Showed strong hiring growth in the past month","avatarUrl":null,"rating":null,"data":null},"StartupResult:8667152":{"__typename":"StartupResult","id":"8667152","badges":[{"__ref":"Badge:ACTIVELY_HIRING"},{"__ref":"Badge:B2B-8667152"},{"__ref":"Badge:COMPANY_STAGE-8667152"}],"companySize":"SIZE_51_200","highConcept":"Sydecar is on a mission to transform the world of private markets","highlightedJobListings":[{"__ref":"JobListingSearchResult:3748205"},{"__ref":"JobListingSearchResult:3748202"}],"logoUrl":"https://photos.wellfound.com/startups/i/8667152-IMAGEHASHPLACEHOLDER0000000000ab-medium_jpg.jpg?buster=1788984367","name":"Sydecar","slug":"sydecar-2"},"Badge:B2B-8667152":{"__typename":"Badge","id":"B2B-8667152","name":"B2B_BADGE","label":"B2B","tooltip":null,"avatarUrl":null,"rating":null,"data":null},"Badge:COMPANY_STAGE-8667152":{"__typename":"Badge","id":"COMPANY_STAGE-8667152","name":"COMPANY_STAGE_BADGE","label":"Growth Stage","tooltip":"Expanding market presence","avatarUrl":null,"rating":null,"data":"growth_stage"},"JobListingSearchResult:4697947":{"__typename":"JobListingSearchResult","autoPosted":false,"atsSource":null,"description":"Confident powers analytical testing labs — the labs that test samples on behalf of businesses and report product safety to consumers and regulators at high volume. When a lab publishes a result throug …[trimmed for the fixture]","jobType":"full-time","liveStartAt":1789063154,"locationNames":["San Francisco Bay Area"],"primaryRoleTitle":"Software Engineer","remote":true,"remoteConfig":{"__typename":"JobListingRemoteConfig","kind":"REMOTE","wfhFlexible":false},"acceptedRemoteLocationNames":["Canada","South America","United States","Latin America"],"slug":"senior-software-engineer","title":"Senior Software Engineer","compensation":"$100k – $180k • 0.05% – 0.25%","yearsExperienceMin":5,"yearsExperienceMax":null,"id":"4697947","isBookmarked":false},"JobListingSearchResult:4579450":{"__typename":"JobListingSearchResult","autoPosted":false,"atsSource":"AtsIntegration::Greenhouse::Listing","description":"Join us in pioneering the next generation of nuclear reactors! You'll leverage your software skills alongside nuclear engineers to model, simulate, design, and deploy advanced fission power technology …[trimmed for the fixture]","jobType":"full-time","liveStartAt":1786552154,"locationNames":["Santa Clara"],"primaryRoleTitle":"Software Engineer","remote":true,"remoteConfig":null,"acceptedRemoteLocationNames":["United States"],"slug":"software-engineer","title":"Software Engineer","compensation":"$110k – $200k","yearsExperienceMin":null,"yearsExperienceMax":null,"id":"4579450","isBookmarked":false},"JobListingSearchResult:3685218":{"__typename":"JobListingSearchResult","autoPosted":false,"atsSource":"AtsIntegration::Greenhouse::Listing","description":"Join us in pioneering the next generation of nuclear reactors! You'll leverage your software skills alongside nuclear engineers to model, simulate, design, and deploy advanced fission power technology …[trimmed for the fixture]","jobType":"full-time","liveStartAt":1775147834,"locationNames":["Santa Clara"],"primaryRoleTitle":"Software Engineer","remote":true,"remoteConfig":null,"acceptedRemoteLocationNames":["United States"],"slug":"senior-software-engineer","title":"Senior Software Engineer","compensation":"$200k – $250k","yearsExperienceMin":null,"yearsExperienceMax":null,"id":"3685218","isBookmarked":false},"JobListingSearchResult:4617952":{"__typename":"JobListingSearchResult","autoPosted":false,"atsSource":"AtsIntegration::Greenhouse::Listing","description":"Thanks for your interest in Oklo!  We are searching for a Software Engineer to join our team. \n\nJoin us in pioneering the next generation of nuclear reactors! You'll leverage your software skills alon …[trimmed for the fixture]","jobType":"full-time","liveStartAt":1787346519,"locationNames":["Santa Clara"],"primaryRoleTitle":"Software Engineer","remote":true,"remoteConfig":{"__typename":"JobListingRemoteConfig","kind":"ONSITE_OR_REMOTE","wfhFlexible":true},"acceptedRemoteLocationNames":["United States"],"slug":"software-engineer-applied-ai-ml","title":"Software Engineer (Applied AI/ML)","compensation":"$200k – $250k","yearsExperienceMin":null,"yearsExperienceMax":null,"id":"4617952","isBookmarked":false},"JobListingSearchResult:3748205":{"__typename":"JobListingSearchResult","autoPosted":false,"atsSource":"AtsIntegration::Ashby::Listing","description":"## **About Us**\n\nSydecar is on a mission to transform the world of private markets. Our goal is to make these markets more accessible, transparent, and liquid, and we're achieving this by revolutioniz …[trimmed for the fixture]","jobType":"full-time","liveStartAt":1789083964,"locationNames":["San Francisco"],"primaryRoleTitle":"Software Engineer","remote":true,"remoteConfig":{"__typename":"JobListingRemoteConfig","kind":"ONSITE_OR_REMOTE","wfhFlexible":true},"acceptedRemoteLocationNames":["United States"],"slug":"software-engineer","title":"Software Engineer","compensation":"$150k – $170k","yearsExperienceMin":null,"yearsExperienceMax":null,"id":"3748205","isBookmarked":false},"JobListingSearchResult:3748202":{"__typename":"JobListingSearchResult","autoPosted":false,"atsSource":"AtsIntegration::Ashby::Listing","description":"## **About Us**\n\nSydecar is on a mission to transform the world of private markets. Our goal is to make these markets more accessible, transparent, and liquid, and we're achieving this by revolutioniz …[trimmed for the fixture]","jobType":"full-time","liveStartAt":1779321707,"locationNames":["San Francisco"],"primaryRoleTitle":"Software Engineer","remote":true,"remoteConfig":{"__typename":"JobListingRemoteConfig","kind":"ONSITE","wfhFlexible":true},"acceptedRemoteLocationNames":["United States"],"slug":"senior-software-engineer","title":"Senior Software Engineer","compensation":"$190k – $255k","yearsExperienceMin":null,"yearsExperienceMax":null,"id":"3748202","isBookmarked":false}}}}}}</script></body></html>'''

# A second landing capture, kept for the pay shapes the first one has none of:
# both its rows print "No equity", which is a STATEMENT the listing made and
# not a missing value.
LISTING_NO_EQUITY_NEXT_DATA = r'''<html><head><script>turnstileLoad = function () { turnstile.render('#turnstile_widget', {sitekey: k}); };</script><script src="https://challenges.cloudflare.com/turnstile/v0/api.js?onload=turnstileLoad" async="" defer=""></script><script>window.__ENV={"CLOUDFLARE_TURNSTILE_SITE_KEY":"0x4AAAAAAAgpA-Qx7SsJOW-g"};</script><script>var a=document.createElement('script');a.src='/cdn-cgi/challenge-platform/scripts/jsd/main.js';</script><link href="/_next/static/css/app.css"/></head><body><img src="https://photos.wellfound.com/startups/i/1-logo.jpg"/><script id="__NEXT_DATA__" type="application/json">{"props":{"pageProps":{"apolloState":{"data":{"ROOT_QUERY":{"__typename":"Query","talent":{"__typename":"Talent","seoLandingPageJobSearchResults({\"location\":\"london\",\"page\":1,\"role\":\"sales\"})":{"__typename":"Results","totalStartupCount":193,"totalJobCount":437,"perPage":20,"pageCount":10,"startups":[{"__ref":"StartupResult:10564596"},{"__ref":"StartupResult:10368792"}]}}},"StartupResult:10564596":{"__typename":"StartupResult","id":"10564596","badges":[{"__ref":"Badge:ACTIVELY_HIRING"},{"__ref":"Badge:QUICK_RESPONDER-10564596"},{"__ref":"Badge:GROWING_FAST-10564596"}],"companySize":"SIZE_11_50","highConcept":"Applied AI for businesses using records inside workflows it already runs, owned outright","highlightedJobListings":[{"__ref":"JobListingSearchResult:4656830"}],"logoUrl":"https://photos.wellfound.com/startups/i/10564596-IMAGEHASHPLACEHOLDER0000000000ab-medium_jpg.jpg?buster=1749725201","name":"Briidge.one","slug":"briidgeone"},"Badge:ACTIVELY_HIRING":{"__typename":"Badge","id":"ACTIVELY_HIRING","name":"ACTIVELY_HIRING_BADGE","label":"Actively Hiring","tooltip":"Actively processing applications","avatarUrl":null,"rating":null,"data":null},"Badge:QUICK_RESPONDER-10564596":{"__typename":"Badge","id":"QUICK_RESPONDER-10564596","name":"QUICK_RESPONDER_BADGE","label":"Responds within three weeks","tooltip":"Based on past data, Briidge.one usually responds to incoming applications within three weeks","avatarUrl":null,"rating":null,"data":null},"Badge:GROWING_FAST-10564596":{"__typename":"Badge","id":"GROWING_FAST-10564596","name":"GROWING_FAST_BADGE","label":"Growing fast","tooltip":"Showed strong hiring growth in the past month","avatarUrl":null,"rating":null,"data":null},"StartupResult:10368792":{"__typename":"StartupResult","id":"10368792","badges":[{"__ref":"Badge:ACTIVELY_HIRING"}],"companySize":"SIZE_11_50","highConcept":"Enabling Entrepreneurship Globally..!!","highlightedJobListings":[{"__ref":"JobListingSearchResult:3193662"}],"logoUrl":"https://photos.wellfound.com/startups/i/10368792-IMAGEHASHPLACEHOLDER0000000000ab-medium_jpg.jpg?buster=1736352172","name":"WeCommerce-Global","slug":"wecommerce-global-1"},"JobListingSearchResult:4656830":{"__typename":"JobListingSearchResult","autoPosted":false,"atsSource":null,"description":"**About Us**\n\nBriidge.one is a custom AI and software transformation company helping established businesses turn fragmented operations, legacy systems and proprietary data into intelligent digital inf …[trimmed for the fixture]","jobType":"full-time","liveStartAt":1788175613,"locationNames":["Atlanta","Austin","Boston","California","Chicago","Dallas","Denver","Los Angeles","Miami","Missouri","New York City","Ohio","Pennsylvania","Philadelphia","Phoenix","San Diego","Seattle","Texas","Virginia","Washington DC","San Francisco","San Jose","London","Berkeley","Florida","Toronto","Las Vegas","Amsterdam","Montreal","Manchester","New Jersey","Ontario","Melbourne","Washington","Colorado","Kentucky","San Mateo","Georgia","Calgary","Alberta","Stockholm","Nevada","Los Altos","Montana","Alaska","Rio de Janeiro","Hawaii","New York","Perth","Sydney","Naples","Milan","Edinburgh","Livermore","Virginia Beach","Brisbane","Birmingham","Stuttgart","Los Gatos","São Paulo","Eindhoven","Glasgow","Rotterdam","Adelaide","Liverpool","Dundee","Canberra","California City","San Francisco Bay Area","New South Wales","Greater London","Florianópolis","Los Angeles County","Las Vegas","Washington"],"primaryRoleTitle":"Sales Development Representative","remote":true,"remoteConfig":{"__typename":"JobListingRemoteConfig","kind":"REMOTE","wfhFlexible":false},"acceptedRemoteLocationNames":["Austin, Texas","Australia","Boston, Massachusetts","Brazil","California, United States","Canada","Dallas, Texas","Los Angeles, Los Angeles County","Miami, Florida","New York City, New York","Philadelphia, Pennsylvania","Phoenix, Arizona","San Diego, San Diego County","Seattle, Washington","Texas, United States","United States","Virginia, United States","Washington DC, District of Columbia","San Francisco, California","San Jose, California","London, Greater London","Florida, United States","Las Vegas, Nevada","Massachusetts, United States","Santa Monica, Los Angeles County","Manchester, United Kingdom","United Kingdom","New Jersey, United States","Ontario, Canada","Washington, United States","Colorado, United States","Calgary, Alberta","Alberta, Canada","Los Altos, California","Arizona, United States","Netherlands","Rio de Janeiro, State of Rio de Janeiro","New York, United States","Perth, Western Australia","Sydney, New South Wales","Colombia","New Zealand","Austria","Vienna, Austria","Brisbane, Queensland","Los Gatos, California","São Paulo, State of São Paulo","Hamilton, Ontario","London, Ontario","Adelaide, South Australia","Liverpool, United Kingdom","Canberra, Australian Capital Territory","California City, California","Auckland, New Zealand","Wellington, New Zealand","San Francisco Bay Area, United States","England, United Kingdom","New South Wales, Australia","Greater London, England","Brisbane City, Queensland","Christchurch, Christchurch City","Los Angeles County, United States","São Paulo, State of São Paulo","Sydney, New South Wales"],"slug":"lead-generation-executive-clone","title":"Sales Development Specialist","compensation":"$30k – $50k • No equity","yearsExperienceMin":3,"yearsExperienceMax":null,"id":"4656830","isBookmarked":false},"JobListingSearchResult:3193662":{"__typename":"JobListingSearchResult","autoPosted":false,"atsSource":null,"description":"WeCommerce.PK is an innovative startup dedicated to transforming the e-commerce landscape in Pakistan. Our mission is to empower local businesses by providing them with cutting-edge technology solutio …[trimmed for the fixture]","jobType":"full-time","liveStartAt":1786379450,"locationNames":["Dubai","San Francisco","London","Lahore"],"primaryRoleTitle":"Sales Development Representative","remote":true,"remoteConfig":{"__typename":"JobListingRemoteConfig","kind":"ONSITE_OR_REMOTE","wfhFlexible":false},"acceptedRemoteLocationNames":["Australia","China","Europe","Japan","South America","United States","United Kingdom","Eastern Europe","United Arab Emirates","South Korea","Pakistan"],"slug":"sales-office-coordinator","title":"Sales & Office Coordinator","compensation":"$12k – $36k • No equity","yearsExperienceMin":3,"yearsExperienceMax":null,"id":"3193662","isBookmarked":false}}}}}}</script></body></html>'''

# The /jobs feed, whose Apollo types are DIFFERENT — `JobListing`/`Startup`
# rather than `JobListingSearchResult`/`StartupResult` — and thinner: no
# description, no job type, no badges, and the company edge points the other
# way (the job holds a `__ref` to its company instead of the company listing
# its jobs). One parser reads both, and this fixture is what proves it.
FEED_NEXT_DATA = r'''<html><head><script>turnstileLoad = function () { turnstile.render('#turnstile_widget', {sitekey: k}); };</script><script src="https://challenges.cloudflare.com/turnstile/v0/api.js?onload=turnstileLoad" async="" defer=""></script><script>window.__ENV={"CLOUDFLARE_TURNSTILE_SITE_KEY":"0x4AAAAAAAgpA-Qx7SsJOW-g"};</script><script>var a=document.createElement('script');a.src='/cdn-cgi/challenge-platform/scripts/jsd/main.js';</script><link href="/_next/static/css/app.css"/></head><body><img src="https://photos.wellfound.com/startups/i/1-logo.jpg"/><script id="__NEXT_DATA__" type="application/json">{"props":{"pageProps":{"apolloState":{"data":{"ROOT_QUERY":{"__typename":"Query","talent":{"__typename":"Talent"}},"JobListing:4584538":{"__typename":"JobListing","id":"4584538","slug":"senior-data-scientist","title":"Senior Data Scientist","compensation":"$140k – $165k","locationNames":[],"acceptedRemoteLocationNames":["United States"],"remoteConfig":null,"liveStartAt":1789633434,"remote":true,"primaryRole":{"__typename":"Role","slug":"data-scientist-1"},"startup":{"__ref":"Startup:10232282"}},"Startup:10232282":{"__typename":"Startup","id":"10232282","name":"Nex","logoUrl":"https://photos.wellfound.com/startups/i/10232282-IMAGEHASHPLACEHOLDER0000000000ab-medium_jpg.jpg?buster=1782760539","slug":"nex-7"},"JobListing:4238913":{"__typename":"JobListing","id":"4238913","slug":"software-engineer-agents-internal-audit","title":"Software Engineer, Agents (Internal Audit)","compensation":"$170k – $300k","locationNames":["San Francisco"],"acceptedRemoteLocationNames":["United States"],"remoteConfig":null,"liveStartAt":1789644174,"remote":true,"primaryRole":{"__typename":"Role","slug":"developer"},"startup":{"__ref":"Startup:7792161"}},"Startup:7792161":{"__typename":"Startup","id":"7792161","name":"Fieldguide","logoUrl":"https://photos.wellfound.com/startups/i/7792161-IMAGEHASHPLACEHOLDER0000000000ab-medium_jpg.jpg?buster=1593118684","slug":"fieldguide"},"JobListing:4722726":{"__typename":"JobListing","id":"4722726","slug":"senior-software-engineer-robot-data-collection","title":"Senior Software Engineer - Robot Data Collection","compensation":"$43k – $43k","locationNames":["Santa Clara"],"acceptedRemoteLocationNames":[],"remoteConfig":{"__ref":"JobListingRemoteConfig:1418506"},"liveStartAt":1789612365,"remote":false,"primaryRole":{"__typename":"Role","slug":"developer"},"startup":{"__ref":"Startup:9471899"}},"Startup:9471899":{"__typename":"Startup","id":"9471899","name":"Welocalize","logoUrl":"https://photos.wellfound.com/startups/i/9471899-IMAGEHASHPLACEHOLDER0000000000ab-medium_jpg.jpg?buster=1680890395","slug":"welocalize-2"},"JobListingRemoteConfig:1418506":{"__typename":"JobListingRemoteConfig","id":"1418506","kind":"ONSITE","wfhFlexible":false},"JobListing:4722595":{"__typename":"JobListing","id":"4722595","slug":"senior-software-engineer-ii-full-stack","title":"Senior Software Engineer II, Full-Stack","compensation":"$156k – $251k","locationNames":["New York City"],"acceptedRemoteLocationNames":[],"remoteConfig":null,"liveStartAt":1789589390,"remote":false,"primaryRole":{"__typename":"Role","slug":"developer"},"startup":{"__ref":"Startup:28470"}},"Startup:28470":{"__typename":"Startup","id":"28470","name":"Braze","logoUrl":"https://photos.wellfound.com/startups/i/28470-IMAGEHASHPLACEHOLDER0000000000ab-medium_jpg.jpg?buster=1710992240","slug":"braze"}}}}}}</script></body></html>'''

# A job DETAIL page. No `__NEXT_DATA__` anywhere on it — a different
# application serves this route — and one schema.org JobPosting instead.
JOB_DETAIL_HTML = r'''<html><head><title>Senior Software Engineer at Confident LIMS | Wellfound</title><script type="application/ld+json">{"@context": "http://schema.org/", "@type": "JobPosting", "title": "Senior Software Engineer", "identifier": {"@type": "PropertyValue", "name": "Confident LIMS", "value": "4697947"}, "employmentType": "FULL_TIME", "hiringOrganization": {"@type": "Organization", "name": "Confident LIMS", "sameAs": "https://www.confidentlims.com/", "logo": "https://photos.wellfound.com/startups/i/829771-IMAGEHASHPLACEHOLDER0000000000ab-medium_jpg.jpg?buster=1742329133"}, "image": "https://photos.wellfound.com/startups/i/829771-IMAGEHASHPLACEHOLDER0000000000ab-medium_jpg.jpg?buster=1742329133", "industry": "SaaS, Information Technology, Analytics, Software, and Web Development", "directApply": true, "description": "<p>Confident powers analytical testing labs — the labs that test samples on behalf of businesses and report product safety to consumers and regulators at high volume. When a lab pu …[trimmed for the fixture]</p>", "datePosted": "2026-09-10T17:59:14Z", "jobLocation": [{"@type": "Place", "address": {"@type": "PostalAddress", "addressRegion": "California", "addressCountry": "United States"}, "latitude": 37.8272, "longitude": -122.291}], "jobLocationType": "TELECOMMUTE", "applicantLocationRequirements": [{"@type": "Country", "name": "Canada"}, {"@type": "Country", "name": "United States"}, {"@type": "Country", "name": "Argentina"}, {"@type": "Country", "name": "Brazil"}, {"@type": "Country", "name": "Chile"}, {"@type": "Country", "name": "Colombia"}, {"@type": "Country", "name": "Uruguay"}, {"@type": "Country", "name": "Paraguay"}, {"@type": "Country", "name": "Peru"}, {"@type": "Country", "name": "Venezuela"}, {"@type": "Country", "name": "Ecuador"}, {"@type": "Country", "name": "Bolivia"}, {"@type": "Country", "name": "Guyana"}, {"@type": "Country", "name": "Suriname"}, {"@type": "Country", "name": "Falkland Islands (Islas Malvinas)"}, {"@type": "Country", "name": "French Guiana"}], "experienceRequirements": {"@type": "OccupationalExperienceRequirements", "monthsOfExperience": 60}, "baseSalary": {"@type": "MonetaryAmount", "currency": "USD", "value": {"@type": "QuantitativeValue", "unitText": "YEAR", "minValue": 100000.0, "maxValue": 180000.0}}, "jobBenefits": "Lots of paid time off - We grant paid time off for more than just regular vacation days. 18 company holidays + up to 20  …[trimmed]"}</script></head><body><div>photos.wellfound.com</div></body></html>'''

# The branded refusal a plain HTTP client gets: HTTP 403, the site's own
# styling, its name in the markup. A title or text check calls it a real page.
BRANDED_BLOCK_HTML = r'''<html><head><title>Security Check | Wellfound</title></head><body><h1>403 / Security check</h1><p>Enable JavaScript and cookies to continue</p>pan></div></noscript></div></div><script>(function(){window._cf_chl_opt = {cFPWv: 'g',cH: 'alPEM224TOnZPTnmhgUnIcWCUlMSnL_ZEwTkeV4U80Y-1789658100-1.2.1.1-Z_dzARmbIdvGsbc1unYVFM3TCi9r2H.hzqK4V9HMb3hjJrovIQ7lDlKI8AXMCP0i',cITimeS: '1789658100',cRay: 'a3c910584fbcc7e7',cTplB: '0',cTplC:1,cTplO:0,cTplV:<script src='/cdn-cgi/challenge-platform/h/g/orchestrate/chl_page/v1?ray=a3c910584fbcc7e7'></script><p>Cloudflare Ray ID</p></body></html>'''

# The interstitial a real browser gets instead, from the same address.
INTERSTITIAL_HTML = r'''<html><head><title>Just a moment...</title></head><body><div id='cf-wrapper'></div><script>window._cf_chl_opt={cType:'managed',cZone:'wellfound.com',cRay:'a3c910584fbcc7e7'};</script><script src='/cdn-cgi/challenge-platform/h/b/orchestrate/chl_page/v1'></script></body></html>'''

# A page Wellfound SERVED, carrying the site's OWN Cloudflare Turnstile.
#
# This fixture exists for one check and it is the most important one in the
# file: `challenges.cloudflare.com` and `turnstile` are on this GOOD page and
# absent from both refusals above, so the marker CLAUDE.md §19 recommends is
# inverted here. Counted on the real captures (2026-09-17): 1 and 6 on every
# served landing page, 0 and 0 on both refusals.
SERVED_WITH_SITE_TURNSTILE_HTML = LISTING_NEXT_DATA



# ---------------------------------------------------------------------------
# The parser, asserted on VALUES rather than on coverage
# ---------------------------------------------------------------------------
# A column can be 100% populated and entirely wrong (CLAUDE.md §10), so every
# check below pins a figure from the real capture rather than counting
# non-nulls.

def check_listing_parses():
    import product_parser as P
    page = P.parse_listing_page(LISTING_NEXT_DATA, page=1)
    equal("listing: row count", len(page.rows), 6)
    equal("listing: totalJobCount read from the site", page.total_jobs, 1881)
    equal("listing: totalStartupCount read from the site",
          page.total_companies, 923)
    equal("listing: pageCount read from the site", page.pages_available, 47)
    equal("listing: perPage", page.page_size, 20)
    equal("listing: the server's own page number", page.echoed_page, 1)
    check("listing: page not repeated", not page.page_repeated)
    equal("listing: every row carries the page it came from",
          sorted({r.page for r in page.rows}), [1])
    equal("listing: positions are 1..n in the site's order",
          [r.position for r in page.rows], [1, 2, 3, 4, 5, 6])
    equal("listing: data_source is recorded",
          sorted({r.data_source for r in page.rows}), ["apollo"])
    equal("listing: source column", sorted({r.source for r in page.rows}),
          ["wellfound.com"])


def check_listing_values():
    import product_parser as P
    rows = {r.sku: r for r in P.parse_listing(LISTING_NEXT_DATA)}
    r = rows["4697947"]
    equal("row: title", r.title, "Senior Software Engineer")
    equal("row: url is rebuilt from id and slug", r.url,
          "https://wellfound.com/jobs/4697947-senior-software-engineer")
    equal("row: company name", r.company_name, "Confident LIMS")
    equal("row: company id", r.company_id, "829771")
    equal("row: company url", r.company_url,
          "https://wellfound.com/company/confidentlims")
    # `SIZE_11_50` is an enum token; the column carries the range it denotes.
    equal("row: company size is the range, not the token", r.company_size,
          "11-50")
    equal("row: company tagline", r.company_tagline, "The easiest way to test")
    check("row: badges are display labels, not enum names",
          "Actively Hiring" in (r.company_badges or []),
          repr(r.company_badges))
    check("row: badge enum names are NOT written through",
          not any("_BADGE" in b for b in (r.company_badges or [])),
          repr(r.company_badges))
    equal("row: job type", r.job_type, "full-time")
    equal("row: primary role", r.primary_role, "Software Engineer")
    equal("row: years of experience", r.years_experience_min, 5)
    # liveStartAt is a unix timestamp; the column is UTC ISO-8601.
    equal("row: posted_at is ISO, not an epoch", r.posted_at,
          "2026-09-10T17:59:14+00:00")
    equal("row: locations", r.locations, ["San Francisco Bay Area"])
    equal("row: remote", r.remote, True)
    equal("row: remote kind", r.remote_kind, "REMOTE")
    check("row: accepted remote locations",
          "United States" in (r.remote_locations or []),
          repr(r.remote_locations))


def check_compensation_is_split_into_numbers():
    """The site publishes pay as ONE rendered string. These are the nine
    shapes measured across the 312 non-null values in the 2026-09-17
    captures, with their counts; each is pinned because getting any of them
    wrong writes a wrong number into a column a consumer will average."""
    import product_parser as P

    def c(text):
        return P.parse_compensation(text)

    #  202 of 312
    equal("pay: plain range, low", c("$140k – $250k").salary_min, 140000.0)
    equal("pay: plain range, high", c("$140k – $250k").salary_max, 250000.0)
    equal("pay: plain range, currency", c("$140k – $250k").currency, "USD")
    #   41 of 312 — salary AND equity, split on U+2022
    both = c("$180k – $200k • 0.5% – 1.0%")
    equal("pay: with equity, salary low", both.salary_min, 180000.0)
    equal("pay: with equity, equity low", both.equity_min, 0.5)
    equal("pay: with equity, equity high", both.equity_max, 1.0)
    equal("pay: with equity, has_equity", both.has_equity, True)
    #   45 of 312 — "No equity" is a STATEMENT, not a missing value
    ne = c("$36k – $60k • No equity")
    equal("pay: no-equity keeps the salary", ne.salary_min, 36000.0)
    equal("pay: no-equity is False, not None", ne.has_equity, False)
    #    9 of 312 — equity clause alone
    equal("pay: bare 'No equity' has no salary", c("No equity").salary_min, None)
    equal("pay: bare 'No equity' is False", c("No equity").has_equity, False)
    #    2 of 312 — an equity range with NO salary. Splitting on the bullet
    #    and taking [0] as the salary would write 0.5 into a salary column.
    eq_only = c("0.5% – 1.0%")
    equal("pay: equity-only has no salary", eq_only.salary_min, None)
    equal("pay: equity-only reads as equity", eq_only.equity_min, 0.5)
    #    8 of 312
    equal("pay: GBP", c("£120k – £160k").currency, "GBP")
    #    1 of 312
    equal("pay: EUR", c("€60k – €90k").currency, "EUR")
    #    3 of 312 — `L` is the Indian lakh, 1e5. Stripping non-digits would
    #    read this as 30 to 80.
    inr = c("₹30L – ₹80L")
    equal("pay: INR lakh, low", inr.salary_min, 3000000.0)
    equal("pay: INR lakh, high", inr.salary_max, 8000000.0)
    equal("pay: INR currency", inr.currency, "INR")
    #    1 of 312 — Indian grouping is 2-2-3, so a three-digit group pattern
    #    would not match it.
    mixed = c("₹1,50,000 – ₹30L • No equity")
    equal("pay: Indian grouping", mixed.salary_min, 150000.0)
    equal("pay: mixed grouping and lakh", mixed.salary_max, 3000000.0)
    # absence
    equal("pay: None in, nothing out", c(None).salary_min, None)
    equal("pay: empty string in, nothing out", c("").has_equity, None)
    # A currency this repo has never seen must NOT be guessed at.
    equal("pay: no symbol means no currency", c("100k – 200k").currency, None)


def check_no_equity_on_a_real_capture():
    """`has_equity` False on rows that really say so — and the salary kept."""
    import product_parser as P
    rows = P.parse_listing(LISTING_NO_EQUITY_NEXT_DATA)
    check("no-equity fixture parses", len(rows) >= 2, "got %d" % len(rows))
    for r in rows:
        equal("no-equity row %s: has_equity is False" % r.sku, r.has_equity,
              False)
        check("no-equity row %s: salary survived the split" % r.sku,
              r.salary_min is not None, repr(r.compensation))


def check_salary_period_is_null_on_a_listing_row():
    """The listing string carries no period, so the column must not invent one.

    `$140k` on a job board reads as a year, but the PAGE does not say so.
    CLAUDE.md §8: never present a guess as a fact. The detail page does state
    one, and the next check pins that it is read.
    """
    import product_parser as P
    rows = P.parse_listing(LISTING_NEXT_DATA)
    equal("listing rows never claim a salary period",
          sorted({r.salary_period for r in rows}), [None])


def check_feed_uses_different_types_and_one_parser_reads_both():
    """The /jobs feed's Apollo types differ from a landing page's.

    `JobListing`/`Startup` rather than `JobListingSearchResult`/
    `StartupResult`, the company edge points the other way, and three columns
    are legitimately absent. A parser that knew only the landing shape would
    return zero rows here — in silence.
    """
    import product_parser as P
    rows = P.parse_listing(FEED_NEXT_DATA)
    equal("feed: row count", len(rows), 4)
    check("feed: every row has an id", all(r.sku for r in rows))
    check("feed: every row has a title", all(r.title for r in rows))
    check("feed: every row resolved its company",
          all(r.company_name for r in rows),
          repr([r.company_name for r in rows]))
    # Measured, and the reason `description` is NOT in CORE_FIELDS: the feed's
    # thinner type carries none on any row.
    equal("feed: no descriptions, and that is the site",
          sorted({bool(r.description) for r in rows}), [False])
    equal("feed: no badges either",
          sorted({r.company_badges is None for r in rows}), [True])
    # And no pagination arithmetic at all — there is no Results node.
    page = P.parse_listing_page(FEED_NEXT_DATA, page=1)
    equal("feed: publishes no pageCount", page.pages_available, None)
    equal("feed: publishes no totalJobCount", page.total_jobs, None)


def check_detail_page_is_a_different_mechanism():
    """A job page has no `__NEXT_DATA__` and one schema.org JobPosting.

    This is CLAUDE.md §20's "a DETAIL page may publish a different JSON-LD
    type than the listing" in its sharpest form: a different MECHANISM. The
    failure it guards is silent — the listing parser returns [] rather than
    raising — so it is pinned directly, in both directions.
    """
    import product_parser as P
    check("detail: carries no __NEXT_DATA__",
          P.extract_next_data(JOB_DETAIL_HTML) is None)
    equal("detail: the LISTING parser finds nothing on it",
          P.parse_listing(JOB_DETAIL_HTML), [])
    row = P.parse_detail(JOB_DETAIL_HTML,
                         "https://wellfound.com/jobs/4697947-senior-software-engineer")
    check("detail: the detail parser finds the job", row is not None)
    equal("detail: sku from the identifier block", row.sku, "4697947")
    equal("detail: title", row.title, "Senior Software Engineer")
    equal("detail: company", row.company_name, "Confident LIMS")
    equal("detail: data_source", row.data_source, "jsonld")
    equal("detail: employmentType mapped to the site's own word",
          row.job_type, "full-time")
    # monthsOfExperience 60 -> 5 years, the same figure the listing states.
    equal("detail: months of experience become years",
          row.years_experience_min, 5)
    equal("detail: salary period IS stated here", row.salary_period, "YEAR")
    check("detail: benefits text is read", bool(row.benefits))
    check("detail: industry is read", bool(row.industry))
    # schema.org has no expression for equity, and the column says so rather
    # than reporting zero.
    equal("detail: equity is absent, not zero", row.equity_min, None)
    equal("detail: and the DETAIL parser finds nothing on a listing",
          P.parse_detail(LISTING_NEXT_DATA), None)


def check_the_two_sources_agree_about_pay():
    """Where both views publish a salary they must agree.

    CLAUDE.md §4 says to check whether structured and displayed prices
    disagree on every new site. Here they do not: job 4697947 is
    `'$100k – $180k • 0.05% – 0.25%'` on the listing and 100000-180000 USD in
    the detail page's `baseSalary`. That agreement is what lets `--mode job`
    enrich a `--mode role` run instead of contradicting it, and it is pinned
    so a future parser change cannot break it quietly.
    """
    import product_parser as P
    listing = {r.sku: r for r in P.parse_listing(LISTING_NEXT_DATA)}["4697947"]
    detail = P.parse_detail(JOB_DETAIL_HTML,
                            "https://wellfound.com/jobs/4697947-senior-software-engineer")
    equal("cross-source: same sku", listing.sku, detail.sku)
    equal("cross-source: salary low agrees", listing.salary_min,
          detail.salary_min)
    equal("cross-source: salary high agrees", listing.salary_max,
          detail.salary_max)
    equal("cross-source: currency agrees", listing.salary_currency,
          detail.salary_currency)
    equal("cross-source: years of experience agree",
          listing.years_experience_min, detail.years_experience_min)
    equal("cross-source: url agrees", listing.url, detail.url)


def check_an_out_of_range_page_is_detected_from_the_payload():
    """`?page=48` of a 47-page listing answers 200 with page 1 AGAIN.

    Measured 2026-09-17: the response carried the same 37 job ids as page 1.
    A run that trusted its own request would collect page 1 for as long as it
    was asked to and report success. The server states which page it really
    used inside the Apollo cache key, and that is an unambiguous signal
    rather than the weaker "no new sku" heuristic (CLAUDE.md §17).
    """
    import product_parser as P
    page = P.parse_listing_page(LISTING_NEXT_DATA, page=48)
    equal("page echo: the server said page 1", page.echoed_page, 1)
    equal("page echo: we asked for 48", page.requested_page, 48)
    check("page echo: detected as a repeat", page.page_repeated)
    # ...and the same payload read as page 1 is NOT a repeat.
    check("page echo: no false positive on a real page 1",
          not P.parse_listing_page(LISTING_NEXT_DATA, page=1).page_repeated)


def check_pagination_is_planned_from_the_sites_own_number():
    import product_parser as P
    import page_flow
    # The site says 47; asking for 60 plans 47, not 60.
    equal("pages: capped by the site's own pageCount",
          P.pages_to_fetch(60, 47), 47)
    equal("pages: a smaller request is honoured", P.pages_to_fetch(3, 47), 3)
    equal("pages: unknown ceiling honours the request",
          P.pages_to_fetch(5, None), 5)
    equal("pages: page_flow agrees with the parser",
          page_flow.pages_to_plan(60, 47), P.pages_to_fetch(60, 47))
    # There is no hard ceiling on top of the site's figure. Unlike a sibling
    # repo, Wellfound does not cap what it will serve, and a cap here would
    # silently truncate a legitimate run.
    equal("pages: no invented ceiling", page_flow.pages_to_plan(200, 200), 200)


def check_only_the_landing_routes_are_addressable():
    """The two page kinds give OPPOSITE answers, so the question is per URL.

    `?page=2` on /jobs does not fail and does not empty — it returns the
    identical 46 job ids as page 1. A `page_url()` used unconditionally there
    would find no new sku, conclude the listing was exhausted, and report a
    COMPLETE run holding page 1 (CLAUDE.md §18).
    """
    import page_flow
    for url, want in (
            ("https://wellfound.com/role/r/software-engineer", True),
            ("https://wellfound.com/role/software-engineer", True),
            ("https://wellfound.com/role/l/sales/london", True),
            ("https://wellfound.com/jobs", False),
            ("https://wellfound.com/jobs/4697947-senior-software-engineer", False)):
        equal("addressable: %s" % url, page_flow.pagination_is_addressable(url),
              want)


def check_url_building():
    import product_parser as P
    equal("url: page 1 carries no ?page",
          P.page_url("https://wellfound.com/role/r/software-engineer", 1),
          "https://wellfound.com/role/r/software-engineer")
    equal("url: page N",
          P.page_url("https://wellfound.com/role/r/software-engineer", 3),
          "https://wellfound.com/role/r/software-engineer?page=3")
    # Replaced, not duplicated, and the other parameters survive.
    equal("url: ?page is replaced, not appended",
          P.page_url("https://wellfound.com/role/r/x?page=2&utm=a", 5),
          "https://wellfound.com/role/r/x?utm=a&page=5")
    equal("url: role", P.role_url("software-engineer"),
          "https://wellfound.com/role/software-engineer")
    equal("url: remote role", P.role_url("software-engineer", remote=True),
          "https://wellfound.com/role/r/software-engineer")
    equal("url: role + location",
          P.role_url("data-scientist", location="new-york"),
          "https://wellfound.com/role/l/data-scientist/new-york")
    # A location wins over --remote: /role/l/ is the only shape that takes one.
    equal("url: location wins over remote",
          P.role_url("sales", location="london", remote=True),
          "https://wellfound.com/role/l/sales/london")
    equal("url: job", P.job_url("4697947", "senior-software-engineer"),
          "https://wellfound.com/jobs/4697947-senior-software-engineer")
    equal("url: sku recovered from a job URL",
          P.sku_from_url("https://wellfound.com/jobs/4697947-senior-software-engineer"),
          "4697947")


def check_route_and_mode_are_derived_from_the_url():
    import product_parser as P
    # `/role/r/x` must beat `/role/x`, or the literal "r" becomes a role slug.
    equal("route: /role/r/ is not a role named 'r'",
          P.route_of("https://wellfound.com/role/r/software-engineer"),
          "role_remote")
    equal("route: /role/l/", P.route_of("https://wellfound.com/role/l/sales/london"),
          "role_location")
    equal("route: /role/", P.route_of("https://wellfound.com/role/sales"),
          "role_plain")
    equal("route: /jobs", P.route_of("https://wellfound.com/jobs"), "jobs_feed")
    equal("route: /jobs/{id}-{slug}",
          P.route_of("https://wellfound.com/jobs/4697947-x"), "job_detail")
    equal("route: /company/", P.route_of("https://wellfound.com/company/openai"),
          "company")
    for url, mode in (("https://wellfound.com/role/r/x", "role"),
                      ("https://wellfound.com/jobs", "jobs"),
                      ("https://wellfound.com/jobs/1-x", "job")):
        equal("mode from %s" % url, P.mode_for_url(url), mode)


def check_unsupported_urls_are_refused_with_a_reason():
    """A wrong reason sends the reader hunting for a typo (CLAUDE.md §5)."""
    import product_parser as P
    ok, why = P.is_supported_url("https://wellfound.com/role/r/software-engineer")
    check("supported: a landing page is accepted", ok, why)
    ok, why = P.is_supported_url("https://example.com/role/r/x")
    check("supported: another host is refused", not ok)
    check("supported: ...and the reason names the host", "example.com" in why, why)
    # angel.co really IS Wellfound — it redirects here — so "not a Wellfound
    # host" would be a false statement, not merely an unhelpful one.
    ok, why = P.is_supported_url("https://angel.co/role/r/x")
    check("supported: angel.co is refused", not ok)
    check("supported: ...and the reason says it redirects here",
          "redirects" in why.lower(), why)
    # /company/ is a Wellfound route and IS gated; the refusal says which.
    ok, why = P.is_supported_url("https://wellfound.com/company/openai")
    check("supported: /company/ is refused", not ok)
    check("supported: ...and the reason names Cloudflare, not a typo",
          "Cloudflare" in why, why)
    ok, why = P.is_supported_url("https://wellfound.com/nothing/here")
    check("supported: an unknown route is refused", not ok)


def check_category_label_names_the_query():
    import product_parser as P
    equal("label: remote role",
          P.category_from_url("https://wellfound.com/role/r/software-engineer"),
          "role/software-engineer/remote")
    equal("label: role + location",
          P.category_from_url("https://wellfound.com/role/l/data-scientist/new-york"),
          "role/data-scientist@new-york")
    equal("label: the feed",
          P.category_from_url("https://wellfound.com/jobs"), "jobs")
    equal("label: one job",
          P.category_from_url("https://wellfound.com/jobs/4697947-x"),
          "job/4697947")


def check_page_states_on_real_captures():
    import product_parser as P
    equal("state: a landing page is content",
          P.detect_page_state(SERVED_WITH_SITE_TURNSTILE_HTML, 200, mode="role"),
          "content")
    equal("state: a job page is content",
          P.detect_page_state(JOB_DETAIL_HTML, 200, mode="job"), "content")
    equal("state: the branded 403 is blocked",
          P.detect_page_state(BRANDED_BLOCK_HTML, 403, mode="role"), "blocked")
    equal("state: the interstitial is blocked",
          P.detect_page_state(INTERSTITIAL_HTML, 403, mode="role"), "blocked")
    # The status alone settles it, because the branded refusal wears the
    # site's own name and a text check calls it a real page.
    equal("state: 403 is blocked whatever the markup says",
          P.detect_page_state("<html><title>Wellfound</title></html>", 403),
          "blocked")
    equal("state: 404 is not a block", P.detect_page_state("<html></html>", 404),
          "not_found")
    # A served page whose payload we could not read is OUR bug, never
    # "0 jobs" (CLAUDE.md §20).
    broken = ('<html><body><img src="https://photos.wellfound.com/x.jpg">'
              '<script id="__NEXT_DATA__" type="application/json">'
              '{"props":{"pageProps":{"apolloState":{"data":{"ROOT_QUERY":{}}}}}}'
              '</script></body></html>')
    equal("state: served but unreadable is parse_error, not empty",
          P.detect_page_state(broken, 200, mode="role"), "parse_error")


def check_markers_do_not_match_a_page_wellfound_serves():
    """Count every marker on a page known GOOD before trusting it (§18).

    This is the check that caught the mistake this repo would otherwise have
    shipped. `challenges.cloudflare.com` is the marker the rest of this
    family settled on, and on Wellfound it is INVERTED: the site loads
    Cloudflare Turnstile as part of its own application — the api.js script,
    a published `CLOUDFLARE_TURNSTILE_SITE_KEY`, and a fetch wrapper that
    renders a widget into `#turnstile_widget` — so the marker is on every
    good page and on neither refusal.
    """
    import product_parser as P
    good = SERVED_WITH_SITE_TURNSTILE_HTML
    # The evidence, asserted rather than described:
    check("marker evidence: a GOOD page carries challenges.cloudflare.com",
          "challenges.cloudflare.com" in good)
    check("marker evidence: neither refusal does",
          "challenges.cloudflare.com" not in BRANDED_BLOCK_HTML
          and "challenges.cloudflare.com" not in INTERSTITIAL_HTML)
    # ...therefore it must not be in the set, and nor may a bare
    # `cdn-cgi/challenge-platform`, which a served page loads too (the
    # passive JS-detections beacon at .../scripts/jsd/main.js).
    markers = [m for _, m in P.BOT_CHALLENGE_MARKERS]
    for banned in ("challenges.cloudflare.com", "cf-turnstile", "turnstile"):
        check("marker set excludes %r" % banned, banned not in markers,
              repr(markers))
    check("marker set does not use the bare cdn-cgi prefix",
          "cdn-cgi/challenge-platform" not in markers, repr(markers))
    # The set must be silent on every good page and fire on both refusals.
    equal("markers: silent on a served landing page",
          P.detect_bot_challenge(good), None)
    equal("markers: silent on a served job page",
          P.detect_bot_challenge(JOB_DETAIL_HTML), None)
    equal("markers: fire on the branded 403",
          P.detect_bot_challenge(BRANDED_BLOCK_HTML), "cloudflare")
    equal("markers: fire on the interstitial",
          P.detect_bot_challenge(INTERSTITIAL_HTML), "cloudflare")


def check_only_one_refusal_skin_carries_a_widget():
    """The two refusals are the same vendor and NOT the same page.

    Counted 2026-09-18 across four real refusals:

        branded "Security Check | Wellfound"   _cf_chl_opt 7x, turnstile 0x
        "Just a moment..." (browser)           _cf_chl_opt 7x, turnstile 1x

    So the no-JS skin carries **no widget at all**, and that is the precise
    sense in which a page is unsolvable (CLAUDE.md §19: "unsolvable" is a
    property of a PAGE with nothing on it, never of a vendor). Paying for a
    task built from a page like that buys an ERROR_CAPTCHA_UNSOLVABLE, which
    is why the engines refuse to build one without a captured sitekey.

    Both must still classify as blocked, because a caller's move is the same
    either way — a different exit.
    """
    import product_parser as P
    for label, html in (("branded", BRANDED_BLOCK_HTML),
                        ("interstitial", INTERSTITIAL_HTML)):
        equal("%s refusal is detected as Cloudflare" % label,
              P.detect_bot_challenge(html), "cloudflare")
        equal("%s refusal is state=blocked" % label,
              P.detect_page_state(html, 403, mode="role"), "blocked")
        # Neither publishes a sitekey a static read could use: Cloudflare
        # calls turnstile.render() once and keeps nothing.
        equal("%s refusal publishes no usable sitekey" % label,
              P.site_turnstile_sitekey(html), None)
    # The branded skin specifically has nothing on it at all.
    for marker in ("challenges.cloudflare.com", "cf-turnstile",
                   "turnstile.render"):
        check("the branded refusal carries no %r" % marker,
              marker not in BRANDED_BLOCK_HTML)


def check_the_sites_own_turnstile_is_recognised_as_configured():
    """"Did we meet a captcha" is the wrong question; "is one configured, and
    would we recognise it" is the right one (CLAUDE.md §18).

    One is: Wellfound publishes its sitekey in its own page config and
    renders a widget with it when its own fetch wrapper is challenged. That
    widget IS solvable from a static read — unlike Cloudflare's interstitial,
    which publishes no sitekey at all and needs the `turnstile.render`
    interception hook.
    """
    import product_parser as P
    equal("site turnstile: sitekey read from the page's own config",
          P.site_turnstile_sitekey(SERVED_WITH_SITE_TURNSTILE_HTML),
          "0x4AAAAAAAgpA-Qx7SsJOW-g")
    equal("site turnstile: a refusal publishes none",
          P.site_turnstile_sitekey(BRANDED_BLOCK_HTML), None)
    equal("site turnstile: the interstitial publishes none",
          P.site_turnstile_sitekey(INTERSTITIAL_HTML), None)


def check_positive_asset_detection():
    """"Was this built out of the site's own assets?" — the only signal that
    answers correctly for Chromium's own network-error page, which carries
    the site's hostname in its <title> and nothing else of the site's."""
    import product_parser as P
    check("assets: a served page references them",
          P.references_own_assets(SERVED_WITH_SITE_TURNSTILE_HTML) > 0)
    equal("assets: the branded refusal references none",
          P.references_own_assets(BRANDED_BLOCK_HTML), 0)
    equal("assets: the interstitial references none",
          P.references_own_assets(INTERSTITIAL_HTML), 0)
    chrome_error = ("<html><head><title>wellfound.com</title></head><body>"
                    "<div>ERR_PROXY_CONNECTION_FAILED</div></body></html>")
    equal("assets: Chromium's own error page references none",
          P.references_own_assets(chrome_error), 0)
    equal("assets: ...and it does not classify as content",
          P.detect_page_state(chrome_error, None, mode="role"), "unknown")


def check_company_size_tokens():
    import product_parser as P
    for token, want in (("SIZE_1_10", "1-10"), ("SIZE_11_50", "11-50"),
                        ("SIZE_201_500", "201-500"),
                        ("SIZE_5000_PLUS", "5000+")):
        equal("size: %s" % token, P.company_size(token), want)
    # An unknown band is passed through, not dropped: a new value must show
    # up in the data rather than look like a missing one.
    equal("size: an unknown token survives", P.company_size("SIZE_WEIRD"),
          "SIZE_WEIRD")
    equal("size: absent stays absent", P.company_size(None), None)


def check_state_policy():
    import page_flow
    equal("every state has a policy",
          sorted(page_flow.STATE_POLICY),
          ["blocked", "content", "empty", "not_found", "parse_error",
           "unknown"])
    check("content: parsed, not retried, not blocked",
          page_flow.should_parse("content")
          and not page_flow.should_retry("content")
          and not page_flow.counts_as_blocked("content"))
    # ONE blocked state, not two, because Wellfound's two refusal skins —
    # the branded 403 and the "Just a moment..." interstitial — are the same
    # decision by the same vendor and answer to the same two moves. Solving
    # is True because the challenge IS a test once the render hook has
    # captured its parameters; retrying is True because a different exit
    # clears it outright, which is measured and much cheaper.
    check("blocked: retried, solvable, counts as blocked",
          page_flow.should_retry("blocked")
          and page_flow.should_solve("blocked")
          and page_flow.counts_as_blocked("blocked"))
    # A served page we could not read is OUR bug, never "0 jobs" (§20), so
    # it neither counts as blocked nor buys a solve.
    check("parse_error: retried once, never solved, NOT blocked",
          page_flow.should_retry("parse_error")
          and not page_flow.should_solve("parse_error")
          and not page_flow.counts_as_blocked("parse_error")
          and not page_flow.should_parse("parse_error"))
    # Retrying an address that does not exist is waste, and calling it a
    # block sends a user rotating proxies over a typo.
    check("not_found: not retried, not blocked",
          not page_flow.should_retry("not_found")
          and not page_flow.counts_as_blocked("not_found"))
    check("unknown: retried, not solved, NOT blocked",
          page_flow.should_retry("unknown")
          and not page_flow.should_solve("unknown")
          and not page_flow.counts_as_blocked("unknown"))
    check("an unrecognised state falls back to unknown's policy",
          page_flow.should_retry("something-new")
          and not page_flow.should_solve("something-new"))
    equal("at most one solve per page", page_flow.SOLVES_PER_PAGE, 1)


def check_policy_constants_have_a_consumer():
    """§17: a policy constant nothing reads is the same defect as dead code.

    `RETRY_ON_BLOCKED` carried a paragraph of justification in a sibling repo
    and no engine consulted it, so setting it False changed nothing.
    """
    import page_flow
    sources = []
    for name in ("playwright_scraper.py", "selenium_scraper.py",
                 "puppeteer_scraper.py", "scraper_api_client.py"):
        path = os.path.join(HERE, name)
        if os.path.exists(path):
            sources.append(open(path, encoding="utf-8").read())
    joined = "\n".join(sources)
    for constant in ("RETRY_ON_BLOCKED", "BLOCK_RETRIES_WITHOUT_POOL",
                     "SOLVES_PER_PAGE"):
        check("page_flow.%s is CONSULTED by an engine" % constant,
              constant in joined,
              "defined in page_flow and read by nothing")
    for fn in ("pages_to_plan", "ready_selector", "min_matches",
               "content_timeout_ms", "wait_for_count", "classify",
               "should_retry", "should_solve", "counts_as_blocked",
               "should_parse", "concurrency_limit",
               "pagination_is_addressable"):
        check("page_flow.%s has a caller outside its own module" % fn,
              fn in joined, "unused policy")


# ---------------------------------------------------------------------------
# The output contract
# ---------------------------------------------------------------------------

def check_row_schema():
    from output_writer import JobPosting, ROW_CLASS_BY_MODE, UNIQUE_BY_SKU_MODES
    names = [f.name for f in fields(JobPosting)]
    equal("the family prefix is byte-identical and in order (§9)",
          names[:5], ["source", "scraped_at", "url", "sku", "title"])
    for gone in ("price", "currency", "original_price", "discount_pct",
                 "in_stock", "brand"):
        check("the commerce column %r is absent, not null-forever" % gone,
              gone not in names)
    # `rating` is absent because Wellfound publishes none on any route this
    # scraper reads: 0 rating fields across 432 job records and 210 company
    # records in the 2026-09-17 captures. The nearest thing is a company
    # BADGE ("Highly Rated"), which is a label and not a scale.
    check("`rating` is absent — the site publishes none",
          "rating" not in names)
    check("...and the badges that stand in for it are present",
          "company_badges" in names)
    # A salary is a RANGE, which is two columns and not one, and equity is a
    # second range no shop repo has at all.
    for needed in ("salary_min", "salary_max", "salary_currency",
                   "equity_min", "equity_max", "has_equity", "compensation"):
        check("the pay column %r is present" % needed, needed in names)
    equal("every mode maps to a row class",
          sorted(ROW_CLASS_BY_MODE), ["job", "jobs", "role"])
    equal("every mode is one row per sku",
          sorted(UNIQUE_BY_SKU_MODES), ["job", "jobs", "role"])
    equal("all three modes share one class",
          len({c for c in ROW_CLASS_BY_MODE.values()}), 1)


def check_csv_and_json_writers():
    from output_writer import JobPosting, write_csv, write_json
    import product_parser as P
    rows = P.parse_listing(LISTING_NEXT_DATA)
    with tempfile.TemporaryDirectory() as tmp:
        csv_path = os.path.join(tmp, "out.csv")
        write_csv(rows, csv_path, row_cls=JobPosting)
        with open(csv_path, encoding="utf-8") as f:
            reader = list(csv.reader(f))
        equal("CSV header matches the dataclass, in order",
              reader[0], [f.name for f in fields(JobPosting)])
        equal("CSV holds every row", len(reader) - 1, len(rows))
        # `company_badges` is the list column on this site; a landing row
        # carries several, so the join is visible.
        badges_col = reader[0].index("company_badges")
        joined = [r[badges_col] for r in reader[1:] if r[badges_col]]
        check("a list column is joined readably rather than repr()'d",
              any(" | " in v for v in joined), repr(joined[:2]))
        check("no Python list repr leaked into the CSV",
              not any(cell.startswith("[") for row in reader[1:] for cell in row))

        empty_csv = os.path.join(tmp, "empty.csv")
        write_csv([], empty_csv, row_cls=JobPosting)
        with open(empty_csv, encoding="utf-8") as f:
            header = list(csv.reader(f))
        equal("an EMPTY csv still carries its header", len(header), 1)
        equal("...and it is the right one", header[0],
              [f.name for f in fields(JobPosting)])

        json_path = os.path.join(tmp, "out.json")
        write_json(rows, json_path)
        loaded = json.load(open(json_path, encoding="utf-8"))
        equal("JSON holds every row", len(loaded), len(rows))
        equal("JSON keys are the dataclass fields, in order",
              list(loaded[0].keys()), [f.name for f in fields(JobPosting)])
        check("a list column stays a real list in JSON",
              isinstance(loaded[0]["company_badges"], list),
              repr(loaded[0]["company_badges"]))


def check_exit_codes():
    import output_writer as O
    equal("0 ok / 1 crash / 2 usage / 3 blocked / 4 empty / 5 api / 6 partial",
          (O.EXIT_BLOCKED, O.EXIT_NO_PRODUCTS, O.EXIT_API_ERROR, O.EXIT_PARTIAL),
          (3, 4, 5, 6))
    check("page_cap_reached is a COMPLETE stop reason",
          "page_cap_reached" in O.COMPLETE_STOP_REASONS)
    check("single_page_mode is complete by construction",
          "single_page_mode" in O.COMPLETE_STOP_REASONS)
    # The /jobs feed is served at one address — `?page=2` returns the
    # identical rows — so a run that stopped after one page fetched the whole
    # thing. Measured, not assumed.
    check("single_page_listing is complete",
          "single_page_listing" in O.COMPLETE_STOP_REASONS)
    # And the site's own way of saying a listing has ended: it answers an
    # out-of-range page with page 1 under HTTP 200, and states which page it
    # really used. Stopping there fetched everything that exists.
    check("page_echo_mismatch is complete",
          "page_echo_mismatch" in O.COMPLETE_STOP_REASONS)
    check("no_new_products is complete",
          "no_new_products" in O.COMPLETE_STOP_REASONS)


def check_a_partial_run_says_so_and_still_writes():
    """§9: blocked != empty != partial, and all three are distinct exit codes.

    Only the CONSTANT was pinned — `EXIT_PARTIAL == 6` — never the behaviour,
    which is the half a consumer branches on. A partial run has to do four
    things at once and getting any of them wrong is silent: keep the rows it
    did gather, say `partial` rather than `complete`, exit 6, and record
    WHICH pages are missing by number.

    That last one is the reason `pages_failed` is a list: a count stops being
    a description once pages can be fetched independently and page 3 can fail
    while 4 and 5 succeed.
    """
    from output_writer import (finish_run, JobPosting, EXIT_PARTIAL,
                               COMPLETE_STOP_REASONS)
    rows = [JobPosting(sku=str(i), title="t", url="u", page=1, position=i)
            for i in range(1, 6)]
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "run")
        code = finish_run(rows, out, "json", False, blocked=False,
                          stop_reason="blocked_cloudflare", pages_requested=3,
                          pages_completed=1, pages_failed=[2, 3], mode="role",
                          source="wellfound.com", start_url="u", final_url="u")
        equal("a partial run exits 6", code, EXIT_PARTIAL)
        meta = json.load(open(out + ".meta.json", encoding="utf-8"))
        equal("...and says partial, not complete", meta["status"], "partial")
        equal("...and names WHICH pages are missing, by number",
              meta["pages_failed"], [2, 3])
        equal("...and still writes the rows it did gather",
              len(json.load(open(out + ".json", encoding="utf-8"))), 5)
        check("...and its stop_reason is not one of the complete ones",
              meta["stop_reason"] not in COMPLETE_STOP_REASONS,
              meta["stop_reason"])

    # The same call with every page fetched is COMPLETE and exit 0 — the
    # control, without which the check above would pass on a function that
    # always says partial.
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "run")
        code = finish_run(rows, out, "json", False, blocked=False,
                          stop_reason="completed", pages_requested=1,
                          pages_completed=1, pages_failed=[], mode="role",
                          source="wellfound.com", start_url="u", final_url="u")
        equal("a complete run exits 0", code, 0)
        meta = json.load(open(out + ".meta.json", encoding="utf-8"))
        equal("...and says complete", meta["status"], "complete")


def check_a_run_that_finds_nothing_writes_nothing():
    """Never replace last night's good output with []."""
    from output_writer import save
    with tempfile.TemporaryDirectory() as tmp:
        prefix = os.path.join(tmp, "out")
        with open(prefix + ".json", "w", encoding="utf-8") as f:
            f.write('[{"sku": "yesterday"}]')
        code = save([], prefix, "json", allow_empty=False)
        equal("an empty run exits 4", code, 4)
        equal("...and leaves the previous good file alone",
              open(prefix + ".json", encoding="utf-8").read(),
              '[{"sku": "yesterday"}]')
        code = save([], prefix, "json", allow_empty=True)
        equal("--allow-empty WRITES the empty file...", 
              json.load(open(prefix + ".json", encoding="utf-8")), [])
        # ...and still reports exit 4. Pinned deliberately (§10: pin a known
        # behaviour rather than half-guarding it): "zero businesses" is true
        # whether or not the file was written, and a caller that wanted the
        # file still wants to know the result was empty.
        equal("...and still reports exit 4, because it IS empty", code, 4)


def check_page_and_position_are_unique_across_pages():
    """One line, and the column is worthless without it: `position` restarts
    at 1 on every page."""
    import product_parser as P
    page1 = P.parse_listing(LISTING_NEXT_DATA, page=1)
    page2 = P.parse_listing(LISTING_NEXT_DATA, page=2)
    pairs = [(r.page, r.position) for r in page1 + page2]
    equal("page+position is unique across a multi-page run",
          len(set(pairs)), len(pairs))
    equal("page 2's rows really say page 2",
          sorted({r.page for r in page2}), [2])


def check_sidecar_shape():
    from output_writer import run_meta
    meta = run_meta(status="complete", stop_reason="page_cap_reached",
                    pages_requested=50, pages_completed=47, pages_failed=[],
                    products=1874, mode="role", source="wellfound.com",
                    start_url="https://wellfound.com/role/r/software-engineer",
                    final_url="https://wellfound.com/role/r/software-engineer?page=47",
                    extra={"total_jobs": 1881, "total_companies": 923,
                           "pages_available": 47, "paginates_by_url": True})
    for key in ("status", "stop_reason", "pages_requested", "pages_completed",
                "pages_failed", "mode", "source"):
        check("the sidecar records %r" % key, key in meta)
    equal("the sidecar carries the site's own job total",
          meta["total_jobs"], 1881)
    # Both denominators, because the site counts COMPANIES per page while the
    # rows are JOBS. Without the second number a consumer divides one by the
    # other and gets an answer that is wrong for every page.
    equal("...and the COMPANY total beside it", meta["total_companies"], 923)
    equal("...and whether this listing is addressable at all",
          meta["paginates_by_url"], True)
    equal("pages_failed is a LIST of numbers, not a count",
          isinstance(meta["pages_failed"], list), True)


# ---------------------------------------------------------------------------
# The engines — the five checks CLAUDE.md §17 says to steal
# ---------------------------------------------------------------------------

ENGINES = ("playwright_scraper", "selenium_scraper", "puppeteer_scraper")
DRIVER_IMPORTS = {
    "playwright_scraper": "playwright",
    "selenium_scraper": "selenium",
    "puppeteer_scraper": "pyppeteer",
}


def _import_engine(name):
    try:
        return __import__(name)
    except ImportError as e:
        skip(name, "engine library absent (%s)" % e)
        return None


def check_engines_import_their_driver_at_module_level():
    """For the guarded imports above to MEAN anything.

    A sibling repo imported `launch`/`connect` inside the launch path, so the
    module imported cleanly with no pyppeteer installed: the group never
    skipped, and the CI job that exists to fail on unexpected skips could not
    have caught a broken import. It also let CI run against a stub version
    for a while without anything noticing. This drifts back silently, so it
    is asserted with an `ast` walk rather than trusted.
    """
    for module, driver in DRIVER_IMPORTS.items():
        path = os.path.join(HERE, module + ".py")
        if not os.path.exists(path):
            check("%s exists" % module, False)
            continue
        tree = ast.parse(open(path, encoding="utf-8").read())
        top_level = set()
        for node in tree.body:          # module level ONLY
            if isinstance(node, ast.Import):
                top_level.update(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                top_level.add(node.module.split(".")[0])
        check("%s imports %s at MODULE level" % (module, driver),
              driver in top_level,
              "top-level imports: %s" % sorted(top_level))


def check_shared_calls_bind_against_the_real_signature():
    """§17's check #1, and the one that earns its keep.

    A sibling repo shipped `classify(html, url=…)` in two of three engines
    against a callee taking `status` second, and BOTH crashed on their first
    fetch — invisible to import, --help, compileall, the undefined-name walk
    and 400+ green assertions, because none of those calls a function the way
    a live run does.

    This walks every engine's AST for calls into the shared modules and binds
    each one against the callee's real signature.
    """
    import page_flow
    import product_parser
    import output_writer
    targets = {"page_flow": page_flow, "product_parser": product_parser,
               "output_writer": output_writer}
    bound = 0
    for module in ENGINES + ("scraper_api_client",):
        path = os.path.join(HERE, module + ".py")
        if not os.path.exists(path):
            continue
        source = open(path, encoding="utf-8").read()
        tree = ast.parse(source)
        # Which shared names this file imported directly (`from x import y`).
        direct = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module in targets:
                for alias in node.names:
                    direct[alias.asname or alias.name] = (
                        targets[node.module], alias.name)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            owner = attr = None
            if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                if func.value.id in targets:
                    owner, attr = targets[func.value.id], func.attr
            elif isinstance(func, ast.Name) and func.id in direct:
                owner, attr = direct[func.id]
            if owner is None:
                continue
            # A name that is NOT THERE is the loudest possible failure and
            # this check used to swallow it: `getattr(..., None)` returned
            # None, `not callable(None)` was true, and the call was skipped.
            # Three calls into a page_flow API that does not exist in this
            # repo -- comparable(), next_page_selector(),
            # next_page_candidates(), all of them Tokopedia's, all arriving
            # with copied code -- sat in two engines under a green run of
            # this very function. Absent is not "nothing to bind".
            if not hasattr(owner, attr):
                check("%s.%s exists (called from %s:%d)"
                      % (getattr(owner, "__name__", owner), attr,
                         module + ".py", node.lineno),
                      False,
                      "the engine calls a name the shared module does not "
                      "define; a live run reaches this as AttributeError")
                continue
            callee = getattr(owner, attr)
            if not callable(callee) or inspect.isclass(callee):
                continue
            try:
                signature = inspect.signature(callee)
            except (TypeError, ValueError):
                continue
            positional = [inspect.Parameter.empty] * len(node.args)
            keywords = {}
            for kw in node.keywords:
                if kw.arg is None:          # **kwargs — cannot be checked here
                    keywords = None
                    break
                keywords[kw.arg] = inspect.Parameter.empty
            if keywords is None:
                continue
            try:
                signature.bind(*positional, **keywords)
                bound += 1
            except TypeError as e:
                check("%s:%d %s.%s(...) binds against its real signature"
                      % (module, node.lineno, owner.__name__, attr),
                      False, "%s; signature is %s" % (e, signature))
    check("every shared-module call in every engine binds (%d checked)" % bound,
          bound > 40, "only %d calls were checked — is the walk finding them?"
          % bound)


def _argparse_flags(module_name):
    """Every --flag a module's parser defines, without running the CLI."""
    path = os.path.join(HERE, module_name + ".py")
    tree = ast.parse(open(path, encoding="utf-8").read())
    # Only calls on the argparse parser itself. A browser's option object
    # also has `add_argument`, and counting Chrome's own switches
    # (`--no-sandbox`, `--window-size=…`) as CLI flags made this check
    # compare nonsense.
    parsers = {"p"}
    for node in ast.walk(tree):
        if (isinstance(node, ast.Assign) and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Attribute)
                and node.value.func.attr in ("add_argument_group",
                                             "add_mutually_exclusive_group")):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    parsers.add(target.id)
    flags = set()
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "add_argument"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id in parsers):
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str) \
                        and arg.value.startswith("--"):
                    flags.add(arg.value)
    return flags


# The family's flag contract (CLAUDE.md §9), plus this repo's own additions.
CONTRACT_FLAGS = {
    "--url", "--pages", "--category", "--format", "--out", "--delay",
    "--retries", "--retry-delay", "--concurrency", "--proxy", "--proxy-file",
    "--proxy-rotate", "--proxy-shuffle", "--proxy-block-retries",
    "--twocaptcha-key", "--captcha-api", "--solve-captcha", "--min-score",
    "--cdp-endpoint", "--allow-empty", "--dump-html",
}
# The flags this SITE adds on top of the family contract. `--role`,
# `--location` and `--remote` build a landing URL so a run needs no
# hand-assembled address; there is no `--country` and no `--sort`, because
# Wellfound serves one host in one language and offers no ordering control.
SITE_FLAGS = {"--mode", "--role", "--location", "--remote", "--locale"}


def check_engine_flag_sets():
    """§17's check #2: against the contract AND against each other, both ways.

    A missing flag fails; so does closing a difference the README documents.
    """
    sets = {}
    for module in ENGINES:
        if not os.path.exists(os.path.join(HERE, module + ".py")):
            continue
        sets[module] = _argparse_flags(module)
    for module, flags in sets.items():
        missing = (CONTRACT_FLAGS | SITE_FLAGS) - flags
        check("%s defines every contract flag" % module, not missing,
              "missing %s" % sorted(missing))
    # The ONE documented difference: pyppeteer downloads its own Chromium
    # and could not launch it on the development machine, so it needs a way
    # to point at another one. Its twins have no equivalent because they do
    # not ship a browser. Listed here so that closing the difference — or
    # growing a second one — fails the build (§17).
    DOCUMENTED_DIFFERENCES = {"puppeteer_scraper": {"--chromium-path"}}
    names = sorted(sets)
    for i in range(len(names) - 1):
        a, b = names[i], names[i + 1]
        only_a = sets[a] - sets[b] - DOCUMENTED_DIFFERENCES.get(a, set())
        only_b = sets[b] - sets[a] - DOCUMENTED_DIFFERENCES.get(b, set())
        check("%s and %s define the same flags" % (a, b),
              not only_a and not only_b,
              "only in %s: %s; only in %s: %s"
              % (a, sorted(only_a), b, sorted(only_b)))


BANNED_FLAGS = ("--antidetect", "--country-code")


def check_banned_and_removed_flags():
    """Scoped to the ENGINES.

    `--country` is banned on the ENGINES, and there is no exception here:
    Wellfound serves one host in one language, so such a flag could only
    contradict what the URL already says. On `fingerprint_client.py` the same
    name is legitimate — there it picks a fingerprint locale, not a target —
    which is why this check is scoped to the engines rather than to the tree
    (CLAUDE.md §10).

    What the rule is really about is a flag that can disagree with the URL,
    and the equivalent on this site IS enforced: `--role`, `--location` and
    `--remote` together with `--url` are refused, because a `--location` that
    disagreed with the one already in a /role/l/… path would silently scrape
    a different listing than the address names.
    """
    for module in ENGINES:
        path = os.path.join(HERE, module + ".py")
        if not os.path.exists(path):
            continue
        source = open(path, encoding="utf-8").read()
        for flag in BANNED_FLAGS:
            check("%s does not define %s" % (module, flag),
                  '"%s"' % flag not in source)
        check("%s refuses --country alongside --url" % module,
              "--url already carries the whole query" in source,
              "the refusal that makes --country safe here is missing")


def check_undefined_names_in_every_module():
    """§10: compileall proves a file PARSES, not that its names RESOLVE.

    A live run of a sibling repo's pyppeteer engine died with NameError on a
    line reached only while fetching, after an import had been removed — the
    module imported cleanly, --help worked, compileall passed and CI was
    green. Kept COARSE (pooled bindings, no scope tracking) so it
    under-reports rather than inventing problems.
    """
    import builtins
    modules = [f for f in sorted(os.listdir(HERE))
               if f.endswith(".py") and f != "smoke_test.py"]
    for filename in modules:
        tree = ast.parse(open(os.path.join(HERE, filename), encoding="utf-8").read())
        # Module-level dunders exist without being assigned anywhere.
        defined = set(dir(builtins)) | {"__file__", "__name__", "__doc__",
                                        "__package__", "__spec__"}
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    defined.add((alias.asname or alias.name).split(".")[0])
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef,
                                   ast.ClassDef)):
                defined.add(node.name)
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                defined.add(node.id)
            elif isinstance(node, ast.arg):
                defined.add(node.arg)
            elif isinstance(node, ast.ExceptHandler) and node.name:
                defined.add(node.name)
            elif isinstance(node, ast.alias) and node.asname:
                defined.add(node.asname)
        used = {n.id for n in ast.walk(tree)
                if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}
        unresolved = sorted(used - defined)
        check("%s: every name resolves" % filename, not unresolved,
              "%s" % unresolved)


def _import_graph(entrypoint):
    """Every local module an entrypoint reaches, transitively."""
    local = {f[:-3] for f in os.listdir(HERE) if f.endswith(".py")}
    seen, queue = set(), [entrypoint]
    while queue:
        name = queue.pop()
        if name in seen or name not in local:
            continue
        seen.add(name)
        tree = ast.parse(open(os.path.join(HERE, name + ".py"),
                              encoding="utf-8").read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                queue.extend(a.name.split(".")[0] for a in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                queue.append(node.module.split(".")[0])
    return seen


def check_dockerfile_copies_everything_the_entrypoint_imports():
    """§10: all three repos in this family shipped an image that died with
    ModuleNotFoundError on every invocation, --help included, because
    proxy_pool.py was missing from the COPY list. CI never built the image;
    this check needs no Docker."""
    path = os.path.join(HERE, "Dockerfile")
    if not os.path.exists(path):
        check("Dockerfile exists", False)
        return
    dockerfile = open(path, encoding="utf-8").read()
    # Only the COPY instructions, continuations included — a comment above
    # them naming a file is not a file the image carries.
    copy_lines, joining = [], False
    for line in dockerfile.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if joining or stripped.upper().startswith("COPY "):
            copy_lines.append(stripped)
            joining = stripped.endswith("\\")
    copied = set(re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\.py", " ".join(copy_lines)))
    entry = re.search(r'(?:CMD|ENTRYPOINT)\s*\[?\s*"?(?:python3?"?,\s*"?)?'
                      r'([A-Za-z_][A-Za-z0-9_]*)\.py', dockerfile)
    entrypoint = entry.group(1) if entry else "playwright_scraper"
    needed = _import_graph(entrypoint)
    missing = sorted(needed - copied)
    check("the Dockerfile COPYs every module %s.py imports" % entrypoint,
          not missing, "missing %s" % missing)
    for unwanted in ("smoke_test", "test_smoke"):
        check("the image does not carry %s.py" % unwanted,
              unwanted not in copied)


def check_env_example_documents_exactly_what_the_loader_reads():
    import env_config
    path = os.path.join(HERE, ".env.example")
    if not os.path.exists(path):
        check(".env.example exists", False)
        return
    documented = set(re.findall(r"^\s*#?\s*([A-Z][A-Z0-9_]+)\s*=", 
                                open(path, encoding="utf-8").read(), re.M))
    read = set(env_config.ENV_KEYS)
    check("every variable the loader reads is documented",
          not (read - documented), "undocumented: %s" % sorted(read - documented))
    check("every documented variable is actually read",
          not (documented - read), "unread: %s" % sorted(documented - read))


def check_a_copied_env_example_reads_as_UNSET():
    """§17: `cp .env.example .env` followed by a run must not connect.

    The placeholder check was a literal set in a sibling repo, and the two
    credentialled URLs are documented the way the vendor documents them —
    `ws://{login}-zone-…:{password}@cb.2captcha.com:9222` — so neither
    literal matched, the run connected with the string `{login}-zone-…` as
    its username, and got a 401 a long way from its cause.
    """
    import env_config
    example = os.path.join(HERE, ".env.example")
    if not os.path.exists(example):
        check(".env.example exists", False)
        return
    text = open(example, encoding="utf-8").read()
    values = dict(re.findall(r"^([A-Z][A-Z0-9_]+)=(.*)$", text, re.M))
    check("the example actually sets every variable",
          set(values) == set(env_config.ENV_KEYS),
          "example has %s, loader reads %s"
          % (sorted(values), sorted(env_config.ENV_KEYS)))
    # Every CREDENTIAL must read as unset. The default TARGET must not: it is
    # a real, usable URL, and blanking it would remove the one setting this
    # file exists to make convenient (§17's check #3 says exactly this — the
    # credentials unset, the non-credential default still usable).
    CREDENTIALS = {"TWOCAPTCHA_KEY", "WELLFOUND_CDP_ENDPOINT",
                   "WELLFOUND_PROXY"}
    before = dict(os.environ)
    try:
        for name, raw in values.items():
            os.environ[name] = raw
            got = env_config.env_value(name)
            if name in CREDENTIALS:
                check("a copied .env.example leaves %s unset" % name,
                      got is None, "got %r" % got)
            else:
                check("...while %s stays a usable default" % name,
                      got == raw.strip(), "got %r" % got)
    finally:
        os.environ.clear()
        os.environ.update(before)
    # And the counter-check: a real credential must still come through, or
    # the placeholder rule would have made the loader useless. Deliberately
    # NOT 32 hex characters — that is the shape of a real 2captcha key, and
    # this repo's own credential scan (rightly) fails on one.
    try:
        os.environ["TWOCAPTCHA_KEY"] = "not-a-real-key-but-a-real-value"
        equal("a real value is still read",
              env_config.env_value("TWOCAPTCHA_KEY"),
              "not-a-real-key-but-a-real-value")
    finally:
        os.environ.clear()
        os.environ.update(before)


def check_credential_scan_is_one_implementation_invoked_from_both():
    """§17: two sources of truth, one dead and one holed.

    `.github/ci_checks.py` sat in three repos invoked by NOTHING, while
    tests.yml carried an inline grep doing a narrower version of the same job
    — one that matched only ws:// and wss://, so an http://user:pass@
    credential would have sailed past CI.
    """
    script = os.path.join(HERE, ".github", "ci_checks.py")
    check("the credential scan exists as a script", os.path.exists(script))
    if not os.path.exists(script):
        return
    workflow_dir = os.path.join(HERE, ".github", "workflows")
    workflow = os.path.join(workflow_dir, "tests.yml")
    # Triggered on the whole .github directory being absent, never on this one
    # file being missing: two suites in this family run INSIDE the Docker
    # image, which deliberately COPYs no .github/, and a check that quietly
    # starts passing once its input disappears is the same failure this
    # function is about (CLAUDE.md §22).
    if not os.path.isdir(workflow_dir):
        skip("ci-wiring", "no .github/ in this tree (the Docker image)")
    elif os.path.exists(workflow):
        text = open(workflow, encoding="utf-8").read()
        check("CI INVOKES the script rather than reimplementing it",
              "ci_checks.py" in text)
        # ...and does not ALSO reimplement it. The original version of this
        # check asserted only the first half, and the workflow carried inline
        # `python - <<EOF` copies of the --help and sample checks alongside
        # the call — justified in a comment as keeping the two from drifting
        # apart. They drifted: the inline sample copy still imported the row
        # dataclass under a name this repo renamed, and it failed on the
        # repo's FIRST push while the script it duplicated passed.
        #
        # Scoped to the OFFLINE job, because the docker job legitimately
        # names `sample_output.json` for a different purpose — asserting the
        # image does NOT contain it. A guard that fired there would be wrong,
        # and a guard people have to argue with is one they learn to
        # suppress.
        offline = text.split("  engine-smoke:", 1)[0]
        for marker, what in (("from output_writer import", "the row schema"),
                             ("sample_output.json", "the sample output"),
                             ("subprocess.run([sys.executable", "the --help contract")):
            check("the offline job does not reimplement the check for %s" % what,
                  marker not in offline,
                  "tests.yml's offline job mentions %r — one implementation, "
                  "in ci_checks.py, invoked from both" % marker)
        # And the guard must have had something to read, or it passed for the
        # wrong reason (CLAUDE.md §22).
        check("...and the offline job was actually found to scan",
              "ci_checks.py" in offline, "no offline job in tests.yml")
    result = subprocess.run([sys.executable, script, "--all"], cwd=HERE,
                            capture_output=True, text=True)
    check("the credential scan passes on this repo's own tree",
          result.returncode == 0,
          (result.stdout + result.stderr)[-600:])


BANNED_WORDING = (
    "cloud browser", "antidetect browser", "2scraper Antidetect Browser",
    "gate.2prx.com", "ANTIDETECT_LOCAL_API",
)


def check_the_credential_scan_survives_a_venv_in_the_tree():
    """A guard people have to argue with is one they learn to suppress.

    Found by cloning this repo the way a stranger does and following the
    README: `python3 -m venv` puts a virtualenv in the working tree, and the
    credential scan walked into pip's vendored code and flagged a 32-hex
    string in `_elffile.py` as key-shaped. Correct about the string, wrong
    about the file, and the first thing a new user would have seen.

    The fix is structural rather than a longer list of names — a directory
    holding `pyvenv.cfg` is a virtualenv whatever it is called — and this
    pins BOTH halves, because narrowing a credential scan is exactly how one
    stops catching things. CLAUDE.md §22 records a sibling repo whose scan
    caught an UNTRACKED `.env.bak` holding a live key, so scanning must not
    be reduced to tracked files.
    """
    import importlib.util
    script = os.path.join(HERE, ".github", "ci_checks.py")
    if not os.path.exists(script):
        skip("credential-scan", "no .github/ in this tree (the Docker image)")
        return
    spec = importlib.util.spec_from_file_location("_ci_checks", script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    check("the scan knows a virtualenv structurally, not by name",
          hasattr(mod, "_is_virtualenv"))
    if not hasattr(mod, "_is_virtualenv"):
        return

    with tempfile.TemporaryDirectory() as tmp:
        odd = os.path.join(tmp, "whatever-i-called-it")
        os.makedirs(os.path.join(odd, "lib"))
        open(os.path.join(odd, "pyvenv.cfg"), "w").write("home = /usr\n")
        check("...so a venv under any name is recognised",
              mod._is_virtualenv(pathlib.Path(odd)))
        plain = os.path.join(tmp, "src")
        os.makedirs(plain)
        check("...and an ordinary directory is not",
              not mod._is_virtualenv(pathlib.Path(plain)))

    # The other half: it must still walk files git does not track, because a
    # key pasted into a scratch file is the case this scan exists for.
    scanned = [str(p) for p in mod.scanned_files()]
    check("the scan still reads this repo's own files", len(scanned) > 20,
          "%d file(s)" % len(scanned))
    check("...and is not limited to git's index",
          "git ls-files" not in open(script, encoding="utf-8").read())


def check_banned_wording():
    """§12: enforced by this test rather than by review."""
    for root, dirs, files in os.walk(HERE):
        dirs[:] = [d for d in dirs if d not in
                   (".git", "__pycache__", ".pytest_cache", "node_modules")]
        for filename in files:
            if not filename.endswith((".py", ".md", ".yml", ".yaml", ".txt",
                                      ".toml", ".html", ".example")):
                continue
            path = os.path.join(root, filename)
            text = open(path, encoding="utf-8", errors="replace").read().lower()
            for phrase in BANNED_WORDING:
                if phrase.lower() in text and filename != "smoke_test.py":
                    check("%s contains no %r" % (
                        os.path.relpath(path, HERE), phrase), False)
    check("banned-wording scan ran", True)


def check_concurrency_with_the_browser_stubbed():
    """§10: a live run cannot always reach this machinery.

    Page 1 is fetched alone and decides how many pages there are, so a
    blocked page 1 means the workers never start. Driven directly instead,
    with the browser replaced.
    """
    engine = _import_engine("playwright_scraper")
    if engine is None:
        return

    class Args:
        delay = 0
        retries = 1
        retry_delay = 0
        out = "unused"
        mode = "search"
        sort = "a-z"
        pages = 50

    fetched = []
    import threading
    lock = threading.Lock()

    def fake_fetch(session, args, pool, page_num, url):
        with lock:
            fetched.append(page_num)
        outcome = engine.PageOutcome(page_num=page_num, url=url)
        # Page 6 is the end of this listing: no rows, but a served page.
        outcome.products = [] if page_num >= 6 else [object()] * 15
        outcome.state = "empty" if page_num >= 6 else "content"
        return outcome

    class FakeSession:
        def __init__(self, *a, **k):
            self.pool = None
        def open(self):
            return self
        def close(self):
            pass

    class FakePlaywright:
        def __enter__(self):
            return None
        def __exit__(self, *a):
            return False

    real_fetch = engine._fetch_one_page
    real_session = engine._BrowserSession
    real_pw = engine.sync_playwright
    engine._fetch_one_page = fake_fetch
    engine._BrowserSession = FakeSession
    engine.sync_playwright = lambda: FakePlaywright()
    try:
        specs = [(n, "u%d" % n) for n in range(2, 51)]
        results, unattempted, exhausted = engine._fetch_pages_concurrently(
            Args(), None, specs, 4)
    finally:
        engine._fetch_one_page = real_fetch
        engine._BrowserSession = real_session
        engine.sync_playwright = real_pw

    check("every page fetched was fetched exactly once",
          len(fetched) == len(set(fetched)), "%r" % sorted(fetched))
    check("dispatch STOPPED at the end of the listing", exhausted)
    check("...so the 49 queued pages cost far fewer fetches",
          len(fetched) < 15, "fetched %d of 49" % len(fetched))
    check("unattempted pages are REPORTED, not counted as failed",
          len(unattempted) > 0 and all(isinstance(n, int) for n in unattempted))
    equal("attempted + unattempted covers the whole queue",
          len(set(fetched)) + len(unattempted), 49)
    equal("outcomes are restorable to page order",
          [o.page_num for o in sorted(results, key=lambda o: o.page_num)],
          sorted(o.page_num for o in results))


def check_a_dead_worker_neither_hangs_nor_loses_its_siblings():
    engine = _import_engine("playwright_scraper")
    if engine is None:
        return

    class Args:
        delay = 0
        retries = 1
        retry_delay = 0
        out = "unused"
        mode = "search"
        sort = "a-z"
        pages = 10

    def exploding_fetch(session, args, pool, page_num, url):
        if page_num == 3:
            raise RuntimeError("worker died")
        outcome = engine.PageOutcome(page_num=page_num, url=url)
        outcome.products = [object()] * 15
        outcome.state = "content"
        return outcome

    class FakeSession:
        def __init__(self, *a, **k):
            self.pool = None
        def open(self):
            return self
        def close(self):
            pass

    class FakePlaywright:
        def __enter__(self):
            return None
        def __exit__(self, *a):
            return False

    real_fetch, real_session, real_pw = (engine._fetch_one_page,
                                         engine._BrowserSession,
                                         engine.sync_playwright)
    engine._fetch_one_page = exploding_fetch
    engine._BrowserSession = FakeSession
    engine.sync_playwright = lambda: FakePlaywright()
    try:
        specs = [(n, "u%d" % n) for n in range(2, 8)]
        results, unattempted, exhausted = engine._fetch_pages_concurrently(
            Args(), None, specs, 3)
    finally:
        engine._fetch_one_page = real_fetch
        engine._BrowserSession = real_session
        engine.sync_playwright = real_pw

    check("the run returned rather than hanging", True)
    check("the dead worker's siblings still delivered their pages",
          len(results) >= 3, "%d results" % len(results))
    check("page 3 is not reported as a success",
          3 not in [o.page_num for o in results])


def check_worker_pools_start_on_different_exits():
    engine = _import_engine("playwright_scraper")
    if engine is None:
        return
    from proxy_pool import ProxyPool
    pool = ProxyPool(["http://a:1", "http://b:2", "http://c:3"], rotate="per-run")
    firsts = [engine._worker_pool(pool, i).current for i in range(3)]
    equal("three workers start on three different exits",
          len(set(firsts)), 3)
    equal("a missing pool stays missing", engine._worker_pool(None, 0), None)


def check_fingerprint_kwargs_are_ones_the_driver_accepts():
    """§10: an unknown key in new_context(**kwargs) is a TypeError at launch,
    on the PAID path, at runtime."""
    engine = _import_engine("playwright_scraper")
    if engine is None:
        return
    try:
        from fingerprint_client import playwright_context_kwargs
    except ImportError as e:
        skip("fingerprint", str(e))
        return
    sample = {"id": "x", "country": "US",
              "userAgent": "Mozilla/5.0 Chrome/140.0.0.0",
              "screen": {"width": 1920, "height": 1080},
              "timezone": "America/New_York", "language": "en-US",
              "devicePixelRatio": 2}
    kwargs = playwright_context_kwargs(sample)
    from playwright.sync_api import sync_playwright  # noqa: F401
    import playwright.sync_api as pw_api
    signature = inspect.signature(pw_api.Browser.new_context)
    unknown = [k for k in kwargs if k not in signature.parameters]
    check("every fingerprint kwarg is one new_context accepts", not unknown,
          "unknown: %s" % unknown)


def check_every_engine_exposes_the_same_public_surface():
    for module in ENGINES:
        engine = _import_engine(module)
        if engine is None:
            continue
        for name in ("scrape", "parse_args", "PageOutcome", "_fetch_one_page",
                     "_parse_for_mode", "_target_url"):
            check("%s.%s exists" % (module, name), hasattr(engine, name))
        outcome = engine.PageOutcome(page_num=1, url="u")
        for field_name in ("state", "total_available", "total_companies",
                           "pages_available", "echoed_page", "products",
                           "blocked_by", "load_failed", "final_url"):
            check("%s.PageOutcome carries %r" % (module, field_name),
                  hasattr(outcome, field_name))
        check("%s.PageOutcome.ok is True for a fresh outcome" % module,
              outcome.ok)
        equal("%s shares CORE_FIELDS with its twins" % module,
              tuple(engine.CORE_FIELDS),
              ("title", "url", "sku", "company_name", "company_id"))
        # Shorter on purpose: a job page's schema.org block publishes no
        # company id, so checking one source's fields against another
        # source's floor tells a correct run it is broken.
        equal("%s shares CORE_FIELDS_JOB with its twins" % module,
              tuple(engine.CORE_FIELDS_JOB),
              ("title", "url", "sku", "company_name"))
        equal("%s shares CORE_FIELD_FLOOR with its twins" % module,
              engine.CORE_FIELD_FLOOR, 99)


def check_every_solve_is_counted_against_the_budget():
    """`SOLVES_PER_PAGE` is a MONEY limit, so every call that can buy must be
    counted — CLAUDE.md §17's "a policy constant nothing reads".

    `handle_captcha_if_present` is called TWICE per attempt in every engine:
    once before the page is classified (so a challenge is cleared before
    anything is judged) and once after, for the state that says the page
    really is gated. Only the second was counted, and the first therefore
    bought a solve on every block attempt, for free, silently.

    Measured live 2026-09-17 from a datacenter address, which meets a real
    Cloudflare challenge on every fetch: one page bought THREE Turnstile
    solves before the fix and ONE after, with the cap set to 1 both times.
    Every token was refused either way, so the three purchases bought
    nothing at all.

    Asserted on the source, because the branch only runs when a challenge is
    actually rendered and the suite must pass offline.
    """
    for module in ENGINES:
        path = os.path.join(HERE, module + ".py")
        if not os.path.exists(path):
            continue
        source = open(path, encoding="utf-8").read()
        calls = source.count("if handle_captcha_if_present(")
        check("%s calls the solver from two places, as designed" % module,
              calls == 2, "found %d call site(s)" % calls)
        # Both must sit under a budget test. Counting the guard is the cheap
        # way to say that without parsing the control flow.
        guards = source.count("_solve_budget(args, solves_bought)")
        check("%s gates BOTH solve call sites on the budget" % module,
              guards == calls,
              "%d budget guard(s) for %d call site(s)" % (guards, calls))
        check("%s increments the counter beside each guard" % module,
              source.count("solves_bought += 1") == calls,
              "%d increment(s) for %d call site(s)"
              % (source.count("solves_bought += 1"), calls))
    # And the constant must still be the one thing that decides it.
    import page_flow
    equal("at most one purchase per page", page_flow.SOLVES_PER_PAGE, 1)


def check_a_dead_proxy_is_reported_as_a_proxy_failure():
    """CLAUDE.md §8: a proxy failure is not a timeout, and the two want
    opposite responses — another try at the same exit versus a different one.

    The engines all compute the reason (`_proxy_failure`) and, WITH a pool,
    log it on rotation. Without a pool — a single `--proxy`, which is the
    common case — an earlier version dropped it and reported only "gave up
    loading", so a refused proxy read exactly like a slow site. Found by
    running it rather than by reading it: `--proxy http://127.0.0.1:9`
    printed the generic message while `_proxy_failure()` had already
    identified ERR_PROXY_CONNECTION_FAILED.

    Asserted on the SOURCE rather than by launching a browser, because the
    branch only runs when a navigation fails and the suite must pass with no
    engine library installed at all.
    """
    for module in ENGINES:
        path = os.path.join(HERE, module + ".py")
        if not os.path.exists(path):
            continue
        source = open(path, encoding="utf-8").read()
        # Anchored on the GIVE-UP branch — the one that reports and returns —
        # not on the `if load_failed: break` inside the retry loop, which
        # comes first in the file and would make this check read the wrong
        # block and pass for the wrong reason (CLAUDE.md §22).
        marker = "        outcome.load_failed = True"
        if marker not in source:
            check("%s has a give-up branch to check" % module, False)
            continue
        end = source.index(marker)
        branch = source[max(0, end - 1800):end]
        check("%s names the proxy when the proxy was the fault" % module,
              "if exit_failed:" in branch,
              "the give-up branch does not consult exit_failed")
        check("%s still has a plain message for a non-proxy failure" % module,
              "after %d attempt(s)" in branch,
              "the non-proxy branch was lost")
    # ...and the detector the branch depends on must actually match the
    # string Chromium produces. Measured live 2026-09-17 against a dead
    # local port: `net::ERR_PROXY_CONNECTION_FAILED`.
    engine = _import_engine("playwright_scraper")
    if engine is None:
        skip("proxy-failure", "playwright_scraper not importable here")
    else:
        class _E(Exception):
            pass
        got = engine._proxy_failure(
            _E("Page.goto: net::ERR_PROXY_CONNECTION_FAILED at https://x/"))
        equal("the marker list matches what Chromium really raises", got,
              "ERR_PROXY_CONNECTION_FAILED")
        equal("...and a plain timeout is NOT read as a proxy failure",
              engine._proxy_failure(_E("Page.goto: Timeout 25000ms exceeded.")),
              "")


def check_engines_do_not_evaluate_a_string_in_the_browser():
    """§18: a site whose CSP omits `unsafe-eval` kills wait_for_function with
    an EvalError and takes the run down with exit 1. Wellfound has not been
    measured for that, and the cheap habit costs nothing where it would have
    been allowed."""
    for module in ENGINES:
        path = os.path.join(HERE, module + ".py")
        if not os.path.exists(path):
            continue
        tree = ast.parse(open(path, encoding="utf-8").read())
        called = {node.func.attr for node in ast.walk(tree)
                  if isinstance(node, ast.Call)
                  and isinstance(node.func, ast.Attribute)}
        for banned in ("wait_for_function", "waitForFunction", "waitFor"):
            check("%s never CALLS %s" % (module, banned), banned not in called,
                  "poll through page_flow.wait_for_count instead")


def check_credentials_never_reach_a_log():
    """§8: an EXCEPTION MESSAGE is a log, and the masker must be GLOBAL.

    A Playwright connection error repeats the endpoint five times (the
    message plus a four-line call log), so a masker handling only the first
    occurrence prints the password four times and looks like it is working.
    """
    for module in ENGINES:
        engine = _import_engine(module)
        if engine is None:
            continue
        masked = engine._mask_credentials(
            "tried ws://u:supersecret@h1:9222 and ws://u:supersecret@h2:9222 "
            "and again ws://u:supersecret@h1:9222")
        check("%s masks EVERY occurrence" % module,
              "supersecret" not in masked, masked)
        check("%s keeps the host and port, which are the useful half" % module,
              "h1:9222" in masked and "h2:9222" in masked, masked)
    from proxy_pool import mask
    masked = mask("http://user:secret@exit.example.com:2334")
    check("proxy_pool.mask hides the password", "secret" not in masked)
    check("proxy_pool.mask keeps the exit", "exit.example.com:2334" in masked)


def check_sample_output_matches_the_schema():
    from output_writer import JobPosting
    expected = [f.name for f in fields(JobPosting)]
    json_path = os.path.join(HERE, "sample_output.json")
    csv_path = os.path.join(HERE, "sample_output.csv")
    if not os.path.exists(json_path):
        check("sample_output.json exists", False)
        return
    rows = json.load(open(json_path, encoding="utf-8"))
    check("sample_output.json holds rows", bool(rows))
    equal("sample_output.json keys match the schema, in order",
          list(rows[0].keys()), expected)
    check("sample_output.json is from a real run (wellfound.com rows)",
          all(r["source"] == "wellfound.com" for r in rows))
    check("...and carries no fabrication markers",
          not any("example" in (r.get("url") or "").lower() or
                  "lorem" in (r.get("title") or "").lower() for r in rows))
    if os.path.exists(csv_path):
        header = next(csv.reader(open(csv_path, encoding="utf-8")))
        equal("sample_output.csv header matches the schema", header, expected)


def check_readme_numbers_are_not_stale():
    """§17's check #4: diff every numeric claim against what is on disk.

    Only the figures that MUST hold are pinned: a number that legitimately
    varies between runs is written as a range in the README and not checked
    here.
    """
    path = os.path.join(HERE, "README.md")
    if not os.path.exists(path):
        check("README.md exists", False)
        return
    readme = open(path, encoding="utf-8").read()
    import product_parser as P
    # Wellfound publishes no page cap of its own — 47 pages really is all
    # 923 companies — so there is no MAX_PAGES to check the README against.
    # What IS worth pinning is the page size the site states, because the
    # README quotes it while explaining that a "page" is twenty COMPANIES
    # and not twenty jobs.
    if "20 companies" in readme or "twenty companies" in readme:
        equal("the README's page size matches the parser", P.PAGE_SIZE, 20)
    from output_writer import JobPosting
    column_count = len(fields(JobPosting))
    claimed = re.findall(r"(\d+)\s+columns", readme)
    for number in claimed:
        equal("the README's column count matches the schema",
              int(number), column_count)


_TREE_BEFORE = None


def _tree_state():
    result = subprocess.run(["git", "status", "--porcelain"], cwd=HERE,
                            capture_output=True, text=True)
    if result.returncode != 0:
        return None
    return sorted(line for line in result.stdout.splitlines()
                  if not line.endswith(".pyc"))


def check_no_test_mutates_the_working_tree():
    """§10: one suite used its own file as a fake chromedriver and chmod'd it
    to 755, leaving a mode change in git status.

    Compares the tree against how it looked when the suite STARTED, not
    against a clean checkout — otherwise this is permanently red while
    anyone is editing, and a check that is always red teaches everyone to
    ignore checks.
    """
    if _TREE_BEFORE is None:
        skip("git status", "not a git repository")
        return
    after = _tree_state()
    changed = sorted(set(after) - set(_TREE_BEFORE))
    check("the suite itself changed nothing in the working tree",
          not changed, "%s" % changed)


def check_captcha_capability_claims_match_the_code():
    """§19: the most expensive bug this family can ship is a SENTENCE.

    It fails in both directions and this family has shipped both:

      * saying a captcha CANNOT be solved, when the true statement is that
        THIS REPO does not implement the task type. 2Captcha solves
        enterprise reCAPTCHA and Cloudflare Turnstile and has for years, so
        such a sentence tells a reader not to buy something that works.
      * saying this repo DOES solve something it builds no task type for --
        which is what the README said here: it billed the Managed Challenge
        solve to `--twocaptcha-key`, while the only thing that clears one is
        `Captcha.setAutoSolve` over `--cdp-endpoint`.

    Neither is visible to any other check: nothing fails, nothing crashes,
    and the output is correct.
    """
    readme = open(os.path.join(HERE, "README.md"), encoding="utf-8").read()
    solver = open(os.path.join(HERE, "captcha_solver.py"), encoding="utf-8").read()
    low = readme.lower()

    # Conclusions about the PRODUCT. Phrases about a page carrying no widget
    # are deliberately absent -- a page really can carry none, and calling
    # THAT unsolvable is honest.
    for phrase in ("cannot be solved", "can't be solved", "neither is solvable",
                   "is not solvable", "solver is inapplicable", "no solver can"):
        check("README: no %r -- write 'this repo does not implement X'" % phrase,
              phrase not in low)

    # The positive direction, stated as a PAIRING rather than a keyword
    # search so it cannot go quiet by accident: if the task type is absent,
    # the README has to say so in those words.
    if "TurnstileTaskProxyless" not in solver:
        check("README says plainly that TurnstileTaskProxyless is not built here",
              "does not implement `turnstiletaskproxyless`" in low,
              "the solver builds no Turnstile task, so the README must not let "
              "a reader believe --twocaptcha-key clears a Managed Challenge")
        check("...and the Managed Challenge is not billed to --twocaptcha-key",
              "(`--twocaptcha-key`) - for the managed challenge" not in low
              and "(`--twocaptcha-key`) \u2014 for the managed challenge" not in low)
    else:
        check("a built Turnstile task needs the render interception too",
              "TURNSTILE_INTERCEPT_JS" in solver)

    # Whatever the README credits with clearing the challenge must be a thing
    # the engines actually do.
    if "setautosolve" in low:
        srcs = ""
        for name in ("playwright_scraper.py", "selenium_scraper.py",
                     "puppeteer_scraper.py"):
            path = os.path.join(HERE, name)
            if os.path.exists(path):
                srcs += open(path, encoding="utf-8").read()
        check("README credits Captcha.setAutoSolve, and an engine calls it",
              "Captcha.setAutoSolve" in srcs)
def check_no_statement_is_unreachable():
    """A statement sitting after a return/raise/break/continue in the SAME
    block, which therefore can never run.

    Narrow on purpose: it makes no claim about reachability in general, only
    about a block whose control flow has already left. Measured across the
    eighteen repos of this family on 2026-09-16 it reported six problems and
    zero false positives.

    `check_undefined_names_in_every_module` cannot see this class at all, by
    design -- it pools every binding in the file rather than tracking scopes,
    so a name used inside dead code passes as long as anything else in the
    module binds it. What was hiding in that blind spot here, and in five
    sibling repos, byte for byte: a function whose `def` line had been lost,
    leaving its docstring and body absorbed into the end of the function
    above it. Present since this repo's first commit, invisible to import,
    `--help`, `compileall`, and every green run of this suite.
    """
    for filename in sorted(f for f in os.listdir(HERE) if f.endswith(".py")):
        tree = ast.parse(open(os.path.join(HERE, filename),
                              encoding="utf-8").read())
        dead = []
        for node in ast.walk(tree):
            for field in ("body", "orelse", "finalbody"):
                block = getattr(node, field, None)
                if not isinstance(block, list):
                    continue
                for i, stmt in enumerate(block[:-1]):
                    if isinstance(stmt, (ast.Return, ast.Raise,
                                         ast.Continue, ast.Break)):
                        dead.append(block[i + 1].lineno)
                        break
        check("%s: no statement the control flow can never reach" % filename,
              not dead, "first at line %d" % min(dead) if dead else "")


def check_x_debug_header_is_redacted():
    """SECURITY.md names the Scraper API's x-debug header as a place
    credentials reach a log unmasked. It was then logged verbatim.

    The fixtures are assembled from pieces rather than written out whole,
    because this file is scanned by the credential check like every other
    and a fixture that LOOKS like a live key fails it. They are the SHAPES a
    credential takes, not the literals this repo happens to contain today.
    """
    try:
        import scraper_api_client as sac
    except ImportError:
        return

    pw = "SeCr" + "EtPw"
    key = "abcdef01" * 4
    raw = ("cdpurl=ws://acct-zone-scraping_browser-pid-7:" + pw
           + "@cb.2captcha.com:9222 cost=0.00145 key=" + key + " status=200")
    out = sac._redact_debug_header(raw)
    check("x-debug: the credential and the key are gone",
                 pw not in out and key not in out)
    check("x-debug: the cost, host and status survive",
                 "cost=0.00145" in out and "cb.2captcha.com:9222" in out
                 and "status=200" in out)

    s1, s2 = "secret" + "one", "secret" + "two"
    two = sac._redact_debug_header(
        "a=http://u1:" + s1 + "@h1:1 b=http://u2:" + s2 + "@h2:2")
    check("x-debug: both credentials are masked, not just the first",
                 s1 not in two and s2 not in two)

    src = inspect.getsource(sac)
    check("x-debug: the log line calls the redactor",
                 'logger.info("x-debug: %s", _redact_debug_header(debug))' in src)



CHECKS = [v for k, v in sorted(globals().items()) if k.startswith("check_")]


def main():
    global VERBOSE
    parser = argparse.ArgumentParser(description="wellfound-scraper offline suite")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    VERBOSE = args.verbose

    global _TREE_BEFORE
    _TREE_BEFORE = _tree_state()

    for fn in CHECKS:
        if VERBOSE:
            print("\n== %s" % fn.__name__)
        try:
            fn()
        except Exception as e:  # noqa: BLE001 — a broken check is a failure
            import traceback
            FAILURES.append("%s raised %s: %s" % (fn.__name__, type(e).__name__, e))
            print("  ERROR %s raised %s: %s" % (fn.__name__, type(e).__name__, e))
            if VERBOSE:
                traceback.print_exc()

    print("\n%d checks passed, %d failed, %d group(s) skipped."
          % (PASSED, len(FAILURES), len(SKIPS)))
    for line in SKIPS:
        print("  skipped: %s" % line)
    if FAILURES:
        print("\nFailures:")
        for line in FAILURES:
            print("  - %s" % line)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
