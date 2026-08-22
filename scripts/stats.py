"""Collect engagement on published posts and turn it into next week's instructions."""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

import linkedin
import store
import tg
from llm import complete, load_env

TRACK_DAYS = 30
LIKE_WEIGHT, COMMENT_WEIGHT = 1, 3


def collect() -> None:
    """One row per post per check, so the growth curve stays visible."""
    records = store.read_jsonl(store.STATS_FILE)
    cutoff = datetime.now(timezone.utc) - timedelta(days=TRACK_DAYS)

    latest: dict[str, dict] = {}
    for record in records:
        latest[record["urn"]] = record

    for urn, record in latest.items():
        try:
            published = datetime.fromisoformat(record["published_at"])
        except (ValueError, KeyError):
            continue
        if published < cutoff:
            continue
        try:
            counts = linkedin.social_actions(urn)
        except linkedin.AccessDenied:
            print("engagement counts need Marketing Developer Platform partner access, "
                  "which this app does not have - skipping collection.\n"
                  "Numbers can still be entered by hand into data/stats.jsonl.")
            return
        except RuntimeError as error:
            print(f"  {urn}: {error}")
            continue
        engagement = counts["likes"] * LIKE_WEIGHT + counts["comments"] * COMMENT_WEIGHT
        store.append_jsonl(store.STATS_FILE, {
            **{k: record[k] for k in ("urn", "id", "pillar", "slug", "variant", "published_at", "text")},
            "checked_at": store.now(), **counts, "engagement": engagement,
        })
        print(f"  {record['slug']}: {counts['likes']} likes, {counts['comments']} comments")


def weekly() -> None:
    records = store.read_jsonl(store.STATS_FILE)
    if not records:
        print("no stats yet - skipping the weekly brief")
        return
    latest: dict[str, dict] = {}
    for record in records:
        latest[record["urn"]] = record

    if not any(r.get("engagement", 0) for r in latest.values()):
        print("no engagement data recorded yet - skipping the brief")
        return

    rows = sorted(latest.values(), key=lambda r: r.get("engagement", 0), reverse=True)
    summary = "\n\n".join(
        f"[{r['pillar']}] variant {r.get('variant','a')} | likes {r.get('likes',0)} "
        f"comments {r.get('comments',0)} | published {r.get('published_at','')[:10]}\n"
        f"{r.get('text','')[:400]}"
        for r in rows
    )
    brief = complete("weekly", {
        "pillars": (store.ROOT / "content" / "pillars.md").read_text(),
        "stats": summary,
        "state": str(store.read_state()),
    }, tier="smart")
    tg.send_message(f"Weekly brief\n\n{brief}")
    (store.ROOT / "content" / "weekly_brief.md").write_text(
        f"# Weekly brief - {store.now()[:10]}\n\n{brief}\n")
    print(brief)


def main() -> None:
    load_env()
    parser = argparse.ArgumentParser()
    parser.add_argument("--weekly", action="store_true", help="generate and send the weekly brief")
    args = parser.parse_args()
    if args.weekly:
        weekly()
    else:
        collect()


if __name__ == "__main__":
    main()
