// SCENE 4 (realisation) + SCENE 5 (the connected parts become AlfaStack).
const Desk = {
  build(parent) {
    const S = this;
    S.root = G(parent, { filter: 'url(#rough)' });
    S.cam = G(S.root);
    const w = S.cam;
    el('rect', { x: -400, y: -400, width: 1880, height: 1760, fill: P('#3E5A86', .6) }, w);
    scribbleText(w, -200, 20, 1500, 900, '#E6E9F5', .07, 9, 28);
    el('rect', { x: -400, y: 1330, width: 1880, height: 1000, fill: P('#2C2A45', .7) }, w);
    // window with moon (night: years later)
    const win = G(w, { transform: 'translate(860 250)' });
    cut('rect', { x: -130, y: -110, width: 260, height: 220, rx: 6 }, win, '#241F4A', 8);
    el('path', { d: 'M-40 -60 a40 40 0 1 0 50 60 a34 34 0 1 1 -50 -60z', fill: P('#F4E7C4') }, win);
    for (let i = 0; i < 6; i++) el('circle', { cx: -100 + rnd(i) * 200, cy: -90 + rnd(i + 3) * 180, r: 4, fill: '#F2C94C' }, win);
    el('path', { d: 'M0 -110 L0 110 M-130 0 L130 0', stroke: '#6B4A36', 'stroke-width': 8 }, win);
    // the kid's crayon shop drawing, pinned on the wall (callback)
    const dr = G(w, { transform: 'translate(190 250) rotate(-5)' });
    cut('rect', { x: -90, y: -90, width: 180, height: 170 }, dr, '#FFFCF3', 5);
    el('path', { d: 'M-50 40 L-50 -20 L0 -60 L50 -20 L50 40Z M-20 40 L-20 5 L20 5 L20 40', fill: 'none', stroke: C.terracotta, 'stroke-width': 6 }, dr);
    flat('rect', { x: -22, y: -100, width: 44, height: 20, transform: 'rotate(6)' }, dr, '#EFD98C');
    // same clock position as the shop
    const clk = G(w, { transform: 'translate(640 470)' });
    cut('circle', { r: 44 }, clk, C.cream, 6);
    el('circle', { r: 44, fill: 'none', stroke: C.terracotta, 'stroke-width': 7 }, clk);
    S.clkM = el('path', { d: 'M0 0 L0 -34', stroke: C.ink, 'stroke-width': 4, 'stroke-linecap': 'round' }, clk);
    el('path', { d: 'M0 0 L-18 -14', stroke: C.ink, 'stroke-width': 6, 'stroke-linecap': 'round' }, clk);

    // brand night background for scene 5 (fades in)
    S.night = el('rect', { x: -400, y: -400, width: 1880, height: 2800, fill: P('#221E47', .5) }, w);
    S.stars = G(w);
    for (let i = 0; i < 40; i++) el('circle', { cx: rnd(i * 2) * 1080, cy: rnd(i * 2 + 1) * 1700, r: 2 + rnd(i) * 3, fill: '#F2C94C', opacity: .8 }, S.stars);

    // connection lines (behind founder)
    S.home = [[200, 470], [560, 330], [920, 470], [170, 820], [930, 820], [880, 985]];
    S.kinds = ['person', 'box', 'gear', 'coin', 'tag', 'machine'];
    S.NB = [300, 955];
    // edge: [a, b, time]; -1 = notebook
    S.edges = [[-1, 3, 31.2], [3, 0, 31.8], [0, 1, 32.3], [1, 2, 32.75], [2, 4, 33.15], [4, 5, 33.5], [5, 3, 33.8], [0, 4, 34.05], [1, 5, 34.25]];
    S.lineG = G(w);
    S.lines = S.edges.map(() => el('path', { fill: 'none', stroke: C.red, 'stroke-width': 7, 'stroke-linecap': 'round' }, S.lineG));

    // foreground group: founder, desk, props (drops away in scene 5)
    S.fg = G(w);
    S.crit = S.kinds.slice(0, 5).map(k => makeCritter(S.fg, k));
    S.pG = G(S.fg, { transform: 'translate(560 985) scale(1.05)' });
    S.p = makePrashant(S.pG, 'adult', 'desk');
    const ctr = G(S.fg);
    cut('rect', { x: -40, y: 1000, width: 1160, height: 340 }, ctr, C.woodDark, 0);
    for (let x = 0; x < 1100; x += 120) el('path', { d: `M${x} 1010 L${x} 1330`, stroke: '#5E3820', 'stroke-width': 5, opacity: .6 }, ctr);
    cut('rect', { x: -40, y: 960, width: 1160, height: 46, rx: 6 }, ctr, C.wood, 6);
    // laptop (back of lid facing us)
    cut('path', { d: 'M420 975 L700 975 L690 800 L430 800Z' }, S.fg, '#B9B8BE', 6);
    el('circle', { cx: 560, cy: 885, r: 16, fill: '#fff', opacity: .5 }, S.fg);
    // old notebook, still with the red thread
    cut('path', { d: 'M230 972 L370 972 L360 940 L240 940Z' }, S.fg, C.teal, 5);
    el('path', { d: 'M300 972 C300 990, 310 1000, 296 1020', fill: 'none', stroke: C.red, 'stroke-width': 6 }, S.fg);
    // chai
    const chai = G(S.fg, { transform: 'translate(150 968)' });
    cut('path', { d: 'M-22 -54 L22 -54 L16 0 L-16 0Z' }, chai, '#C9C4C0', 4);
    flat('path', { d: 'M-20 -40 L20 -40 L16 -2 L-16 -2Z' }, chai, '#B7743F');
    // machine critter sits on desk (front layer)
    S.crit.push(makeCritter(S.fg, 'machine'));
    S.planes = [0, 1, 2, 3].map(() => makePlane(w));
  },

  critPos(i, t) {
    const S = this;
    const h = S.home[i];
    const conn = S.edges.find(e => e[0] === i || e[1] === i)[2];
    const settle = E.inOut(seg(t, conn, conn + .3));
    const amp = i === 5 ? 20 : 46;
    const wx = Math.sin(t * (1.3 + i * .23) + i * 2) * amp * (1 - settle);
    let x = h[0] + wx, y = h[1];
    const conv = E.inOut(seg(t, 37.5 + i * .05, 38.35 + i * .05));
    x = lerp(x, 540, conv); y = lerp(y, 800, conv);
    const vx = Math.cos(t * (1.3 + i * .23) + i * 2);
    return { x, y, conv, settle, flip: vx < 0 && settle < .5, walk: settle < .5 ? 1 : 0 };
  },
  pt(i, t) { if (i < 0) return this.NB; const p = this.critPos(i, t); const s = 1.05 * (1 - p.conv); return [p.x, p.y - 48 * s]; },

  render(t) {
    const S = this;
    const z = 1.12 * lerp(1, 1.05, seg(t, 28.2, 37));
    camT(S.cam, 540, 930, z);
    S.clkM.setAttribute('transform', `rotate(${t * 30})`);
    const nightP = E.inOut(seg(t, 37.2, 37.9));
    S.night.setAttribute('opacity', nightP); S.stars.setAttribute('opacity', nightP);
    const drop = E.in(seg(t, 37.2, 37.9));
    S.fg.setAttribute('transform', `translate(0 ${drop * 1300})`);

    // critters
    S.crit.forEach((c, i) => {
      const p = S.critPos(i, t);
      const connected = t > S.edges.find(e => e[0] === i || e[1] === i)[2];
      const s = 1.05 * (1 - p.conv);
      // critters live in fg (which drops) – counter the drop so they stay
      const hopT = S.edges.filter(e => e[0] === i || e[1] === i).map(e => e[2]);
      let hop = 0; hopT.forEach(h => { hop += Math.sin(seg(t, h, h + .3) * Math.PI) * 26; });
      // planes arriving make them hop too
      c.set({ t, x: p.x, y: p.y - drop * 1300, s, walk: p.walk, flip: p.flip, hop, smile: connected, spin: t * (connected ? 200 : 90), lookX: connected ? Math.sin(t + i) : (p.flip ? -1 : 1), blink: ((t + i * .7) % 2.6) < .1 });
      show(c.g, s > .02);
    });

    // connection lines
    const col = mixHex(C.red, C.purple, E.inOut(seg(t, 37.4, 38.1)));
    S.lines.forEach((ln, k) => {
      const [a, b, tt] = S.edges[k];
      const p = E.out(seg(t, tt, tt + .28));
      let vis = p > 0;
      const A = S.pt(a, t), B = S.pt(b, t);
      let e = lp(A, B, p);
      if (a === -1) {
        const rel = seg(t, 34.5, 35.0);
        if (rel > 0) {
          // the founder lets go: the thread to him falls away
          const sag = rel * 260;
          ln.setAttribute('d', `M${A[0]} ${A[1]} Q${(A[0] + B[0]) / 2} ${(A[1] + B[1]) / 2 + sag} ${lerp(B[0], A[0] + 30, rel)} ${lerp(B[1], A[1] + 60, rel)}`);
          ln.setAttribute('opacity', 1 - rel);
          show(ln, rel < 1);
          return;
        }
        ln.setAttribute('opacity', 1);
      }
      const conv = seg(t, 38.2, 38.6);
      show(ln, vis && conv < 1);
      ln.setAttribute('opacity', 1 - conv);
      ln.setAttribute('stroke', col);
      const mid = [(A[0] + e[0]) / 2, (A[1] + e[1]) / 2 + 30 * (1 - p)];
      ln.setAttribute('d', `M${A[0].toFixed(1)} ${A[1].toFixed(1)} Q${mid[0].toFixed(1)} ${mid[1].toFixed(1)} ${e[0].toFixed(1)} ${e[1].toFixed(1)}`);
    });

    // paper planes along the ring
    const ring = S.edges.slice(1, 7);
    S.planes.forEach((pl, k) => {
      const u = (t - 34.8) * 1.5 + k * 1.5;
      const vis = t > 34.8 + k * .25 && t < 37.6;
      show(pl, vis);
      if (!vis) return;
      const ed = ring[Math.floor(u) % ring.length], f = E.inOut(u % 1);
      const A = S.pt(ed[0], t), B = S.pt(ed[1], t);
      const x = lerp(A[0], B[0], f), y = lerp(A[1], B[1], f) - Math.sin(f * Math.PI) * 60;
      const ang = Math.atan2(B[1] - A[1], B[0] - A[0]) * 180 / Math.PI;
      tf(pl, { x, y, r: ang - Math.cos(f * Math.PI) * 25, s: 1.1 });
    });

    // founder
    const fp = { t, face: { mouth: 'flat', lookX: 0, lookY: .8, blink: (t % 3.2) < .12 ? 1 : 0 } };
    if (t < 30.4) { fp.typing = true; }
    else if (t < 31.0) { fp.face = { lookX: -.6 + Math.sin(t * 6) * .8, lookY: -.8, mouth: 'o', brow: .7 }; }
    else if (t < 34.5) {
      fp.hL = lp([-70, -18], [-248, -26], E.out(seg(t, 31.0, 31.25)));
      const cur = [...S.edges].reverse().find(e => t > e[2]);
      const tgt = cur ? S.pt(cur[1], t) : S.NB;
      fp.face = { lookX: clamp((tgt[0] - 560) / 300, -1, 1), lookY: clamp((tgt[1] - 640) / 300, -1, 1), mouth: 'smile', brow: .3, blink: 0 };
    } else {
      fp.hL = lp([-248, -26], [-70, -18], E.inOut(seg(t, 34.5, 34.9)));
      const pl = S.planes[0];
      fp.face = { lookX: Math.sin(t * 1.4) * .8, lookY: -.6, mouth: 'smile', happy: t > 35.8 ? 1 : 0, blink: 0 };
      fp.headTilt = t > 35.8 ? 5 * E.inOut(seg(t, 35.8, 36.3)) : 0;
      fp.headDy = 6 * E.inOut(seg(t, 34.6, 35.2));
    }
    S.p.pose(fp);
  }
};

function mixHex(a, b, p) {
  const pa = [1, 3, 5].map(i => parseInt(a.substr(i, 2), 16)), pb = [1, 3, 5].map(i => parseInt(b.substr(i, 2), 16));
  return '#' + pa.map((v, i) => Math.round(lerp(v, pb[i], p)).toString(16).padStart(2, '0')).join('');
}
