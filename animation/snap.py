import sys, asyncio
from playwright.async_api import async_playwright
async def main(page_name, times, out):
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
        pg = await b.new_page(viewport={'width':1080,'height':1920})
        pg.on('console', lambda m: print('CONSOLE', m.text))
        pg.on('pageerror', lambda e: print('PAGEERR', e))
        await pg.goto(f'file:///home/user/Story/animation/{page_name}')
        await pg.evaluate('document.fonts.ready')
        await pg.wait_for_timeout(300)
        for t in times:
            await pg.evaluate(f'renderAt({t})')
            await pg.screenshot(path=f'{out}_{t:05.2f}.png')
        await b.close()
asyncio.run(main(sys.argv[1], [float(x) for x in sys.argv[3:]] or [0], sys.argv[2]))
