#!/usr/bin/env bash
# Usage: render.sh <input.mp4> <output.mp4>
# Hook stays the full clip; code card 3-6 s; "30 years" caption 6 s to end.
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"
python3 "$DIR/make_overlays.py" "$TMP"
ffmpeg -y -i "$1" -loop 1 -i "$TMP/hook.png" -loop 1 -i "$TMP/code.png" -loop 1 -i "$TMP/muscle.png" \
  -filter_complex "\
[2]format=rgba,fade=in:st=3:d=0.2:alpha=1,fade=out:st=5.85:d=0.15:alpha=1[code];\
[3]format=rgba,fade=in:st=6:d=0.2:alpha=1[mus];\
[0][1]overlay=0:0:shortest=1[a];[a][code]overlay=0:0:shortest=1[b];[b][mus]overlay=0:0:shortest=1,format=yuv420p[v]" \
  -map "[v]" -map 0:a -c:v libx264 -crf 18 -preset medium -c:a copy -movflags +faststart "$2"
rm -rf "$TMP"
