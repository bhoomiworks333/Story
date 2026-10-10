// Renders every pop-up asset and caption in assets.html to a transparent PNG in build/.
// Usage: node snap_assets.js
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const dir = __dirname;
const out = path.join(dir, 'build');
fs.mkdirSync(out, { recursive: true });
const tl = JSON.parse(fs.readFileSync(path.join(dir, 'timeline.json'), 'utf8'));

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const pg = await b.newPage({ viewport: { width: 1400, height: 1920 }, deviceScaleFactor: 1 });
  await pg.goto('file://' + path.join(dir, 'assets.html'));
  // Captions: white Inter ExtraBold with a black outline, built from the same two-layer .ol trick.
  await pg.evaluate((caps) => {
    const host = document.getElementById('captions');
    caps.forEach(([, , text], i) => {
      const d = document.createElement('div');
      d.className = 'asset cap'; d.id = 'cap' + i;
      d.innerHTML = '<span class="ol" style="font-size:56px;--sw:11px;font-weight:800;word-spacing:9px;letter-spacing:0.5px;max-width:960px">' +
        '<span class="s"></span><span class="f"></span></span>';
      d.querySelector('.s').textContent = text;
      d.querySelector('.f').textContent = text;
      host.appendChild(d);
    });
  }, tl.captions);
  await pg.evaluate('document.fonts.ready');
  await pg.waitForTimeout(300);
  const ids = ['cash', 'gpay', 'chat', 'notes', 'q500', 'tag', ...tl.captions.map((_, i) => 'cap' + i)];
  for (const id of ids) {
    await pg.locator('#' + id).screenshot({ path: path.join(out, id + '.png'), omitBackground: true });
  }
  await b.close();
  console.log('rendered', ids.length, 'assets');
})();
