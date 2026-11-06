#!/usr/bin/env python3
"""Paint chapter scenes locally with Z-Image Turbo (via mflux on Apple Silicon).

    python3 scripts/paint.py                  # every scene, 3 versions each
    python3 scripts/paint.py 1 5 --versions 1 --size 1536x864
    python3 scripts/paint.py 3 --dry-run      # print the prompt only
    python3 scripts/paint.py 8 --strength 0.6 # follow the reference photo more closely

A scene with a `reference` in prompts.toml starts from that photo in
production/references/ and keeps its layout; `strength` (0-1) sets how closely.

Prompts come from production/prompts.toml. Drafts go to production/masters/drafts/
as <file>-s<seed>.png; existing drafts are skipped. A gallery of all drafts is
written to production/masters/drafts/index.html. Copy the one you pick to
production/masters/<file>.png and run scripts/process_art.py on it.

Needs mflux (uv tool install mflux). The first run downloads the 4-bit model
(about 6 GB) into ~/.cache/huggingface.
"""

import argparse
import hashlib
import shutil
import subprocess
import sys
import time
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = ROOT / "production" / "prompts.toml"
DRAFTS = ROOT / "production" / "masters" / "drafts"
REFERENCES = ROOT / "production" / "references"
MODEL = "filipstrand/Z-Image-Turbo-mflux-4bit"
COMMAND = "mflux-generate-z-image-turbo"


def build_prompt(cfg: dict, scene: dict) -> str:
    parts = [cfg["style"]["text"], scene["text"]]
    if scene.get("flat"):
        parts.append(cfg["style"]["flat"])
    parts += [cfg["composition"][scene["copy"]], cfg["style"]["rules"]]
    return " ".join(parts)


def find_command() -> str | None:
    return shutil.which(COMMAND) or next(
        (str(p) for p in [Path.home() / ".local" / "bin" / COMMAND] if p.exists()), None
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("scenes", nargs="*", type=int, help="scene numbers, 1-10 (default: all)")
    parser.add_argument("--versions", type=int, default=3, help="versions per scene, each with its own seed (default 3)")
    parser.add_argument("--size", default="2048x1152", help="WIDTHxHEIGHT, multiples of 16 (default 2048x1152)")
    parser.add_argument("--steps", type=int, default=9)
    parser.add_argument("--strength", type=float, help="override every scene's reference strength (0-1)")
    parser.add_argument("--no-reference", action="store_true", help="paint from the text alone")
    parser.add_argument("--dry-run", action="store_true", help="print prompts without painting")
    args = parser.parse_args()

    cfg = tomllib.loads(PROMPTS.read_text(encoding="utf-8"))
    scenes = cfg["scene"]
    picked = [scenes[n - 1] for n in args.scenes] if args.scenes else scenes
    width, height = (int(v) for v in args.size.lower().split("x"))

    command = find_command()
    if not command and not args.dry_run:
        print(f"{COMMAND} not found: uv tool install mflux", file=sys.stderr)
        return 1

    DRAFTS.mkdir(parents=True, exist_ok=True)
    for scene in picked:
        prompt = build_prompt(cfg, scene)
        reference = None if args.no_reference else scene.get("reference")
        strength = args.strength if args.strength is not None else scene.get("strength", 0.4)
        if reference and not (REFERENCES / reference).exists():
            print(f"{scene['file']}: reference {reference} not found in {REFERENCES}", file=sys.stderr)
            return 1
        # Prefer the warm-tinted copy (scripts/tint_references.py) so gray photos don't pull the palette gray.
        ref_path = None
        if reference:
            tinted = REFERENCES / "tinted" / reference
            ref_path = tinted if tinted.exists() else REFERENCES / reference
        suffix = f"-r{strength:.2f}{'t' if ref_path and ref_path.parent.name == 'tinted' else ''}" if reference else ""
        # A short fingerprint of the prompt, so editing a prompt never reuses an old draft's name.
        suffix += "-p" + hashlib.sha1(prompt.encode()).hexdigest()[:4]
        seeds = [scene["seed"] + 1000 * k for k in range(args.versions)]
        todo = [s for s in seeds if not (DRAFTS / f"{scene['file']}-s{s}{suffix}.png").exists()]
        print(f"\n{scene['file']}: seeds {', '.join(map(str, todo)) or 'all done'}"
              + (f" (reference {reference} at {strength})" if reference else ""))
        if args.dry_run:
            print(prompt)
            continue
        for seed in todo:
            out = DRAFTS / f"{scene['file']}-s{seed}{suffix}.png"
            start = time.monotonic()
            cmd = [command, "--model", MODEL, "--steps", str(args.steps), "--seed", str(seed),
                   "--width", str(width), "--height", str(height),
                   "--negative-prompt", cfg["style"]["negative"],
                   "--prompt", prompt, "--output", str(out)]
            if ref_path:
                cmd += ["--image", str(ref_path), str(strength)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0 or not out.exists():
                print(f"  failed (seed {seed}):\n{result.stderr[-800:]}", file=sys.stderr)
                return 1
            print(f"  {out.relative_to(ROOT)}  {time.monotonic() - start:.0f}s")
            write_gallery(scenes)
    write_gallery(scenes)
    return 0


def write_gallery(scenes: list[dict]) -> None:
    """A page of every draft, grouped by scene, at production/masters/drafts/index.html."""
    rows = []
    for scene in scenes:
        files = sorted(DRAFTS.glob(f"{scene['file']}-*.png"))
        if not files:
            continue
        cells = "".join(
            f'<figure><a href="{f.name}"><img src="{f.name}" loading="lazy" alt=""></a><figcaption>{f.name}</figcaption></figure>'
            for f in files
        )
        rows.append(f"<section><h2>{scene['file']}</h2><div>{cells}</div></section>")
    (DRAFTS / "index.html").write_text(
        "<!doctype html><meta charset=utf-8><title>Painting drafts</title>"
        "<style>body{font:15px/1.4 Georgia,serif;margin:24px;background:#efe7d6;color:#1d2320}"
        "section div{display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));gap:14px}"
        "img{width:100%;display:block;border-radius:2px}figure{margin:0}figcaption{font-size:12px;color:#69746d}"
        "h2{font-weight:600;margin:28px 0 10px}</style><h1>Painting drafts</h1>" + "".join(rows),
        encoding="utf-8",
    )


if __name__ == "__main__":
    sys.exit(main())
