#!/usr/bin/env bash
# Turn approved master paintings into web images.
#
#   scripts/process-art.sh production/masters/03-canal.png [more ...]
#
# Writes assets/art/<name>-2560.webp and <name>-1440.webp. Then point the
# chapter's image at them in index.html:
#
#   <img src="assets/art/03-canal-1440.webp"
#        srcset="assets/art/03-canal-1440.webp 1440w, assets/art/03-canal-2560.webp 2560w"
#        sizes="100vw" width="2560" height="1440" alt="...">
#
# Set OUT_DIR to write somewhere else.
set -euo pipefail

command -v cwebp >/dev/null || { echo "cwebp not found: brew install webp" >&2; exit 1; }
[ $# -gt 0 ] || { sed -n '2,15p' "$0"; exit 1; }

out="${OUT_DIR:-$(cd "$(dirname "$0")/.." && pwd)/assets/art}"
mkdir -p "$out"

for src in "$@"; do
  name="$(basename "${src%.*}")"
  for w in 2560 1440; do
    cwebp -quiet -q 82 -m 6 -sharp_yuv -resize "$w" 0 "$src" -o "$out/$name-$w.webp"
  done
  ls -lh "$out/$name"-*.webp | awk '{print $5, $NF}'
done
