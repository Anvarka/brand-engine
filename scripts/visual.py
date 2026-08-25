"""Render the image that ships with a post.

Deterministic on purpose: the model supplies structure, this module draws it. An image
model would produce prettier pictures with "NDGC" written on them, and for an audience of
recommender-system engineers a misspelled metric costs more than plain graphics gain.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import textwrap
from pathlib import Path
from typing import Literal

from PIL import Image, ImageDraw, ImageFont
from pydantic import BaseModel

import store
from llm import complete, load_env

WIDTH, HEIGHT = 1200, 1500       # 4:5 portrait: the tallest format LinkedIn allows in feed,
                                 # and the natural shape for a top-to-bottom pipeline
BG = "#1c1b22"                   # matches the brand mark
FG = "#f7f7fa"
MUTED = "#8b8a95"
ACCENT = "#5b8dd9"

FONT_DIRS = [
    "/usr/share/fonts/truetype/dejavu",              # ubuntu runner
    "/System/Library/Fonts/Supplemental",            # macOS
    "/opt/homebrew/opt/fontconfig/share/fonts",
]
SANS = ["DejaVuSans.ttf", "Arial.ttf", "Helvetica.ttc"]
SANS_BOLD = ["DejaVuSans-Bold.ttf", "Arial Bold.ttf", "Arial.ttf"]
MONO = ["DejaVuSansMono.ttf", "Menlo.ttc", "Courier New.ttf"]


class Node(BaseModel):
    id: str
    label: str


class Edge(BaseModel):
    source: str
    target: str
    label: str


class Visual(BaseModel):
    kind: Literal["schema", "code", "concept"]
    title: str
    nodes: list[Node]
    edges: list[Edge]
    code: str
    alt_text: str


# ------------------------------------------------------------------------------- fonts

def font(names: list[str], size: int) -> ImageFont.FreeTypeFont:
    for directory in FONT_DIRS:
        for name in names:
            path = Path(directory) / name
            if path.exists():
                try:
                    return ImageFont.truetype(str(path), size)
                except OSError:
                    continue
    return ImageFont.load_default(size)


def canvas() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    return image, ImageDraw.Draw(image)


def draw_title(draw: ImageDraw.ImageDraw, title: str, width: int = 34) -> int:
    """Returns the y coordinate where the body may start."""
    face = font(SANS_BOLD, 52)
    y = 90
    for line in textwrap.wrap(title, width=width)[:3]:
        draw.text((90, y), line, font=face, fill=FG)
        y += 66
    return y + 40


def draw_footer(image: Image.Image, draw: ImageDraw.ImageDraw) -> None:
    mark = store.ROOT / "assets" / "mark.png"
    label_x = 90
    if mark.exists():
        logo = Image.open(mark).convert("RGBA").resize((56, 56))
        image.paste(logo, (90, HEIGHT - 116), logo)
        label_x = 166
    draw.text((label_x, HEIGHT - 100), "TLIAMOV LAB", font=font(SANS, 26), fill=MUTED)


# ------------------------------------------------------------------------------ kinds

def render_schema(spec: Visual, out: Path) -> Path:
    """Graphviz lays the graph out; we only supply styling."""
    if not shutil.which("dot"):
        print("graphviz not installed - falling back to a concept card")
        return render_concept(spec, out)

    def esc(text: str) -> str:
        return text.replace('"', "'")

    lines = [
        "digraph G {",
        f'  bgcolor="{BG}"; rankdir=TB; splines=ortho; nodesep=0.55; ranksep=0.75;',
        f'  node [shape=box style="rounded,filled" fillcolor="#26252e" color="{MUTED}"'
        f'   fontcolor="{FG}" fontname="DejaVu Sans" fontsize=20 margin="0.35,0.25" penwidth=2];',
        f'  edge [color="{ACCENT}" fontcolor="{MUTED}" fontname="DejaVu Sans" fontsize=16 penwidth=2];',
    ]
    for node in spec.nodes[:7]:
        lines.append(f'  "{esc(node.id)}" [label="{esc(node.label[:24])}"];')
    known = {n.id for n in spec.nodes[:7]}
    for edge in spec.edges:
        if edge.source in known and edge.target in known:
            label = f' [label="{esc(edge.label[:18])}"]' if edge.label else ""
            lines.append(f'  "{esc(edge.source)}" -> "{esc(edge.target)}"{label};')
    lines.append("}")

    dot_file = out.with_suffix(".dot")
    dot_file.write_text("\n".join(lines))
    graph_png = out.with_name(out.stem + "-graph.png")
    subprocess.run(["dot", "-Tpng", "-Gdpi=220", str(dot_file), "-o", str(graph_png)],
                   check=True, capture_output=True)

    image, draw = canvas()
    body_top = draw_title(draw, spec.title)
    graph = Image.open(graph_png).convert("RGB")
    box_w, box_h = WIDTH - 180, HEIGHT - body_top - 170
    # Fill the frame instead of merely fitting inside it: a thin diagram floating in a
    # square of empty background reads as a rendering mistake.
    scale = min(box_w / graph.width, box_h / graph.height)
    graph = graph.resize((int(graph.width * scale), int(graph.height * scale)), Image.LANCZOS)
    image.paste(graph, ((WIDTH - graph.width) // 2, body_top + (box_h - graph.height) // 2))
    draw_footer(image, draw)
    image.save(out)
    dot_file.unlink(missing_ok=True)
    graph_png.unlink(missing_ok=True)
    return out


def render_code(spec: Visual, out: Path) -> Path:
    from pygments import lex
    from pygments.lexers import PythonLexer
    from pygments.token import Token

    palette = {
        Token.Keyword: "#c792ea", Token.Name.Function: "#82aaff",
        Token.Name.Class: "#82aaff", Token.String: "#c3e88d",
        Token.Comment: "#6b6a75", Token.Number: "#f78c6c",
        Token.Operator: ACCENT, Token.Name.Builtin: "#ffcb6b",
    }

    def colour(token_type) -> str:
        while token_type is not Token:
            if token_type in palette:
                return palette[token_type]
            token_type = token_type.parent
        return FG

    image, draw = canvas()
    y = draw_title(draw, spec.title)

    lines = [line.rstrip() for line in spec.code.strip("\n").split("\n")][:22]
    panel_w = WIDTH - 140
    # Shrink until the longest line fits: a code card with a truncated line is worse
    # than a slightly smaller one.
    size = 30
    while size > 15:
        face = font(MONO, size)
        longest = max((draw.textlength(line, font=face) for line in lines), default=0)
        if longest <= panel_w - 60:
            break
        size -= 1
    face = font(MONO, size)
    line_height = int(size * 1.42)

    panel_h = len(lines) * line_height + 56
    available = HEIGHT - y - 150
    top = y + max(0, (available - panel_h) // 2)
    draw.rounded_rectangle((70, top, WIDTH - 70, top + panel_h), radius=18, fill="#26252e")

    x, y_line = 100, top + 28
    for token_type, value in lex("\n".join(lines), PythonLexer()):
        for index, part in enumerate(value.split("\n")):
            if index:
                x, y_line = 100, y_line + line_height
            if part:
                draw.text((x, y_line), part, font=face, fill=colour(token_type))
                x += draw.textlength(part, font=face)

    draw_footer(image, draw)
    image.save(out)
    return out


def render_concept(spec: Visual, out: Path) -> Path:
    image, draw = canvas()
    face = font(SANS_BOLD, 68)
    lines = textwrap.wrap(spec.title, width=22)[:6]
    total = len(lines) * 88
    y = (HEIGHT - total) // 2 - 40
    draw.rectangle((90, y - 30, 98, y + total + 10), fill=ACCENT)
    for line in lines:
        draw.text((136, y), line, font=face, fill=FG)
        y += 88
    draw_footer(image, draw)
    image.save(out)
    return out


RENDERERS = {"schema": render_schema, "code": render_code, "concept": render_concept}


def build(post: str, pillar: str, out: Path) -> tuple[Path, Visual]:
    spec = complete("visual", {"post": post, "pillar": pillar}, schema=Visual, tier="cheap")
    if spec.kind == "schema" and len(spec.nodes) < 2:
        spec.kind = "concept"          # a schema with one box is not a schema
    path = RENDERERS[spec.kind](spec, out)
    return path, spec


# ------------------------------------------------------------------------------- demo

DEMOS = [
    Visual(kind="schema", title="Where cold-start recall is actually lost",
           nodes=[Node(id="a", label="new item"), Node(id="b", label="metadata encoder"),
                  Node(id="c", label="candidate set"), Node(id="d", label="ranker"),
                  Node(id="e", label="impressions")],
           edges=[Edge(source="a", target="b", label="no history"),
                  Edge(source="b", target="c", label="embeds"),
                  Edge(source="c", target="d", label="top-k"),
                  Edge(source="d", target="e", label="serves"),
                  Edge(source="e", target="b", label="feedback")],
           code="", alt_text="Pipeline from a new item to impressions."),
    Visual(kind="code", title="Recall@k that respects the candidate set",
           nodes=[], edges=[],
           code='''def recall_at_k(candidates, relevant, k=200):
    """Share of relevant items the retriever put in reach of the ranker."""
    if not relevant:
        return 0.0
    top = set(candidates[:k])
    hits = sum(1 for item in relevant if item in top)
    return hits / len(relevant)


# the ranker can only reorder what retrieval returned
headroom = 1.0 - recall_at_k(candidates, relevant)''',
           alt_text="Python function computing recall at k."),
    Visual(kind="concept", title="Offline metrics measure how well you copy the old policy",
           nodes=[], edges=[], code="", alt_text="Typographic statement about offline metrics."),
]


def main() -> None:
    load_env()
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="render one image of each kind")
    parser.add_argument("--out-dir", type=Path, default=Path("/tmp"))
    args = parser.parse_args()

    if not args.demo:
        parser.print_help()
        return

    args.out_dir.mkdir(parents=True, exist_ok=True)
    for spec in DEMOS:
        path = RENDERERS[spec.kind](spec, args.out_dir / f"demo-{spec.kind}.png")
        print(f"{spec.kind:8} -> {path} ({Image.open(path).size[0]}x{Image.open(path).size[1]})")


if __name__ == "__main__":
    main()
