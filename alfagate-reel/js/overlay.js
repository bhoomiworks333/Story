// 2D layer over the 3D frame: documentary supers, captions, the grid → app-tiles morph, the end card, grain, fades.
import { SHOTS, VO_AT } from './shots.js';
import { clamp, range, smooth, smoother, easeOut, easeInOut, lerp, window01, rng } from './util.js';
import { PURPLE, PURPLE_D, drawIcon } from './screens.js';

const W = 1080, H = 1920;
const SUPERS = [
  // [a, b, title, subtitle, style]
  [0.9, 7.2, '4,500 YEARS AGO', 'Indus Valley · c. 2500 BCE · illustrative reconstruction', 'top'],
  [7.9, 9.8, 'MOHENJO-DARO', 'Covered street drains', 'loc'],
  [10.1, 11.75, 'HARAPPA', 'Planned streets', 'loc'],
  [12.0, 14.15, 'DHOLAVIRA', 'Reservoirs & water channels', 'loc'],
  [15.25, 16.55, '2026', '', 'year'],
  [16.85, 18.55, 'PAPER REGISTERS', '', 'tag'],
  [18.85, 20.55, 'ENDLESS GROUP CHATS', '', 'tag'],
  [20.85, 22.75, 'MANUAL ACCOUNTS', '', 'tag'],
  [28.9, 29.55, "MAYBE IT'S TIME TO UPGRADE.", '', 'center'],
];

export async function createOverlay(cv, world) {
  const c = cv.getContext('2d');
  const vo = await (await fetch('vo/vo.json')).json();
  const caps = vo.lines.map((l, i) => ({ a: VO_AT[i], b: VO_AT[i] + l.dur, text: l.text }));
  // film grain plates
  const grain = [];
  for (let k = 0; k < 6; k++) {
    const g = document.createElement('canvas'); g.width = 540; g.height = 960; const gc = g.getContext('2d'), im = gc.createImageData(540, 960), R = rng(900 + k);
    for (let i = 0; i < im.data.length; i += 4) { const v = 128 + (R() + R() + R() - 1.5) * 90; im.data[i] = im.data[i + 1] = im.data[i + 2] = v; im.data[i + 3] = 255; }
    gc.putImageData(im, 0, 0); grain.push(g);
  }
  // freeze-frame of the city from directly above, the source image for the morph
  const gridA = SHOTS.find((s) => s.id === 'gridA');
  world.render({ id: 'gridA', ...gridA.cam(gridA.b - 0.001, 1) });
  const city = document.createElement('canvas'); city.width = W; city.height = H; city.getContext('2d').drawImage(world.glCanvas, 0, 0);
  const icon = world.icon;

  // top-down projection used by the grid shots (camera height h, vertical fov 40°)
  const pxPerM = (h) => 960 / (h * Math.tan((20 * Math.PI) / 180));
  const gridH = (u) => lerp(250, 300, smoother(u));

  function superText(t, [a, b, title, sub, style]) {
    const k = window01(t, a, b, 0.35, 0.3); if (k <= 0) return;
    c.save(); c.globalAlpha = k; c.shadowColor = 'rgba(0,0,0,0.55)'; c.shadowBlur = 18;
    const rise = (1 - easeOut(range(t, a, a + 0.6))) * 14;
    if (style === 'top') {
      c.fillStyle = 'rgba(255,255,255,0.9)'; c.fillRect(90, 262 + rise, 70 * easeOut(range(t, a, a + 0.8)), 3);
      spaced(title, 90, 330 + rise, '600 54px Inter', '#fff', 10);
      spaced(sub.toUpperCase(), 92, 384 + rise, '500 27px Inter', 'rgba(255,255,255,0.88)', 2);
    } else if (style === 'loc') {
      spaced(title, 90, 330 + rise, '700 46px Inter', '#fff', 8);
      c.fillStyle = 'rgba(255,255,255,0.9)'; c.fillRect(90, 350 + rise, 46, 3);
      spaced(sub.toUpperCase(), 92, 400 + rise, '500 30px Inter', 'rgba(255,255,255,0.92)', 2);
    } else if (style === 'year') {
      c.shadowBlur = 30; spaced(title, W / 2, 1000, '700 170px Inter', '#fff', 26, 'center');
    } else if (style === 'tag') {
      spaced(title, 90, 330 + rise, '700 44px Inter', '#fff', 7);
      c.fillStyle = '#ff5a4f'; c.fillRect(90, 350 + rise, 46, 3);
    } else if (style === 'center') {
      spaced(title, W / 2, 980, '700 50px Inter', '#fff', 5, 'center');
    }
    c.restore();
  }
  function spaced(s, x, y, font, color, sp, align = 'left') {
    c.font = font; c.fillStyle = color; c.textBaseline = 'alphabetic';
    if ('letterSpacing' in c) { c.letterSpacing = `${sp}px`; c.textAlign = align; c.fillText(s, x + (align === 'center' ? sp / 2 : 0), y); c.letterSpacing = '0px'; }
    else { c.textAlign = align; c.fillText(s, x, y); }
  }
  function captions(t, low) {
    const cap = caps.find((k) => t >= k.a - 0.05 && t < k.b + 0.25); if (!cap) return;
    const k = Math.min(range(t, cap.a - 0.05, cap.a + 0.1), 1 - range(t, cap.b + 0.1, cap.b + 0.25));
    c.save(); c.globalAlpha = k; c.font = '600 44px Inter'; c.textAlign = 'center'; c.textBaseline = 'alphabetic';
    const words = cap.text.split(' '), lines = []; let line = '';
    for (const w of words) { const tst = line ? line + ' ' + w : w; if (c.measureText(tst).width > 880 && line) { lines.push(line); line = w; } else line = tst; }
    lines.push(line);
    const y0 = (low === 'app' ? 1600 : low ? 1660 : 1470) - (lines.length - 1) * 58;
    lines.forEach((l, i) => {
      const w = c.measureText(l).width;
      c.fillStyle = 'rgba(0,0,0,0.42)'; c.beginPath(); c.roundRect(W / 2 - w / 2 - 20, y0 + i * 58 - 44, w + 40, 58, 12); c.fill();
      c.fillStyle = '#fff'; c.fillText(l, W / 2, y0 + i * 58);
    });
    c.restore();
  }
  // golden lines tracing the city's streets from above
  function streetLines(t, u, h, alpha) {
    const s = pxPerM(h), prog = easeInOut(range(t, 29.8, 31.2));
    c.save(); c.globalAlpha = alpha; c.strokeStyle = '#ffd98a'; c.lineCap = 'round'; c.shadowColor = 'rgba(255,200,110,0.9)'; c.shadowBlur = 22;
    const ln = (x0, y0, x1, y1, w) => { c.lineWidth = w; c.beginPath(); c.moveTo(x0, y0); c.lineTo(lerp(x0, x1, prog), lerp(y0, y1, prog)); c.stroke(); };
    ln(W / 2, H / 2, W / 2, -20, 5); ln(W / 2, H / 2, W / 2, H + 20, 5);
    ln(W / 2, H / 2, -20, H / 2, 5); ln(W / 2, H / 2, W + 20, H / 2, 5);
    for (const z of [-95, 95]) { const y = H / 2 + z * s; ln(W / 2, y, -20, y, 3); ln(W / 2, y, W + 20, y, 3); }
    c.restore();
  }
  function morph(t) {
    const u = range(t, 31.8, 33.6), e = easeInOut(range(t, 31.9, 33.2));
    const s = pxPerM(gridH(1)), gx = 4.5 * s, gz = 4 * s, z2 = 95 * s;
    // background: city dissolving into deep purple
    c.drawImage(city, 0, 0);
    c.fillStyle = `rgba(22,12,52,${0.55 + 0.45 * e})`; c.fillRect(0, 0, W, H);
    streetLines(33, 1, gridH(1), 1 - e);
    const src = [[0, H / 2 - z2 + 24, W / 2 - gx, z2 - gz - 24], [W / 2 + gx, H / 2 - z2 + 24, W / 2 - gx, z2 - gz - 24],
      [0, H / 2 + gz, W / 2 - gx, z2 - gz - 24], [W / 2 + gx, H / 2 + gz, W / 2 - gx, z2 - gz - 24]];
    const T = 380, gap = 36, dst = [[W / 2 - gap / 2 - T, H / 2 - gap / 2 - T], [W / 2 + gap / 2, H / 2 - gap / 2 - T], [W / 2 - gap / 2 - T, H / 2 + gap / 2], [W / 2 + gap / 2, H / 2 + gap / 2]];
    // the four modules from the real app: Visitors, Maintenance, Complaints, Notices
    const labels = ['Visitors', 'Maintenance', 'Complaints', 'Notices'], iconOrder = [0, 1, 2, 3];
    const tint = [['rgba(143,92,255,0.14)', '#8f5cff'], ['rgba(143,92,255,0.14)', '#8f5cff'], ['rgba(245,158,11,0.16)', '#f59e0b'], ['rgba(143,92,255,0.14)', '#8f5cff']];
    src.forEach(([sx, sy, sw, sh], i) => {
      const [dx, dy] = dst[i];
      const x = lerp(sx, dx, e), y = lerp(sy, dy, e), w = lerp(sw, T, e), h = lerp(sh, T, e), r = lerp(0, 56, e);
      c.save(); c.beginPath(); c.roundRect(x, y, w, h, r); c.clip();
      c.drawImage(city, sx, sy, sw, sh, x, y, w, h);
      const f = smooth(range(t, 32.5, 33.3));
      c.fillStyle = `rgba(255,255,255,${f})`; c.fillRect(x, y, w, h);
      c.restore();
      if (f0(t) > 0) {
        c.save(); c.globalAlpha = f0(t);
        c.fillStyle = tint[i][0]; c.beginPath(); c.roundRect(x + w / 2 - 70, y + h / 2 - 110, 140, 140, 40); c.fill();
        drawIcon(c, iconOrder[i], x + w / 2, y + h / 2 - 40, tint[i][1], 2.6);
        c.font = '700 40px Manrope'; c.fillStyle = '#1f1b2e'; c.textAlign = 'center'; c.fillText(labels[i], x + w / 2, y + h / 2 + 90);
        c.restore();
      }
    });
    // everything converges: a thin ring connecting the four systems
    const ring = smooth(range(t, 33.0, 33.6));
    if (ring > 0) { c.save(); c.globalAlpha = ring; c.strokeStyle = 'rgba(255,255,255,0.8)'; c.lineWidth = 3; c.beginPath(); c.arc(W / 2, H / 2, 34, 0, Math.PI * 2 * ring); c.stroke();
      c.fillStyle = PURPLE; c.beginPath(); c.arc(W / 2, H / 2, 26, 0, 7); c.fill(); c.restore(); }
    // push in and fade to the phone shot
    const out = range(t, 33.55, 33.9); if (out > 0) { c.fillStyle = `rgba(245,243,251,${out})`; c.fillRect(0, 0, W, H); }
  }
  const f0 = (t) => smooth(range(t, 32.7, 33.3));

  function brand(t) {
    const g = c.createRadialGradient(W / 2, 820, 60, W / 2, 900, 1200); g.addColorStop(0, '#8a62f0'); g.addColorStop(0.55, PURPLE_D); g.addColorStop(1, '#241050');
    c.fillStyle = g; c.fillRect(0, 0, W, H);
    // faint street grid remains in the background: the idea carried to the end
    c.save(); c.globalAlpha = 0.07; c.strokeStyle = '#fff'; c.lineWidth = 2;
    for (let x = 60; x < W; x += 120) { c.beginPath(); c.moveTo(x, 0); c.lineTo(x, H); c.stroke(); }
    for (let y = 40; y < H; y += 120) { c.beginPath(); c.moveTo(0, y); c.lineTo(W, y); c.stroke(); }
    c.restore();
    const a = range(t, 37.7, 38.5), sc = 0.82 + 0.18 * easeOut(a) + Math.sin(clamp(a) * Math.PI) * 0.03;
    const S = 300 * sc;
    c.save(); c.globalAlpha = smooth(range(t, 37.6, 38.0)); c.shadowColor = 'rgba(20,0,60,0.5)'; c.shadowBlur = 60; c.shadowOffsetY = 20;
    c.beginPath(); c.roundRect(W / 2 - S / 2, 760 - S / 2, S, S, S * 0.22); c.clip(); c.drawImage(icon, 6, 6, 500, 500, W / 2 - S / 2, 760 - S / 2, S, S); c.restore();
    const w1 = easeOut(range(t, 38.2, 38.9));
    c.save(); c.globalAlpha = w1; c.textAlign = 'center'; c.font = '800 118px Manrope'; c.fillStyle = '#fff'; c.fillText('AlfaGate', W / 2, 1060 + (1 - w1) * 24); c.restore();
    const w2 = easeOut(range(t, 38.7, 39.4));
    c.save(); c.globalAlpha = w2 * 0.95; c.textAlign = 'center'; c.font = '500 50px Inter'; c.fillStyle = '#fff';
    c.fillText('Run your society', W / 2, 1150 + (1 - w2) * 16); c.fillText('like it’s audited.', W / 2, 1214 + (1 - w2) * 16); c.restore();
    const w3 = easeOut(range(t, 40.2, 40.9));
    if (w3 > 0) {
      c.save(); c.globalAlpha = w3; c.textAlign = 'center';
      c.font = '600 38px Inter'; const txt = 'Comment “ALFAGATE” for a demo'; const tw = c.measureText(txt).width;
      c.fillStyle = 'rgba(255,255,255,0.14)'; c.strokeStyle = 'rgba(255,255,255,0.6)'; c.lineWidth = 2;
      c.beginPath(); c.roundRect(W / 2 - tw / 2 - 40, 1310, tw + 80, 84, 42); c.fill(); c.stroke();
      c.fillStyle = '#fff'; c.fillText(txt, W / 2, 1364);
      c.font = '500 34px Inter'; c.fillStyle = 'rgba(255,255,255,0.8)'; c.fillText('alfagate.in', W / 2, 1466);
      c.restore();
    }
  }

  function draw(t, s, u) {
    c.clearRect(0, 0, W, H);
    if (s.id === 'gridMorph') morph(t);
    if (s.id === 'brand') brand(t);
    if (s.id === 'gridA') { c.fillStyle = `rgba(20,10,5,${0.25 * smooth(range(t, 29.8, 31.0))})`; c.fillRect(0, 0, W, H); streetLines(t, u, gridH(u), 1); }
    if (s.id === 'app') { const k = range(t, 37.25, 37.6); if (k > 0) { c.fillStyle = `rgba(90,51,196,${smooth(k)})`; c.fillRect(0, 0, W, H); } }
    for (const sp of SUPERS) superText(t, sp);
    captions(t, s.id === 'brand' ? true : s.id === 'app' ? 'app' : false);
    // grain
    const ancient = t < 15.2 || s.id === 'gridA';
    c.save(); c.globalCompositeOperation = 'overlay'; c.globalAlpha = ancient ? 0.11 : 0.07;
    c.drawImage(grain[Math.floor(t * 24) % grain.length], 0, 0, W, H); c.restore();
    // fades: open from black, dip before the grid, hard black flash on the cut to 2026
    let black = 1 - smooth(range(t, 0, 0.7));
    black = Math.max(black, smooth(range(t, 29.25, 29.6)) * (t < 29.6 ? 1 : 0), t >= 29.6 && t < 30.0 ? 1 - smooth(range(t, 29.6, 30.0)) : 0);
    black = Math.max(black, t >= 15.2 && t < 15.28 ? 1 : 0);
    if (black > 0) { c.fillStyle = `rgba(0,0,0,${black})`; c.fillRect(0, 0, W, H); }
  }
  return { draw };
}
