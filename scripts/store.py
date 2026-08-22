"""Persistence: pipeline state, the draft queue, ideas and stats.

Drafts are markdown files with a flat key/value front matter so they stay reviewable and
editable by hand - the queue is meant to be readable in a git diff.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
QUEUE = ROOT / "content" / "queue"
PUBLISHED = ROOT / "content" / "published"
STATE_FILE = DATA / "state.json"
IDEAS_FILE = DATA / "ideas.jsonl"
STATS_FILE = DATA / "stats.jsonl"

SECTIONS = ("variant_a", "variant_b", "chosen")

DEFAULT_STATE: dict[str, Any] = {
    "tg_offset": 0,
    "pillar_cursor": 0,
    "awaiting_rewrite": "",
    "token_issued_at": "",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ------------------------------------------------------------------------------- state

def read_state() -> dict[str, Any]:
    state = dict(DEFAULT_STATE)
    if STATE_FILE.exists():
        state.update(json.loads(STATE_FILE.read_text()))
    return state


def write_state(state: dict[str, Any]) -> None:
    DATA.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n")


# ------------------------------------------------------------------------------ drafts

class Draft:
    def __init__(self, meta: dict[str, str], body: dict[str, str], path: Path):
        self.meta = meta
        self.body = body
        self.path = path

    # convenience accessors -------------------------------------------------
    @property
    def id(self) -> str:
        return self.meta.get("id", "")

    @property
    def status(self) -> str:
        return self.meta.get("status", "")

    @status.setter
    def status(self, value: str) -> None:
        self.meta["status"] = value

    def text(self, variant: str = "") -> str:
        variant = variant or self.meta.get("variant", "a")
        return self.body.get("chosen") or self.body.get(f"variant_{variant}", "")

    # io --------------------------------------------------------------------
    @classmethod
    def create(cls, slug: str, pillar: str, idea: str, source_url: str = "") -> "Draft":
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
        short = hashlib.sha1(f"{slug}{now()}".encode()).hexdigest()[:8]
        meta = {
            "id": f"{stamp}-{short}",
            "slug": slug,
            "pillar": pillar,
            "status": "pending",
            "created": now(),
            "idea": idea.replace("\n", " "),
            "source_url": source_url,
            "variant": "",
            "tg_message_id": "",
            "rewrite_note": "",
            "post_urn": "",
            "published_at": "",
        }
        path = QUEUE / f"{stamp}-{slug}.md"
        return cls(meta, {}, path)

    @classmethod
    def load(cls, path: Path) -> "Draft":
        raw = path.read_text()
        _, _, rest = raw.partition("---\n")
        front, _, body_raw = rest.partition("---\n")
        meta = {}
        for line in front.splitlines():
            if ":" in line:
                key, _, value = line.partition(":")
                meta[key.strip()] = value.strip()
        body: dict[str, str] = {}
        current = None
        for line in body_raw.splitlines():
            marker = line.strip()
            if marker.startswith("<!--") and marker.endswith("-->"):
                current = marker[4:-3].strip()
                body[current] = ""
                continue
            if current:
                body[current] += line + "\n"
        return cls(meta, {k: v.strip() for k, v in body.items()}, path)

    def save(self) -> Path:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        front = "\n".join(f"{k}: {v}" for k, v in self.meta.items())
        chunks = [f"---\n{front}\n---\n"]
        for section in SECTIONS:
            if self.body.get(section):
                chunks.append(f"\n<!-- {section} -->\n{self.body[section].strip()}\n")
        self.path.write_text("".join(chunks))
        return self.path

    def publish_to_archive(self) -> Path:
        PUBLISHED.mkdir(parents=True, exist_ok=True)
        target = PUBLISHED / self.path.name
        self.path = target
        self.save()
        for stale in QUEUE.glob(f"*{self.meta['slug']}.md"):
            stale.unlink()
        return target


def iter_drafts(folder: Path = QUEUE) -> Iterator[Draft]:
    for path in sorted(folder.glob("*.md")):
        yield Draft.load(path)


def find_draft(draft_id: str) -> Draft | None:
    for draft in iter_drafts():
        if draft.id == draft_id:
            return draft
    return None


# ------------------------------------------------------------------- ideas and stats

def append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(exist_ok=True)
    with path.open("a") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def rewrite_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records))


def url_hash(url: str) -> str:
    return hashlib.sha1(url.encode()).hexdigest()[:12]
