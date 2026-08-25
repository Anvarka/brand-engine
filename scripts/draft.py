"""Pick what to write about, write it, have it reviewed, send it for approval."""
from __future__ import annotations

import argparse
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

import store
import tg
from llm import complete, load_env

PILLARS = [
    "paper_teardown", "recsys_101", "war_story",
    "industry_teardown", "hot_take", "build_log",
]
# Pillars fed by local files rather than by the feed harvest.
LOCAL_MATERIAL = {
    "recsys_101": "course_notes.md",
    "war_story": "war_stories.md",
    "build_log": "build_log.md",
}
TOP_N_FEWSHOT = 3
HALF_LIFE_DAYS = 7      # an idea is worth half as much a week after it appeared
SUPERSEDE_HOURS = store.DRAFT_TTL_HOURS  # never let a stale draft block the next slot


class Critique(BaseModel):
    hook: int
    specificity: int
    single_claim: int
    credibility: int
    voice_fit: int
    banned_hits: list[str]
    char_count: int
    verdict: Literal["pass", "revise"]
    edits: list[str]


# ------------------------------------------------------------------ choosing a subject

def next_pillar(state: dict, forced: str = "") -> str:
    if forced:
        return forced
    return PILLARS[state.get("pillar_cursor", 0) % len(PILLARS)]


def local_topic(pillar: str, state: dict) -> tuple[str, str] | None:
    """Next unused `## section` from the pillar's local material file."""
    path = store.ROOT / "content" / LOCAL_MATERIAL[pillar]
    if not path.exists():
        return None
    sections = re.split(r"^## ", path.read_text(), flags=re.M)[1:]
    used = set(state.get("used_topics", []))
    for section in sections:
        title = section.splitlines()[0].strip()
        key = f"{pillar}:{title}"
        if key in used or len(section.strip()) < 200:
            continue
        return title, section.strip()[:8000]
    return None


def best_local_section(pillar: str, query: str) -> str:
    """Attach the local material a feed idea refers to.

    A seeded idea like "Cold start (Lecture 4)" carries a two-line summary; the lecture
    itself is what makes the post specific. Matching on word overlap is enough here -
    there are nine sections, not nine thousand.
    """
    if pillar not in LOCAL_MATERIAL:
        return ""
    path = store.ROOT / "content" / LOCAL_MATERIAL[pillar]
    if not path.exists():
        return ""
    wanted = set(re.findall(r"[a-z]{4,}", query.lower()))
    best, best_score = "", 0
    for section in re.split(r"^## ", path.read_text(), flags=re.M)[1:]:
        title = section.splitlines()[0].strip()
        score = len(wanted & set(re.findall(r"[a-z]{4,}", title.lower())))
        if score > best_score:
            best, best_score = section.strip(), score
    return best[:8000] if best_score else ""


def freshness_score(idea: dict) -> float:
    """Relevance decayed by age, so today's good paper beats last month's better one.

    Age comes from the feed's own publication timestamp where the feed provides one, and
    from our discovery time otherwise.
    """
    stamp = idea.get("published_ts") or 0
    if stamp:
        age_days = (datetime.now(timezone.utc).timestamp() - stamp) / 86400
    else:
        try:
            seen = datetime.fromisoformat(idea.get("scored_at", ""))
            age_days = (datetime.now(timezone.utc) - seen).total_seconds() / 86400
        except ValueError:
            age_days = 0.0
    age_days = max(age_days, 0.0)
    return idea.get("relevance", 0) * 0.5 ** (age_days / HALF_LIFE_DAYS)


def feed_idea(pillar: str) -> tuple[dict, list[dict]] | None:
    ideas = store.read_jsonl(store.IDEAS_FILE)
    candidates = [i for i in ideas if not i.get("used") and i.get("pillar") == pillar]
    if not candidates:
        candidates = [i for i in ideas if not i.get("used")]
    if not candidates:
        return None
    best = max(candidates, key=freshness_score)
    return best, ideas


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return (slug or "post")[:48]


# ---------------------------------------------------------------------- generation

def few_shot_blocks() -> tuple[str, str]:
    """Best and worst performing published posts, as structural examples."""
    stats = store.read_jsonl(store.STATS_FILE)
    latest: dict[str, dict] = {}
    for record in stats:
        latest[record["urn"]] = record
    if len(latest) < 3:
        return "(no published history yet)", "(no published history yet)"
    ranked = sorted(latest.values(), key=lambda r: r.get("engagement", 0), reverse=True)
    def render(records: list[dict]) -> str:
        return "\n\n---\n\n".join(
            f"engagement {r.get('engagement', 0)}:\n{r.get('text', '')}" for r in records
        ) or "(none)"
    return render(ranked[:TOP_N_FEWSHOT]), render(ranked[-TOP_N_FEWSHOT:])


def split_variants(raw: str) -> tuple[str, str]:
    def grab(tag: str) -> str:
        match = re.search(rf"<{tag}>(.*?)</{tag}>", raw, re.S)
        return match.group(1).strip() if match else ""
    variant_a, variant_b = grab("variant_a"), grab("variant_b")
    if not variant_a and not variant_b:  # model ignored the tags - fall back to a split
        halves = raw.strip().split("\n\n\n", 1)
        variant_a = halves[0].strip()
        variant_b = halves[1].strip() if len(halves) > 1 else ""
    return variant_a, variant_b


def generate(pillar: str, idea: str, material: str, rewrite_note: str = "") -> tuple[str, str]:
    voice = (store.ROOT / "content" / "voice.md").read_text()
    pillars = (store.ROOT / "content" / "pillars.md").read_text()
    few_shot, anti_patterns = few_shot_blocks()
    note = f"# Revision instructions (apply these)\n\n{rewrite_note}" if rewrite_note else ""
    raw = complete("draft", {
        "voice": voice,
        "pillars": pillars,
        "pillar": pillar,
        "idea": idea,
        "material": material[:12000],
        "few_shot": few_shot,
        "anti_patterns": anti_patterns,
        "rewrite_note": note,
    })
    return split_variants(raw)


def translate(text: str) -> str:
    """Russian gloss of a finished post. For the approval message only - never published."""
    if not text.strip():
        return ""
    return complete("gloss", {"text": text}, tier="cheap").strip()


def review(text: str, material: str) -> Critique:
    voice = (store.ROOT / "content" / "voice.md").read_text()
    return complete("critic", {"voice": voice, "material": material[:8000], "draft": text},
                    schema=Critique)


def generate_reviewed(pillar: str, idea: str, material: str, note: str = "") -> tuple[str, str, list[Critique]]:
    """One generation, one critic pass, at most one automatic revision."""
    variant_a, variant_b = generate(pillar, idea, material, note)
    critiques = [review(variant_a, material), review(variant_b, material)]
    if all(c.verdict == "pass" for c in critiques):
        return variant_a, variant_b, critiques

    edits = []
    for label, critique in zip("AB", critiques):
        if critique.verdict == "revise":
            edits.append(f"Variant {label}: " + "; ".join(critique.edits + [
                f"remove banned phrase {phrase!r}" for phrase in critique.banned_hits]))
    revised_note = (note + "\n" if note else "") + "\n".join(edits)
    variant_a, variant_b = generate(pillar, idea, material, revised_note)
    return variant_a, variant_b, [review(variant_a, material), review(variant_b, material)]


# --------------------------------------------------------------------------- entry

def resolve_material(draft: store.Draft) -> str:
    """Rebuild the source text a draft was written from.

    The draft file stores only a reference - a lecture section or a URL - so a rewrite
    has to load the content back. Passing the bare reference would leave the model with
    nothing to be faithful to, and the critic with nothing to check.
    """
    ref = draft.meta.get("material_ref", "")

    if " :: " in ref:
        filename, _, title = ref.partition(" :: ")
        path = store.ROOT / "content" / filename
        if path.exists():
            for section in re.split(r"^## ", path.read_text(), flags=re.M)[1:]:
                if section.splitlines()[0].strip() == title.strip():
                    return section.strip()[:8000]

    if ref.startswith("http"):
        for idea in store.read_jsonl(store.IDEAS_FILE):
            if idea.get("url") == ref:
                material = (f"Source: {idea['source']} - {idea['title']}\n{idea['url']}\n\n"
                            f"{idea['summary']}")
                local = best_local_section(draft.meta.get("pillar", ""),
                                           f"{idea['title']} {idea['summary']}")
                return material + (f"\n\n# Related material from your own course\n\n{local}" if local else "")

    return draft.meta.get("idea", "")


def handle_rewrite(draft: store.Draft, dry_run: bool) -> None:
    note = draft.meta.get("rewrite_note", "")
    material = resolve_material(draft)
    print(f"regenerating {draft.id} with note: {note!r}")
    variant_a, variant_b, critiques = generate_reviewed(
        draft.meta["pillar"], draft.meta["idea"], material, note)
    draft.body["variant_a"], draft.body["variant_b"] = variant_a, variant_b
    draft.body["ru_a"], draft.body["ru_b"] = translate(variant_a), translate(variant_b)
    draft.status = "pending"
    draft.save()
    report(draft, critiques)
    if not dry_run:
        tg.send_draft(draft)


def report(draft: store.Draft, critiques: list[Critique]) -> None:
    print(f"\n=== {draft.path.name} [{draft.meta['pillar']}] ===")
    for label, critique in zip("AB", critiques):
        print(f"  {label}: {critique.verdict} ({critique.char_count} chars) "
              f"hook={critique.hook} spec={critique.specificity} claim={critique.single_claim} "
              f"cred={critique.credibility} voice={critique.voice_fit} banned={critique.banned_hits}")
    for label in ("a", "b"):
        print(f"\n--- variant {label.upper()} ---\n{draft.body.get(f'variant_{label}', '')}")


def main() -> None:
    load_env()
    parser = argparse.ArgumentParser()
    parser.add_argument("--pillar", default="", help="force a pillar instead of the rotation")
    parser.add_argument("--dry-run", action="store_true", help="write the draft file but do not send to Telegram")
    args = parser.parse_args()

    state = store.read_state()

    pending_rewrite = [d for d in store.iter_drafts() if d.status == "rewrite_requested"]
    if pending_rewrite:
        handle_rewrite(pending_rewrite[0], args.dry_run)
        return

    # A slot must always produce a draft. An unanswered one is replaced, not allowed to
    # block generation - one missed tap used to stall the whole pipeline silently.
    for stale in store.iter_drafts():
        if stale.status != "pending":
            continue
        stale.status = "superseded"
        stale.meta["skip_reason"] = "replaced by a newer draft"
        stale.save()
        print(f"superseded {stale.id}")
        if not args.dry_run:
            tg.send_message(f"Предыдущий драфт «{stale.meta['slug']}» остался без ответа — "
                            f"заменяю его новым.")

    pillar = next_pillar(state, args.pillar)
    material_ref = ""

    if pillar in LOCAL_MATERIAL:
        topic = local_topic(pillar, state)
        if not topic:
            print(f"no unused material for {pillar}, falling back to the feed")
            pillar = "paper_teardown"
        else:
            title, material = topic
            idea = f"Explain one non-obvious point from: {title}"
            slug = slugify(title)
            material_ref = f"{LOCAL_MATERIAL[pillar]} :: {title}"
            state.setdefault("used_topics", []).append(f"{pillar}:{title}")

    if pillar not in LOCAL_MATERIAL or not material_ref:
        picked = feed_idea(pillar)
        if not picked:
            print("no unused ideas - run harvest.py first")
            return
        idea_record, all_ideas = picked
        pillar = idea_record.get("pillar", pillar)
        idea = f"{idea_record['angle']}\n\nWhy now: {idea_record.get('why_now', '')}"
        material = (f"Source: {idea_record['source']} - {idea_record['title']}\n"
                    f"{idea_record['url']}\n\n{idea_record['summary']}")
        local = best_local_section(pillar, f"{idea_record['title']} {idea_record['summary']}")
        if local:
            material += f"\n\n# Related material from your own course\n\n{local}"
        material_ref = idea_record["url"]
        slug = slugify(idea_record["title"])
        for record in all_ideas:
            if record["hash"] == idea_record["hash"]:
                record["used"] = True
        store.rewrite_jsonl(store.IDEAS_FILE, all_ideas)

    draft = store.Draft.create(slug=slug, pillar=pillar, idea=idea, source_url=material_ref)
    draft.meta["material_ref"] = material_ref
    variant_a, variant_b, critiques = generate_reviewed(pillar, idea, material)
    draft.body["variant_a"], draft.body["variant_b"] = variant_a, variant_b
    draft.body["ru_a"], draft.body["ru_b"] = translate(variant_a), translate(variant_b)
    draft.save()
    report(draft, critiques)

    state["pillar_cursor"] = state.get("pillar_cursor", 0) + 1
    store.write_state(state)

    if not args.dry_run:
        tg.send_draft(draft)
        print(f"\nsent to Telegram for approval: {draft.id}")


if __name__ == "__main__":
    main()
