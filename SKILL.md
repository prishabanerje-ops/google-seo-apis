---
name: google-seo-apis
description: >
  PageSpeed Insights v5 + Core Web Vitals (CrUX real-user field data) and
  Google Search Console Search Analytics via OAuth. Use when the user asks
  about "PageSpeed", "PSI", "Core Web Vitals", "CWV", "LCP", "INP", "CLS",
  "FCP", "Lighthouse", "CrUX", "real user metrics", "Search Console",
  "GSC", "clicks", "impressions", "CTR", "position", "search traffic",
  "top queries", "top pages", or "last N days traffic".
user-invokable: true
argument-hint: "[pagespeed|gsc|check|auth] [url|property]"
metadata:
  author: Aakash Srivastava
  version: "1.0.0"
  category: seo
---

# Google SEO APIs

Lightweight skill with two scripts:

- **`psi.py`** — PageSpeed Insights v5: Lighthouse lab scores + CrUX real-user
  field data (LCP, INP, CLS, FCP) in a single API call. Pure Python stdlib.
- **`gsc.py`** — Google Search Console Search Analytics: top queries and pages
  with clicks, impressions, CTR, position. Uses OAuth Desktop App credentials.

**Repo:** `~/Documents/google-seo-apis` (adjust to actual clone location)
**Venv:** `venv/` inside the repo root

---

## Prerequisites

Check credential status before running any command:

```bash
cd ~/Documents/google-seo-apis
source venv/bin/activate
python scripts/auth.py --check
```

Expected output when ready:
```
  API key        ✓ OK
  OAuth token    ✓ OK (expires YYYY-MM-DD)
  GSC property   ✓ OK (sc-domain:...)
```

If anything shows `✗ MISSING`, see the Setup section below.

---

## Commands

### PageSpeed + CrUX

```bash
python scripts/psi.py <url> [--strategy mobile|desktop|both] [--json]
```

**Examples:**
```bash
# Default (both strategies)
python scripts/psi.py https://example.com

# Mobile only
python scripts/psi.py https://example.com --strategy mobile

# JSON output for piping
python scripts/psi.py https://example.com --json
```

**Output sections:**
- `LIGHTHOUSE (Lab Data)` — Performance, Accessibility, Best Practices, SEO scores
- `CORE WEB VITALS (Real Users — CrUX Field Data)` — LCP, INP, CLS, FCP with
  Good / Needs Improvement / Poor ratings

**CWV thresholds:**

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| LCP | ≤ 2.5s | 2.5s–4.0s | > 4.0s |
| INP | ≤ 200ms | 200ms–500ms | > 500ms |
| CLS | ≤ 0.1 | 0.1–0.25 | > 0.25 |
| FCP | ≤ 1.8s | 1.8s–3.0s | > 3.0s |

If CrUX shows "No field data available": the URL has insufficient Chrome traffic.
Show Lighthouse lab scores only and note the limitation.

---

### Google Search Console

```bash
python scripts/gsc.py [--property sc-domain:example.com] [--days 30]
                      [--dimension query|page] [--top 10]
                      [--csv output.csv] [--json]
```

**Examples:**
```bash
# Last 7 days, top 10 queries
python scripts/gsc.py --days 7

# Last 30 days, by page (not query)
python scripts/gsc.py --days 30 --dimension page

# Top 25 queries, export to CSV
python scripts/gsc.py --top 25 --csv traffic.csv

# Different property
python scripts/gsc.py --property https://www.example.com/ --days 14

# JSON output
python scripts/gsc.py --days 7 --json
```

**Output columns:** Rank, Query/Page, Clicks, Impressions, CTR, Position

**`--json` format:**
```json
{
  "property": "sc-domain:example.com",
  "dimension": "query",
  "days": 7,
  "rows": [{"query": "...", "clicks": 120, "impressions": 1800, "ctr": 0.067, "position": 3.2}]
}
```

**Note:** GSC data has a 2–3 day lag. Today's traffic will not appear yet.

---

## Setup

### First-time setup

```bash
cd ~/Documents/google-seo-apis
bash setup/setup.sh          # Mac/Linux
# or: .\setup\setup.ps1      # Windows PowerShell
```

### API Key (for PSI)

Add to `~/.config/google-seo-apis/config.json`:
```json
{
  "api_key": "AIzaSy..."
}
```

PSI works without an API key but at a lower rate limit (unauthenticated).

### OAuth (for GSC)

One-time browser login:
```bash
python scripts/auth.py --auth --creds ~/client_secret.json
```

A browser window opens → sign in with your Google account → grant access.
Token is saved to `~/.config/google-seo-apis/oauth-token.json` and auto-refreshes.

See `docs/03-credentials.md` for full instructions including how to create
the `client_secret.json` file in Google Cloud Console.

### GSC Property

Add your property to config:
```json
{
  "api_key": "AIzaSy...",
  "oauth_client_path": "/Users/you/client_secret.json",
  "gsc_property": "sc-domain:yourdomain.com"
}
```

Property formats:
- `sc-domain:example.com` — domain property (recommended)
- `https://www.example.com/` — URL prefix property

---

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `OAuth token: MISSING` | No token saved | Run `python scripts/auth.py --auth --creds ~/client_secret.json` |
| `Token refresh failed` | Refresh token expired | Re-run `--auth` |
| `HttpError 403` on GSC | OAuth not granted access | Ensure you own the GSC property in your Google account |
| `No field data available` | URL has low Chrome traffic | Show Lighthouse lab data only |
| `PSI 400 Bad Request` | Invalid or private URL | Check URL is publicly reachable |
| `ModuleNotFoundError` | Venv not activated | `source venv/bin/activate` first |

---

## Output Conventions

- Always show CWV ratings as: `✓ Good`, `⚠ Needs Improvement`, `✗ Poor`
- For GSC results, highlight quick wins: queries ranked 4–10 with > 500 impressions
- Note GSC data lag when reporting recent traffic
- After analysis, offer: "Export to CSV with `--csv filename.csv`"
