#!/usr/bin/env python3
"""Tint the black-and-white reference photos into the paintings' palette.

    ~/.local/share/uv/tools/mflux/bin/python scripts/tint_references.py

Needs Pillow, which comes with mflux, so run it with mflux's Python (above).
Gray photos pull the paintings gray; mapping white to cream paper and black to
sepia ink lets the image generator start from the right palette. Writes
production/references/tinted/<name>, which scripts/paint.py prefers.
"""

from pathlib import Path

from PIL import Image, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
REFS = ROOT / "production" / "references"
OUT = REFS / "tinted"
PAPER = (241, 233, 214)   # cream
INK = (52, 44, 36)        # warm sepia-black
MID = (168, 142, 104)     # tan


def tint(src: Path, dest: Path) -> None:
    gray = ImageOps.grayscale(Image.open(src))
    gray = ImageOps.autocontrast(gray, cutoff=1)
    gray = gray.filter(ImageFilter.GaussianBlur(0.8))  # soften photo grain into wash
    warm = ImageOps.colorize(gray, black=INK, white=PAPER, mid=MID, blackpoint=10, whitepoint=245, midpoint=150)
    warm.save(dest, quality=92)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    for src in sorted(REFS.glob("*.jpg")):
        tint(src, OUT / src.name)
        print(f"tinted {src.name}")


if __name__ == "__main__":
    main()
