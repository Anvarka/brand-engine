"""Drain the Telegram updates queue and apply approvals to the draft files.

Runs on a schedule rather than a webhook: approval only marks a draft ready, publishing
happens in its own slot, so a 20-minute lag costs nothing.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

import store
import tg
from llm import load_env

EXPIRE_HOURS = store.DRAFT_TTL_HOURS


def handle_callback(query: dict, state: dict) -> None:
    data = query.get("data", "")
    action, _, rest = data.partition(":")
    draft_id, _, variant = rest.partition(":")
    draft = store.find_draft(draft_id)

    if not draft:
        tg.answer_callback(query["id"], "draft not found (already published or skipped)")
        return

    if action == "ok":
        draft.status = "approved"
        draft.meta["variant"] = variant or "a"
        draft.body["chosen"] = draft.body.get(f"variant_{draft.meta['variant']}", "")
        draft.meta["approved_at"] = store.now()
        draft.save()
        tg.answer_callback(query["id"], f"variant {variant.upper()} queued")
        tg.send_message(f"✅ Вариант {(variant or 'a').upper()} принят: {draft.meta['slug']}\n"
                        f"Опубликуется в ближайший слот (вт/чт/сб 09:17).")
        print(f"approved {draft_id} variant {variant}")

    elif action == "rw":
        state["awaiting_rewrite"] = draft_id
        tg.answer_callback(query["id"], "send your note as a normal message")
        tg.send_message(f"What should change in {draft.meta['slug']}? Reply with a short note "
                        f"(e.g. 'shorter, lead with the number').")
        print(f"rewrite requested for {draft_id}")

    elif action == "sk":
        draft.status = "skipped"
        draft.save()
        tg.answer_callback(query["id"], "skipped")
        tg.send_message(f"⏭ Пропущено: {draft.meta['slug']}")
        print(f"skipped {draft_id}")


def handle_message(message: dict, state: dict) -> None:
    draft_id = state.get("awaiting_rewrite")
    text = (message.get("text") or "").strip()
    if not draft_id or not text:
        return
    draft = store.find_draft(draft_id)
    if not draft:
        state["awaiting_rewrite"] = ""
        return
    draft.meta["rewrite_note"] = text.replace("\n", " ")
    draft.status = "rewrite_requested"
    draft.save()
    state["awaiting_rewrite"] = ""
    tg.send_message("Noted - regenerating on the next draft run.")
    print(f"rewrite note stored for {draft_id}: {text[:60]}")


def run_rewrites() -> None:
    """Regenerate anything the user asked to rewrite, right here.

    Waiting for the next scheduled draft run would cost up to two days and eat that
    slot - a "make it shorter" note must not push the whole week back.
    """
    pending = [d for d in store.iter_drafts() if d.status == "rewrite_requested"]
    if not pending:
        return
    import draft  # imported lazily: only a rewrite needs the model client
    for item in pending:
        try:
            draft.handle_rewrite(item, dry_run=False)
        except Exception as error:
            print(f"  rewrite of {item.id} failed: {error}")
            tg.send_message(f"Не смог переписать {item.meta['slug']}: {error}")


def expire_stale() -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=EXPIRE_HOURS)
    for draft in store.iter_drafts():
        if draft.status != "pending":
            continue
        try:
            created = datetime.fromisoformat(draft.meta.get("created", ""))
        except ValueError:
            continue
        if created < cutoff:
            draft.status = "skipped"
            draft.meta["skip_reason"] = f"no answer within {EXPIRE_HOURS}h"
            draft.save()
            print(f"expired {draft.id}")


def main() -> None:
    load_env()
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="drain updates once and exit (default)")
    parser.parse_args()

    state = store.read_state()
    updates = tg.get_updates(state.get("tg_offset", 0))
    print(f"{len(updates)} update(s)")

    try:
        for update in updates:
            # Advance the offset first: a malformed update must not be retried forever.
            state["tg_offset"] = update["update_id"] + 1
            try:
                if "callback_query" in update:
                    handle_callback(update["callback_query"], state)
                elif "message" in update:
                    handle_message(update["message"], state)
            except Exception as error:  # one bad update must not block the queue
                print(f"  update {update['update_id']} failed: {error}")
        run_rewrites()
        expire_stale()
    finally:
        store.write_state(state)


if __name__ == "__main__":
    main()
