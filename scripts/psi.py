#!/usr/bin/env python3
"""
PageSpeed Insights v5 + CrUX field data checker.

A single PSI v5 API call returns both Lighthouse lab scores and CrUX real-user
field data (loadingExperience). No separate CrUX API call is needed.

CrUX field data is only present when the URL has enough real-user Chrome traffic.
If loadingExperience is empty, "No field data available" is shown and lab data only.

Author: Aakash Srivastava

Usage:
    python scripts/psi.py https://example.com
    python scripts/psi.py https://example.com --strategy desktop
    python scripts/psi.py https://example.com --strategy both
    python scripts/psi.py https://example.com --json
"""

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auth import get_api_key

PSI_ENDPOINT = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
TIMEOUT = 30

CWV_THRESHOLDS = {
    "lcp": {"good": 2500,  "poor": 4000,  "unit": "ms", "label": "LCP"},
    "inp": {"good": 200,   "poor": 500,   "unit": "ms", "label": "INP"},
    "cls": {"good": 0.1,   "poor": 0.25,  "unit": "",   "label": "CLS"},
    "fcp": {"good": 1800,  "poor": 3000,  "unit": "ms", "label": "FCP"},
}

PRIVATE_PATTERNS = (
    "localhost", "127.", "10.", "192.168.", "169.254.",
    "172.16.", "172.17.", "172.18.", "172.19.", "172.20.",
    "172.21.", "172.22.", "172.23.", "172.24.", "172.25.",
    "172.26.", "172.27.", "172.28.", "172.29.", "172.30.",
    "172.31.",
)


def validate_url(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        raise ValueError(f"URL must start with http:// or https://: {url}")
    parsed = urllib.parse.urlparse(url)
    host = parsed.hostname or ""
    for pat in PRIVATE_PATTERNS:
        if host == pat.rstrip(".") or host.startswith(pat):
            raise ValueError(f"Private/loopback URLs are not allowed: {url}")
    return url


def format_score(score: float) -> str:
    pct = int(round(score * 100))
    if score >= 0.90:
        rating = "✓ Good"
    elif score >= 0.50:
        rating = "⚠ Needs Improvement"
    else:
        rating = "✗ Poor"
    return f"{pct:<5}{rating}"


def rate_cwv(metric: str, value: float) -> str:
    t = CWV_THRESHOLDS[metric]
    if value <= t["good"]:
        return "✓ Good"
    elif value < t["poor"]:
        return "⚠ Needs Improvement"
    else:
        return "✗ Poor"


def run_psi(url: str, strategy: str, api_key: Optional[str]) -> dict:
    params = {
        "url": url,
        "strategy": strategy,
        "category": ["performance", "accessibility", "best-practices", "seo"],
    }
    if api_key:
        params["key"] = api_key
    query = urllib.parse.urlencode(params, doseq=True)
    full_url = f"{PSI_ENDPOINT}?{query}"
    with urllib.request.urlopen(full_url, timeout=TIMEOUT) as resp:
        return json.loads(resp.read())


def _extract_cwv(loading_exp: dict) -> Optional[dict]:
    metrics = loading_exp.get("metrics", {})
    if not metrics:
        return None
    raw = {
        "lcp": metrics.get("LARGEST_CONTENTFUL_PAINT_MS", {}).get("percentile"),
        "inp": metrics.get("INTERACTION_TO_NEXT_PAINT", {}).get("percentile"),
        "cls": (metrics.get("CUMULATIVE_LAYOUT_SHIFT_SCORE", {}).get("percentile") or 0) / 100,
        "fcp": metrics.get("FIRST_CONTENTFUL_PAINT_MS", {}).get("percentile"),
    }
    return raw if any(v is not None for v in raw.values()) else None


def print_report(data: dict, url: str, strategy: str):
    SEP = "─" * 55
    print(f"\nPageSpeed Insights — {url} ({strategy})")
    print(SEP)

    cats = data.get("lighthouseResult", {}).get("categories", {})
    print("LIGHTHOUSE (Lab Data)")
    for key, label in [
        ("performance",    "Performance"),
        ("accessibility",  "Accessibility"),
        ("best-practices", "Best Practices"),
        ("seo",            "SEO"),
    ]:
        score = cats.get(key, {}).get("score")
        if score is not None:
            print(f"  {label:<18}{format_score(score)}")

    print()
    cwv = _extract_cwv(data.get("loadingExperience", {}))
    if cwv:
        print("CORE WEB VITALS (Real Users — CrUX Field Data)")
        targets = {"lcp": "< 2.5s", "inp": "< 200ms", "cls": "< 0.1", "fcp": "< 1.8s"}
        labels  = {"lcp": "LCP", "inp": "INP", "cls": "CLS", "fcp": "FCP"}
        for key in ("lcp", "inp", "cls", "fcp"):
            val = cwv.get(key)
            if val is None:
                continue
            if key == "cls":
                display = f"{val:.2f}"
            else:
                display = f"{val / 1000:.1f}s"
            rating = rate_cwv(key, val)
            print(f"  {labels[key]:<5}{display:<8}{rating:<25}(target: {targets[key]})")
    else:
        print("CORE WEB VITALS")
        print("  No field data available for this URL (insufficient traffic)")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Check PageSpeed Insights scores and Core Web Vitals"
    )
    parser.add_argument("url", help="URL to analyze (must start with https://)")
    parser.add_argument(
        "--strategy",
        choices=["mobile", "desktop", "both"],
        default="mobile",
        help="Analysis strategy (default: mobile)",
    )
    parser.add_argument("--json", action="store_true", dest="json_out",
                        help="Output raw JSON")
    args = parser.parse_args()

    try:
        url = validate_url(args.url)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    api_key = get_api_key()
    if not api_key:
        print("Note: No API key configured — running unauthenticated (lower rate limit).",
              file=sys.stderr)

    strategies = ["mobile", "desktop"] if args.strategy == "both" else [args.strategy]
    for strategy in strategies:
        try:
            data = run_psi(url, strategy, api_key)
        except Exception as e:
            print(f"Error calling PSI API: {e}", file=sys.stderr)
            sys.exit(1)
        if args.json_out:
            print(json.dumps(data, indent=2))
        else:
            print_report(data, url, strategy)


if __name__ == "__main__":
    main()
