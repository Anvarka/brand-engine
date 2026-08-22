"""Pull the text out of the RecSys course decks into one markdown file.

A .pptx is a zip of XML, so this needs no dependencies. Run it once (and again whenever
the decks change) to give the recsys_101 pillar its raw material.
"""
from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path

import store

DEFAULT_COURSE = Path.home() / "proj" / "online_course_resSys" / "recSys_course"
OUT = store.ROOT / "content" / "course_notes.md"
SLIDE_RE = re.compile(r"ppt/slides/slide(\d+)\.xml$")
TEXT_RE = re.compile(r"<a:t>(.*?)</a:t>", re.S)


def deck_text(path: Path) -> str:
    lines: list[str] = []
    with zipfile.ZipFile(path) as archive:
        slides = sorted(
            (n for n in archive.namelist() if SLIDE_RE.match(n)),
            key=lambda n: int(SLIDE_RE.match(n).group(1)),
        )
        for index, name in enumerate(slides, start=1):
            xml = archive.read(name).decode("utf-8", "ignore")
            fragments = [re.sub(r"\s+", " ", t).strip() for t in TEXT_RE.findall(xml)]
            fragments = [f for f in fragments if f]
            if fragments:
                lines.append(f"- slide {index}: " + " | ".join(fragments))
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--course-dir", type=Path, default=DEFAULT_COURSE)
    args = parser.parse_args()

    decks = sorted(args.course_dir.glob("*.pptx"))
    if not decks:
        raise SystemExit(f"no .pptx found in {args.course_dir}")

    chunks = ["# Course notes\n",
              "Auto-extracted from the lecture decks by scripts/course_extract.py.\n",
              "Raw material for the recsys_101 pillar; each `##` section is one topic.\n"]
    for deck in decks:
        text = deck_text(deck)
        if text:
            chunks.append(f"\n## {deck.stem}\n\n{text}\n")
    OUT.write_text("\n".join(chunks))
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB) from {len(decks)} decks")


if __name__ == "__main__":
    main()
