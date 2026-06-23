#!/usr/bin/env python3
"""
Credential loader for google-seo-apis.

Reads ~/.config/google-seo-apis/config.json with environment variable fallbacks.
Used by psi.py and gsc.py.

Usage:
    python scripts/auth.py --check
"""

import argparse
import json
import os
import sys
from typing import Optional

CONFIG_PATH = os.path.expanduser("~/.config/google-seo-apis/config.json")

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]


def _load_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        return {}
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def get_api_key() -> Optional[str]:
    config = _load_config()
    return config.get("api_key") or os.environ.get("GOOGLE_API_KEY") or None


def get_service_account_path() -> Optional[str]:
    config = _load_config()
    return (
        config.get("service_account_path")
        or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        or None
    )


def get_gsc_property() -> Optional[str]:
    config = _load_config()
    return config.get("gsc_property") or os.environ.get("GSC_PROPERTY") or None


def get_gsc_credentials():
    sa_path = get_service_account_path()
    if not sa_path or not os.path.exists(sa_path):
        return None
    try:
        from google.oauth2 import service_account
        return service_account.Credentials.from_service_account_file(
            sa_path, scopes=SCOPES
        )
    except Exception:
        return None


def _check():
    SEP = "─" * 40
    print("Credential Status")
    print(SEP)

    def status(value):
        return "✓ OK" if value else "✗ MISSING"

    api_key  = get_api_key()
    sa_path  = get_service_account_path()
    gsc_prop = get_gsc_property()

    print(f"  API Key (PSI/CrUX)        {status(api_key)}")
    print(f"  Service Account (GSC)     {status(sa_path)}")
    print(f"  GSC Property              {status(gsc_prop)}")
    print(SEP)

    if not api_key:
        print("\n  → Set up API Key: see docs/03-credentials.md (Part A)")
    if not sa_path:
        print("\n  → Set up Service Account: see docs/03-credentials.md (Part B)")
    if not gsc_prop:
        print("\n  → Set GSC property in config: see docs/03-credentials.md")

    if api_key and sa_path and gsc_prop:
        print("\n  All credentials configured. You're ready to run the scripts.")


def main():
    parser = argparse.ArgumentParser(description="Check google-seo-apis credentials")
    parser.add_argument("--check", action="store_true", help="Check credential status")
    args = parser.parse_args()
    if args.check:
        _check()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
