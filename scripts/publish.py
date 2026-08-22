"""Publish the oldest approved draft to LinkedIn.

LinkedIn's API has no scheduled publishing, so this script *is* the scheduler: the
workflow runs it in the desired slot and it takes whatever is approved and waiting.
"""
from __future__ import annotations

import argparse
import json
import os

import linkedin
import store
import tg
from llm import load_env


def post_url(urn: str) -> str:
    return f"https://www.linkedin.com/feed/update/{urn}/"


def placement() -> str:
    """`vars.LINK_PLACEMENT` arrives as an empty string when the repo variable is unset,
    so an explicit falsy check is needed, not a dict default.

    Default is `body`: posting the link as the first comment needs partner-level access
    that the self-serve product does not grant (verified 403 ACCESS_DENIED)."""
    return os.environ.get("LINK_PLACEMENT") or "body"


def source_link(draft: store.Draft) -> str:
    url = draft.meta.get("source_url", "")
    return url if url.startswith("http") else ""


def attach_source(urn: str, url: str) -> None:
    """LinkedIn suppresses reach on posts with an outbound link in the body, so the
    source goes into the first comment. If that call fails the link is not lost - it is
    sent to Telegram to be pasted by hand."""
    if not url or placement() == "none":
        return
    try:
        linkedin.create_comment(urn, f"Source: {url}")
        print(f"source posted as a comment: {url}")
    except linkedin.AccessDenied:
        print("commenting needs partner access - sending the link to Telegram instead")
        tg.send_message(f"Paste the source as the first comment:\n{url}\n\n{post_url(urn)}")
    except RuntimeError as error:
        print(f"comment failed: {error}")
        tg.send_message(f"Could not post the source as a comment - paste it yourself:\n{url}\n\n{post_url(urn)}")


def main() -> None:
    load_env()
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="print the API payload, send nothing")
    parser.add_argument("--visibility", default="PUBLIC", choices=["PUBLIC", "CONNECTIONS"])
    args = parser.parse_args()

    approved = sorted(
        (d for d in store.iter_drafts() if d.status == "approved"),
        key=lambda d: d.meta.get("approved_at", ""),
    )
    if not approved:
        print("nothing approved - the slot is skipped")
        return

    draft = approved[0]
    text = draft.text()
    if not text.strip():
        print(f"{draft.id} has an empty chosen variant - marking failed")
        draft.status = "failed"
        draft.save()
        return

    url = source_link(draft)
    body = text
    if url and placement() == "body":
        body = f"{text}\n\nSource: {url}"

    if args.dry_run:
        print(json.dumps(linkedin.post_payload(body, args.visibility), indent=2, ensure_ascii=False))
        print(f"\nsource link: {url or '(none)'} | placement: {placement()}")
        return

    urn = linkedin.create_post(body, args.visibility)
    attach_source(urn, url)
    draft.meta["post_urn"] = urn
    draft.meta["published_at"] = store.now()
    draft.status = "published"
    draft.publish_to_archive()

    store.append_jsonl(store.STATS_FILE, {
        "urn": urn, "id": draft.id, "pillar": draft.meta["pillar"], "slug": draft.meta["slug"],
        "variant": draft.meta.get("variant", "a"), "published_at": draft.meta["published_at"],
        "checked_at": store.now(), "likes": 0, "comments": 0, "engagement": 0,
        "text": text,
    })

    tg.send_message(f"Published [{draft.meta['pillar']}] {draft.meta['slug']}\n{post_url(urn)}")
    print(f"published {urn}")


if __name__ == "__main__":
    main()
