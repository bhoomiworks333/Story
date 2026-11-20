# python3 snap.py OUTDIR t1 t2 ...  -> screenshots (needs `python3 -m http.server 8765` running here)
import sys, asyncio, os
from playwright.async_api import async_playwright
ARGS = ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']
async def main():
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(args=ARGS, executable_path='/opt/pw-browsers/chromium')
        pg = await b.new_page(viewport={'width': 1080, 'height': 1920})
        pg.on('console', lambda m: print('console:', m.text))
        pg.on('pageerror', lambda e: print('ERR', e))
        await pg.goto('http://localhost:8765/index.html')
        await pg.wait_for_function('window.ready === true', timeout=60000)
        await pg.evaluate('document.fonts.ready')
        for t in sys.argv[2:]:
            await pg.evaluate(f'renderAt({t})')
            await pg.screenshot(path=f'{out}/s_{t}.jpg', type='jpeg', quality=88)
        await b.close()
asyncio.run(main())
