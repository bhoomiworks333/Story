// Renders every pop-up in assets.html to a transparent PNG in hf/assets/.
// Usage: NODE_PATH=$(npm root -g) node snap_assets.js
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const pg = await b.newPage({ viewport: { width: 1400, height: 3000 }, deviceScaleFactor: 1 });
  await pg.goto('file://' + path.join(__dirname, 'assets.html'));
  await pg.evaluate('document.fonts.ready');
  await pg.waitForTimeout(300);
  for (const id of ['nb0', 'nb1', 'nb2', 'nb3', 'nb4', 'wa1', 'wa2', 'register', 'kaunsa', 'detect', 'aapki']) {
    await pg.locator('#' + id).screenshot({ path: path.join(__dirname, 'hf', 'assets', id + '.png'), omitBackground: true });
  }
  await b.close();
})();
