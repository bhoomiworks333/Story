# Garba chanda reel (reach)

Output: `output/garba_chanda_reel.mp4` (1080×1920, 30fps, 31.9 s, no music), a smaller
`output/garba_chanda_reel_preview.mp4`, and `output/garba_chanda_reel.srt`.

v2 is built with HyperFrames: the take plays as shot (no zoom, no hands crop), with white-box
captions (black Inter SemiBold, 2-4 words, hard cuts) and pop-ups animated with GSAP.

Rebuild:
```
NODE_PATH=$(npm root -g) node snap_assets.js       # pop-up PNGs -> build/, copy them to hf/assets/
ffmpeg -i <take.mp4> -an -c:v libx264 -crf 16 -g 30 -keyint_min 30 -pix_fmt yuv420p hf/assets/take.mp4
python3 gen_hf.py                                  # hf/index.html + output srt
cd hf && HYPERFRAMES_BROWSER_PATH=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell \
  npx hyperframes@0.8.145 render -o ../build/hf_silent.mp4 --fps 30
```
then mux the take's audio plus 0.85 s of the counting SFX at the start (loudnorm -16 LUFS).

Caption timing was aligned from audio pauses and sibilant anchors, not from a transcript.
`build.py` is the v1 (PIL/ffmpeg) pipeline with the zooms and hands hook, kept for reference.
