// Renders the 10800x1350 desk strip in index.html into ten 1080x1350 slides
// at output/carousel/slide-NN.png, plus the full strip as panorama.png.
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
(async () => {
  const out = path.join(__dirname, '..', 'output', 'carousel');
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 10800, height: 1350 } });
  await page.goto('file://' + path.join(__dirname, 'index.html'));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(500);
  const strip = await page.$('#strip');
  await strip.screenshot({ path: path.join(out, 'panorama.png') });
  for (let i = 0; i < 10; i++) {
    const f = path.join(out, `slide-${String(i + 1).padStart(2, '0')}.png`);
    await page.screenshot({ path: f, clip: { x: i * 1080, y: 0, width: 1080, height: 1350 } });
  }
  await browser.close();
})();
