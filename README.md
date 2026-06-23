# Google SEO APIs

![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)
![License MIT](https://img.shields.io/badge/License-MIT-green)
![Works on Mac + Windows](https://img.shields.io/badge/Platform-Mac%20%7C%20Windows-lightgrey)

Check any website's PageSpeed score and pull Google Search Console data from
your terminal — with one setup command, no manual pip installs.

---

## Quick Start

**Prerequisites:** [Python 3.8+](https://www.python.org/downloads/) and [Git](https://git-scm.com/)

```bash
# 1. Clone
git clone https://github.com/prishabanerje-ops/google-seo-apis
cd google-seo-apis

# 2. Setup (Mac/Linux)
bash setup/setup.sh

# Windows (PowerShell):
# .\setup\setup.ps1

# 3. Run
source venv/bin/activate          # Mac/Linux
# venv\Scripts\activate           # Windows

python scripts/psi.py https://example.com
```

---

## What You Can Do

**PageSpeed Insights** — Lighthouse scores + real-user Core Web Vitals in one call:

```
PageSpeed Insights — https://example.com (mobile)
───────────────────────────────────────────────────────
LIGHTHOUSE (Lab Data)
  Performance       72   ⚠ Needs Improvement
  Accessibility     94   ✓ Good
  Best Practices    83   ✓ Good
  SEO               91   ✓ Good

CORE WEB VITALS (Real Users — CrUX Field Data)
  LCP   3.2s    ✗ Poor           (target: < 2.5s)
  INP   180ms   ✓ Good           (target: < 200ms)
  CLS   0.05    ✓ Good           (target: < 0.1)
  FCP   1.9s    ✓ Good           (target: < 1.8s)
```

**Google Search Console** — top queries and pages with clicks, impressions, CTR:

```
GSC Search Analytics — sc-domain:example.com
Last 30 days | Top 10 queries
──────────────────────────────────────────────────────────────────────
#   Query                                   Clicks  Impressions    CTR    Pos
1   health insurance uae                      1240        18400   6.7%    3.2
2   buy health insurance online                830        12100   6.9%    2.8
```

---

## Setup Guide

Follow these steps in order:

1. [Create a Google Cloud Project](docs/01-google-cloud-project.md)
2. [Enable the APIs](docs/02-enable-apis.md)
3. [Set up credentials](docs/03-credentials.md) — API key (PSI) + Service Account (GSC)

Then run the setup script from Quick Start above.

---

## Running the Scripts

- [PageSpeed Insights guide](docs/04-running-psi.md) — strategies, score interpretation, CrUX data
- [Search Console guide](docs/05-running-gsc.md) — queries, pages, date range, CSV export

---

## Advanced Usage

[Environment variables, JSON output, scheduled runs, scripting](docs/06-advanced.md)

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: googleapiclient` | Activate venv first: `source venv/bin/activate` |
| PSI returns error 400 | URL must start with `https://` |
| GSC returns 403 | Add the service account email to Search Console users |
| No CrUX field data shown | Normal for low-traffic URLs — Lighthouse data still shown |
| `setup.ps1` blocked on Windows | Run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` |

---

## License

MIT — see [LICENSE](LICENSE)
