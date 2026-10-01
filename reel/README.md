# Fine-tuning reel edit

Source: the ~1-minute cut (720×1280, 59 s). Output: `output/finetune_reel_final.mp4` (59 s, 1080×1920, 30 fps, H.264 + AAC 320k, −14 LUFS).

## Layout (v3)

The talking head is left exactly as shot: no trims, zooms or reframes. Every image pops in at the top of the frame, and captions stay on throughout.

| File | On screen | Spoken line |
|---|---|---|
| `01_comment_1..4_*` | 1.6–4.9 s, stacked one by one | "a lot of you asked" |
| `02_hf_model` | 15.8–22.9 s | "a model that already exists" |
| `03_dataset` | 24.8–28.2 s | "a dataset" |
| `04_unsloth_gh` | 28.2–31.3 s | "Unsloth" |
| `06_rtx4090` | 31.3–34.7 s | "an RTX 4090" |
| `05_colab` | 34.7–37.0 s | "Google Colab" |
| `07_before_after` | 39.6–42.9 s | "you test it" (made by `card7.py`) |

## Build

```
cd reel
python3 card7.py      # before/after card
python3 audio.py      # voice cleanup, music bed, pops, ducking, -14 LUFS mix
python3 render.py     # final; add --preview for a fast low-quality pass
```

Edit decisions (image times, pops, caption snapping) live in `timeline.py`.
