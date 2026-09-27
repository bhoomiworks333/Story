// Procedural, tileable canvas textures. Every texture is generated from a fixed seed so renders are repeatable.
import * as THREE from 'three';
import { rng, fbm, clamp } from './util.js';

function canvas(n) { const c = document.createElement('canvas'); c.width = c.height = n; return c; }
function toTex(c, srgb = true, repeat = true) {
  const t = new THREE.CanvasTexture(c);
  if (srgb) t.colorSpace = THREE.SRGBColorSpace;
  if (repeat) t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.anisotropy = 8;
  t.needsUpdate = true;
  return t;
}
// per-pixel pass over a canvas: f(x, y, [r,g,b]) -> [r,g,b]
function pixels(c, f) {
  const ctx = c.getContext('2d'), n = c.width;
  const im = ctx.getImageData(0, 0, n, n), d = im.data;
  const px = [0, 0, 0];
  for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) {
    const i = (y * n + x) * 4;
    px[0] = d[i]; px[1] = d[i + 1]; px[2] = d[i + 2];
    const o = f(x, y, px);
    d[i] = clamp(o[0], 0, 255); d[i + 1] = clamp(o[1], 0, 255); d[i + 2] = clamp(o[2], 0, 255); d[i + 3] = 255;
  }
  ctx.putImageData(im, 0, 0);
}
const hsl = (h, s, l) => `hsl(${h},${s}%,${l}%)`;

// Harappan fired brick in English bond. Bricks keep the 1:2:4 ratio (7 × 14 × 28 cm). One tile = 2.24 m square.
export function brick(seed = 3, opts = {}) {
  const N = 1024, M = N / 2.24; // px per metre
  const col = canvas(N), bmp = canvas(N);
  const c = col.getContext('2d'), b = bmp.getContext('2d');
  const R = rng(seed);
  const mortar = opts.mortar || '#8b6a4d';
  c.fillStyle = mortar; c.fillRect(0, 0, N, N);
  b.fillStyle = '#000'; b.fillRect(0, 0, N, N);
  const course = 0.08 * M, bh = 0.07 * M, gap = 0.01 * M;
  const base = opts.hue ?? 17;
  let row = 0;
  for (let y = 0; y < N - 1; y += course, row++) {
    const header = row % 2 === 1;
    const w = (header ? 0.14 : 0.28) * M;
    const off = header ? -0.07 * M : 0;
    for (let x = off; x < N; x += w) {
      const h = base + (R() - 0.5) * 12;
      const s = 34 + R() * 22;
      let l = 36 + R() * 18;
      if (R() < 0.08) l -= 10; // over-fired dark bricks
      if (R() < 0.12) l += 9;  // weathered pale bricks
      const ch = () => (R() - 0.5) * gap * 0.9;
      const bx = x + gap / 2 + ch(), by = y + gap / 2 + ch();
      const bw = w - gap + ch(), bb = bh + ch();
      for (const dx of [0, -N, N]) {
        c.fillStyle = hsl(h, s, l); c.fillRect(bx + dx, by, bw, bb);
        // bevel for bump: dark mortar, mid edge, bright centre
        b.fillStyle = '#6a6a6a'; b.fillRect(bx + dx, by, bw, bb);
        b.fillStyle = '#b8b8b8'; b.fillRect(bx + dx + 2, by + 2, bw - 4, bb - 4);
        const g = 200 + R() * 40 | 0;
        b.fillStyle = `rgb(${g},${g},${g})`;
        b.fillRect(bx + dx + 4, by + 3, bw - 8, bb - 6);
      }
    }
  }
  const dust = opts.dust ?? 0.35;
  pixels(col, (x, y, p) => {
    const u = x / N, v = y / N;
    const g = fbm(u * 64, v * 64, 3, seed, 64) - 0.5;           // grain
    const blot = fbm(u * 6, v * 6, 4, seed + 9, 6);              // dirt / lime bloom
    const streak = fbm(u * 40, v * 3, 3, seed + 21, 40);         // vertical rain streaks
    const k = 1 + g * 0.35 - (streak - 0.5) * 0.18;
    let r = p[0] * k, gg = p[1] * k, bb = p[2] * k;
    const d = clamp((blot - 0.45) * 2.2) * dust;                 // buff dust settles into the wall
    r = r * (1 - d) + 196 * d; gg = gg * (1 - d) + 170 * d; bb = bb * (1 - d) + 138 * d;
    return [r, gg, bb];
  });
  b.filter = 'blur(1.2px)'; b.drawImage(bmp, 0, 0); b.filter = 'none';
  pixels(bmp, (x, y, p) => { const g = (fbm(x / N * 96, y / N * 96, 2, seed + 5, 96) - 0.5) * 60; return [p[0] + g, p[0] + g, p[0] + g]; });
  return { map: toTex(col), bump: toTex(bmp, false), tile: 2.24 };
}

// Mud plaster for roofs and courtyard floors. One tile = 4 m.
export function mud(seed = 7, base = [176, 142, 104]) {
  const N = 1024, col = canvas(N), bmp = canvas(N);
  pixels(col, (x, y) => {
    const u = x / N, v = y / N;
    const n1 = fbm(u * 8, v * 8, 5, seed, 8), n2 = fbm(u * 90, v * 90, 2, seed + 3, 90);
    const crack = Math.abs(fbm(u * 14, v * 14, 4, seed + 8, 14) - 0.5) < 0.012 ? 0.78 : 1;
    const k = (0.82 + n1 * 0.32 + (n2 - 0.5) * 0.12) * crack;
    return [base[0] * k, base[1] * k, base[2] * k];
  });
  pixels(bmp, (x, y) => {
    const u = x / N, v = y / N;
    const h = fbm(u * 30, v * 30, 4, seed + 1, 30) * 200 + (Math.abs(fbm(u * 14, v * 14, 4, seed + 8, 14) - 0.5) < 0.012 ? -80 : 0);
    return [h, h, h];
  });
  return { map: toTex(col), bump: toTex(bmp, false), tile: 4 };
}

// Packed earth for streets and open ground. One tile = 6 m.
export function earth(seed = 11, base = [168, 132, 96]) {
  const N = 1024, col = canvas(N), bmp = canvas(N);
  const R = rng(seed);
  pixels(col, (x, y) => {
    const u = x / N, v = y / N;
    const n1 = fbm(u * 5, v * 5, 5, seed, 5), n2 = fbm(u * 120, v * 120, 2, seed + 4, 120);
    const k = 0.78 + n1 * 0.4 + (n2 - 0.5) * 0.18;
    return [base[0] * k, base[1] * k, base[2] * k];
  });
  const c = col.getContext('2d'), b = bmp.getContext('2d');
  pixels(bmp, (x, y) => { const h = fbm(x / N * 60, y / N * 60, 3, seed + 2, 60) * 150; return [h, h, h]; });
  for (let i = 0; i < 900; i++) { // pebbles and potsherds
    const x = R() * N, y = R() * N, r = 0.6 + R() * 2.2, l = 34 + R() * 16;
    c.fillStyle = R() < 0.3 ? hsl(15, 40, l) : hsl(30, 14, l + 6);
    c.beginPath(); c.ellipse(x, y, r, r * (0.6 + R() * 0.4), R() * 3, 0, 7); c.fill();
    b.fillStyle = '#bbb'; b.beginPath(); b.arc(x, y, r, 0, 7); b.fill();
  }
  return { map: toTex(col), bump: toTex(bmp, false), tile: 6 };
}

// Dressed sandstone masonry (Dholavira). Irregular courses. One tile = 3 m.
export function stone(seed = 19) {
  const N = 1024, M = N / 3, col = canvas(N), bmp = canvas(N);
  const c = col.getContext('2d'), b = bmp.getContext('2d'), R = rng(seed);
  c.fillStyle = '#6f6556'; c.fillRect(0, 0, N, N); b.fillStyle = '#000'; b.fillRect(0, 0, N, N);
  const rows = [];
  let y = 0; while (y < N) { let h = (0.18 + R() * 0.22) * M; if (N - y - h < 0.15 * M) h = N - y; rows.push([y, h]); y += h; }
  for (const [ry, rh] of rows) {
    let x = -R() * 0.5 * M;
    while (x < N) {
      const w = (0.35 + R() * 0.7) * M, g = 3 + R() * 3;
      const l = 52 + R() * 16, h = 32 + R() * 14, s = 14 + R() * 16;
      for (const dx of [0, -N, N]) {
        c.fillStyle = hsl(h, s, l); c.fillRect(x + dx + g, ry + g, w - 2 * g, rh - 2 * g);
        b.fillStyle = '#777'; b.fillRect(x + dx + g, ry + g, w - 2 * g, rh - 2 * g);
        b.fillStyle = '#ccc'; b.fillRect(x + dx + g + 6, ry + g + 6, w - 2 * g - 12, rh - 2 * g - 12);
      }
      x += w;
    }
  }
  pixels(col, (x, y, p) => {
    const u = x / N, v = y / N, g = fbm(u * 80, v * 80, 3, seed, 80) - 0.5, bl = fbm(u * 5, v * 5, 4, seed + 3, 5);
    const k = 1 + g * 0.3 + (bl - 0.5) * 0.25;
    return [p[0] * k, p[1] * k, p[2] * k];
  });
  b.filter = 'blur(2px)'; b.drawImage(bmp, 0, 0); b.filter = 'none';
  pixels(bmp, (x, y, p) => { const g = (fbm(x / N * 50, y / N * 50, 3, seed + 7, 50) - 0.5) * 90; return [p[0] + g, p[0] + g, p[0] + g]; });
  return { map: toTex(col), bump: toTex(bmp, false), tile: 3 };
}

// Large-scale variation, sampled at ~70 m so repeating tiles never read as a pattern.
export function macroNoise(seed = 29) {
  const N = 512, c = canvas(N);
  pixels(c, (x, y) => { const v = fbm(x / N * 6, y / N * 6, 5, seed, 6) * 255; return [v, fbm(x / N * 12, y / N * 12, 4, seed + 1, 12) * 255, v]; });
  return toTex(c, false);
}

// Tileable normal map for flowing water.
export function waterNormal(seed = 31) {
  const N = 512, c = canvas(N), H = new Float32Array(N * N);
  for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) H[y * N + x] = fbm(x / N * 8, y / N * 16, 5, seed, 8) ;
  const ctx = c.getContext('2d'), im = ctx.createImageData(N, N);
  for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
    const hx = H[y * N + (x + 1) % N] - H[y * N + (x - 1 + N) % N];
    const hy = H[((y + 1) % N) * N + x] - H[((y - 1 + N) % N) * N + x];
    const s = 18, nx = -hx * s, ny = -hy * s, nz = 1, l = Math.hypot(nx, ny, nz);
    const i = (y * N + x) * 4;
    im.data[i] = (nx / l * 0.5 + 0.5) * 255; im.data[i + 1] = (ny / l * 0.5 + 0.5) * 255; im.data[i + 2] = (nz / l * 0.5 + 0.5) * 255; im.data[i + 3] = 255;
  }
  ctx.putImageData(im, 0, 0);
  return toTex(c, false);
}

// Generic helper for the modern scene: draw with a callback, then add grain.
export function painted(N, draw, { grain = 0.08, seed = 41, srgb = true } = {}) {
  const c = canvas(N); draw(c.getContext('2d'), N, rng(seed));
  if (grain) pixels(c, (x, y, p) => { const g = 1 + (fbm(x / N * 128, y / N * 128, 2, seed, 128) - 0.5) * grain * 2; return [p[0] * g, p[1] * g, p[2] * g]; });
  return toTex(c, srgb);
}
