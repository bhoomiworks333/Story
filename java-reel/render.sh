#!/usr/bin/env bash
# Usage: render.sh <input.mp4> <output.mp4>
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$1")
python3 "$DIR/make_overlays.py" "$DUR" | ffmpeg -y -i "$1" \
  -f rawvideo -pix_fmt rgba -s 2160x3840 -r 30 -i - \
  -filter_complex "[0][1]overlay=0:0:eof_action=pass,format=yuv420p[v]" \
  -map "[v]" -map 0:a -c:v libx264 -crf 18 -preset medium -c:a copy -movflags +faststart "$2"
