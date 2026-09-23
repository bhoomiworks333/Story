# AlfaStack Founder Story: animation source

This is a code-built paper cut-out animation. Every frame is a pure function of time (`renderAt(t)` in `main.js`),
rendered with headless Chromium and encoded with ffmpeg.

- Output: `../output/alfastack_founder_story.mp4`, 1080×1920 (9:16), 24 fps, 57 s, subtitles burned in.
- Audio: `soundtrack.wav` is a **placeholder** made from synthesised music plus sound effects (`audio.py`). There is **no voiceover** yet.

## Re-render

```bash
pip install playwright imageio-ffmpeg pillow numpy
python3 render.py /tmp/frames 4            # all frames (≈18 min on 4 cores)
python3 render.py /tmp/frames 4 28-38      # only a time range, for quick checks
python3 audio.py                           # rebuilds soundtrack.wav
FF=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
$FF -y -framerate 24 -i /tmp/frames/f%05d.jpg -i soundtrack.wav -c:v libx264 -pix_fmt yuv420p -crf 18 \
    -preset slow -c:a aac -b:a 192k -shortest -movflags +faststart ../output/alfastack_founder_story.mp4
```

`python3 snap.py index.html /tmp/snap 5.0 13.6 38.0` screenshots single moments.

## Files

| File | What it is |
|---|---|
| `lib.js` | SVG helpers, easing, paper texture patterns, torn-edge cut-outs, text cards |
| `characters.js` | Prashant (kid / teen / college / adult), father, customers, task critters, props |
| `scene_shop.js` | Scenes 0–2 (hook, shop, the question) and the closing kid callback |
| `scene_nb.js` | Scene 3: the notebook years |
| `scene_desk.js` | Scenes 4–5: adult Prashant connects the business, and the parts converge into the logo |
| `scene_factory.js` | Scene 6: the ecosystem (camera-eye, sensor, AlfaStack, robot arm) |
| `scene_brand.js` | Logo, tagline, end card, and the adult close-up |
| `main.js` | Timeline, subtitles, hero text cards |

The logo is a **vector redraw** of the 325 px PNG. If you send the official SVG, I'll swap it in.

## Voiceover recording sheet (for Prashant)

Record in a quiet room on a phone. Speak as if telling a friend, not presenting. Each line has to fit its window.
Pauses are part of the film.

| # | Starts | Ends | Line |
|---|---|---|---|
| 1 | 0:02.3 | 0:05.0 | Growing up, I spent a lot of time in my father's shop. |
| 2 | 0:05.3 | 0:07.9 | He was running the whole business… |
| 3 | 0:08.3 | 0:11.3 | …and somehow, carrying all of it in his head. |
| (silence) | 0:11.3 | 0:19.3 | *No voice. The question is on screen and the music drops out.* |
| 4 | 0:19.3 | 0:21.3 | That question never really left me. |
| 5 | 0:21.6 | 0:23.7 | So I started learning. |
| 6 | 0:24.0 | 0:27.5 | Technology. Systems. How things could work differently. |
| 7 | 0:28.6 | 0:30.6 | And slowly, an idea took shape. |
| 8 | 0:30.9 | 0:34.3 | What if a business didn't have to depend on one person's memory? |
| 9 | 0:34.7 | 0:37.2 | What if everything could just… talk to each other? |
| (end) | 0:37.2 | 0:57.0 | *No voice. The visuals and text cards carry the ending.* |

If his natural pace differs, send the recording and I'll re-time the subtitles and scenes to his voice. That is
easier than making him match the timings.
