// Brand layer (logo lives across scenes 5, 6 and the end card) + Scene 7 adult close-up.
function makeLogoIcon(parent) {
  const g = G(parent);
  const o = { g };
  const P2 = C.purple;
  const inner = G(g, { transform: 'translate(-130 -140)' });
  o.top = G(inner);
  el('path', { d: 'M20 60 L130 12 L240 60 L130 108 Z', fill: P2, stroke: P2, 'stroke-width': 10, 'stroke-linejoin': 'round' }, o.top);
  el('path', { d: 'M20 60 L20 85 L130 133 L240 85 L240 60', fill: 'none', stroke: P2, 'stroke-width': 10, 'stroke-linejoin': 'round' }, o.top);
  const band = dy => `M20 ${125 + dy} L130 ${173 + dy} L240 ${125 + dy} L240 ${150 + dy} L130 ${198 + dy} L20 ${150 + dy} Z`;
  o.bands = [band(0), band(65)].map(d => {
    const p = el('path', { d, fill: 'none', stroke: P2, 'stroke-width': 10, 'stroke-linejoin': 'round' }, inner);
    p.L = p.getTotalLength(); p.setAttribute('stroke-dasharray', p.L); return p;
  });
  o.nodes = [[252, 106, 240, 124], [8, 166, 20, 150], [252, 172, 240, 190], [8, 232, 20, 215]].map(([x, y, x2, y2]) => {
    const n = G(inner);
    el('path', { d: `M${x} ${y} L${x2} ${y2}`, stroke: P2, 'stroke-width': 8, 'stroke-linecap': 'round' }, n);
    n.dot = el('circle', { cx: x, cy: y, r: 11, fill: P2 }, n);
    n.cx = x; n.cy = y;
    return n;
  });
  o.set = (p, glow = 0) => {
    const a = E.back(seg(p, 0, .3));
    o.top.setAttribute('transform', `translate(130 60) scale(${a}) translate(-130 -60)`);
    o.bands.forEach((b, i) => b.setAttribute('stroke-dashoffset', b.L * (1 - E.out(seg(p, .2 + i * .15, .6 + i * .15)))));
    o.nodes.forEach((n, i) => {
      const q = E.back(seg(p, .55 + i * .08, .75 + i * .08));
      n.setAttribute('opacity', clamp(q));
      const pulse = glow * (1 + Math.sin(glow * 20 + i * 1.5) * .5);
      n.dot.setAttribute('r', 11 * q + pulse * 8);
    });
  };
  return o;
}

const Brand = {
  build(parent) {
    const S = this;
    S.root = parent;
    S.endBg = el('rect', { x: 0, y: 0, width: 1080, height: 1920, fill: P('#221E47', .5) }, parent);
    S.endStars = G(parent);
    for (let i = 0; i < 30; i++) el('circle', { cx: rnd(i * 5) * 1080, cy: rnd(i * 5 + 1) * 1920, r: 2 + rnd(i + 7) * 3, fill: '#F2C94C', opacity: .7 }, S.endStars);
    S.iconG = G(parent);
    S.icon = makeLogoIcon(S.iconG);
    S.word = el('text', { 'font-family': 'Liberation Sans, Arial, sans-serif', 'font-weight': 700, fill: '#C0C0C0', 'letter-spacing': -2 }, parent);
    S.word.textContent = 'Alfastack';
    S.tag = el('text', { x: 540, y: 1175, 'text-anchor': 'middle', 'font-family': 'Nunito', 'font-weight': 800, 'font-size': 52, fill: '#FBF4E4' }, parent);
    S.tag.textContent = 'Transforming Tomorrow, Today!';
    S.built = el('text', { x: 540, y: 720, 'text-anchor': 'middle', 'font-family': 'Caveat', 'font-weight': 700, 'font-size': 96, fill: '#FBF4E4' }, parent);
    S.built.textContent = 'So we built';
    S.line = el('text', { x: 540, y: 1110, 'text-anchor': 'middle', 'font-family': 'Nunito', 'font-weight': 700, 'font-size': 40, fill: '#D9D3F2' }, parent);
    el('tspan', { x: 540, dy: 0 }, S.line).textContent = 'From running everything manually';
    el('tspan', { x: 540, dy: 56 }, S.line).textContent = 'to building systems that run together.';
  },
  render(t) {
    const S = this;
    // end-card background
    const endA = seg(t, 53.4, 53.9);
    op(S.endBg, endA); op(S.endStars, endA);
    // icon
    let vis = (t > 38.15 && t < 46.9) || t > 54.1;
    show(S.iconG, vis);
    if (t < 47) {
      const mv = E.inOut(seg(t, 41.1, 41.8));
      const x = 540, y = lerp(760, 330, mv), s = lerp(1.5, .62, mv);
      const glow = t > 43.55 && t < 44.1 ? (t - 43.55) : 0;
      S.icon.set(seg(t, 38.15, 39.3), glow);
      const out = seg(t, 46.4, 46.9);
      tf(S.iconG, { x, y, s: s * (1 + Math.sin(seg(t, 43.55, 44.1) * Math.PI) * .12) });
      S.iconG.setAttribute('opacity', 1 - out);
    } else {
      S.icon.set(seg(t, 54.1, 55.0));
      S.iconG.setAttribute('opacity', 1);
      tf(S.iconG, { x: 205, y: 905, s: .72 });
    }
    // wordmark
    const wStack = t > 38.9 && t < 41.5, wEnd = t > 54.4;
    show(S.word, wStack || wEnd);
    if (wStack) {
      const p = E.out(seg(t, 38.9, 39.4)), out = seg(t, 40.85, 41.15);
      S.word.setAttribute('x', 540); S.word.setAttribute('y', 1080 + (1 - p) * 40); S.word.setAttribute('text-anchor', 'middle');
      S.word.setAttribute('font-size', 150); S.word.setAttribute('opacity', p * (1 - out));
    } else if (wEnd) {
      const p = E.out(seg(t, 54.4, 54.9));
      S.word.setAttribute('x', 318 + (1 - p) * 30); S.word.setAttribute('y', 950); S.word.setAttribute('text-anchor', 'start');
      S.word.setAttribute('font-size', 132); S.word.setAttribute('opacity', p);
    }
    const tg = seg(t, 39.6, 40.0) * (1 - seg(t, 40.85, 41.15));
    op(S.tag, t < 42 ? tg : 0);
    op(S.built, seg(t, 53.8, 54.3));
    op(S.line, seg(t, 55.2, 55.8));
  }
};

// Adult close-up (46.5–49): watches the system, same head tilt as the kid
const Closeup = {
  build(parent) {
    const S = this;
    S.root = G(parent, { filter: 'url(#rough)' });
    el('rect', { x: -10, y: -10, width: 1100, height: 1940, fill: P('#2B2660', .5) }, S.root);
    for (let i = 0; i < 30; i++) el('circle', { cx: rnd(i * 3) * 1080, cy: rnd(i * 3 + 1) * 1000, r: 2 + rnd(i) * 3, fill: '#F2C94C', opacity: .7 }, S.root);
    el('circle', { cx: 540, cy: 980, r: 420, fill: '#996EFF', opacity: .12 }, S.root);
    S.pG = G(S.root, { transform: 'translate(540 1700) scale(2.2)' });
    S.p = makePrashant(S.pG, 'adult', 'desk');
  },
  render(t) {
    const S = this;
    const tilt = 8 * E.inOut(seg(t, 47.6, 48.2));
    S.pG.setAttribute('transform', `translate(540 ${1700 - seg(t, 46.5, 49) * 30}) scale(2.2)`);
    S.p.pose({ t, hL: [-60, 200], hR: [60, 200], headTilt: tilt, face: { lookX: -.3, lookY: -.7, mouth: t > 47.3 ? 'smile' : 'flat', blink: (t > 47.0 && t < 47.12) ? 1 : 0 } });
  }
};
