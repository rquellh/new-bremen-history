#!/usr/bin/env python3
"""Prepare a generated video clip for scroll scrubbing.

    python3 scripts/normalize_clip.py generated.mp4 assets/video/03-canal.mp4 [--width 1920]

The page seeks the clip to match the scroll position, forward and backward, so
it needs a keyframe every few frames (fast seeks), no B-frames, no audio, and
faststart so the browser can begin before the whole file arrives. Then add the
clip to its chapter in index.html:

    <section class="chapter" id="canal" data-video="assets/video/03-canal.mp4" data-zoom="1 1" ...>

The chapter's still painting stays as the fallback and as the frame shown while
the clip loads, so generate the clip from that still as its first frame.
Needs ffmpeg and ffprobe (brew install ffmpeg).
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

FPS = 30
GOP = 6  # frames between keyframes: 0.2 s at 30 fps
CRF = 23


def normalize(src: Path, dest: Path, width: int) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(src), "-an",
            "-vf", f"scale={width}:-2:flags=lanczos,fps={FPS},format=yuv420p",
            "-c:v", "libx264", "-preset", "slow", "-crf", str(CRF), "-profile:v", "high",
            "-g", str(GOP), "-keyint_min", str(GOP), "-sc_threshold", "0", "-bf", "0",
            "-movflags", "+faststart",
            str(dest),
        ],
        check=True,
    )


def describe(path: Path) -> str:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
            "-show_entries", "stream=width,height,nb_read_frames,duration",
            "-of", "default=nw=1", str(path),
        ],
        check=True, capture_output=True, text=True,
    )
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", type=Path, help="the generated clip")
    parser.add_argument("dest", type=Path, help="where to write the web clip, e.g. assets/video/03-canal.mp4")
    parser.add_argument("--width", type=int, default=1920, help="output width in pixels (default 1920)")
    args = parser.parse_args()

    missing = [tool for tool in ("ffmpeg", "ffprobe") if not shutil.which(tool)]
    if missing:
        print(f"{' and '.join(missing)} not found: brew install ffmpeg", file=sys.stderr)
        return 1
    if not args.source.is_file():
        print(f"{args.source}: not a file", file=sys.stderr)
        return 1

    normalize(args.source, args.dest, args.width)
    print(describe(args.dest))
    print(f"{args.dest.stat().st_size / 1024 / 1024:.1f} MB  {args.dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
