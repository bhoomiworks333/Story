# Fine-tuning reel edit

Source: the ~1-minute cut (720×1280, 59 s). Output: `output/finetune_reel_final.mp4` (1080×1920, 30 fps, H.264 + AAC 320k, −14 LUFS).

## Drop in the screenshots

Put the image files in `reel/assets/` with these names (any of .png/.jpg/.webp), then run the build again. If a file is missing, a red PLACEHOLDER card is shown in its place.

| File | Shown from | Spoken line |
|---|---|---|
| `02_hf_model.*` | 15.8 s | "a model that already exists… Hugging Face" (card) |
| `03_dataset_full.*` | 23.9 s | "You need a dataset" (full screen, hides speaker + captions) |
| `04_unsloth_gh.*` | 27.4 s | "a tool like Unsloth" (card) |
| `06_rtx4090.*` | 31.3 s | "an RTX 4090" |
| `05_colab_full.*` | 34.7 s | "Google Colab GPUs" (full screen) |
| `07_before_after.png` | 38.3 s | "and after training you test it" (card, made by `card7.py`) |

Each card is fitted into a 950×372 area at the top of the frame. Wide crops (about 2.5:1) use that space best.

## Build

```
cd reel
python3 card7.py      # before/after card
python3 audio.py      # voice cleanup, music bed, pops, ducking, -14 LUFS mix
python3 render.py     # final; add --preview for a fast low-quality pass
```

Edit decisions live in `timeline.py`: the dead-air trim, card times, punch-ins, pops and caption snapping.
