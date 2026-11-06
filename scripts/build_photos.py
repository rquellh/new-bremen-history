#!/usr/bin/env python3
"""Build the chapter images from real photographs listed in production/photos.toml.

    .venv/bin/python scripts/build_photos.py              # every chapter
    .venv/bin/python scripts/build_photos.py 03-canal     # just one

For each photo it:
1. downloads the original into production/references/ (git-ignored) if missing;
2. removes captions written or printed on the photo (the `clean` rectangles),
   filling only the writing itself from the surrounding pixels (OpenCV inpainting);
3. renders it in the ink style (scripts/ink_photo.py), inventing nothing;
4. writes WebPs to assets/art/ and a before/after preview of any cleaning to
   production/masters/photos/.

Needs the project venv: uv venv .venv && uv pip install --python .venv/bin/python
opencv-python-headless numpy pillow
"""

import argparse
import html
import re
import sys
import tomllib
import urllib.request
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ink_photo import ink_array  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "production" / "photos.toml"
ORIGINALS = ROOT / "production" / "references"
PREVIEWS = ROOT / "production" / "masters" / "photos"
ART = ROOT / "assets" / "art"
PAGE = ROOT / "index.html"
WIDTHS = (2048, 1280)
QUALITY = 82


def fetch(photo: dict) -> Path:
    slug = photo["nbha"].lower().replace("nbha", "").replace("photos", "").strip().replace(" ", "-")
    dest = ORIGINALS / f"{photo['file']}--nbha-{slug}.jpg"
    if not dest.exists():
        req = urllib.request.Request(photo["url"], headers={"User-Agent": "new-bremen-history-build/1.0"})
        dest.write_bytes(urllib.request.urlopen(req, timeout=60).read())
        print(f"  downloaded {photo['nbha']}")
    return dest


def clean(gray: np.ndarray, rects: list[list[float]]) -> tuple[np.ndarray, np.ndarray]:
    """Fill in writing inside the given rectangles. Returns (cleaned, mask)."""
    h, w = gray.shape
    # Writing is a thin stroke that differs sharply from its neighborhood.
    background = cv2.medianBlur(gray, 21)
    strokes = (cv2.absdiff(gray, background) > 28).astype(np.uint8) * 255
    mask = np.zeros_like(gray)
    for x, y, rw, rh in rects:
        x0, y0, x1, y1 = int(x * w), int(y * h), int((x + rw) * w), int((y + rh) * h)
        mask[y0:y1, x0:x1] = strokes[y0:y1, x0:x1]
    mask = cv2.dilate(mask, np.ones((5, 5), np.uint8))
    return cv2.inpaint(gray, mask, 9, cv2.INPAINT_TELEA), mask


def build(photo: dict) -> None:
    print(photo["file"])
    gray = cv2.imread(str(fetch(photo)), cv2.IMREAD_GRAYSCALE)
    if photo.get("clean"):
        cleaned, mask = clean(gray, photo["clean"])
        PREVIEWS.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(PREVIEWS / f"{photo['file']}-clean.png"), np.vstack([gray, cleaned]))
        print(f"  cleaned {int(mask.astype(bool).sum())} px of written caption")
        gray = cleaned
    inked = ink_array(gray, width=WIDTHS[0])
    for width in WIDTHS:
        height = round(inked.shape[0] * width / inked.shape[1])
        img = inked if width == inked.shape[1] else cv2.resize(inked, (width, height), interpolation=cv2.INTER_AREA)
        out = ART / f"{photo['file']}-{width}.webp"
        cv2.imwrite(str(out), img, [cv2.IMWRITE_WEBP_QUALITY, QUALITY])
        print(f"  {out.relative_to(ROOT)}  {width}x{height}  {out.stat().st_size // 1024} KB")
    sync_page(photo, inked.shape[1], inked.shape[0])


def sync_page(photo: dict, width: int, height: int) -> None:
    """Point the chapter's image, alt text, caption and credit in index.html at this photo."""
    page = PAGE.read_text(encoding="utf-8")
    f = photo["file"]
    credit = html.escape(photo["credit"], quote=True).replace("&#x27;", "&rsquo;")
    kind = photo.get("kind", "photograph")  # or "drawing"
    label = "Drawing" if kind == "drawing" else "Photo"
    lazy = 'fetchpriority="high"' if f.startswith("01") else 'loading="lazy"'
    figure = (
        f'<figure class="art">\n        <img src="assets/art/{f}-1280.webp" '
        f'srcset="assets/art/{f}-1280.webp 1280w, assets/art/{f}-2048.webp 2048w" '
        f'sizes="(max-width: 720px) 100vw, 60vw" width="{width}" height="{height}" {lazy}\n'
        f'             alt="{kind.capitalize()}: {credit}">\n'
        f'        <figcaption>{credit} New Bremen Historic Association.</figcaption>\n      </figure>'
    )
    fig_re = re.compile(r'<figure class="art">\s*<img src="assets/art/' + re.escape(f) + r'-1280\.webp".*?</figure>', re.S)
    page, n = fig_re.subn(lambda m: figure, page, count=1)
    if n != 1:
        print(f"  index.html: no figure found for {f}; left unchanged", file=sys.stderr)
        return
    # The credit line in the same chapter: the first one after this figure.
    start = page.index(figure)
    credit_re = re.compile(r'<p class="credit">(?:Photo|Drawing): .*?</p>', re.S)
    m = credit_re.search(page, start)
    if m:
        new = f'<p class="credit">{label}: {credit} <span>New Bremen Historic Association</span></p>'
        page = page[: m.start()] + new + page[m.end() :]
    PAGE.write_text(page, encoding="utf-8")
    print("  index.html updated")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("files", nargs="*", help="chapter files to build, e.g. 03-canal (default: all)")
    args = parser.parse_args()
    photos = tomllib.loads(CONFIG.read_text(encoding="utf-8"))["photo"]
    picked = [p for p in photos if not args.files or p["file"] in args.files]
    if not picked:
        print("no matching photos", file=sys.stderr)
        return 1
    ORIGINALS.mkdir(parents=True, exist_ok=True)
    ART.mkdir(parents=True, exist_ok=True)
    for photo in picked:
        build(photo)
    return 0


if __name__ == "__main__":
    sys.exit(main())
