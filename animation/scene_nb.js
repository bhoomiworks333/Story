// SCENE 3: years pass inside the notebook. The red thread stays as the bookmark.
const Notebook = {
  build(parent) {
    const S = this;
    S.root = G(parent, { filter: 'url(#rough)' });
    const w = S.root;
    S.bgWarm = el('rect', { x: -10, y: -10, width: 1100, height: 1940, fill: P('#E9B949', .6) }, w);
    S.bgDusk = el('rect', { x: -10, y: -10, width: 1100, height: 1940, fill: P('#4A5A8C', .6) }, w);
    scribbleText(w, 0, 20, 1080, 1900, '#3A2A10', .08, 5, 28);

    // ----- pile row (father's mess getting organised) -----
    S.row = G(w);
    const r1 = G(S.row, { transform: 'translate(230 470)' });
    S.i1a = makeCritter(r1, 'paper');
    S.i1b = G(r1);
    cut('path', { d: 'M-70 0 L70 0 L60 -40 L-60 -40Z' }, S.i1b, '#6E4630', 5);
    cut('rect', { x: -44, y: -110, width: 88, height: 84, rx: 4 }, S.i1b, '#FFFDF5', 5);
    el('path', { d: 'M-20 -70 L-4 -54 L24 -90', fill: 'none', stroke: '#4E9A55', 'stroke-width': 9, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, S.i1b);
    const r2 = G(S.row, { transform: 'translate(540 470)' });
    S.link = el('path', { d: 'M-70 -40 L70 -40', stroke: C.red, 'stroke-width': 6, 'stroke-dasharray': 140, 'stroke-linecap': 'round' }, r2);
    S.b1 = makeCritter(r2, 'box'); S.b2 = makeCritter(r2, 'box');
    const r3 = G(S.row, { transform: 'translate(850 470)' });
    S.led = makeLedger(r3, '#6A3E7C');
    S.ledClosed = G(r3);
    cut('rect', { x: -70, y: -40, width: 140, height: 44, rx: 5 }, S.ledClosed, '#6A3E7C', 5);
    cut('rect', { x: 40, y: -52, width: 20, height: 30 }, S.ledClosed, '#F2C94C', 3);
    el('path', { d: 'M-40 -18 L20 -18', stroke: '#fff', 'stroke-width': 4, opacity: .6 }, S.ledClosed);
    S.ledEyes = G(S.ledClosed);
    el('circle', { cx: -14, cy: -22, r: 5, fill: C.ink }, S.ledEyes); el('circle', { cx: 10, cy: -22, r: 5, fill: C.ink }, S.ledEyes);

    // ----- notebook -----
    S.outer = G(w);
    S.inner = G(S.outer);
    // bookmark thread
    S.bm = el('path', { fill: 'none', stroke: C.red, 'stroke-width': 6, 'stroke-linecap': 'round' }, S.inner);
    // right page (base)
    S.rightPage = G(S.inner);
    cut('rect', { x: 0, y: -320, width: 480, height: 640, rx: 6 }, S.rightPage, '#FBF6EA', 6);
    for (let y = -270; y < 310; y += 44) el('path', { d: `M24 ${y} L456 ${y}`, stroke: '#9DB9D6', 'stroke-width': 2, opacity: .5 }, S.rightPage);
    // left page (visible only when open)
    S.leftPage = G(S.inner);
    cut('rect', { x: -480, y: -320, width: 480, height: 640, rx: 6 }, S.leftPage, '#FBF6EA', 6);
    for (let y = -270; y < 310; y += 44) el('path', { d: `M-456 ${y} L-24 ${y}`, stroke: '#9DB9D6', 'stroke-width': 2, opacity: .5 }, S.leftPage);
    el('path', { d: 'M0 -320 L0 320', stroke: '#CDBF9F', 'stroke-width': 6 }, S.leftPage);
    // vignettes
    S.vig = [this.vigA(G(S.inner)), this.vigB(G(S.inner)), this.vigC(G(S.inner))];
    // flipping pages
    S.flips = [];
    for (let i = 0; i < 6; i++) {
      const f = G(S.inner);
      f.face = cut('rect', { x: 0, y: -320, width: 480, height: 640, rx: 6 }, f, '#FBF6EA', 5);
      f.shade = el('rect', { x: 0, y: -320, width: 480, height: 640, fill: '#5A4A30', opacity: 0 }, f);
      S.flips.push(f);
    }
    // cover
    S.cover = G(S.inner);
    S.coverFront = G(S.cover);
    cut('rect', { x: 0, y: -320, width: 480, height: 640, rx: 14 }, S.coverFront, C.teal, 8);
    flat('rect', { x: 20, y: -320, width: 30, height: 640 }, S.coverFront, '#256F6A');
    el('path', { d: 'M240 -90 l22 46 l50 6 l-38 34 l10 50 l-44 -24 l-44 24 l10 -50 l-38 -34 l50 -6z', fill: P('#F2C94C'), stroke: EDGE, 'stroke-width': 5 }, S.coverFront);
    cut('rect', { x: 130, y: 120, width: 220, height: 70, rx: 8 }, S.coverFront, '#FBF6EA', 4);
    S.coverBack = G(S.cover);
    cut('rect', { x: 0, y: -320, width: 480, height: 640, rx: 14 }, S.coverBack, '#FBF6EA', 6);
  },

  // --- vignettes on the spread (local coords: spread -480..480, -320..320) ---
  vigA(g) {
    const o = { g };
    cut('rect', { x: -460, y: 236, width: 440, height: 60, rx: 4 }, g, C.wood, 5);
    o.kidG = G(g, { transform: 'translate(-250 250) scale(.66)' });
    o.kid = makePrashant(o.kidG, 'kid', 'desk');
    cut('rect', { x: -170, y: 200, width: 130, height: 40, rx: 2, transform: 'rotate(-4 -105 220)' }, g, '#FFFDF5', 4);
    // crayon drawing on right page: the shop, papa, and boxes linked by lines
    const dg = G(g, { fill: 'none', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' });
    const strokes = [
      ['M110 40 L110 -120 L240 -210 L370 -120 L370 40 Z', '#D5664A', 9],
      ['M190 40 L190 -40 L290 -40 L290 40', '#2F8C86', 8],
      ['M240 -130 m-22 0 a22 22 0 1 0 44 0 a22 22 0 1 0 -44 0', '#EDB441', 8],
      ['M80 130 l60 0 l0 50 l-60 0z', '#2F6DB5', 7],
      ['M200 130 l60 0 l0 50 l-60 0z', '#2F6DB5', 7],
      ['M320 130 l60 0 l0 50 l-60 0z', '#2F6DB5', 7],
      ['M140 155 L200 155 M260 155 L320 155', C.red, 7],
      ['M240 40 L240 130', C.red, 7],
    ];
    o.strokes = strokes.map(([d, c, sw]) => { const p = el('path', { d, stroke: c, 'stroke-width': sw }, dg); const L = p.getTotalLength(); p.setAttribute('stroke-dasharray', L); p.L = L; return p; });
    return o;
  },
  vigB(g) {
    const o = { g };
    cut('rect', { x: -460, y: 236, width: 700, height: 60, rx: 4 }, g, C.wood, 5);
    o.kidG = G(g, { transform: 'translate(-300 250) scale(.66)' });
    o.kid = makePrashant(o.kidG, 'teen', 'desk');
    // chunky old monitor
    cut('rect', { x: -130, y: 30, width: 240, height: 190, rx: 16 }, g, '#D9CFB6', 6);
    flat('rect', { x: -108, y: 50, width: 196, height: 140, rx: 10 }, g, '#1F3A2E');
    o.lines = [];
    for (let i = 0; i < 6; i++) o.lines.push(el('rect', { x: -96, y: 62 + i * 20, width: 60 + rnd(i) * 100, height: 8, fill: '#7CE39A', opacity: .9 }, g));
    cut('rect', { x: -40, y: 220, width: 60, height: 20 }, g, '#BFB49A', 4);
    cut('path', { d: 'M-170 262 L90 262 L100 286 L-180 286Z' }, g, '#E8E0CC', 4);
    // taped flowchart on the right page
    const fc = G(g, { transform: 'translate(300 -60) rotate(3)' });
    cut('rect', { x: -130, y: -170, width: 260, height: 300 }, fc, '#FFFDF5', 5);
    flat('rect', { x: -40, y: -185, width: 80, height: 26, transform: 'rotate(-4)' }, fc, '#EFD98C');
    const fg = G(fc, { fill: 'none', stroke: '#2B2340', 'stroke-width': 5, 'stroke-linecap': 'round' });
    o.fstrokes = ['M-40 -130 h80 v44 h-80z', 'M0 -86 v40', 'M-90 -46 h70 v40 h-70z M20 -46 h70 v40 h-70z', 'M-55 -6 v40 M55 -6 v40', 'M-80 34 h160 v44 h-160z']
      .map(d => { const p = el('path', { d }, fg); p.L = p.getTotalLength(); p.setAttribute('stroke-dasharray', p.L); return p; });
    return o;
  },
  vigC(g) {
    const o = { g };
    cut('rect', { x: -460, y: 236, width: 600, height: 60, rx: 4 }, g, C.wood, 5);
    o.kidG = G(g, { transform: 'translate(-300 250) scale(.66)' });
    o.kid = makePrashant(o.kidG, 'college', 'desk');
    // laptop (side view)
    cut('path', { d: 'M-150 236 L60 236 L60 222 L-150 222Z' }, g, '#8D8C92', 4);
    cut('path', { d: 'M40 222 L10 70 L-160 90 L-140 222Z' }, g, '#B9B8BE', 5);
    flat('path', { d: 'M22 206 L-2 88 L-144 104 L-128 206Z' }, g, '#26213F');
    el('text', { x: -70, y: 175, 'text-anchor': 'middle', 'font-family': 'Nunito', 'font-weight': 800, 'font-size': 56, fill: '#9BE0C8' }, g).textContent = '{ }';
    // books
    cut('rect', { x: 70, y: 196, width: 120, height: 26 }, g, C.terracotta, 4);
    cut('rect', { x: 78, y: 170, width: 104, height: 26 }, g, C.teal, 4);
    // sticky-note network on right page
    const pos = [[160, -200], [360, -170], [260, -40], [130, 90], [380, 80]];
    const cols = ['#F7D774', '#F4A6B0', '#9FD3E6', '#B8E0A0', '#F7D774'];
    o.links = [[0, 2], [1, 2], [2, 3], [2, 4], [0, 1], [3, 4]].map(([a, b]) => {
      const p = el('path', { d: `M${pos[a][0]} ${pos[a][1]} L${pos[b][0]} ${pos[b][1]}`, stroke: C.red, 'stroke-width': 6, 'stroke-linecap': 'round' }, g);
      p.L = p.getTotalLength(); p.setAttribute('stroke-dasharray', p.L); return p;
    });
    o.notes = pos.map(([x, y], i) => {
      const n = G(g, { transform: `translate(${x} ${y}) rotate(${(rnd(i) - .5) * 12})` });
      cut('rect', { x: -50, y: -44, width: 100, height: 88 }, n, cols[i], 4);
      for (let k = 0; k < 3; k++) el('path', { d: `M-34 ${-20 + k * 18} L${10 + rnd(i * 5 + k) * 24} ${-20 + k * 18}`, stroke: '#2B2340', 'stroke-width': 4, opacity: .6 }, n);
      return n;
    });
    return o;
  },

  render(t) {
    const S = this;
    const dusk = E.inOut(seg(t, 20.5, 27.5));
    S.bgDusk.setAttribute('opacity', dusk);

    // notebook transforms
    const zoomIn = E.out(seg(t, 18.7, 19.25));
    const spin = E.inOut(seg(t, 19.2, 19.95));
    const open = E.inOut(seg(t, 19.95, 20.4)) * (1 - E.inOut(seg(t, 27.55, 27.85)));
    const fly = E.inOut(seg(t, 27.85, 28.45));
    let s = lerp(6, 1, zoomIn) * (1 - Math.sin(spin * Math.PI) * .18);
    let x = 540, y = 900;
    s = lerp(s, .3, fly); x = lerp(x, 280, fly); y = lerp(y, 1000, fly);
    S.outer.setAttribute('transform', `translate(${x} ${y}) rotate(${spin * 360 + fly * -8}) scale(${s})`);
    S.inner.setAttribute('transform', `translate(${-240 * (1 - open)} 0)`);
    const cs = Math.cos(open * Math.PI);
    S.cover.setAttribute('transform', `scale(${cs.toFixed(4)} 1)`);
    show(S.coverFront, cs > 0); show(S.coverBack, cs <= 0 && open < .97);
    show(S.leftPage, open > .5);
    // bookmark sway
    const sw = Math.sin(t * 2.4) * 14;
    S.bm.setAttribute('d', `M${40} 300 C${50} 380, ${40 + sw} 420, ${30 + sw * 1.6} 470`);

    // vignette windows
    const win = [[20.25, 22.55], [22.55, 25.15], [25.15, 27.6]];
    S.vig.forEach((v, i) => {
      const a = win[i][0], b = win[i][1];
      const vis = open > .95 && t >= a - .15 && t < b + .15;
      const o2 = Math.min(seg(t, a - .15, a + .15), 1 - seg(t, b - .15, b + .15));
      op(v.g, vis ? o2 : 0);
    });
    const A = S.vig[0], B = S.vig[1], Cc = S.vig[2];
    A.kid.pose({ t, hR: [80 + Math.sin(t * 16) * 18, -40 + Math.cos(t * 13) * 8], hL: [-60, -20], face: { lookX: .6, lookY: .9, mouth: 'pout', blink: (t % 2.2) < .1 ? 1 : 0 } });
    A.strokes.forEach((p, i) => p.setAttribute('stroke-dashoffset', p.L * (1 - seg(t, 20.5 + i * .2, 20.8 + i * .2))));
    B.kid.pose({ t, typing: true, hL: [120, -40 + Math.sin(t * 20) * 6], hR: [200, -40 + Math.sin(t * 23) * 6], face: { lookX: 1, lookY: .3, mouth: 'flat', brow: -.3, blink: (t % 2.6) < .1 ? 1 : 0 } });
    B.lines.forEach((l, i) => l.setAttribute('width', (40 + ((t * 3 + i * .7) % 1) * 140).toFixed(0)));
    B.fstrokes.forEach((p, i) => p.setAttribute('stroke-dashoffset', p.L * (1 - seg(t, 22.9 + i * .3, 23.3 + i * .3))));
    const aha = t > 26.6;
    Cc.kid.pose({ t, typing: !aha, hL: [120, -40], hR: [200, -40], headTilt: aha ? 6 : 0, face: { lookX: aha ? .8 : .9, lookY: aha ? -.6 : .4, mouth: aha ? 'grin' : 'flat', brow: aha ? 1 : 0, blink: (t % 2.4) < .1 ? 1 : 0 } });
    Cc.links.forEach((p, i) => p.setAttribute('stroke-dashoffset', p.L * (1 - seg(t, 25.8 + i * .22, 26.1 + i * .22))));
    Cc.notes.forEach((n, i) => n.setAttribute('opacity', E.out(seg(t, 25.4 + i * .12, 25.6 + i * .12))));

    // page flips (bursts)
    const bursts = [22.25, 24.85];
    S.flips.forEach((f, i) => {
      const b = bursts[Math.floor(i / 3)], st = b + (i % 3) * .12;
      const p = seg(t, st, st + .4);
      const vis = p > 0 && p < 1 && open > .95;
      show(f, vis);
      if (!vis) return;
      const c = Math.cos(E.inOut(p) * Math.PI);
      f.setAttribute('transform', `scale(${c.toFixed(4)} 1)`);
      f.shade.setAttribute('opacity', (1 - Math.abs(c)) * .35);
    });

    // pile row
    const rowIn = E.back(seg(t, 19.6, 20.1)) * (1 - seg(t, 27.7, 28.1));
    S.row.setAttribute('opacity', clamp(rowIn));
    const f1 = t > 22.55;
    const pop1 = 1 + Math.sin(seg(t, 22.55, 22.85) * Math.PI) * .25;
    show(S.i1a.g, !f1); show(S.i1b, f1);
    S.i1a.set({ t, r: Math.sin(t * 5) * 12, s: .9, walk: .6, lookX: Math.sin(t * 3) });
    tf(S.i1b, { s: pop1 });
    const f2 = E.back(seg(t, 25.1, 25.45));
    S.link.setAttribute('stroke-dashoffset', 140 * (1 - f2));
    S.b1.set({ t, x: -70, y: 0, s: .7, r: lerp(-14, 0, f2), smile: f2 > .5, lookX: f2 > .5 ? 1 : -1, hop: f2 > 0 && f2 < 1 ? 20 : 0 });
    S.b2.set({ t, x: 70, y: 0, s: .7, r: lerp(12, 0, f2), smile: f2 > .5, lookX: f2 > .5 ? -1 : 1, hop: f2 > 0 && f2 < 1 ? 20 : 0 });
    const f3 = t > 27.25;
    show(S.led.g, !f3); show(S.ledClosed, f3);
    const flap = Math.sin(t * 16) * 35;
    S.led.l.setAttribute('transform', `rotate(${flap})`); S.led.r.setAttribute('transform', `rotate(${-flap})`);
    tf(S.led.g, { y: -20 + Math.sin(t * 4) * 18, r: Math.sin(t * 3) * 8, s: .75 });
    tf(S.ledClosed, { s: 1 + Math.sin(seg(t, 27.25, 27.55) * Math.PI) * .25 });
  }
};
