#!/usr/bin/env python3
"""Turn approved master paintings into web images.

    python3 scripts/process_art.py production/masters/03-canal.png [more ...]

Writes WebPs at 2560 and 1440 pixels wide to assets/art/ and prints the <img>
attributes to paste into the chapter in index.html. Images are never enlarged:
a smaller master (a 1K playground image, say) is kept at its own width. Needs
cwebp (brew install webp).
"""

import argparse
import shutil
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIDTHS = (2560, 1440)
QUALITY = 82


def image_size(path: Path) -> tuple[int, int]:
    """Width and height of a PNG or JPEG, read from its header."""
    with path.open("rb") as f:
        head = f.read(26)
        if head.startswith(b"\x89PNG\r\n\x1a\n"):
            return struct.unpack(">II", head[16:24])
        if head.startswith(b"\xff\xd8"):
            f.seek(2)
            while True:
                marker, length = struct.unpack(">2sH", f.read(4))
                if marker[0] != 0xFF:
                    break
                if 0xC0 <= marker[1] <= 0xCF and marker[1] not in (0xC4, 0xC8, 0xCC):
                    h, w = struct.unpack(">xHH", f.read(5))
                    return w, h
                f.seek(length - 2, 1)
    raise ValueError(f"{path}: can't read the size (use a PNG or JPEG master)")


def target_widths(source_width: int) -> list[int]:
    widths = [w for w in WIDTHS if w <= source_width]
    if source_width < WIDTHS[0] and source_width not in widths:
        widths.append(source_width)
    return sorted(set(widths), reverse=True)


def convert(src: Path, out_dir: Path, widths: list[int]) -> dict[int, Path]:
    outputs = {}
    for width in widths:
        dest = out_dir / f"{src.stem}-{width}.webp"
        subprocess.run(
            ["cwebp", "-quiet", "-q", str(QUALITY), "-m", "6", "-sharp_yuv",
             "-resize", str(width), "0", str(src), "-o", str(dest)],
            check=True,
        )
        outputs[width] = dest
    return outputs


def markup(outputs: dict[int, Path], size: tuple[int, int]) -> str:
    rel = {w: p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else p.as_posix() for w, p in outputs.items()}
    small, large = min(rel), max(rel)
    srcset = ", ".join(f"{rel[w]} {w}w" for w in sorted(rel))
    height = round(large * size[1] / size[0])
    return (
        f'src="{rel[small]}"\n'
        f'srcset="{srcset}"\n'
        f'sizes="100vw" width="{large}" height="{height}"'
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("masters", nargs="+", type=Path, help="master images (PNG, JPEG, TIFF or WebP)")
    parser.add_argument("--out", type=Path, default=ROOT / "assets" / "art", help="output folder (default: assets/art)")
    args = parser.parse_args()

    if not shutil.which("cwebp"):
        print("cwebp not found: brew install webp", file=sys.stderr)
        return 1

    args.out.mkdir(parents=True, exist_ok=True)
    for src in args.masters:
        if not src.is_file():
            print(f"skipping {src}: not a file", file=sys.stderr)
            continue
        size = image_size(src)
        if size[0] < WIDTHS[0]:
            print(f"note: {src.name} is {size[0]}x{size[1]}; kept at that size, not enlarged")
        outputs = convert(src, args.out.resolve(), target_widths(size[0]))
        for width, path in sorted(outputs.items()):
            print(f"{path.stat().st_size / 1024:6.0f} KB  {path}")
        print(f"\n<img> attributes for {src.name}:\n{markup(outputs, size)}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
