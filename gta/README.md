# "GTA 7 by Monday": a 3D skit for Build with Prashant

This is a 3D low-poly short of about 42 s (1080×1920, 30 fps). Prashant asks his purple cube AI buddy **Stacky** (AlfaStack
#996EFF) to build GTA 7. Every frame comes from `renderAt(t)` in `main.js` (Three.js in headless Chromium).
Output: `../output/gta7_by_monday.mp4`.

## Rebuild
```bash
npm i                                   # three@0.170.0
pip install kokoro-onnx soundfile playwright
python3 tts.py                          # script.json -> vo/*.wav + vo/lines.json (timings + mouth envelopes)
python3 audio.py                        # -> mix.wav (voice + lo-fi bed + sfx)
python3 -m http.server 8765 &           # page loads modules/json over http
python3 render.py /tmp/frames 4         # all frames (resumable)
ffmpeg -framerate 30 -i /tmp/frames/f%05d.jpg -i mix.wav -c:v libx264 -pix_fmt yuv420p -crf 18 \
  -c:a aac -b:a 192k -shortest -movflags +faststart ../output/gta7_by_monday.mp4
```
`python3 snap.py OUTDIR 1.0 12.5` screenshots single moments.

Kokoro needs `kokoro-v1.0.onnx` and `voices-v1.0.bin` in `/tmp/claude-0/kokoro/`. They come from the kokoro-onnx GitHub releases.
Voices: Prashant = `hm_psi`, Stacky = `am_puck`. To use real voices, drop recordings in as `vo/lNN.wav`. Then rerun
the timing part of `tts.py` and re-render.

## Script
To change a line, edit `script.json`. Timing, captions and lip-flap all follow it.
    PRASHANT: Stacky, how long did GTA Six take to build?
    STACKY  : About twelve years. Thousands of developers.
    PRASHANT: Hmm. Okay.
    PRASHANT: Let's build GTA Seven.
    STACKY  : Sorry... what?
    PRASHANT: By Monday. I have a budget.
    STACKY  : How much?
    PRASHANT: Five hundred rupees. And this laptop.
    STACKY  : This laptop opens Chrome in two business days.
    PRASHANT: Fine. Smaller. One city?
    STACKY  : No.
    PRASHANT: One street?
    STACKY  : No.
    PRASHANT: One car?
    STACKY  : One auto rickshaw. It only turns left.
    PRASHANT: Ship it.
    STACKY  : Shipped. It is honking. At nothing.
    PRASHANT: Honestly? That's how every product starts.
    STACKY  : Small. Ugly. Shipped.
    PRASHANT: Okay... now GTA Eight?
    STACKY  : Goodnight, Prashant.
