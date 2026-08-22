"""One-time (well, every-60-days) LinkedIn OAuth. Run locally, not in CI.

Opens the consent page, catches the redirect on localhost, exchanges the code for an
access token, resolves the person URN, and records the issue date so token_watch.py can
warn before it expires.
"""
from __future__ import annotations

import argparse
import http.server
import json
import os
import secrets
import threading
import urllib.parse
import urllib.request
import webbrowser
from datetime import datetime, timezone

import store
from llm import load_env

REDIRECT = "http://localhost:8000/callback"
AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
SCOPES = "openid profile w_member_social"

received: dict[str, str] = {}


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 (stdlib naming)
        query = urllib.parse.urlparse(self.path).query
        received.update({k: v[0] for k, v in urllib.parse.parse_qs(query).items()})
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        ok = "code" in received
        self.wfile.write(
            b"<h2>Done - back to the terminal.</h2>" if ok
            else b"<h2>No code in the redirect. Check the app settings.</h2>")

    def log_message(self, *_: object) -> None:
        pass


def exchange(code: str) -> dict:
    payload = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT,
        "client_id": os.environ["LINKEDIN_CLIENT_ID"],
        "client_secret": os.environ["LINKEDIN_CLIENT_SECRET"],
    }).encode()
    request = urllib.request.Request(
        TOKEN_URL, data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode())


def main() -> None:
    load_env()
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    for required in ("LINKEDIN_CLIENT_ID", "LINKEDIN_CLIENT_SECRET"):
        if not os.environ.get(required):
            raise SystemExit(f"{required} is not set - copy it from the LinkedIn app page into .env")

    state_token = secrets.token_urlsafe(16)
    url = f"{AUTH_URL}?" + urllib.parse.urlencode({
        "response_type": "code",
        "client_id": os.environ["LINKEDIN_CLIENT_ID"],
        "redirect_uri": REDIRECT,
        "state": state_token,
        "scope": SCOPES,
    })

    server = http.server.HTTPServer(("localhost", args.port), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"Add {REDIRECT} as an authorized redirect URL in the LinkedIn app, then approve:\n{url}\n")
    webbrowser.open(url)

    while "code" not in received and "error" not in received:
        server.handle_request()
    server.shutdown()

    if "error" in received:
        raise SystemExit(f"authorization failed: {received}")
    if received.get("state") != state_token:
        raise SystemExit("state mismatch - aborting")

    tokens = exchange(received["code"])
    access_token = tokens["access_token"]
    os.environ["LINKEDIN_ACCESS_TOKEN"] = access_token

    import linkedin  # imported late: it needs the token in the environment
    person_urn = f"urn:li:person:{linkedin.userinfo()['sub']}"

    state = store.read_state()
    state["token_issued_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    store.write_state(state)

    print("\nPut these in .env locally and in the repo secrets:\n")
    print(f"LINKEDIN_ACCESS_TOKEN={access_token}")
    print(f"LINKEDIN_PERSON_URN={person_urn}")
    print(f"\nexpires in {tokens.get('expires_in', 0) // 86400} days"
          f" | refresh_token present: {'refresh_token' in tokens}")


if __name__ == "__main__":
    main()
