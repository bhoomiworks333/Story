# Garba chanda reel (reach)

Output: `output/garba_chanda_reel.mp4` (1080×1920, 30fps, ~32.8 s, captions burned in, no music) and
`output/garba_chanda_reel.srt`.

Rebuild:
```
NODE_PATH=$(npm root -g) node snap_assets.js          # pop-ups + captions -> build/*.png
python3 build.py <take.mp4> <counting_sfx.mp3> ../../output/garba_chanda_reel.mp4
```
All timings live in `timeline.json` (source-take seconds; output = source + 0.9 s hook).
Caption timing was aligned from audio pauses and sibilant anchors, not from a transcript.
