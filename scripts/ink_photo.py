#!/usr/bin/env python3
"""Render a real photograph in the site's ink-wash style, without AI.

    ~/.local/share/uv/tools/mflux/bin/python scripts/ink_photo.py photo.jpg out.png [--width 2048]

Needs OpenCV, NumPy and Pillow (they come with mflux, so run it with mflux's
Python). Every step is an ordinary, deterministic image filter: nothing is
generated or invented, so every building, vehicle and person stays exactly as
photographed. Only the rendering changes:

1. even out the contrast;
2. lightly denoise film grain at the photo's own resolution;
3. break the tones into soft ink-wash layers;
4. trace the photo's own edges as thin ink lines;
5. map paper white to cream and black to sepia ink;
6. enlarge with Lanczos and gentle sharpening, and let the borders fade into the paper.
"""

import argparse
from pathlib import Path

import cv2
import numpy as np

PAPER = np.array([214, 233, 241], np.float32)  # BGR of #f1e9d6, cream
MID = np.array([104, 142, 168], np.float32)    # tan
INK = np.array([36, 44, 52], np.float32)       # sepia-black


def ink_photo(src: Path, width: int = 2048, levels: int = 6, line_strength: float = 0.4, border: bool = True) -> np.ndarray:
    gray = cv2.imread(str(src), cv2.IMREAD_GRAYSCALE)
    if gray is None:
        raise SystemExit(f"can't read {src}")
    return ink_array(gray, width, levels, line_strength, border)


def ink_array(gray: np.ndarray, width: int = 2048, levels: int = 6, line_strength: float = 0.4, border: bool = True) -> np.ndarray:
    """The ink treatment for a grayscale image already in memory; returns BGR."""
    # Work at the photo's own resolution: enlarging first only blurs what the
    # filters then see.
    gray = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
    gray = cv2.createCLAHE(clipLimit=1.4, tileGridSize=(8, 8)).apply(gray)

    # 2. Light denoise: takes the film grain, keeps fine detail.
    gray = cv2.fastNlMeansDenoising(gray, None, h=5, templateWindowSize=7, searchWindowSize=21)
    tone = gray.astype(np.float32) / 255

    # 3. Mostly the photo's own tone, with a faint hint of stepped ink washes.
    steps = cv2.GaussianBlur(np.clip(np.floor(tone * levels) / (levels - 1), 0, 1), (0, 0), 1.5)
    wash = 1 - (1 - (0.2 * steps + 0.8 * tone)) * 0.88

    # 4. Thin ink lines on the photo's long structural edges only, so texture
    # (dirt, grass, grain) doesn't get outlined.
    edges = cv2.Canny(cv2.GaussianBlur(gray, (0, 0), 1.0), 60, 150)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(edges, connectivity=8)
    min_len = max(30, gray.shape[1] // 35)
    keep = np.zeros(count, bool)
    keep[1:] = np.maximum(stats[1:, cv2.CC_STAT_WIDTH], stats[1:, cv2.CC_STAT_HEIGHT]) >= min_len
    lines = cv2.GaussianBlur(np.where(keep[labels], 1.0, 0.0).astype(np.float32), (0, 0), 0.7) * line_strength
    t = np.clip(wash * (1 - lines), 0, 1)[..., None]  # 1 = paper, 0 = ink

    # 5. Gradient map to cream paper and sepia ink.
    color = np.where(t > 0.5, MID + (PAPER - MID) * ((t - 0.5) / 0.5), INK + (MID - INK) * (t / 0.5))

    # Enlarge with Lanczos and a gentle unsharp mask, then a whisper of grain.
    height = round(color.shape[0] * width / color.shape[1])
    color = cv2.resize(color, (width, height), interpolation=cv2.INTER_LANCZOS4)
    color = cv2.addWeighted(color, 1.45, cv2.GaussianBlur(color, (0, 0), 1.4), -0.45, 0)
    grain = cv2.GaussianBlur(np.random.default_rng(1).normal(0, 1, (height, width)).astype(np.float32), (0, 0), 0.8) * 2
    color = color + grain[..., None]
    t = cv2.resize(t[..., 0], (width, height), interpolation=cv2.INTER_LINEAR)[..., None]

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
    parser.add_argument("--lines", type=float, default=0.4, help="ink line strength 0-1 (default 0.4)")
    parser.add_argument("--no-border", action="store_true", help="keep the edges instead of fading them into paper")
    args = parser.parse_args()
    args.dest.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(args.dest), ink_photo(args.src, args.width, args.levels, args.lines, not args.no_border))
    print(f"wrote {args.dest}")


if __name__ == "__main__":
    main()
