#!/usr/bin/env python3
"""Generate the mulberry-paper texture laid over every painting.

    python3 scripts/make_paper.py

Writes assets/paper-fibers.svg: a seamless tile of long, curly paper fibers and
small flecks. The page multiplies it over the paintings so every chapter shares
the same handmade paper, whatever paper the image model drew.
"""

import math
import random
from pathlib import Path

TILE = 900
OUT = Path(__file__).resolve().parent.parent / "assets" / "paper-fibers.svg"
rng = random.Random(1833)


def fiber() -> list[tuple[float, float]]:
    """One fiber: a wandering, slightly curly line built from short segments."""
    x, y = rng.uniform(0, TILE), rng.uniform(0, TILE)
    angle = rng.uniform(0, math.tau)
    length = rng.uniform(18, 70)
    steps = max(4, int(length / 6))
    pts = [(x, y)]
    for _ in range(steps):
        angle += rng.gauss(0, 0.45)
        x += math.cos(angle) * length / steps
        y += math.sin(angle) * length / steps
        pts.append((x, y))
    return pts


def wrapped(pts: list[tuple[float, float]], attrs: str) -> list[str]:
    # A mark that crosses an edge is drawn again on the opposite side, so the
    # tile repeats without seams. Marks fully inside are drawn once.
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    shifts_x = [0] + ([-TILE] if max(xs) > TILE else []) + ([TILE] if min(xs) < 0 else [])
    shifts_y = [0] + ([-TILE] if max(ys) > TILE else []) + ([TILE] if min(ys) < 0 else [])
    out = []
    for dx in shifts_x:
        for dy in shifts_y:
            d = "M" + " ".join(f"{px + dx:.0f},{py + dy:.0f}" for px, py in pts)
            out.append(f'<path d="{d}" {attrs}/>')
    return out


def main() -> None:
    marks = []
    for _ in range(90):
        tone = rng.choice(["#b9a47c", "#c8b48c", "#a8916a", "#d6c6a3"])
        width = rng.uniform(0.5, 1.3)
        opacity = rng.uniform(0.25, 0.55)
        marks += wrapped(fiber(), f'stroke="{tone}" stroke-width="{width:.1f}" opacity="{opacity:.2f}"')
    for _ in range(35):
        x, y = rng.uniform(0, TILE), rng.uniform(0, TILE)
        r = rng.uniform(0.6, 1.8)
        marks.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r:.1f}" fill="#8f7a55" stroke="none" opacity="{rng.uniform(0.15, 0.4):.2f}"/>')

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{TILE}" height="{TILE}" viewBox="0 0 {TILE} {TILE}">'
        '<g fill="none" stroke-linecap="round" stroke-linejoin="round">'
        + "".join(marks)
        + "</g></svg>"
    )
    OUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
