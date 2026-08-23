# brand-engine

A LinkedIn posting pipeline for an ML engineer working on recommender systems.
It harvests material, drafts posts, reviews them against a rubric, asks for approval in
Telegram, and publishes the approved one through the LinkedIn API on a fixed slot.

Manual effort per post: one button.

```
harvest  ──▶ data/ideas.jsonl
                   │
draft   ──▶ two variants ──▶ critic pass ──▶ content/queue/*.md ──▶ Telegram + buttons
                                                                        │
approve ──▶ status: approved / rewrite_requested / skipped ◀────────────┘
                   │
publish ──▶ LinkedIn Posts API ──▶ content/published/ + data/stats.jsonl
                   │
stats / weekly ──▶ engagement ──▶ few-shot examples for the next draft
```

## Layout

| Path | What it is |
|------|------------|
| `content/voice.md` | tone, hard rules, stop-list, your writing samples — **the highest-leverage file** |
| `content/pillars.md` | the seven post formats and the failure mode each one has |
| `content/war_stories.md` | your raw incident notes; the only source of truth for war-story posts |
| `content/course_notes.md` | text extracted from the RecSys lecture decks |
| `content/queue/` | drafts awaiting a decision |
| `content/published/` | archive with the post URN |
| `prompts/` | prompt templates, split into a cacheable prefix and the variable part |
| `data/sources.json` | feeds and the keyword prefilter |
| `data/state.json` | Telegram offset, pillar cursor, token issue date |

## Setup

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env          # then fill it in
.venv/bin/python scripts/llm.py --list-models   # confirm the model ids for your key
.venv/bin/python scripts/course_extract.py      # refresh course_notes.md from the decks
```

**LinkedIn access.** A personal account is not enough — the API needs a developer app,
and LinkedIn requires every app to be attached to a Company Page you administer.

1. Company Page — <https://www.linkedin.com/company/setup/new>. Any name; it exists only
   to own the app. Skip if you already administer one.
2. App — <https://www.linkedin.com/developers/apps/new>. Pick that page, upload any logo.
3. On the app's **Settings** tab press *Verify* and open the generated link as the page
   admin. Products stay locked until this is done.
4. **Products** tab — request *Share on LinkedIn* and *Sign In with LinkedIn using OpenID
   Connect*. Both are self-serve and usually granted immediately.
5. **Auth** tab — add the redirect URL `http://localhost:8000/callback`, then copy the
   Client ID and Client Secret into `.env`.

```bash
.venv/bin/python scripts/auth_linkedin.py     # browser consent, prints the token and URN
.venv/bin/python scripts/linkedin.py --check  # confirm the token works
```

It prints `LINKEDIN_ACCESS_TOKEN` and `LINKEDIN_PERSON_URN`. Non-partner apps get **no
refresh token** — the token dies after 60 days, and `token_watch.py` pings Telegram on
day 53 so it never expires silently.

**GitHub.** Secrets: `OPENAI_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`,
`LINKEDIN_ACCESS_TOKEN`, `LINKEDIN_PERSON_URN`. Repository variables (optional):
`LLM_MODEL_CHEAP`, `LLM_MODEL_DEFAULT`, `LLM_MODEL_SMART`, `LINKEDIN_API_VERSION`,
`LINK_PLACEMENT`.

## Schedule

GitHub cron is **UTC**. Author is on MSK (UTC+3); the audience is EU/US.

| Workflow | UTC | MSK | Does |
|----------|-----|-----|------|
| `harvest` | 04:47 daily | 07:47 | fetch feeds, score new items |
| `draft` | 05:07 Mon/Wed/Fri | 08:07 | write two variants, send for approval |
| `approve` | every 20 min, 05–21 | 08–24 | apply your Telegram taps |
| `publish` | 16:07 Tue/Thu/Sat | 19:07 | post the oldest approved draft |
| `stats` | 19:00 daily | 22:00 | engagement snapshot |
| `weekly` | 17:00 Sun | 20:00 | strategy brief to Telegram |
| `token-watch` | 08:00 Mon | 11:00 | warn before the token expires |

The publishing slot follows the **readers**: 16:07 UTC is 12:07 in New York — the US
lunch peak — and 18:07 in Berlin. It also leaves the author a full working day to approve,
since the draft arrives 35 hours earlier.

A draft may wait `DRAFT_TTL_HOURS` (44) before it is dropped. That number is not arbitrary:
it must exceed the 35 hours between a draft and its slot, and fall short of the 48 hours
between two draft runs — so a missed tap costs exactly one post, never the following one.

Scheduled workflows are disabled by GitHub after 60 days without repository activity. The
jobs commit state on almost every run, so the repo stays active on its own.

Approval and publishing are deliberately separate: LinkedIn has no scheduled publishing,
so the slot is ours to choose, and a 20-minute approval lag costs nothing.

## The approval message

Two Telegram messages per draft: the English variants first, then a Russian gloss carrying
the buttons. The gloss exists so the decision can be made by reading Russian — it is
generated on the cheap model and is never published.

```
[✅ A]  [✅ B]
[✏️ Переписать]  [⏭ Пропустить]
```

*Переписать* asks for a note as a plain reply ("shorter", "lead with the number"); the next
`draft` run regenerates from it. A draft nobody answers within 48 hours is skipped, and the
slot goes to the next approved one.

## Source links

`LINK_PLACEMENT` controls where the source URL of a paper or article ends up:

- `body` (default) — appended to the post as `Source: <url>`.
- `comment` — posts it as the first comment, which is where an outbound link costs the
  least reach. **Requires partner access this app does not have** (verified: 403
  `ACCESS_DENIED` on `socialActions.CREATE`), so it falls back to sending the link to
  Telegram for manual pasting.
- `none` — no link at all.

## What the self-serve tier cannot do

`Share on LinkedIn` grants publishing and nothing else. Verified against the live API on
2026-08-23:

| Works | Denied (partner-only) |
|-------|----------------------|
| `POST /rest/posts` — publish | `POST /rest/socialActions/{urn}/comments` — comment |
| `DELETE /rest/posts/{urn}` — delete | `GET /rest/socialActions/{urn}` — likes and comment counts |
| `GET /v2/userinfo` — identity | |

The consequence: **engagement cannot be collected automatically.** `stats.py` detects the
403 and stops instead of failing daily; `weekly` skips the brief while no numbers exist.
Until numbers are entered by hand into `data/stats.jsonl`, the pillar rotation stays
round-robin and drafts get no few-shot examples of what performed.

## Running by hand

```bash
.venv/bin/python scripts/harvest.py --dry-run    # feeds only, no LLM calls
.venv/bin/python scripts/draft.py --dry-run      # write a draft, skip Telegram
.venv/bin/python scripts/draft.py --pillar hot_take
.venv/bin/python scripts/publish.py --dry-run    # print the API payload
.venv/bin/python scripts/stats.py --weekly
```

## Before the first real post

1. Fill the **Voice samples** section of `content/voice.md`. Until then drafts read
   correct but anonymous.
2. Add 3–5 entries to `content/war_stories.md`. The war-story pillar invents nothing, so
   with an empty file it simply falls back to other pillars.
3. Run `scripts/profile_kit.py` and update the profile itself — posts drive traffic to it.
