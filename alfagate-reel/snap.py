# Screenshot single moments: python3 snap.py OUTDIR t1 t2 ...
import sys, asyncio, os, subprocess, time
from playwright.async_api import async_playwright
CHROME = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
ARGS = ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']
HERE = os.path.dirname(os.path.abspath(__file__))
async def main():
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    srv = subprocess.Popen(['python3', '-m', 'http.server', '8811'], cwd=HERE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.8)
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch(executable_path=CHROME, args=ARGS)
            pg = await b.new_page(viewport={'width': 1080, 'height': 1920})
            pg.on('console', lambda m: print('console:', m.text) if m.type in ('error', 'warning') else None)
            pg.on('pageerror', lambda e: print('pageerror:', e))
            t0 = time.time()
            await pg.goto('http://localhost:8811/index.html')
            await pg.wait_for_function('window.ready === true', timeout=300000)
            print('load', round(time.time() - t0, 1), 's')
            for t in sys.argv[2:]:
                t1 = time.time(); sid = await pg.evaluate(f'renderAt({float(t)})')
                await pg.screenshot(path=f'{out}/t{float(t):06.2f}.jpg', type='jpeg', quality=90)
                print(t, sid, round(time.time() - t1, 2), 's')
            await b.close()
    finally:
        srv.kill()
asyncio.run(main())
