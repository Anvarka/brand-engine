"""Phase 0: generate LinkedIn profile copy from the author's own material.

Runs once, writes content/profile/draft.md for manual editing. The profile converts the
traffic that posts create, so it comes before any automation.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import store
from llm import complete, load_env


def gather_material(extra: list[Path]) -> str:
    chunks = []
    notes = store.ROOT / "content" / "course_notes.md"
    if notes.exists():
        chunks.append("# RecSys course taught by the author (extracted lecture decks)\n"
                      + notes.read_text()[:20000])
    war = store.ROOT / "content" / "war_stories.md"
    if war.exists() and len(war.read_text()) > 400:
        chunks.append("# Production war stories\n" + war.read_text()[:6000])
    for path in extra:
        if path.exists():
            chunks.append(f"# {path.name}\n" + path.read_text()[:6000])
    return "\n\n---\n\n".join(chunks)


def main() -> None:
    load_env()
    parser = argparse.ArgumentParser()
    parser.add_argument("--add", type=Path, nargs="*", default=[],
                        help="extra files to feed in: CV, repo READMEs, notes")
    args = parser.parse_args()

    material = gather_material(args.add)
    if len(material) < 500:
        raise SystemExit("not enough material - run scripts/course_extract.py or pass --add <cv.md>")

    output = complete("profile", {
        "voice": (store.ROOT / "content" / "voice.md").read_text(),
        "material": material,
    }, tier="smart")

    target = store.ROOT / "content" / "profile" / "draft.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(f"# Profile copy - generated {store.now()[:10]}\n\n{output}\n")
    print(output)
    print(f"\nwritten to {target}")


if __name__ == "__main__":
    main()
