"""Pull feeds, drop what is already known, score the rest into data/ideas.jsonl."""
from __future__ import annotations

import argparse
import json
import re
from typing import Literal

from pydantic import BaseModel

import store
from llm import complete, load_env

BATCH = 10
MAX_PER_FEED = 15
SUMMARY_CHARS = 700


class ScoredItem(BaseModel):
    index: int
    pillar: str
    relevance: float
    angle: str
    why_now: str


class ScoredBatch(BaseModel):
    items: list[ScoredItem]


def clean(html: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html or "")).strip()


def fetch_feeds(verbose: bool = True) -> list[dict]:
    import feedparser

    config = json.loads((store.DATA / "sources.json").read_text())
    keywords = [k.lower() for k in config["keywords"]]
    collected: list[dict] = []

    for feed in config["feeds"]:
        try:
            parsed = feedparser.parse(feed["url"])
        except Exception as error:  # a dead feed must never break the run
            print(f"  {feed['name']}: FAILED ({error})")
            continue
        if parsed.bozo and not parsed.entries:
            print(f"  {feed['name']}: no entries ({getattr(parsed, 'bozo_exception', 'unknown')})")
            continue

        kept = 0
        for entry in parsed.entries[:MAX_PER_FEED]:
            title = clean(entry.get("title", ""))
            summary = clean(entry.get("summary", ""))[:SUMMARY_CHARS]
            haystack = f"{title} {summary}".lower()
            if not feed["always_keep"] and not any(k in haystack for k in keywords):
                continue
            collected.append({
                "url": entry.get("link", ""),
                "title": title,
                "summary": summary,
                "source": feed["name"],
                "published": entry.get("published", ""),
            })
            kept += 1
        if verbose:
            print(f"  {feed['name']}: {kept} kept of {len(parsed.entries)}")
    return collected


def score(items: list[dict]) -> list[dict]:
    pillars = (store.ROOT / "content" / "pillars.md").read_text()
    scored: list[dict] = []

    for start in range(0, len(items), BATCH):
        batch = items[start:start + BATCH]
        payload = [
            {"index": i, "title": item["title"], "summary": item["summary"], "source": item["source"]}
            for i, item in enumerate(batch)
        ]
        result = complete(
            "score_idea",
            {"pillars": pillars, "items": json.dumps(payload, ensure_ascii=False, indent=1)},
            schema=ScoredBatch,
            tier="cheap",
        )
        for entry in result.items:
            if entry.index >= len(batch):
                continue
            item = dict(batch[entry.index])
            item.update({
                "pillar": entry.pillar,
                "relevance": entry.relevance,
                "angle": entry.angle,
                "why_now": entry.why_now,
                "hash": store.url_hash(item["url"]),
                "used": False,
                "scored_at": store.now(),
            })
            scored.append(item)
    return scored


def main() -> None:
    load_env()
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="fetch and filter, but do not call the LLM")
    parser.add_argument("--min-relevance", type=float, default=0.45)
    args = parser.parse_args()

    print("fetching feeds...")
    items = fetch_feeds()
    known = {record["hash"] for record in store.read_jsonl(store.IDEAS_FILE)}
    fresh = [item for item in items if item["url"] and store.url_hash(item["url"]) not in known]
    print(f"{len(items)} passed the keyword filter, {len(fresh)} are new")

    if args.dry_run:
        for item in fresh[:20]:
            print(f"  [{item['source']}] {item['title'][:90]}")
        return
    if not fresh:
        return

    kept = 0
    for item in score(fresh):
        if item["pillar"] == "none" or item["relevance"] < args.min_relevance:
            continue
        store.append_jsonl(store.IDEAS_FILE, item)
        kept += 1
    print(f"stored {kept} ideas above relevance {args.min_relevance}")


if __name__ == "__main__":
    main()
