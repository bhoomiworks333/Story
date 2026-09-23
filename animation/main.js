// Master timeline. renderAt(t) is pure: every frame sets all state from t.
DEFS = document.getElementById('defs');
const ROOT = document.getElementById('root');
const TURB = document.getElementById('turb');
const DURATION = 57.0;

const SCENES = [
  { s: Shop, from: 0, to: 18.75 },
  { s: Shop, from: 48.3, to: 53.8, alias: true },
];
const L = {};
L.shop = G(ROOT); Shop.build(L.shop);
if (typeof Notebook !== 'undefined') { L.nb = G(ROOT); Notebook.build(L.nb); }
if (typeof Desk !== 'undefined') { L.desk = G(ROOT); Desk.build(L.desk); }
if (typeof Factory !== 'undefined') { L.fac = G(ROOT); Factory.build(L.fac); }
if (typeof Closeup !== 'undefined') { L.close = G(ROOT); Closeup.build(L.close); }
L.brand = G(ROOT); if (typeof Brand !== 'undefined') Brand.build(L.brand);
L.ui = G(ROOT);

// ---------- subtitles (first-person VO) ----------
const SUBS = [
  [2.3, 5.0, ['Growing up, I spent a lot of time', 'in my father’s shop.']],
  [5.3, 7.9, ['He was running the whole business…']],
  [8.3, 11.3, ['…and somehow, carrying all of it', 'in his head.']],
  [19.3, 21.3, ['That question never really left me.']],
  [21.6, 23.7, ['So I started learning.']],
  [24.0, 27.5, ['Technology. Systems.', 'How things could work differently.']],
  [28.6, 30.6, ['And slowly, an idea took shape.']],
  [30.9, 34.3, ['What if a business didn’t have to', 'depend on one person’s memory?']],
  [34.7, 37.2, ['What if everything could just…', 'talk to each other?']],
];
const subEls = SUBS.map(([a, b, text]) => {
  const g = paperText(L.ui, { text, y: 1600, size: 46, font: 'Nunito', color: '#FBF4E4', bg: '#2B2340', w: text.length > 1 ? 940 : 820, rot: 0, pad: 26 });
  g.win = [a, b];
  return g;
});
// hero text cards
const CARDS = [
  [14.4, 17.3, ['Why does Papa have to', 'remember everything?'], 1560, 76],
  [42.0, 46.3, ['One connected system.', 'Many moving parts.'], 1560, 72],
  [49.3, 51.7, ['Why does Papa have to', 'remember everything?'], 1560, 76],
  [51.9, 53.5, ['He shouldn’t have to.'], 1560, 80],
];
const cardEls = CARDS.map(([a, b, text, y, size]) => {
  const g = paperText(L.ui, { text, y, size, font: 'Caveat', color: '#2B2340', bg: '#FBF4E4', w: 900, rot: -2, pad: 40 });
  g.win = [a, b];
  return g;
});

function sceneOpacity(t, a, b, fin = 0, fout = 0) {
  if (t < a || t > b) return 0;
  return Math.min(fin ? seg(t, a, a + fin) : 1, fout ? 1 - seg(t, b - fout, b) : 1);
}

window.renderAt = function (t) {
  TURB.setAttribute('seed', 1 + Math.floor(t * 12) % 7);
  // shop: 0–18.75 and callback 48.3–53.8
  const shopA = sceneOpacity(t, 0, 18.75) || sceneOpacity(t, 48.3, 53.8, .6, 0);
  op(L.shop, shopA); if (shopA > 0) Shop.render(t);
  if (L.nb) { const a = sceneOpacity(t, 18.7, 28.9, 0, .6); op(L.nb, a); if (a > 0) Notebook.render(t); }
  if (L.desk) { const a = sceneOpacity(t, 28.2, 41.6, .6, .5); op(L.desk, a); if (a > 0) Desk.render(t); }
  if (L.fac) { const a = sceneOpacity(t, 41.0, 46.8, .3, .3); op(L.fac, a); if (a > 0) Factory.render(t); }
  if (L.close) { const a = sceneOpacity(t, 46.5, 48.95, .3, .6); op(L.close, a); if (a > 0) Closeup.render(t); }
  if (typeof Brand !== 'undefined') Brand.render(t);
  subEls.forEach(g => cardAnim(g, t, g.win[0], g.win[1], false));
  cardEls.forEach(g => cardAnim(g, t, g.win[0], g.win[1], true));
};
window.DURATION = DURATION;
renderAt(0);
