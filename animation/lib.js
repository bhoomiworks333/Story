// Core helpers: SVG creation, easing, paper-cut texture, limbs.
const NS = 'http://www.w3.org/2000/svg';
const W = 1080, H = 1920;

function el(tag, attrs = {}, parent) {
  const e = document.createElementNS(NS, tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]);
  if (parent) parent.appendChild(e);
  return e;
}
const G = (parent, attrs = {}) => el('g', attrs, parent);

const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const seg = (t, a, b) => clamp((t - a) / (b - a));
const lerp = (a, b, p) => a + (b - a) * p;
const E = {
  inOut: p => p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2,
  out: p => 1 - Math.pow(1 - p, 3),
  in: p => p * p * p,
  back: p => { const c = 1.9; return 1 + (c + 1) * Math.pow(p - 1, 3) + c * Math.pow(p - 1, 2); },
  elastic: p => p === 0 || p === 1 ? p : Math.pow(2, -10 * p) * Math.sin((p * 10 - .75) * (2 * Math.PI / 3)) + 1,
};
// deterministic pseudo-random
function rnd(i) { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); }

// transform helper: pivot at element's local origin
function tf(e, o = {}) {
  const { x = 0, y = 0, s = 1, r = 0 } = o;
  const sx = o.sx ?? s, sy = o.sy ?? s;
  e.setAttribute('transform', `translate(${x.toFixed(2)} ${y.toFixed(2)}) rotate(${r.toFixed(2)}) scale(${sx.toFixed(4)} ${sy.toFixed(4)})`);
}
function show(e, v) { e.style.display = v ? '' : 'none'; }
function op(e, v) { e.setAttribute('opacity', clamp(v).toFixed(3)); show(e, v > 0.001); }

// ---------- paper textures ----------
let DEFS;
const patCache = {};
function P(color, k = 1) {
  const id = 'p' + color.replace('#', '') + (k === 1 ? '' : 'k' + String(k).replace('.', ''));
  if (!patCache[id]) {
    const p = el('pattern', { id, patternUnits: 'userSpaceOnUse', width: 512, height: 512 }, DEFS);
    el('rect', { width: 512, height: 512, fill: color }, p);
    el('image', { href: 'crayon.png', width: 512, height: 512, opacity: .55 * k }, p);
    el('image', { href: 'crayon_dark.png', width: 512, height: 512, opacity: .6 * k }, p);
    patCache[id] = true;
  }
  return `url(#${id})`;
}
const EDGE = '#FBF4E4';
// paper cut-out shape with white torn edge
function cut(tag, attrs, parent, color, edge = 7) {
  return el(tag, Object.assign({ fill: P(color), stroke: EDGE, 'stroke-width': edge, 'stroke-linejoin': 'round', 'paint-order': 'stroke' }, attrs), parent);
}
// flat (no edge) textured shape
function flat(tag, attrs, parent, color) {
  return el(tag, Object.assign({ fill: P(color) }, attrs), parent);
}

// limb: polyline with paper edge. returns updater(points)
function limb(parent, color, w, edge = 7) {
  const g = G(parent);
  const a = el('path', { fill: 'none', stroke: EDGE, 'stroke-width': w + edge, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, g);
  const b = el('path', { fill: 'none', stroke: P(color), 'stroke-width': w, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, g);
  const upd = pts => {
    let d = `M${pts[0][0].toFixed(1)} ${pts[0][1].toFixed(1)}`;
    if (pts.length === 3) d += ` Q${pts[1][0].toFixed(1)} ${pts[1][1].toFixed(1)} ${pts[2][0].toFixed(1)} ${pts[2][1].toFixed(1)}`;
    else for (let i = 1; i < pts.length; i++) d += ` L${pts[i][0].toFixed(1)} ${pts[i][1].toFixed(1)}`;
    a.setAttribute('d', d); b.setAttribute('d', d);
  };
  upd.g = g;
  return upd;
}
const lp = (a, b, p) => [lerp(a[0], b[0], p), lerp(a[1], b[1], p)];

// handwritten squiggle lines for backgrounds (like reference)
function scribbleText(parent, x0, y0, w, h, color, opacity = .14, seed = 1, size = 26) {
  const g = G(parent, { opacity, fill: color, 'font-family': 'Caveat', 'font-size': size });
  const syll = ['mm', 'nu', 'wa', 'rn', 'um', 'ow', 'ne', 'mi', 'am', 'lo', 've', 'ru', 'an', 'ce'];
  let i = seed * 100;
  for (let y = y0; y < y0 + h; y += size * 1.35) {
    let line = '';
    while (line.length < w / (size * .38)) {
      const n = 2 + Math.floor(rnd(i++) * 4);
      for (let k = 0; k < n; k++) line += syll[Math.floor(rnd(i++) * syll.length)];
      line += ' ';
    }
    el('text', { x: x0, y }, g).textContent = line;
  }
  return g;
}

// text with paper strip background
function paperText(parent, opts) {
  const g = G(parent);
  const { text, x = 540, y, size = 60, font = 'Caveat', color = '#2B2340', bg = '#FBF4E4', pad = 30, maxW = 960, rot = -1.5 } = opts;
  const lines = Array.isArray(text) ? text : [text];
  const lh = size * 1.12;
  const hh = lines.length * lh + pad * 1.2;
  const bgR = el('path', { fill: P(bg), stroke: EDGE, 'stroke-width': 4 }, g);
  // torn-ish rectangle
  const w2 = Math.min(maxW, opts.w || maxW) / 2, h2 = hh / 2;
  let d = `M${-w2} ${-h2}`;
  for (let k = 1; k <= 12; k++) d += ` L${-w2 + k * (2 * w2 / 12)} ${-h2 + (rnd(k + y) - .5) * 8}`;
  for (let k = 1; k <= 4; k++) d += ` L${w2 + (rnd(k * 3 + y) - .5) * 8} ${-h2 + k * (2 * h2 / 4)}`;
  for (let k = 1; k <= 12; k++) d += ` L${w2 - k * (2 * w2 / 12)} ${h2 + (rnd(k * 7 + y) - .5) * 8}`;
  d += 'Z';
  bgR.setAttribute('d', d);
  const t = el('text', { 'text-anchor': 'middle', 'font-family': font, 'font-size': size, fill: color, 'font-weight': 700 }, g);
  lines.forEach((ln, i) => {
    el('tspan', { x: 0, y: (i - (lines.length - 1) / 2) * lh + size * .34 }, t).textContent = ln;
  });
  g.base = { x, y, rot };
  tf(g, { x, y, r: rot });
  return g;
}
// pop-in / out animation for a text card
function cardAnim(g, t, a, b, wobble = true) {
  const pin = E.back(seg(t, a, a + .35)), pout = seg(t, b - .25, b);
  const v = t >= a && t <= b;
  show(g, v);
  if (!v) return;
  const s = lerp(.6, 1, pin) * lerp(1, .9, pout);
  g.setAttribute('opacity', (Math.min(seg(t, a, a + .15), 1 - pout)).toFixed(3));
  tf(g, { x: g.base.x, y: g.base.y + (wobble ? Math.sin(t * 2) * 3 : 0), r: g.base.rot + (wobble ? Math.sin(t * 1.3) * .6 : 0), s });
}
