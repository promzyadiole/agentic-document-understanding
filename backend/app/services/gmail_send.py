from __future__ import annotations

"""
Send email through the user's Gmail account via the Gmail REST API.

Reuses the OAuth client stored by the Gmail integration under ~/.gmail-mcp/, but
sending needs the `gmail.send` scope, which the triage token does NOT have. So a
separate, send-scoped token is stored at ~/.gmail-mcp/send_credentials.json
(minted once by scripts/gmail_authorize.py). If that token is absent, sending is
simply "not configured" and the app keeps emails as approved drafts.
"""

import base64
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from email.message import EmailMessage

GMAIL_DIR = os.path.expanduser("~/.gmail-mcp")
KEYS = os.path.join(GMAIL_DIR, "gcp-oauth.keys.json")
SEND_CREDS = os.path.join(GMAIL_DIR, "send_credentials.json")
SEND_ENDPOINT = "https://gmail.googleapis.com/gmail/v1/users/me/messages/send"
SEND_SCOPE = "https://www.googleapis.com/auth/gmail.send"


class GmailSendError(Exception):
    pass


def is_configured() -> bool:
    """True only when a send-scoped token exists (so we never pretend to send)."""
    if not (os.path.exists(SEND_CREDS) and os.path.exists(KEYS)):
        return False
    try:
        creds = json.load(open(SEND_CREDS))
        return "gmail.send" in (creds.get("scope") or "") and bool(creds.get("refresh_token"))
    except Exception:
        return False


def _keys() -> dict:
    return json.load(open(KEYS))["installed"]


def _refresh(creds: dict) -> dict:
    keys = _keys()
    data = urllib.parse.urlencode(
        {
            "client_id": keys["client_id"],
            "client_secret": keys["client_secret"],
            "refresh_token": creds["refresh_token"],
            "grant_type": "refresh_token",
        }
    ).encode()
    req = urllib.request.Request(keys["token_uri"], data=data)
    with urllib.request.urlopen(req, timeout=30) as r:
        tok = json.load(r)
    creds["access_token"] = tok["access_token"]
    creds["expiry_date"] = int(time.time() * 1000) + int(tok["expires_in"]) * 1000
    json.dump(creds, open(SEND_CREDS, "w"))
    return creds


def _access_token() -> str:
    creds = json.load(open(SEND_CREDS))
    if creds.get("expiry_date", 0) <= int(time.time() * 1000) + 60000:
        creds = _refresh(creds)
    return creds["access_token"]


def send_email(*, sender: str, to: str, subject: str, body: str) -> str:
    """Send a plain-text email; returns the Gmail message id."""
    if not is_configured():
        raise GmailSendError("Gmail sending is not configured (no send-scoped token).")
    if not to:
        raise GmailSendError("No recipient email address.")

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    req = urllib.request.Request(
        SEND_ENDPOINT, data=json.dumps({"raw": raw}).encode(), method="POST"
    )
    req.add_header("Authorization", "Bearer " + _access_token())
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r).get("id", "")
    except urllib.error.HTTPError as e:
        raise GmailSendError(f"Gmail API error {e.code}: {e.read().decode()[:300]}") from e
    except Exception as e:  # noqa: BLE001
        raise GmailSendError(str(e)) from e
