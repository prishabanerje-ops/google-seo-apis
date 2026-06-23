# Step 4: Run PageSpeed Insights

**Goal:** Check any URL's Lighthouse scores and Core Web Vitals in one command.

---

## 4.1 Activate the Virtual Environment

**Mac/Linux:**
```bash
cd /path/to/google-seo-apis
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
cd C:\path\to\google-seo-apis
venv\Scripts\activate
```

You'll see `(venv)` in your prompt when the environment is active.

---

## 4.2 Run a Basic Check

```bash
python scripts/psi.py https://example.com
```

**Example output:**
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

> **About CrUX data:** "Real Users" data comes from Chrome user experience data.
> It only appears when your URL has sufficient real-user traffic in Chrome.
> New or low-traffic pages show "No field data available for this URL
> (insufficient traffic)" — Lighthouse lab data is still shown.

---

## 4.3 Check Desktop

```bash
python scripts/psi.py https://example.com --strategy desktop
```

Run both mobile and desktop in one command:

```bash
python scripts/psi.py https://example.com --strategy both
```

---

## 4.4 Understanding the Scores

**Lighthouse scores:**

| Score | Rating | What it means |
|-------|--------|--------------|
| 90–100 | ✓ Good | No action needed |
| 50–89 | ⚠ Needs Improvement | Worth investigating |
| 0–49 | ✗ Poor | High priority fix |

**Core Web Vitals thresholds:**

| Metric | Good | Poor | What it measures |
|--------|------|------|-----------------|
| LCP | < 2.5s | ≥ 4.0s | Largest visible element load time |
| INP | < 200ms | ≥ 500ms | Response time to interactions |
| CLS | < 0.1 | ≥ 0.25 | Visual stability (layout shift) |
| FCP | < 1.8s | ≥ 3.0s | First content appears on screen |

LCP and INP have the most direct impact on Google Search rankings.

---

**Next step:** [Run Search Console →](05-running-gsc.md)
