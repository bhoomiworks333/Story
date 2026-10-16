# Tesla Roadster / physical AI reel

Output: `output/tesla_roadster_ai_reel.mp4` (1080x1920, 30 fps, 45.2 s, -16.6 LUFS), a lighter
`_preview.mp4`, and an `.srt`.

## Build
```
python3 gen.py <take.mp4> <hop.mp4> <launch.mp4> <reveal.mp4>          # clips, audio, hf/index.html, srt
cd hf && HYPERFRAMES_BROWSER_PATH=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell \
    npx hyperframes@0.8.164 render -o ../build/silent.mp4 --fps 30 --quality high
python3 gen.py <take.mp4> <hop.mp4> <launch.mp4> <reveal.mp4> --mux    # -> output/
```
Inputs: the talking-head take (720x1280), the two 1918x1078 screen recordings (hop and 0-60 launch), and
the 1280x720 reveal recording. Words were timed with Vosk (`vosk.json`, small en-us model).

## What it does
- Script cuts: "breaking the laws of physics", "ground missile", "AI runs millions of simulations",
  "in the near future ... real time", "let me know in the comments". Pauses over ~0.45 s are cut too.
- 1.1x speed with the pitch kept (`atempo`), light noise reduction, loudnorm -16 LUFS.
- House style from the earlier reels: talking head full frame with no zoom, white-box Inter SemiBold
  captions of 2-4 words as spoken (hard cuts), cards and pop-ups at the top above the eyes.
- Full-screen Tesla cutaways on the hook and on "updated like software"; spec cards on the fans,
  thrusters and top speed. Every shot is reframed so the re-uploader's watermark and the YouTube
  player stay outside the frame; "Footage: Tesla" is shown whenever Tesla footage is on screen.
- 0-60 note: "*Thrust & Rocket trims. Base model: under 1.6 s".
- The generative-design card is an illustration (labelled as such), not a Tesla part.
