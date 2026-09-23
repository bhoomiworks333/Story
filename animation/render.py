# Renders frames deterministically with headless Chromium, in parallel workers.
import sys, asyncio, os, time
from playwright.async_api import async_playwright
FPS = 24
OUT = sys.argv[1]
WORKERS = int(sys.argv[2]) if len(sys.argv) > 2 else 4
ONLY = sys.argv[3] if len(sys.argv) > 3 else None   # "a-b" seconds range
os.makedirs(OUT, exist_ok=True)
async def worker(p, frames, wid):
    b = await p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
    pg = await b.new_page(viewport={'width': 1080, 'height': 1920})
    await pg.goto('file://' + os.path.abspath('index.html'))
    await pg.evaluate('document.fonts.ready'); await pg.wait_for_timeout(500)
    t0 = time.time()
    for i, f in enumerate(frames):
        await pg.evaluate(f'renderAt({f / FPS})')
        await pg.screenshot(path=f'{OUT}/f{f:05d}.jpg', type='jpeg', quality=94)
        if i % 100 == 0: print(wid, f, f'{(time.time()-t0)/(i+1):.3f}s/frame', flush=True)
    await b.close()
async def main():
    async with async_playwright() as p:
        dur = await (await (await p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome')).new_page()).evaluate('57.0')
        n = int(dur * FPS)
        allf = list(range(n))
        if ONLY:
            a, b = map(float, ONLY.split('-')); allf = [f for f in allf if a * FPS <= f < b * FPS]
        chunks = [allf[i::WORKERS] for i in range(WORKERS)]
        await asyncio.gather(*[worker(p, c, i) for i, c in enumerate(chunks)])
asyncio.run(main())
