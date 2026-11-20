# python3 render.py OUTDIR [workers] [a-b]   (needs `python3 -m http.server 8765` running in this folder)
import sys, asyncio, os, json, time
from playwright.async_api import async_playwright
FPS = 30
OUT = sys.argv[1]; WORKERS = int(sys.argv[2]) if len(sys.argv) > 2 else 4
ONLY = sys.argv[3] if len(sys.argv) > 3 else None
ARGS = ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']
os.makedirs(OUT, exist_ok=True)
TOTAL = json.load(open('vo/lines.json'))['total']
async def worker(p, frames, wid):
    b = await p.chromium.launch(args=ARGS, executable_path='/opt/pw-browsers/chromium')
    pg = await b.new_page(viewport={'width': 1080, 'height': 1920})
    await pg.goto('http://localhost:8765/index.html')
    await pg.wait_for_function('window.ready === true', timeout=60000)
    await pg.evaluate('document.fonts.ready')
    t0 = time.time()
    for i, f in enumerate(frames):
        await pg.evaluate(f'renderAt({f / FPS})')
        await pg.screenshot(path=f'{OUT}/f{f:05d}.jpg', type='jpeg', quality=93)
        if i % 100 == 0: print(wid, f, f'{(time.time()-t0)/(i+1):.2f}s/f', flush=True)
    await b.close()
async def main():
    n = int(TOTAL * FPS); allf = list(range(n))
    if ONLY:
        a, c = map(float, ONLY.split('-')); allf = [f for f in allf if a * FPS <= f < c * FPS]
    allf = [f for f in allf if not os.path.exists(f'{OUT}/f{f:05d}.jpg')]
    async with async_playwright() as p:
        await asyncio.gather(*[worker(p, allf[i::WORKERS], i) for i in range(WORKERS)])
asyncio.run(main())
