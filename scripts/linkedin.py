"""LinkedIn REST helpers. Standard library only."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

BASE = "https://api.linkedin.com"


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {os.environ['LINKEDIN_ACCESS_TOKEN']}",
        "X-Restli-Protocol-Version": "2.0.0",
        "LinkedIn-Version": os.environ.get("LINKEDIN_API_VERSION", "202608"),
        "Content-Type": "application/json",
    }


def request(method: str, path: str, body: dict | None = None) -> tuple[dict, dict]:
    """Returns (parsed body, response headers). The created post URN comes back in the
    `x-restli-id` header, not in the body."""
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(body).encode() if body is not None else None,
        headers=_headers(),
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            raw = response.read().decode()
            headers = {k.lower(): v for k, v in response.headers.items()}
            return (json.loads(raw) if raw.strip() else {}), headers
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"linkedin {method} {path} -> {error.code}: {error.read().decode()}") from error


def post_payload(text: str, visibility: str = "PUBLIC") -> dict[str, Any]:
    return {
        "author": os.environ["LINKEDIN_PERSON_URN"],
        "commentary": text,
        "visibility": visibility,
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }


def create_post(text: str, visibility: str = "PUBLIC") -> str:
    _, headers = request("POST", "/rest/posts", post_payload(text, visibility))
    urn = headers.get("x-restli-id", "")
    if not urn:
        raise RuntimeError("post created but no x-restli-id header returned")
    return urn


def create_comment(post_urn: str, text: str) -> str:
    """Comment on your own post. Used to put source links out of the post body, where
    they cost reach."""
    encoded = urllib.parse.quote(post_urn, safe="")
    body, headers = request("POST", f"/rest/socialActions/{encoded}/comments", {
        "actor": os.environ["LINKEDIN_PERSON_URN"],
        "object": post_urn,
        "message": {"text": text},
    })
    return body.get("$URN") or headers.get("x-restli-id", "")


def social_actions(urn: str) -> dict[str, int]:
    encoded = urllib.parse.quote(urn, safe="")
    body, _ = request("GET", f"/rest/socialActions/{encoded}")
    return {
        "likes": body.get("likesSummary", {}).get("totalLikes", 0),
        "comments": body.get("commentsSummary", {}).get("aggregatedTotalComments", 0),
    }


def userinfo() -> dict:
    body, _ = request("GET", "/v2/userinfo")
    return body
