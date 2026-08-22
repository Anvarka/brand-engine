"""Publish the oldest approved draft to LinkedIn.

LinkedIn's API has no scheduled publishing, so this script *is* the scheduler: the
workflow runs it in the desired slot and it takes whatever is approved and waiting.
"""
from __future__ import annotations

import argparse
import json

import linkedin
import store
import tg
from llm import load_env


def post_url(urn: str) -> str:
    return f"https://www.linkedin.com/feed/update/{urn}/"


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

    if args.dry_run:
        print(json.dumps(linkedin.post_payload(text, args.visibility), indent=2, ensure_ascii=False))
        return

    urn = linkedin.create_post(text, args.visibility)
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
