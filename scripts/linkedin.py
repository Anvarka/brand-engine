"""LinkedIn REST helpers. Standard library only."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

BASE = "https://api.linkedin.com"


class AccessDenied(RuntimeError):
    """The endpoint needs Marketing Developer Platform partner access, which the
    self-serve `Share on LinkedIn` product does not grant."""



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
        detail = error.read().decode()
        message = f"linkedin {method} {path} -> {error.code}: {detail}"
        if error.code == 403 and "ACCESS_DENIED" in detail:
            raise AccessDenied(message) from error
        raise RuntimeError(message) from error


def upload_image(path: str | Path) -> str:
    """Three-step media flow: initialize, PUT the bytes, get back an image URN."""
    body, _ = request("POST", "/rest/images?action=initializeUpload", {
        "initializeUploadRequest": {"owner": os.environ["LINKEDIN_PERSON_URN"]},
    })
    value = body.get("value", {})
    upload_url, image_urn = value.get("uploadUrl"), value.get("image")
    if not upload_url or not image_urn:
        raise RuntimeError(f"unexpected initializeUpload response: {body}")

    put = urllib.request.Request(
        upload_url,
        data=Path(path).read_bytes(),
        headers={"Authorization": f"Bearer {os.environ['LINKEDIN_ACCESS_TOKEN']}",
                 "Content-Type": "image/png"},
        method="PUT",
    )
    try:
        with urllib.request.urlopen(put, timeout=120) as response:
            if response.status not in (200, 201):
                raise RuntimeError(f"image upload returned {response.status}")
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"image upload failed: {error.code} {error.read().decode()}") from error
    return image_urn


def post_payload(text: str, visibility: str = "PUBLIC",
                 image_urn: str = "", alt_text: str = "") -> dict[str, Any]:
    payload: dict[str, Any] = {
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
    if image_urn:
        payload["content"] = {"media": {"id": image_urn, "altText": alt_text[:200] or "Diagram"}}
    return payload


def create_post(text: str, visibility: str = "PUBLIC",
                image_urn: str = "", alt_text: str = "") -> str:
    _, headers = request("POST", "/rest/posts",
                         post_payload(text, visibility, image_urn, alt_text))
    urn = headers.get("x-restli-id", "")
    if not urn:
        raise RuntimeError("post created but no x-restli-id header returned")
    return urn


def delete_post(post_urn: str) -> None:
    """Remove a post. Used to clean up the smoke-test post."""
    encoded = urllib.parse.quote(post_urn, safe="")
    request("DELETE", f"/rest/posts/{encoded}")


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


def main() -> None:
    """`python scripts/linkedin.py --check` - confirm the token works and print the URN."""
    import argparse
    import sys

    sys.path.insert(0, str(Path(__file__).parent))
    from llm import load_env

    load_env()
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="verify the token and show the person URN")
    args = parser.parse_args()
    if not args.check:
        parser.print_help()
        return

    if not os.environ.get("LINKEDIN_ACCESS_TOKEN"):
        raise SystemExit("LINKEDIN_ACCESS_TOKEN is not set - run scripts/auth_linkedin.py first")

    info = userinfo()
    urn = f"urn:li:person:{info['sub']}"
    configured = os.environ.get("LINKEDIN_PERSON_URN", "")
    print(f"token works. account: {info.get('name', '?')} <{info.get('email', 'no email scope')}>")
    print(f"person URN: {urn}")
    if configured and configured != urn:
        print(f"WARNING: LINKEDIN_PERSON_URN in the environment is {configured} - update it")


if __name__ == "__main__":
    main()
