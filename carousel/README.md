# Register → ERP carousel (10 slides, 1080×1350)

Source: `index.html`. Render: `node carousel/render.js` → `output/carousel/slide-01.png … slide-10.png`.

## Drop-in assets (put these files in `carousel/assets/`, then re-render)
| File | Slides | What |
|---|---|---|
| `register.jpg` | 1, 8 | Real messy handwritten register page |
| `check-screenshot.png` | 5 | Real AI output with one actual error circled in red |
| `erpnext-import.png` | 7 | ERPNext Data Import screen (demo data) |
| `erp-after.png` | 8 | The same data inside the ERP |

Until a file exists, its frame shows a labelled placeholder.

## Still to fill
- Slide 1: replace `[X]` with the real timed number.
- Slide 1: the table rows (`rows` in the script at the bottom of `index.html`) are demo data; replace them with what is actually on the register photo.
