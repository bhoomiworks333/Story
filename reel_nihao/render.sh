#!/usr/bin/env bash
# Reel edit: denoise + loudnorm, burned-in English subs (covering the source's Hindi captions),
# push-in on "Meeha!", 1 s freeze at the end. Usage: render.sh <source.mp4> [out_dir]
set -euo pipefail
SRC="$1"; OUT_DIR="${2:-$(dirname "$0")/../output}"
HERE="$(cd "$(dirname "$0")" && pwd)"
WORK="${WORK:-$(mktemp -d)}"
NAME="$(basename "${SRC%.*}")"
OUT="$OUT_DIR/${NAME}_final.mp4"
[ "$(realpath "$SRC")" != "$(realpath -m "$OUT")" ] || { echo "refusing to overwrite source"; exit 1; }

# RNNoise model (GregorR/rnnoise-models, "somnolent-hogwash")
MODEL="$WORK/sh.rnnn"
[ -f "$MODEL" ] || curl -sSfL -o "$MODEL" \
  https://raw.githubusercontent.com/GregorR/rnnoise-models/master/somnolent-hogwash-2018-09-01/sh.rnnn

# --- audio: version C (arnndn at mix=0.5; full strength cut the laptop voice by ~6 dB) ---
PRE="aresample=48000,highpass=f=80,lowpass=f=12000,arnndn=m=$MODEL:mix=0.5,afftdn=nf=-25"
J=$(ffmpeg -hide_banner -i "$SRC" -vn -af "$PRE,loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
g(){ echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
LN="loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true"

# --- video: smooth 100%->108% push-in from 16.9 s ("Meeha!") to the last frame, cosine ease,
# sub-pixel via perspective (which only exposes the frame index "in", so t = in/30); centred on
# child + laptop; then scale to 1080x1920, 1 s freeze, burn subs ---
EX=728; EY=289   # colour emoji position, measured against subs.ass
T0=16.9; DUR=2.333; CX=720; CY=1173; W=1440; H=2560
Z="(1+0.08*(1-cos(PI*clip((in/30-$T0)/$DUR\,0\,1)))/2)"
CW="($W/$Z)"; CH="($H/$Z)"
X0="clip($CX-$CW/2\,0\,$W-$CW)"; Y0="clip($CY-$CH/2\,0\,$H-$CH)"
VF="scale=$W:$H,format=yuv420p,perspective=x0='$X0':y0='$Y0':x1='$X0+$CW':y1='$Y0':x2='$X0':y2='$Y0+$CH':x3='$X0+$CW':y3='$Y0+$CH':interpolation=cubic:sense=source:eval=frame"
VF="$VF,scale=1080:1920:flags=lanczos,tpad=stop_mode=clone:stop_duration=1,ass=$HERE/subs.ass"

ffmpeg -hide_banner -y -i "$SRC" -loop 1 -i "$HERE/emoji.png" -filter_complex \
  "[0:v]$VF[v];[v][1:v]overlay=$EX:$EY:enable='lt(t,4)':shortest=1,format=yuv420p[vo];[0:a]$PRE,$LN,aresample=48000,apad=pad_dur=1[ao]" \
  -map "[vo]" -map "[ao]" -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 192k -ar 48000 -t 20.233 -movflags +faststart "$OUT"
echo "$OUT"
