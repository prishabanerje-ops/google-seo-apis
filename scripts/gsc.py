#!/usr/bin/env python3
"""
Google Search Console Search Analytics query tool.

Fetches top queries or pages by clicks, impressions, CTR, and position.
Requires a Service Account with GSC access (see docs/03-credentials.md Part B).

Usage:
    python scripts/gsc.py
    python scripts/gsc.py --property sc-domain:example.com
    python scripts/gsc.py --property sc-domain:example.com --days 90
    python scripts/gsc.py --dimension page --top 20 --csv results.csv
    python scripts/gsc.py --json
"""

import argparse
import csv
import json
import os
import sys
from datetime import date, timedelta
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auth import get_gsc_credentials, get_gsc_property

try:
    from googleapiclient.discovery import build
except ImportError:
    print(
        "Error: google-api-python-client not installed.\n"
        "Run the setup script: bash setup/setup.sh  (Mac) or .\\setup\\setup.ps1  (Windows)",
        file=sys.stderr,
    )
    sys.exit(1)


def build_gsc_service(credentials):
    """Build and return a Search Console API service resource."""
    return build("searchconsole", "v1", credentials=credentials)


def list_properties(service) -> list:
    """Return list of siteUrl strings for all verified properties in the account."""
    resp = service.sites().list().execute()
    return [s["siteUrl"] for s in resp.get("siteEntry", [])]


def query_search_analytics(
    service, property_url: str, days: int, dimension: str, top: int
) -> list:
    """
    Query Search Analytics for top rows ordered by clicks DESCENDING.

    Returns the raw ``rows`` list from the API response, or [] if empty.
    """
    end_date = date.today().isoformat()
    start_date = (date.today() - timedelta(days=days)).isoformat()
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": [dimension],
        "rowLimit": top,
        "orderBy": [{"fieldName": "clicks", "sortOrder": "DESCENDING"}],
    }
    resp = service.searchanalytics().query(siteUrl=property_url, body=body).execute()
    return resp.get("rows", [])


def write_csv(rows: list, path: str, dimension: str):
    """
    Write rows to a CSV file.

    Column order: [dimension, clicks, impressions, ctr, position]
    CTR is formatted as "10.0%"; position as "3.2".
    """
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=[dimension, "clicks", "impressions", "ctr", "position"]
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({
                dimension:     row["keys"][0],
                "clicks":      row["clicks"],
                "impressions": row["impressions"],
                "ctr":         f"{row['ctr'] * 100:.1f}%",
                "position":    f"{row['position']:.1f}",
            })


def print_table(rows: list, dimension: str, property_url: str, days: int):
    """Print a formatted table of Search Analytics rows to stdout."""
    SEP = "─" * 70
    print(f"\nGSC Search Analytics — {property_url}")
    print(f"Last {days} days | Top {len(rows)} {dimension}s")
    print(SEP)
    col = "Query" if dimension == "query" else "Page"
    print(f"{'#':<4}{col:<40}{'Clicks':>8}{'Impressions':>13}{'CTR':>8}{'Pos':>7}")
    print(SEP)
    for i, row in enumerate(rows, 1):
        key = row["keys"][0]
        if len(key) > 38:
            key = key[:35] + "..."
        print(
            f"{i:<4}{key:<40}{int(row['clicks']):>8}"
            f"{int(row['impressions']):>13}"
            f"{row['ctr'] * 100:>7.1f}%"
            f"{row['position']:>7.1f}"
        )
    print()


def main():
    """CLI entrypoint for GSC Search Analytics queries."""
    parser = argparse.ArgumentParser(
        description="Query Google Search Console Search Analytics"
    )
    parser.add_argument("--property", help="GSC property (e.g. sc-domain:example.com)")
    parser.add_argument("--days", type=int, default=30,
                        help="Date range in days (default: 30)")
    parser.add_argument("--dimension", choices=["query", "page"], default="query",
                        help="Group by query or page (default: query)")
    parser.add_argument("--top", type=int, default=10,
                        help="Number of rows to return (default: 10)")
    parser.add_argument("--csv", metavar="FILE", help="Export results to CSV file")
    parser.add_argument("--json", action="store_true", dest="json_out",
                        help="Output raw JSON")
    args = parser.parse_args()

    credentials = get_gsc_credentials()
    if not credentials:
        print(
            "Error: GSC credentials not configured.\n"
            "See docs/03-credentials.md (Part B) to set up a Service Account.",
            file=sys.stderr,
        )
        sys.exit(1)

    service = build_gsc_service(credentials)

    property_url = args.property or get_gsc_property()
    if not property_url:
        properties = list_properties(service)
        if not properties:
            print("No verified properties found in this account.", file=sys.stderr)
            sys.exit(1)
        print("No property specified. Verified properties in your account:")
        for p in properties:
            print(f"  {p}")
        print("\nRe-run with: python scripts/gsc.py --property <property>")
        sys.exit(0)

    rows = query_search_analytics(service, property_url, args.days, args.dimension, args.top)
    if not rows:
        print("No data returned. Check your property URL and date range.")
        sys.exit(0)

    if args.json_out:
        output = {
            "property": property_url,
            "dimension": args.dimension,
            "days": args.days,
            "rows": rows
        }
        print(json.dumps(output, indent=2))
        sys.exit(0)

    print_table(rows, args.dimension, property_url, args.days)

    if args.csv:
        write_csv(rows, args.csv, args.dimension)
        print(f"Exported to {args.csv}")


if __name__ == "__main__":
    main()
