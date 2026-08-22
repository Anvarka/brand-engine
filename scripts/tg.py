"""Telegram: the approval surface. Standard library only, same approach as -ai-digest."""
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.request
from typing import Any

from llm import load_env
from store import Draft

API = "https://api.telegram.org/bot{token}/{method}"
LIMIT = 4000


def _call(method: str, payload: dict[str, Any]) -> dict[str, Any]:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    request = urllib.request.Request(
        API.format(token=token, method=method),
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as error:
        raise RuntimeError(f"telegram {method} failed: {error.read().decode()}") from error


def send_message(text: str, keyboard: list[list[dict[str, str]]] | None = None) -> int:
    """Returns the message id of the last chunk sent."""
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    chunks = [text[i:i + LIMIT] for i in range(0, len(text), LIMIT)] or [""]
    message_id = 0
    for index, chunk in enumerate(chunks):
        payload: dict[str, Any] = {"chat_id": chat_id, "text": chunk, "disable_web_page_preview": True}
        if keyboard and index == len(chunks) - 1:
            payload["reply_markup"] = {"inline_keyboard": keyboard}
        message_id = _call("sendMessage", payload)["result"]["message_id"]
    return message_id


def answer_callback(callback_id: str, text: str) -> None:
    _call("answerCallbackQuery", {"callback_query_id": callback_id, "text": text})


def get_updates(offset: int) -> list[dict[str, Any]]:
    payload = {"offset": offset, "timeout": 0, "allowed_updates": ["callback_query", "message"]}
    return _call("getUpdates", payload).get("result", [])


def send_draft(draft: Draft) -> int:
    """Two messages: the English posts, then the Russian gloss carrying the buttons.

    The gloss is there so the decision can be made by reading Russian; the buttons sit on
    the second message so they are next to whatever was read last.
    """
    source = draft.meta.get("source_url", "")
    link = f"\n{source}" if source.startswith("http") else ""
    note = f"\nRewrite note applied: {draft.meta['rewrite_note']}" if draft.meta.get("rewrite_note") else ""

    variant_a = draft.body.get("variant_a", "")
    variant_b = draft.body.get("variant_b", "")
    send_message(
        f"[{draft.meta['pillar']}] {draft.meta['slug']}{link}{note}\n\n"
        f"--- A ({len(variant_a)} chars) ---\n{variant_a}\n\n"
        f"--- B ({len(variant_b)} chars) ---\n{variant_b}"
    )

    russian_a = draft.body.get("ru_a", "")
    russian_b = draft.body.get("ru_b", "")
    keyboard = [
        [{"text": "✅ A", "callback_data": f"ok:{draft.id}:a"},
         {"text": "✅ B", "callback_data": f"ok:{draft.id}:b"}],
        [{"text": "✏️ Переписать", "callback_data": f"rw:{draft.id}"},
         {"text": "⏭ Пропустить", "callback_data": f"sk:{draft.id}"}],
    ]
    gloss = (f"по-русски (не публикуется)\n\n--- A ---\n{russian_a}\n\n--- B ---\n{russian_b}"
             if russian_a or russian_b else "выбери вариант")
    message_id = send_message(gloss, keyboard)

    draft.meta["tg_message_id"] = str(message_id)
    draft.save()
    return message_id


def main() -> None:
    load_env()
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="send a message with the approval keyboard")
    parser.add_argument("--send", help="send an arbitrary text message")
    args = parser.parse_args()

    if args.test:
        keyboard = [
            [{"text": "✅ A", "callback_data": "ok:test:a"}, {"text": "✅ B", "callback_data": "ok:test:b"}],
            [{"text": "✏️ Rewrite", "callback_data": "rw:test"}, {"text": "⏭ Skip", "callback_data": "sk:test"}],
        ]
        print("sent message id:", send_message("brand-engine: approval keyboard test", keyboard))
    elif args.send:
        print("sent message id:", send_message(args.send))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
