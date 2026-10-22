#!/bin/bash
# Builds the final audio mix for the reel. Run from duet_edit/work.
set -e
U=/root/.claude/uploads/b1b737dd-7786-500b-ba01-8092888fc00f
M="$U/1fc0be68-Caleb_Arredondo_-_Feeling_Blue.mp3"
read TOTAL MUSIC_IN DIP TALK_END TAP <<< $(cd ../scripts && python3 -c "from timeline import *; print(f'{TOTAL:.3f} {MUSIC_IN:.3f} {MUSIC_DIP:.3f} {TALK_END:.3f} {TAP_AT:.3f}')")
ms(){ python3 -c "print(int(round($1*1000)))"; }
MLEN=$(python3 -c "print($TOTAL-$MUSIC_IN)")
FO=$(python3 -c "print($TALK_END-$MUSIC_IN)"); DP=$(python3 -c "print($DIP-$MUSIC_IN)")
FC="[0:a]aresample=48000,aformat=channel_layouts=stereo,adelay=5433:all=1,apad,atrim=0:$TOTAL,asplit=2[voice][key];
[1:a]volume=-1dB[room];
[2:a]volume=3.4dB,adelay=350:all=1[b1];
[3:a]volume=3.4dB,adelay=1550:all=1[b2];
[4:a]volume=-8dB,adelay=2220:all=1[ding];
[5:a]volume=5.4dB,adelay=$(ms $TAP):all=1[tap];
[6:a]atrim=0:$MLEN,asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo,volume=-9.4dB,
 afade=t=in:st=0:d=1,volume='1-0.5*min(max((t-$DP)/0.4,0),1)':eval=frame,afade=t=out:st=$FO:d=1.5,adelay=$(ms $MUSIC_IN):all=1,apad,atrim=0:$TOTAL[mus];
[mus][key]sidechaincompress=threshold=0.03:ratio=4:attack=15:release=350[duck];
[voice][duck][room][b1][b2][ding][tap]amix=inputs=7:normalize=0:duration=first,atrim=0:$TOTAL[mix]"
ffmpeg -v error -y -i talk_clean_rnn.wav -i wake_room.wav -i sfx_buzz1.wav -i sfx_buzz2.wav -i sfx_ding.wav -i sfx_tap.wav -ss 24.28 -i "$M" \
  -filter_complex "$FC" -map "[mix]" -ar 48000 mix_raw.wav
J=$(ffmpeg -hide_banner -i mix_raw.wav -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g(){ echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
ffmpeg -v error -y -i mix_raw.wav -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=48000" mix_final.wav
