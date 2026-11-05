#!/usr/bin/env bash
# Prepare a generated video clip for scroll scrubbing.
#
#   scripts/normalize-clip.sh generated.mp4 assets/video/03-canal.mp4 [width]
#
# The page seeks the clip to match scroll position, forward and backward, so it
# needs a keyframe every few frames (fast seeks), no B-frames, no audio, and
# faststart so the browser can begin before the whole file arrives. Then add
# the clip to its chapter in index.html:
#
#   <section class="chapter" id="canal" data-video="assets/video/03-canal.mp4" data-zoom="1 1" ...>
#
# The chapter's still painting stays as the fallback and as the frame shown
# while the clip loads, so generate the clip from that still as its first frame.
set -euo pipefail

command -v ffmpeg >/dev/null || { echo "ffmpeg not found: brew install ffmpeg" >&2; exit 1; }
[ $# -ge 2 ] || { sed -n '2,16p' "$0"; exit 1; }

in="$1"
out="$2"
width="${3:-1920}"
mkdir -p "$(dirname "$out")"

ffmpeg -hide_banner -loglevel error -y -i "$in" -an \
  -vf "scale=${width}:-2:flags=lanczos,fps=30,format=yuv420p" \
  -c:v libx264 -preset slow -crf 23 -profile:v high \
  -g 6 -keyint_min 6 -sc_threshold 0 -bf 0 \
  -movflags +faststart \
  "$out"

ffprobe -v error -select_streams v:0 -count_frames \
  -show_entries stream=width,height,nb_read_frames,duration -of default=nw=1 "$out"
ls -lh "$out" | awk '{print $5, $NF}'
