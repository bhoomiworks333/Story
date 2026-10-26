#!/bin/bash
# Final audio mix for the Harvey reel. Run from harvey_edit/work.
# Usage: ../scripts/mix_audio.sh [music_file [music_start_offset_seconds]]
set -e
MUSIC="$1"; MOFF="${2:-0}"
read TOTAL WH CH DS DE TE MIN <<< $(cd ../scripts && python3 -c "from timeline import *; print(f'{TOTAL:.3f} {WHOOSH_AT:.3f} {CHIME_AT:.3f} {DIP[0]:.3f} {DIP[1]:.3f} {TALK_END:.3f} {MUSIC_IN:.3f}')")
ms(){ python3 -c "print(int(round($1*1000)))"; }
FC="[0:a]aresample=48000,aformat=channel_layouts=stereo,apad,atrim=0:$TOTAL,asplit=2[voice][key];
[1:a]volume=-3.7dB,adelay=$(ms $WH):all=1[wh];
[2:a]volume=0.7dB,adelay=$(ms $CH):all=1[ch]"
INPUTS=(-i voice_clean.wav -i sfx_whoosh.wav -i sfx_chime.wav); MIX="[voice][wh][ch]"; N=3
if [ -n "$MUSIC" ]; then
  MLEN=$(python3 -c "print($TOTAL-$MIN)")
  MGAIN=$(ffmpeg -hide_banner -ss $MOFF -t $MLEN -i "$MUSIC" -af ebur128 -f null - 2>&1 | grep -E '^\s+I:' | awk '{print -26-$2}')
  D0=$(python3 -c "print($DS-$MIN)"); D1=$(python3 -c "print($DE-$MIN)"); FO=$(python3 -c "print($TE-$MIN)")
  FC="$FC;[3:a]atrim=0:$MLEN,asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,volume=${MGAIN}dB,afade=t=in:st=0:d=0.5,
 volume='1-0.5*min(max((t-$D0)/0.3,0),1)+0.5*min(max((t-$D1)/0.3,0),1)':eval=frame,afade=t=out:st=$FO:d=1.5,adelay=$(ms $MIN):all=1,apad,atrim=0:$TOTAL[m];
[m][key]sidechaincompress=threshold=0.03:ratio=4:attack=15:release=300[duck]"
  INPUTS+=(-ss $MOFF -i "$MUSIC"); MIX="$MIX[duck]"; N=4
fi
[ -z "$MUSIC" ] && FC="$FC;[key]anullsink"
FC="$FC;${MIX}amix=inputs=$N:normalize=0:duration=first,atrim=0:$TOTAL[mix]"
ffmpeg -v error -y "${INPUTS[@]}" -filter_complex "$FC" -map "[mix]" -ar 48000 mix_raw.wav
J=$(ffmpeg -hide_banner -i mix_raw.wav -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g(){ echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -v error -y -i mix_raw.wav -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000" mix_final.wav
