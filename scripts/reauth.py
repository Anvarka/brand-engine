"""Exchange an authorization code for a LinkedIn token, from CI.

LinkedIn issues no refresh token to non-partner apps, so the 60-day token has to be
re-obtained by hand. This path needs no laptop: the consent redirect lands on a static
GitHub Pages page that shows the code, and the code is pasted into this workflow.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

import store
import tg
from llm import load_env

TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
SCOPES = "openid profile w_member_social"


def redirect_uri() -> str:
    return os.environ.get("LINKEDIN_REDIRECT_URI") or \
        "https://anvarka.github.io/brand-engine/callback.html"


def authorize_url() -> str:
    return "https://www.linkedin.com/oauth/v2/authorization?" + urllib.parse.urlencode({
        "response_type": "code",
        "client_id": os.environ["LINKEDIN_CLIENT_ID"],
        "redirect_uri": redirect_uri(),
        "scope": SCOPES,
    })


def exchange(code: str) -> dict:
    payload = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri(),
        "client_id": os.environ["LINKEDIN_CLIENT_ID"],
        "client_secret": os.environ["LINKEDIN_CLIENT_SECRET"],
    }).encode()
    request = urllib.request.Request(
        TOKEN_URL, data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as error:
        detail = error.read().decode()
        # Codes are single-use and expire in minutes; say so instead of dumping a stack.
        raise SystemExit(
            f"LinkedIn rejected the code ({error.code}): {detail}\n"
            f"Codes are single use and expire within minutes - start again from:\n"
            f"{authorize_url()}"
        ) from None


def store_secret(name: str, value: str, repo: str) -> None:
    """GITHUB_TOKEN cannot write secrets, so a fine-grained PAT is required."""
    subprocess.run(["gh", "secret", "set", name, "--repo", repo, "--body", value],
                   check=True, capture_output=True,
                   env={**os.environ, "GH_TOKEN": os.environ["GH_PAT"]})


def main() -> None:
    load_env()
    parser = argparse.ArgumentParser()
    parser.add_argument("--code", default=os.environ.get("LINKEDIN_CODE", ""))
    parser.add_argument("--print-url", action="store_true", help="print the consent URL and exit")
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY", "Anvarka/brand-engine"))
    args = parser.parse_args()

    if args.print_url or not args.code:
        print(authorize_url())
        if not args.code:
            raise SystemExit("no code supplied - open the URL above, approve, copy the code")
        return

    tokens = exchange(args.code.strip())
    access_token = tokens["access_token"]
    os.environ["LINKEDIN_ACCESS_TOKEN"] = access_token

    import linkedin  # imported late: it reads the token from the environment
    person_urn = f"urn:li:person:{linkedin.userinfo()['sub']}"

    store_secret("LINKEDIN_ACCESS_TOKEN", access_token, args.repo)
    store_secret("LINKEDIN_PERSON_URN", person_urn, args.repo)

    state = store.read_state()
    state["token_issued_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    store.write_state(state)

    days = tokens.get("expires_in", 0) // 86400
    tg.send_message(f"✅ Токен LinkedIn обновлён, действует {days} дней. {person_urn}")
    print(f"token stored, valid {days} days, urn {person_urn}")


if __name__ == "__main__":
    main()
