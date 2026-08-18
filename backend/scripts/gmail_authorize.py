#!/usr/bin/env python3
"""
One-time Gmail authorization for SENDING email.

The triage token under ~/.gmail-mcp/credentials.json only has read/modify scopes.
This runs the standard "installed app" loopback OAuth flow to mint a separate,
send-scoped token at ~/.gmail-mcp/send_credentials.json — the only thing the app
uses to send outreach/thank-you emails from your Gmail.

Run it, open the printed URL in your browser, and approve. That's it.
"""

import json
import os
import socket
import sys
import time
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

GMAIL_DIR = os.path.expanduser("~/.gmail-mcp")
KEYS = os.path.join(GMAIL_DIR, "gcp-oauth.keys.json")
SEND_CREDS = os.path.join(GMAIL_DIR, "send_credentials.json")
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

_code_holder = {}


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        qs = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(qs)
        _code_holder["code"] = (params.get("code") or [None])[0]
        _code_holder["error"] = (params.get("error") or [None])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h2>Proziem: Gmail authorized.</h2><p>You can close this tab and return to the app.</p>")

    def log_message(self, *_):  # silence
        pass


def _free_port() -> int:
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def main():
    if not os.path.exists(KEYS):
        sys.exit("Missing ~/.gmail-mcp/gcp-oauth.keys.json — set up the Gmail integration first.")
    keys = json.load(open(KEYS))["installed"]

    port = _free_port()
    redirect_uri = f"http://localhost:{port}"
    auth_url = keys["auth_uri"] + "?" + urllib.parse.urlencode(
        {
            "client_id": keys["client_id"],
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(SCOPES),
            "access_type": "offline",
            "prompt": "consent",
        }
    )

    print("\n=== AUTHORIZE GMAIL SENDING ===", flush=True)
    print("Open this URL in your browser and approve:\n", flush=True)
    print(auth_url + "\n", flush=True)
    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    server = HTTPServer(("127.0.0.1", port), _Handler)
    server.timeout = 300
    print(f"Waiting for authorization on {redirect_uri} …", flush=True)
    while "code" not in _code_holder and "error" not in _code_holder:
        server.handle_request()

    if _code_holder.get("error") or not _code_holder.get("code"):
        sys.exit(f"Authorization failed: {_code_holder.get('error')}")

    # Exchange the code for tokens.
    data = urllib.parse.urlencode(
        {
            "code": _code_holder["code"],
            "client_id": keys["client_id"],
            "client_secret": keys["client_secret"],
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
    ).encode()
    with urllib.request.urlopen(urllib.request.Request(keys["token_uri"], data=data), timeout=30) as r:
        tok = json.load(r)

    creds = {
        "access_token": tok["access_token"],
        "refresh_token": tok.get("refresh_token"),
        "scope": tok.get("scope", " ".join(SCOPES)),
        "token_type": tok.get("token_type", "Bearer"),
        "expiry_date": int(time.time() * 1000) + int(tok.get("expires_in", 3600)) * 1000,
    }
    if not creds["refresh_token"]:
        sys.exit("No refresh_token returned — re-run (revoke prior consent if needed).")
    json.dump(creds, open(SEND_CREDS, "w"))
    print(f"\n✅ Send-scoped token saved to {SEND_CREDS}", flush=True)
    print("Gmail sending is now enabled.", flush=True)


if __name__ == "__main__":
    main()
