#!/bin/bash
cd /home/user/Story/bears_edit
python3 compose.py A > work/render_A.log 2>&1 &
python3 compose.py B > work/render_B.log 2>&1
wait
grep -h wrote work/render_A.log work/render_B.log
for f in bears_*.mp4; do ffprobe -v error -show_entries format=duration -of csv=p=0 $f; done
