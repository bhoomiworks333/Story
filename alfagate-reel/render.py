# Renders every frame deterministically with headless Chromium (parallel workers, resumable), then encodes the MP4.
#   python3 render.py [workers] [a-b seconds]
import sys, asyncio, os, time, subprocess
from playwright.async_api import async_playwright
FPS = 24
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'frames')
WORKERS = int(sys.argv[1]) if len(sys.argv) > 1 else 4
ONLY = sys.argv[2] if len(sys.argv) > 2 else None
CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
ARGS = ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']
PORT = 8813
os.makedirs(OUT, exist_ok=True)

async def open_page(p):
    b = await p.chromium.launch(executable_path=CHROME, args=ARGS)
    pg = await b.new_page(viewport={'width': 1080, 'height': 1920})
    pg.on('pageerror', lambda e: print('pageerror:', e, flush=True))
    await pg.goto(f'http://localhost:{PORT}/index.html')
    await pg.wait_for_function('window.ready === true', timeout=600000)
    return b, pg

async def worker(p, frames, wid):
    b, pg = await open_page(p); t0 = time.time()
    for i, f in enumerate(frames):
        if i and i % 120 == 0: await b.close(); b, pg = await open_page(p)   # keep memory bounded
        await pg.evaluate(f'renderAt({f / FPS})')
        await pg.screenshot(path=f'{OUT}/f{f:05d}.jpg', type='jpeg', quality=95)
        if i % 25 == 0: print(f'w{wid} frame {f} ({i + 1}/{len(frames)}) {(time.time() - t0) / (i + 1):.2f}s/frame', flush=True)
    await b.close()

async def main():
    srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT)], cwd=HERE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.8)
    try:
        dur = float(open(os.path.join(HERE, 'js/shots.js')).read().split('export const DUR = ')[1].split(';')[0])
        allf = list(range(int(round(dur * FPS))))
        if ONLY:
            a, z = map(float, ONLY.split('-')); allf = [f for f in allf if a * FPS <= f < z * FPS]
        allf = [f for f in allf if not os.path.exists(f'{OUT}/f{f:05d}.jpg')]
        print(len(allf), 'frames to render', flush=True)
        async with async_playwright() as p:
            await asyncio.gather(*[worker(p, allf[i::WORKERS], i) for i in range(WORKERS)])
    finally:
        srv.kill()

asyncio.run(main())
