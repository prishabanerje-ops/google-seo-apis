#!/usr/bin/env python3
"""
Credential loader for google-seo-apis.

Reads ~/.config/google-seo-apis/config.json with environment variable fallbacks.
Used by psi.py and gsc.py.

Author: Aakash Srivastava

Usage:
    python scripts/auth.py --check
    python scripts/auth.py --auth --creds /path/to/client_secret.json
"""

import argparse
import http.server
import json
import os
import random
import sys
import time
import urllib.parse
import urllib.request
import webbrowser
from typing import Optional

CONFIG_PATH = os.path.expanduser("~/.config/google-seo-apis/config.json")
TOKEN_PATH = os.path.expanduser("~/.config/google-seo-apis/oauth-token.json")

SCOPES = "https://www.googleapis.com/auth/webmasters.readonly"


def _load_config() -> dict:
    if not os.path.exists(CONFIG_PATH):
        return {}
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_config(config: dict):
    """Atomically write config to CONFIG_PATH."""
    import tempfile
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(
        dir=os.path.dirname(CONFIG_PATH), prefix=".config.", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(config, f, indent=2)
        os.replace(tmp_path, CONFIG_PATH)
    except Exception:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise


def get_api_key() -> Optional[str]:
    config = _load_config()
    return config.get("api_key") or os.environ.get("GOOGLE_API_KEY") or None


def get_gsc_property() -> Optional[str]:
    config = _load_config()
    return config.get("gsc_property") or os.environ.get("GSC_PROPERTY") or None


def get_oauth_client_path() -> Optional[str]:
    config = _load_config()
    return (
        config.get("oauth_client_path")
        or os.environ.get("OAUTH_CLIENT_PATH")
        or None
    )


# ---------------------------------------------------------------------------
# OAuth token helpers
# ---------------------------------------------------------------------------

def _load_oauth_token() -> Optional[dict]:
    """Load saved OAuth token from TOKEN_PATH."""
    if not os.path.exists(TOKEN_PATH):
        return None
    try:
        with open(TOKEN_PATH) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def _save_oauth_token(token_data: dict):
    """Save OAuth token to TOKEN_PATH."""
    os.makedirs(os.path.dirname(TOKEN_PATH), exist_ok=True)
    with open(TOKEN_PATH, "w") as f:
        json.dump(token_data, f, indent=2)


def _load_oauth_client(creds_path: str) -> Optional[dict]:
    """Parse a client_secret JSON file. Supports both 'installed' and 'web' keys."""
    try:
        with open(creds_path) as f:
            data = json.load(f)
        return data.get("installed", data.get("web")) or None
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error reading OAuth client file: {e}", file=sys.stderr)
        return None


def _refresh_oauth_token(client: dict, token_data: dict) -> Optional[dict]:
    """Refresh an expired OAuth access token using the stored refresh_token."""
    if not token_data.get("refresh_token"):
        return None

    params = urllib.parse.urlencode({
        "client_id": client["client_id"],
        "client_secret": client["client_secret"],
        "refresh_token": token_data["refresh_token"],
        "grant_type": "refresh_token",
    }).encode()

    try:
        req = urllib.request.Request(
            client.get("token_uri", "https://oauth2.googleapis.com/token"),
            data=params,
        )
        with urllib.request.urlopen(req) as resp:
            new_data = json.loads(resp.read())
        token_data["access_token"] = new_data["access_token"]
        token_data["expires_at"] = time.time() + new_data.get("expires_in", 3600)
        _save_oauth_token(token_data)
        return token_data
    except Exception as e:
        print(f"Error refreshing OAuth token: {e}", file=sys.stderr)
        return None


def _persist_oauth_client_path(creds_path: str):
    """Save the absolute path to the client_secret file in config for future refresh calls."""
    abs_path = os.path.abspath(os.path.expanduser(creds_path))
    config = _load_config()
    config["oauth_client_path"] = abs_path
    _save_config(config)


# ---------------------------------------------------------------------------
# Public credentials interface
# ---------------------------------------------------------------------------

def get_gsc_credentials():
    """
    Return google.oauth2.credentials.Credentials built from the saved OAuth token.

    Refreshes the token automatically if it is within 60 seconds of expiry.
    Returns None if no token file exists, printing a hint to run --auth.
    """
    token_data = _load_oauth_token()
    if not token_data:
        print(
            "No OAuth token found.\n"
            "Run: python scripts/auth.py --auth --creds /path/to/client_secret.json\n"
            "See docs/03-credentials.md for instructions.",
            file=sys.stderr,
        )
        return None

    # Refresh if expiring soon
    if time.time() > token_data.get("expires_at", 0) - 60:
        oauth_path = get_oauth_client_path()
        if oauth_path:
            client = _load_oauth_client(os.path.expanduser(oauth_path))
            if client:
                token_data = _refresh_oauth_token(client, token_data)
                if not token_data:
                    print(
                        "OAuth token refresh failed.\n"
                        "Run: python scripts/auth.py --auth --creds /path/to/client_secret.json",
                        file=sys.stderr,
                    )
                    return None

    if not token_data or not token_data.get("access_token"):
        return None

    try:
        from google.oauth2.credentials import Credentials
    except ImportError:
        print("Error: google-auth required. Install with: pip install google-auth", file=sys.stderr)
        return None

    # Read client_secret from the client file — never from the stored token
    client_secret = None
    oauth_path = get_oauth_client_path()
    if oauth_path:
        client_data = _load_oauth_client(os.path.expanduser(oauth_path))
        if client_data:
            client_secret = client_data.get("client_secret")

    return Credentials(
        token=token_data["access_token"],
        refresh_token=token_data.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=token_data.get("client_id"),
        client_secret=client_secret,
    )


# ---------------------------------------------------------------------------
# Browser OAuth flow
# ---------------------------------------------------------------------------

def _run_auth_flow(creds_path: str):
    """
    Run OAuth Desktop App browser flow.

    Opens the browser, captures the auth code via a local HTTP server,
    exchanges it for tokens, and saves them to TOKEN_PATH.
    """
    client = _load_oauth_client(creds_path)
    if not client:
        print("Error: Could not load OAuth client credentials.", file=sys.stderr)
        sys.exit(1)

    port = random.randint(8085, 8099)
    redirect_uri = f"http://localhost:{port}"

    auth_url = (
        f"{client.get('auth_uri', 'https://accounts.google.com/o/oauth2/v2/auth')}"
        f"?client_id={client['client_id']}"
        f"&redirect_uri={urllib.parse.quote(redirect_uri)}"
        f"&scope={urllib.parse.quote(SCOPES)}"
        f"&response_type=code"
        f"&access_type=offline"
        f"&prompt=consent"
    )

    auth_code = [None]

    class _Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if "code" in params:
                auth_code[0] = params["code"][0]
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(
                    b"<h1>Authentication successful!</h1><p>You can close this tab.</p>"
                )
            else:
                self.send_response(400)
                self.end_headers()

        def log_message(self, *args):
            pass  # suppress request logs

    server = http.server.HTTPServer(("localhost", port), _Handler)
    server.timeout = 300

    print(f"\nOpening browser for authentication...")
    print(f"\nIf the browser does not open, visit this URL:\n\n  {auth_url}\n")
    print("Waiting up to 5 minutes for authentication...")

    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    server.handle_request()
    server.server_close()

    if not auth_code[0]:
        print("\nAuthentication failed or timed out.", file=sys.stderr)
        sys.exit(1)

    # Exchange code for tokens
    params = urllib.parse.urlencode({
        "code": auth_code[0],
        "client_id": client["client_id"],
        "client_secret": client["client_secret"],
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }).encode()

    try:
        req = urllib.request.Request(
            client.get("token_uri", "https://oauth2.googleapis.com/token"),
            data=params,
        )
        with urllib.request.urlopen(req) as resp:
            token_data = json.loads(resp.read())
    except Exception as e:
        print(f"Error exchanging authorization code: {e}", file=sys.stderr)
        sys.exit(1)

    token_data["expires_at"] = time.time() + token_data.get("expires_in", 3600)
    token_data["client_id"] = client["client_id"]
    # SECURITY: never store client_secret in the token file
    token_data.pop("client_secret", None)

    _save_oauth_token(token_data)
    _persist_oauth_client_path(creds_path)

    print("✓ Authenticated. Token saved.")


# ---------------------------------------------------------------------------
# --check output
# ---------------------------------------------------------------------------

def _check():
    SEP = "─" * 40
    print("Credential Status")
    print(SEP)

    api_key = get_api_key()
    token_data = _load_oauth_token()
    gsc_prop = get_gsc_property()

    # API key
    if api_key:
        print(f"  API key            ✓ OK")
    else:
        print(f"  API key            ✗ MISSING")

    # OAuth token
    if token_data and token_data.get("access_token"):
        expires_at = token_data.get("expires_at", 0)
        import datetime
        expiry = datetime.datetime.fromtimestamp(expires_at).strftime("%Y-%m-%d")
        print(f"  OAuth token        ✓ OK (expires {expiry})")
    else:
        print(
            "  OAuth token        ✗ MISSING — run: "
            "python scripts/auth.py --auth --creds <path>"
        )

    # GSC property
    if gsc_prop:
        print(f"  GSC property       ✓ OK ({gsc_prop})")
    else:
        print(f"  GSC property       ✗ MISSING")

    print(SEP)

    if not api_key:
        print("\n  → Set up API Key: see docs/03-credentials.md (Part A)")
    if not (token_data and token_data.get("access_token")):
        print(
            "\n  → Authenticate with Google: "
            "python scripts/auth.py --auth --creds /path/to/client_secret.json\n"
            "    See docs/03-credentials.md (Part B)"
        )
    if not gsc_prop:
        print("\n  → Set GSC property in config: see docs/03-credentials.md")

    if api_key and token_data and token_data.get("access_token") and gsc_prop:
        print("\n  All credentials configured. You're ready to run the scripts.")


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Manage google-seo-apis credentials")
    parser.add_argument("--check", action="store_true", help="Check credential status")
    parser.add_argument(
        "--auth", action="store_true", help="Run OAuth browser authentication flow"
    )
    parser.add_argument(
        "--creds",
        metavar="PATH",
        help="Path to OAuth client_secret JSON (required with --auth)",
    )
    args = parser.parse_args()

    if args.auth:
        if not args.creds:
            print("Error: --creds is required with --auth", file=sys.stderr)
            sys.exit(1)
        _run_auth_flow(args.creds)
        return

    if args.check:
        _check()
        return

    parser.print_help()


if __name__ == "__main__":
    main()
