"""LinkedIn access tokens live 60 days and non-partner apps get no refresh token,
so the only safe mechanism is a reminder before the expiry."""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import store
import tg
from llm import load_env

WARN_AFTER_DAYS = 53
LIFETIME_DAYS = 60


def main() -> None:
    load_env()
    state = store.read_state()
    issued_raw = state.get("token_issued_at", "")
    if not issued_raw:
        tg.send_message("LinkedIn token: issue date unknown. Run scripts/auth_linkedin.py "
                        "to refresh it and record the date.")
        return

    issued = datetime.fromisoformat(issued_raw)
    age = (datetime.now(timezone.utc) - issued).days
    print(f"token age: {age} days")
    if age < WARN_AFTER_DAYS:
        return

    expires = issued + timedelta(days=LIFETIME_DAYS)
    try:
        import reauth
        link = reauth.authorize_url()
        how = (f"1. Открой ссылку и разреши доступ:\n{link}\n\n"
               f"2. Скопируй код со страницы\n"
               f"3. Запусти воркфлоу reauth с этим кодом:\n"
               f"https://github.com/Anvarka/brand-engine/actions/workflows/reauth.yml")
    except Exception:
        how = "cd ~/proj/brand-engine && python scripts/auth_linkedin.py"

    tg.send_message(
        f"⏳ Токен LinkedIn истекает {expires.date().isoformat()} "
        f"(осталось {LIFETIME_DAYS - age} дн.).\n\n{how}"
    )


if __name__ == "__main__":
    main()
