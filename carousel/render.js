// Renders each .slide in index.html to output/carousel/slide-NN.png at 1080x1350.
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
(async () => {
  const out = path.join(__dirname, '..', 'output', 'carousel');
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 1500 } });
  await page.goto('file://' + path.join(__dirname, 'index.html'));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(300);
  const slides = await page.$$('.slide');
  for (let i = 0; i < slides.length; i++) {
    const f = path.join(out, `slide-${String(i + 1).padStart(2, '0')}.png`);
    await slides[i].screenshot({ path: f });
    console.log(f);
  }
  await browser.close();
})();
