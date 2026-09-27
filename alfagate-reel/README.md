# AlfaGate Reel: "4,500 saal pehle"

A 43.8 s vertical reel (1080×1920, 24 fps) for LinkedIn and Instagram. It opens on reconstructed Indus Valley cities, hard-cuts
to present-day society chaos, asks the question, and resolves into AlfaGate.

- **Output:** `../output/alfagate_reel.mp4`
- **Look:** built from code, not drawn: a photographic-style 3D reconstruction with real lighting, shadows, depth of field and film grain.
  It is CGI, **not live-action footage**. It reads like a documentary reconstruction, not like a camera shoot.
- **Voice:** male Indian voice (Kokoro `hm_psi`, AI-generated), Hinglish, with burned-in captions so the reel works with sound off.
- **Music and SFX:** every sound is synthesised in `audio.py`. There are no samples and no licensed tracks.

## Edit

| Time | Shot | VO | Super |
|---|---|---|---|
| 0.0–7.6 | Aerial descent over Mohenjo-daro at golden hour (citadel mound and Great Bath on the left) | Kya aapko pata hai… 4,500 saal pehle bhi, log apni society itni organized rakhte the? | 4,500 YEARS AGO |
| 7.6–9.9 | Low shot along a brick street drain, water flowing, covers ahead | Mohenjo-daro mein, covered drainage. | MOHENJO-DARO |
| 9.9–11.8 | Elevated shot down a planned main street, people and carts | Harappa mein, planned streets. | HARAPPA |
| 11.8–14.2 | Dholavira stone reservoir, terraces, stair, inlet channel | Dholavira mein, water management. | DHOLAVIRA |
| 14.2–15.2 | Top-down on the ancient grid, drums accelerate | — | — |
| 15.2–16.6 | **Hard cut + silence.** The same framing on a modern gated society; its main road lies where First Street was | — | 2026 |
| 16.6–18.6 | Visitor register, a new entry being written | Gate pe, aaj bhi register. | PAPER REGISTERS |
| 18.6–20.6 | Residents' group chat flooding in | Maintenance, WhatsApp pe. | ENDLESS GROUP CHATS |
| 20.6–22.8 | Accounts spreadsheet full of `#REF!`, then sticky notes | Complaints alag. Hisaab alag. | MANUAL ACCOUNTS |
| 22.8–23.8 | Lock-screen notifications pile up → everything stops | — | — |
| 23.8–29.6 | Slow push on the phone lying on the register; it lights once | Technology itni aage aa gayi… toh society management kyun nahi? | MAYBE IT'S TIME TO UPGRADE. |
| 29.6–31.8 | Top-down city again; golden lines trace the street system | Organized rehna humein hamesha se aata tha. Bas tools badal gaye. | — |
| 31.8–33.9 | The four city blocks become four app tiles: Visitors, Maintenance, Complaints, Notices | (cont.) | — |
| 33.9–37.6 | AlfaGate Home screen: guest at the gate approved, maintenance paid, Complaints opened | Visitors, maintenance, complaints… sab ek app mein. | — |
| 37.6–43.8 | Logo, "Run your society like it's audited.", CTA | AlfaGate. Apni society ko smarter tareeke se manage kijiye. | Comment "ALFAGATE" for a demo · alfagate.in |

The central device is the grid. The street system of an ancient city becomes the four connected modules of a modern one.
The ancient past is never framed as "better": the line *"Organized rehna humein hamesha se aata tha. Bas tools badal gaye"*
carries the brief's thesis, that the principle is old and only the tools are new.

## Historical accuracy

All three claims match the archaeology: covered street drains at Mohenjo-daro, planned streets at Harappa, and
reservoirs and water channels at Dholavira. The reconstruction also follows the evidence in these ways:

- Fired bricks keep the 1:2:4 ratio (7 × 14 × 28 cm), laid in English bond.
- Main streets have blank walls, with doors on the side lanes.
- Houses are built around courtyards and have wells.
- Street drains have removable covers and open inspection points.
- The Great Bath sits on the raised citadel.
- Transport is solid-wheeled bullock carts with zebu oxen.
- People wear unstitched cotton.

These are deliberately left out: temples, palaces, horses, iron, and the Buddhist stupa that was built later at Mohenjo-daro.
One simplification: the "Harappa" shot reuses the same generic Indus street model. It is labelled
*illustrative reconstruction* on screen.

## Product screens and data

- The app shot recreates the real AlfaGate **Home** screen from the supplied screenshots (`drawApp` in `js/screens.js`,
  drawn in the screenshot's own 272 × 592 pt layout). It keeps the layout, colours and modules: Maintenance Due with
  Pay Now, Pending Visitor Requests with Approve/Reject, Quick Actions (Visitors, Complaints, Notices, Emergency), and
  bottom navigation. No feature outside those screenshots is shown.
- **All resident data is fictional:** Aarav Kapoor, A-1204, Green Valley Residency. The Profile screenshot contains a
  real name and mobile number, so it is deliberately not used anywhere in the film.
- The one invented detail is the "Maintenance paid" confirmation toast after Pay Now. The real post-payment screen
  wasn't supplied. Replace it if AlfaGate shows something different.
- The voiceover is the AI voice (Kokoro `hm_psi`), which is the final choice.
- The CTA "Comment ALFAGATE" only works if someone, or an auto-DM, answers those comments.

## Re-render

```bash
npm install                                 # three.js + fonts
pip install playwright imageio-ffmpeg kokoro-onnx soundfile numpy scipy
python3 vo.py <dir with kokoro-v1.0.onnx + voices-v1.0.bin>   # only if the script changes
python3 audio.py                            # soundtrack.wav
python3 render.py 4                         # frames/ (resumable, ~25–35 min on 4 CPU cores)
./encode.sh                                 # ../output/alfagate_reel.mp4
python3 snap.py /tmp/snaps 3 17.5 35.2      # stills at chosen times, for quick checks
```

## Files

| File | What it is |
|---|---|
| `js/shots.js` | The edit: shot list, camera moves, VO timings |
| `js/ancient.js` | Mohenjo-daro city generator, drains, citadel and Great Bath, carts; the Dholavira reservoir |
| `js/figures.js` | Instanced people with a 6-pose walk cycle |
| `js/modern3d.js` | Present-day gated society for the top-down match cut |
| `js/studio.js` | Close-up desk set (register, phone, laptop, tumbler) and the app-shot phone |
| `js/screens.js` | Register handwriting, chat, lock screen, spreadsheet, AlfaGate UI (placeholder) |
| `js/overlay.js` | Supers, captions, the grid → tiles morph, end card, grain, fades |
| `js/tex.js`, `js/mat.js`, `js/world.js` | Procedural textures, triplanar materials, water, sky, lighting, post-processing |
| `audio.py`, `vo.py` | Score, sound design and mix; voiceover generation |
