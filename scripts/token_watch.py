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
    tg.send_message(
        f"LinkedIn token expires {expires.date().isoformat()} ({LIFETIME_DAYS - age} days left).\n\n"
        f"cd ~/proj/brand-engine && python scripts/auth_linkedin.py\n"
        f"then update the LINKEDIN_ACCESS_TOKEN secret in the repo settings."
    )


if __name__ == "__main__":
    main()
