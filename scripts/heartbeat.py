"""Notice when the pipeline goes quiet, and say why.

The pipeline once stalled for three days without a single signal: a draft nobody
answered blocked generation, then expired silently. Green workflows told nobody. This
watchdog makes idleness impossible to confuse with a breakage.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

import store
import tg
from llm import load_env

QUIET_HOURS = 60   # drafts come every 48h, so 60 means something is genuinely stuck


def latest(timestamps: list[str]) -> datetime | None:
    parsed = []
    for value in timestamps:
        try:
            parsed.append(datetime.fromisoformat(value))
        except (ValueError, TypeError):
            continue
    return max(parsed) if parsed else None


def diagnose() -> str:
    """Explain the stall in the terms the operator can act on."""
    drafts = list(store.iter_drafts())
    if any(d.status == "approved" for d in drafts):
        return "есть одобренный драфт — ждёт ближайшего слота публикации"
    if any(d.status == "pending" for d in drafts):
        return "драфт ждёт твоего ответа в Telegram"
    if any(d.status == "rewrite_requested" for d in drafts):
        return "запрошена правка, но перегенерация не отработала — смотри логи approve"

    unused = [i for i in store.read_jsonl(store.IDEAS_FILE) if not i.get("used")]
    if not unused:
        return "кончились идеи: харвест ничего не приносит, проверь data/sources.json"
    return f"идей в запасе {len(unused)}, но драфт не создавался — смотри логи draft"


def main() -> None:
    load_env()
    parser = argparse.ArgumentParser()
    parser.add_argument("--quiet-hours", type=int, default=QUIET_HOURS)
    parser.add_argument("--dry-run", action="store_true", help="print, do not notify")
    args = parser.parse_args()

    published = latest([r.get("published_at", "") for r in store.read_jsonl(store.STATS_FILE)])
    drafted = latest([d.meta.get("created", "") for d in store.iter_drafts(store.QUEUE)]
                     + [d.meta.get("created", "") for d in store.iter_drafts(store.PUBLISHED)])

    last = max([t for t in (published, drafted) if t], default=None)
    if last is None:
        message = "Конвейер ещё ничего не создал и не опубликовал."
    else:
        idle = datetime.now(timezone.utc) - last
        if idle < timedelta(hours=args.quiet_hours):
            print(f"ok: last activity {int(idle.total_seconds() // 3600)}h ago")
            return
        message = (f"Конвейер молчит {int(idle.total_seconds() // 3600)} часов.\n"
                   f"Причина: {diagnose()}")

    print(message)
    if not args.dry_run:
        tg.send_message(f"⚠️ {message}")


if __name__ == "__main__":
    main()
