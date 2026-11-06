#!/usr/bin/env python3
"""Render a real photograph in the site's ink-wash style, without AI.

    ~/.local/share/uv/tools/mflux/bin/python scripts/ink_photo.py photo.jpg out.png [--width 2048]

Needs OpenCV, NumPy and Pillow (they come with mflux, so run it with mflux's
Python). Every step is an ordinary, deterministic image filter: nothing is
generated or invented, so every building, vehicle and person stays exactly as
photographed. Only the rendering changes:

1. even out the contrast;
2. smooth away film grain while keeping edges (edge-preserving filter);
3. break the tones into soft ink-wash layers;
4. trace the photo's own edges as thin ink lines;
5. map paper white to cream and black to sepia ink;
6. let the borders fade into the paper.
"""

import argparse
from pathlib import Path

import cv2
import numpy as np

PAPER = np.array([214, 233, 241], np.float32)  # BGR of #f1e9d6, cream
MID = np.array([104, 142, 168], np.float32)    # tan
INK = np.array([36, 44, 52], np.float32)       # sepia-black


def ink_photo(src: Path, width: int = 2048, levels: int = 6, line_strength: float = 0.5, border: bool = True) -> np.ndarray:
    gray = cv2.imread(str(src), cv2.IMREAD_GRAYSCALE)
    if gray is None:
        raise SystemExit(f"can't read {src}")
    return ink_array(gray, width, levels, line_strength, border)


def ink_array(gray: np.ndarray, width: int = 2048, levels: int = 6, line_strength: float = 0.5, border: bool = True) -> np.ndarray:
    """The ink treatment for a grayscale image already in memory; returns BGR."""
    gray = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
    gray = cv2.createCLAHE(clipLimit=1.4, tileGridSize=(8, 8)).apply(gray)
    height = round(gray.shape[0] * width / gray.shape[1])
    gray = cv2.resize(gray, (width, height), interpolation=cv2.INTER_CUBIC)

    # 2. Smooth grain but keep shapes.
    smooth = cv2.edgePreservingFilter(cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR), flags=cv2.RECURS_FILTER, sigma_s=60, sigma_r=0.35)
    tone = cv2.cvtColor(smooth, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255

    # 3. Ink-wash layers: quantized tones with soft steps, plus some continuous tone; lightened overall.
    # Mostly the photo's own continuous tone, with a softened hint of stepped washes;
    # more steps than this turns flat areas (dirt, siding, sky) blotchy.
    steps = cv2.GaussianBlur(np.clip(np.floor(tone * levels) / (levels - 1), 0, 1), (0, 0), 3.2)
    wash = 1 - (1 - (0.35 * steps + 0.65 * tone)) * 0.85

    # 4. The photo's own edges as ink lines.
    # Trace a smoothed copy, then keep only long connected edges, so texture
    # (dirt, grass, film grain) doesn't get outlined into blotches.
    soft = cv2.GaussianBlur((tone * 255).astype(np.uint8), (0, 0), 1.6)
    edges = cv2.Canny(soft, 55, 140)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(edges, connectivity=8)
    min_len = max(40, width // 30)
    keep = np.zeros(count, bool)
    keep[1:] = np.maximum(stats[1:, cv2.CC_STAT_WIDTH], stats[1:, cv2.CC_STAT_HEIGHT]) >= min_len
    edges = np.where(keep[labels], 255, 0).astype(np.uint8)
    edges = cv2.dilate(edges, np.ones((2, 2), np.uint8))
    lines = cv2.GaussianBlur(edges.astype(np.float32) / 255, (0, 0), 1.2) * line_strength
    t = np.clip(wash * (1 - lines), 0, 1)[..., None]  # 1 = paper, 0 = ink

    # 5. Gradient map to cream paper and sepia ink, plus a little paper grain.
    color = np.where(t > 0.5, MID + (PAPER - MID) * ((t - 0.5) / 0.5), INK + (MID - INK) * (t / 0.5))
    grain = cv2.GaussianBlur(np.random.default_rng(1).normal(0, 1, t.shape[:2]).astype(np.float32), (0, 0), 1.0) * 4
    color = color + grain[..., None]

    # 6. Borders fade into the paper along a slightly irregular edge.
    if border:
        h, w = t.shape[:2]
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        mask = np.clip(np.minimum(np.minimum(xx, w - 1 - xx) / (w * 0.1), np.minimum(yy, h - 1 - yy) / (h * 0.12)), 0, 1)
        rough = cv2.resize(cv2.GaussianBlur(np.random.default_rng(2).random((h // 16 + 1, w // 16 + 1)).astype(np.float32), (0, 0), 1.5), (w, h))
        mask = np.clip(mask * 1.15 - (rough - 0.5) * 0.5, 0, 1)
        mask = mask * mask * (3 - 2 * mask)
        color = PAPER + (color - PAPER) * mask[..., None]

    return np.clip(color, 0, 255).astype(np.uint8)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("src", type=Path)
    parser.add_argument("dest", type=Path)
    parser.add_argument("--width", type=int, default=2048)
    parser.add_argument("--levels", type=int, default=6, help="ink-wash tone layers (default 6)")
    parser.add_argument("--lines", type=float, default=0.5, help="ink line strength 0-1 (default 0.5)")
    parser.add_argument("--no-border", action="store_true", help="keep the edges instead of fading them into paper")
    args = parser.parse_args()
    args.dest.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.dest), ink_photo(args.src, args.width, args.levels, args.lines, not args.no_border))
    print(f"wrote {args.dest}")


if __name__ == "__main__":
    main()
