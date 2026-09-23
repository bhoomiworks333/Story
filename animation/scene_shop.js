// SCENES 0–2 (+ callback in 7): father's shop, the observation and the question.
function camT(g, fx, fy, z, rot = 0) {
  g.setAttribute('transform', `translate(540 960) rotate(${rot}) scale(${z}) translate(${-fx} ${-fy})`);
}

const Shop = {
  build(parent) {
    const S = this;
    S.root = G(parent, { filter: 'url(#rough)' });
    S.cam = G(S.root);
    const w = S.cam;
    // wall + floor
    el('rect', { x: -400, y: -400, width: 1880, height: 1760, fill: P('#F2C14E', .6) }, w);
    scribbleText(w, -200, 20, 1500, 900, '#8A5A12', .12, 2, 28);
    el('rect', { x: -400, y: 1330, width: 1880, height: 1000, fill: P('#8A5638', .7) }, w);
    // bunting
    const bunt = G(w);
    el('path', { d: 'M-20 70 Q540 150 1100 70', fill: 'none', stroke: '#6E4630', 'stroke-width': 4 }, bunt);
    for (let i = 0; i < 12; i++) {
      const x = 20 + i * 90, y = 70 + Math.sin(i / 11 * Math.PI) * 40;
      cut('path', { d: `M${x - 30} ${y} L${x + 30} ${y + 2} L${x} ${y + 56}Z` }, bunt, [C.terracotta, C.teal, C.cream, C.pink][i % 4], 4);
    }
    // shelves
    const shelf = G(w);
    for (const y of [380, 610]) {
      cut('rect', { x: 20, y, width: 1040, height: 26, rx: 4 }, shelf, C.wood, 5);
    }
    const jar = (x, y, col, h = 120) => {
      cut('rect', { x: x - 42, y: y - h, width: 84, height: h, rx: 18 }, shelf, '#F4EBDD', 5);
      flat('rect', { x: x - 34, y: y - h * .7, width: 68, height: h * .64, rx: 12 }, shelf, col);
      cut('rect', { x: x - 36, y: y - h - 18, width: 72, height: 22, rx: 6 }, shelf, C.red, 4);
    };
    const box = (x, y, col, w2 = 110, h = 90) => {
      cut('rect', { x: x - w2 / 2, y: y - h, width: w2, height: h, rx: 4 }, shelf, col, 5);
      el('path', { d: `M${x - w2 / 2 + 10} ${y - h + 22} L${x + w2 / 2 - 10} ${y - h + 22}`, stroke: '#fff', 'stroke-width': 4, opacity: .5 }, shelf);
    };
    const sack = (x, y, col) => {
      cut('path', { d: `M${x - 60} ${y} C${x - 70} ${y - 60}, ${x - 50} ${y - 110}, ${x - 30} ${y - 130} L${x + 30} ${y - 130} C${x + 50} ${y - 110}, ${x + 70} ${y - 60}, ${x + 60} ${y}Z` }, shelf, col, 5);
      el('path', { d: `M${x - 30} ${y - 130} Q${x} ${y - 112} ${x + 30} ${y - 130}`, fill: 'none', stroke: '#7A5A36', 'stroke-width': 5 }, shelf);
    };
    jar(90, 380, '#D8413A'); jar(190, 380, '#EDB441'); jar(290, 380, '#6FA34A');
    box(760, 380, '#2F8C86'); box(880, 380, '#E9868B', 100, 110); box(990, 380, '#C89559', 90, 70);
    sack(110, 610, '#D9C29A'); sack(240, 610, '#CBB185'); box(820, 610, '#D5664A', 130, 100); jar(950, 610, '#8E6BB0', 100);
    // clock
    const clk = G(w, { transform: 'translate(640 470)' });
    cut('circle', { r: 44 }, clk, C.cream, 6);
    el('circle', { r: 44, fill: 'none', stroke: C.terracotta, 'stroke-width': 7 }, clk);
    S.clkH = el('path', { d: 'M0 0 L0 -24', stroke: C.ink, 'stroke-width': 6, 'stroke-linecap': 'round' }, clk);
    S.clkM = el('path', { d: 'M0 0 L0 -34', stroke: C.ink, 'stroke-width': 4, 'stroke-linecap': 'round' }, clk);
    // kid's taped drawing on the wall (sun, like the reference)
    const dr = G(w, { transform: 'translate(420 470) rotate(-6)' });
    cut('rect', { x: -60, y: -66, width: 120, height: 132 }, dr, '#FFFCF3', 5);
    for (let i = 0; i < 10; i++) { const a = i / 10 * Math.PI * 2; el('path', { d: `M${Math.cos(a) * 12} ${-10 + Math.sin(a) * 12} L${Math.cos(a) * 34} ${-10 + Math.sin(a) * 34}`, stroke: C.terracotta, 'stroke-width': 6, 'stroke-linecap': 'round' }, dr); }
    el('path', { d: 'M-40 44 Q0 36 40 44', stroke: '#6FA34A', 'stroke-width': 5, fill: 'none' }, dr);
    flat('rect', { x: -18, y: -76, width: 36, height: 18, transform: 'rotate(8)' }, dr, '#EFD98C');

    // father
    S.fatherG = G(w, { transform: 'translate(560 985)' });
    S.father = makeFather(S.fatherG);
    // orbiting thoughts above father's head
    S.orbit = ['paper', 'box', 'coin', 'gear', 'tag'].map(k => makeCritter(w, k));
    S.clockIcon = G(w);
    cut('circle', { r: 32 }, S.clockIcon, C.cream, 5);
    el('path', { d: 'M0 0 L0 -20 M0 0 L14 6', stroke: C.ink, 'stroke-width': 5, 'stroke-linecap': 'round' }, S.clockIcon);

    S.behind = G(w);
    // counter
    const ctr = G(w);
    cut('rect', { x: -40, y: 1000, width: 1160, height: 340 }, ctr, C.woodDark, 0);
    for (let x = 0; x < 1100; x += 120) el('path', { d: `M${x} 1010 L${x} 1330`, stroke: '#5E3820', 'stroke-width': 5, opacity: .6 }, ctr);
    cut('rect', { x: -40, y: 960, width: 1160, height: 46, rx: 6 }, ctr, C.wood, 6);
    // counter props
    S.ledger = makeLedger(w); tf(S.ledger.g, { x: 400, y: 950, s: .95 });
    S.chai = G(w, { transform: 'translate(690 968)' });
    cut('path', { d: 'M-22 -54 L22 -54 L16 0 L-16 0Z' }, S.chai, '#C9C4C0', 4);
    flat('path', { d: 'M-20 -40 L20 -40 L16 -2 L-16 -2Z' }, S.chai, '#B7743F');
    S.steam = el('path', { d: 'M-6 -64 C-16 -80, 4 -90, -6 -108 M8 -64 C-2 -80, 18 -90, 8 -108', fill: 'none', stroke: '#fff', 'stroke-width': 4, 'stroke-linecap': 'round', opacity: .6 }, S.chai);
    S.phone = makePhone(w); S.phone.x = 850; S.phone.y = 972; S.phone.s = .9;
    // paper pile
    S.pile = G(w);
    S.pileSheets = [];
    for (let i = 0; i < 12; i++) {
      const sh = cut('rect', { x: -80, y: -12, width: 160, height: 14, rx: 2 }, S.pile, i % 3 ? '#FFFCF3' : '#F3E7C9', 4);
      S.pileSheets.push(sh);
    }
    S.paperCrit = makeCritter(w, 'paper');

    // customers
    S.cust = [
      Object.assign(makePerson(w, { cloth: '#9C5BA8', dupatta: '#E9868B', skin: '#B87D55', hairStyle: 'bun' }), { from: [-160, 1070], to: [110, 1070], s: .78 }),
      Object.assign(makePerson(w, { cloth: '#4F7F5A', skin: '#A7704A', hairStyle: 'cap', capColor: '#2F6DB5', mustache: true }), { from: [1240, 1060], to: [975, 1060], s: .8 }),
      Object.assign(makePerson(S.behind, { cloth: '#D5664A', skin: '#C98E62' }), { from: [800, 1300], to: [800, 985], s: .7 }),
    ];
    S.bubbles = [];
    const icons = ['₹', 'box', 'clock'];
    const bpos = [[270, 730], [930, 690], [790, 560]];
    icons.forEach((ic, i) => {
      const b = G(w);
      cut('ellipse', { rx: 70, ry: 56 }, b, '#FFFDF6', 5);
      const tail = i === 0 ? 'M-40 40 L-80 90 L-10 50Z' : i === 1 ? 'M20 44 L50 110 L0 52Z' : 'M0 50 L10 110 L-20 52Z';
      el('path', { d: tail, fill: '#FFFDF6' }, b);
      if (ic === '₹') el('text', { y: 20, 'text-anchor': 'middle', 'font-family': 'Nunito', 'font-weight': 800, 'font-size': 64, fill: '#A87414' }, b).textContent = '₹';
      if (ic === 'box') { cut('rect', { x: -30, y: -26, width: 60, height: 50, rx: 3 }, b, '#C89559', 3); el('path', { d: 'M-30 -10 L30 -10', stroke: '#9A6A36', 'stroke-width': 3 }, b); }
      if (ic === 'clock') { el('circle', { r: 28, fill: 'none', stroke: C.ink, 'stroke-width': 5 }, b); el('path', { d: 'M0 0 L0 -18 M0 0 L12 6', stroke: C.ink, 'stroke-width': 5, 'stroke-linecap': 'round' }, b); }
      el('text', { x: 46, y: -24, 'font-family': 'Nunito', 'font-weight': 800, 'font-size': 40, fill: C.terracotta }, b).textContent = '?';
      b.pos = bpos[i];
      S.bubbles.push(b);
    });

    // kid (foreground)
    S.kidG = G(w, { transform: 'translate(240 1400) scale(.8)' });
    S.kid = makePrashant(S.kidG, 'kid', 'sit');

    // thought bubble + yarn
    S.thought = G(w);
    S.tDots = [[320, 1050, 12], [355, 1000, 17], [395, 950, 22]].map(([x, y, r]) => cut('circle', { cx: x, cy: y, r }, S.thought, '#FFFDF6', 4));
    S.tBub = G(S.thought, { transform: 'translate(480 860)' });
    cut('path', { d: blobPath(0, 0, 150, 120, 9) }, S.tBub, '#FFFDF6', 6);
    S.yarn = el('path', { d: yarnPath(0, 0, 70), fill: 'none', stroke: C.red, 'stroke-width': 5, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, S.tBub);
    S.yarnLen = S.yarn.getTotalLength();
    S.yarn.setAttribute('stroke-dasharray', S.yarnLen);
    S.thread = el('path', { fill: 'none', stroke: C.red, 'stroke-width': 5, 'stroke-linecap': 'round' }, w);
  },

  // p: global time
  render(t) {
    const S = this;
    // ----- camera -----
    let fx = 540, fy = 960, z = 1, rot = 0;
    if (t < 2.2) {
      const p = E.inOut(seg(t, 1.55, 2.15));
      fx = lerp(830, 540, p); fy = lerp(930, 930, p); z = lerp(3.1, 1.12, p);
      rot = lerp(Math.sin(t * 40) * (t < 1.5 ? .8 : 0), 0, p);
    } else if (t < 18.75) {
      const p = E.inOut(seg(t, 11.0, 12.6));
      fx = lerp(540, 360, p); fy = lerp(930, 1040, p); z = lerp(1.12, 1.9, p);
      // slow push during S1
      z *= lerp(1, 1.04, seg(t, 2.2, 11));
      // whip into notebook
      const q = E.in(seg(t, 18.05, 18.75));
      fx = lerp(fx, 240, E.out(seg(t, 17.9, 18.4))); fy = lerp(fy, 1358, E.out(seg(t, 17.9, 18.4)));
      z = z * Math.pow(9, q);
    } else {
      // closing callback (kid close-up, matching adult close-up)
      const p = seg(t, 48.4, 53.4);
      fx = 240; fy = 1141 + p * 6; z = 2.64 * lerp(1, 1.05, p);
    }
    camT(S.cam, fx, fy, z, rot);

    // clock
    S.clkM.setAttribute('transform', `rotate(${t * 30})`);
    S.clkH.setAttribute('transform', `rotate(${120 + t * 2.5})`);
    S.steam.setAttribute('transform', `translate(${Math.sin(t * 2) * 3} 0)`);
    S.steam.setAttribute('opacity', .4 + Math.sin(t * 3) * .2);

    // ----- phone -----
    const ringing = (t < 1.55) || (t > 6.9 && t < 8.3) || (t > 48.9 && t < 50.3);
    S.phone.set(t, ringing);
    let phoneHeld = t < 1.5 ? 0 : t < 6.5 ? E.out(seg(t, 1.5, 1.95)) : t < 8.3 ? 1 - E.inOut(seg(t, 6.5, 6.8)) : t < 11.5 ? E.out(seg(t, 8.3, 8.6)) : 1;
    if (t > 46) phoneHeld = 0;
    show(S.phone.hs, phoneHeld < .05);

    // ----- father -----
    const fp = { t, phone: phoneHeld, write: 0, face: { mouth: 'smile', lookX: 0, lookY: .2 } };
    const blinkF = (t % 3.1) < .12 ? 1 : 0;
    fp.face.blink = blinkF;
    if (t > 2 && t < 4.5) { fp.write = 1; fp.face.mouth = Math.sin(t * 14) > 0 ? 'talk' : 'smile'; fp.face.lookY = .6; fp.face.lookX = -.4; }
    if (t >= 4.5 && t < 6.5) {
      // three questions at once: head snaps between them
      const k = t < 4.95 ? 0 : t < 5.4 ? 1 : t < 5.85 ? 2 : 3;
      const looks = [[-1, .1], [1, -.1], [.6, .8], [0, .2]];
      fp.face.lookX = looks[k][0]; fp.face.lookY = looks[k][1];
      fp.headDx = looks[k][0] * 10; fp.headTilt = looks[k][0] * 5;
      fp.face.mouth = Math.sin(t * 16) > 0 ? 'talk' : 'smile';
      fp.hL = k === 3 ? [-80, -60] : [-120 + k * 90, -150]; fp.eL = [-170, -120];
    }
    if (t >= 6.5 && t < 8.3) {
      fp.face.mouth = t < 6.9 ? 'smile' : 'o'; fp.face.brow = t > 6.95 ? .8 : 0; fp.face.lookX = .9; fp.face.lookY = .5;
      if (t > 7.6) { fp.face.mouth = 'smile'; fp.face.blink = seg(t, 7.6, 7.7) < 1 ? 1 : 0; }
    }
    if (t >= 8.3 && t < 11.5) { fp.write = 1; fp.face.mouth = Math.sin(t * 12) > .2 ? 'talk' : 'smile'; fp.face.lookY = .6; fp.face.lookX = -.4; }
    S.father.pose(fp);

    // ----- orbiting thoughts (8.6–11.5), then fly into bubble (13.2–14.2) -----
    const orbitItems = [...S.orbit.map(o => o), { g: S.clockIcon, isClock: true }];
    orbitItems.forEach((o, i) => {
      const appear = E.back(seg(t, 8.6 + i * .18, 8.9 + i * .18));
      const a = t * 1.6 + i / orbitItems.length * Math.PI * 2;
      let x = 560 + Math.cos(a) * 210, y = 430 + Math.sin(a) * 45;
      let s = .72 * appear * (0.85 + Math.sin(a) * .15);
      const fly = E.inOut(seg(t, 13.2 + i * .08, 14.0 + i * .08));
      x = lerp(x, 480, fly); y = lerp(y, 860, fly); s *= (1 - fly * .8);
      const vis = t > 8.6 && fly < .98 && t < 18.75;
      show(o.g, vis);
      if (!vis) return;
      if (o.isClock) tf(o.g, { x, y, s: s * 1.6, r: Math.sin(t * 3) * 10 });
      else o.set({ t, x, y: y + 40 * s, s, noLegs: true, r: Math.sin(t * 3 + i) * 10 });
    });

    // ----- paper pile -----
    const drops = [0, 0, 0, 0, 3.0, 4.2, 5.6, 6.3, 8.9, 9.6, 10.3, 16.2];
    let h = 0;
    S.pileSheets.forEach((sh, i) => {
      const d = drops[i];
      const p = E.out(seg(t, d, d + .35));
      const vis = t >= d;
      show(sh, vis);
      const y = 985 - h - 8 - (1 - p) * 300;
      tf(sh, { x: 200 + (rnd(i) - .5) * 22, y, r: (rnd(i + 9) - .5) * 8 + (1 - p) * 30 });
      if (vis) h += 14 * p;
    });
    // paper critter walks in and silently sits on the pile
    const walkP = seg(t, 6.6, 7.7), hopP = seg(t, 7.7, 8.1);
    const pileTop = 985 - h - 4;
    let cx = lerp(-80, 120, walkP), cy = 985;
    if (hopP > 0) { cx = lerp(120, 200, hopP); cy = lerp(985, pileTop, hopP) - Math.sin(hopP * Math.PI) * 90; }
    if (t > 8.1) { cx = 200; cy = pileTop; }
    show(S.paperCrit.g, t > 6.5 && t < 18.75);
    const sat = t > 8.1 && t < 8.35 ? .25 : 0;
    S.paperCrit.set({ t, x: cx, y: cy, s: .85 * (1 + sat * .3), walk: walkP > 0 && walkP < 1 ? 1 : 0, lookX: t > 8.2 ? 1 : .6, lookY: t > 8.2 ? -.4 : 0, blink: (t % 2.3) < .1 });

    // ----- customers + bubbles -----
    S.cust.forEach((c, i) => {
      const inP = E.back(seg(t, 4.3 + i * .12, 4.7 + i * .12)), outP = E.in(seg(t, 6.2 + i * .1, 6.6 + i * .1));
      const p = inP * (1 - outP);
      show(c.g, p > .01);
      tf(c.g, { x: lerp(c.from[0], c.to[0], p), y: lerp(c.from[1], c.to[1], p), s: c.s });
      c.head.set({ lookX: i === 1 ? -1 : .8, lookY: i === 2 ? -1 : -.2, mouth: Math.sin(t * 18 + i * 2) > 0 ? 'talk' : 'o', blink: 0 });
      const b = S.bubbles[i];
      const bp = E.back(seg(t, 4.55 + i * .15, 4.8 + i * .15)) * (1 - seg(t, 6.0, 6.25));
      show(b, bp > .01);
      tf(b, { x: b.pos[0], y: b.pos[1] + Math.sin(t * 6 + i) * 4, s: bp });
    });

    // ----- kid -----
    const kp = { t, swing: 1 - seg(t, 11.2, 12.2), chin: 1, face: { lookX: .7, lookY: -.7, mouth: 'smile', blink: (t % 2.7) < .1 ? 1 : 0 } };
    if (t > 4.5 && t < 6.3) { kp.face.lookX = Math.sin(t * 3) > 0 ? -.8 : .9; kp.face.mouth = 'o'; }
    if (t > 6.9 && t < 8.3) { kp.face.lookX = 1; kp.face.lookY = -.5; kp.face.mouth = 'o'; kp.face.brow = .6; }
    if (t > 8.3 && t < 11) { kp.face.mouth = 'o'; kp.face.lookX = .8; kp.face.lookY = -1; }
    if (t > 12.4 && t < 18.75) {
      // eyes: papa -> pile -> papa -> think
      const seq = t < 12.9 ? [1, -1] : t < 13.4 ? [-1, -.6] : t < 13.9 ? [1, -1] : [.3, -.9];
      kp.face.lookX = seq[0]; kp.face.lookY = seq[1];
      kp.face.mouth = t < 13.9 ? 'flat' : 'pout';
      kp.face.brow = t > 13.9 ? -.4 : 0;
      kp.face.frown = t > 13.9 && t < 16.8;
      kp.headTilt = t > 13.9 ? -6 * E.inOut(seg(t, 13.9, 14.4)) : 0;
      if (t > 16.8) { kp.face.mouth = 'smile'; kp.face.frown = false; kp.face.brow = .3; kp.headTilt = lerp(-6, 0, seg(t, 16.8, 17.1)); }
      kp.chin = 1 - E.inOut(seg(t, 17.5, 17.85));
      kp.nbClosed = t > 18.0 ? 1 : 0;
      if (t > 17.5) { kp.face.lookX = -.2; kp.face.lookY = 1; }
    }
    if (t > 48) {
      // closing callback: same head tilt as the adult, then question
      kp.swing = 0; kp.chin = 1;
      kp.headTilt = 8 * (1 - E.inOut(seg(t, 49.2, 49.8)));
      kp.face = { lookX: .6, lookY: -.8, mouth: t < 51.8 ? 'o' : 'smile', blink: (t % 2.9) < .1 ? 1 : 0, happy: t > 52.2 ? 1 : 0 };
      if (t > 49.0 && t < 50.4) { kp.face.lookX = 1; kp.face.lookY = -.3; }
    }
    S.kid.pose(kp);

    // ----- thought bubble -----
    const bubIn = t > 13.0 && t < 18.75;
    show(S.thought, bubIn);
    if (bubIn) {
      S.tDots.forEach((d, i) => { const p = E.back(seg(t, 13.0 + i * .1, 13.2 + i * .1)); d.setAttribute('transform', `translate(${d.getAttribute('cx') * (1 - p)} ${d.getAttribute('cy') * (1 - p)}) scale(${p})`); });
      const bp = E.back(seg(t, 13.25, 13.6));
      tf(S.tBub, { x: 480, y: 860 + Math.sin(t * 2) * 5, s: bp });
      const yp = E.out(seg(t, 13.8, 14.8));
      S.yarn.setAttribute('stroke-dashoffset', S.yarnLen * (1 - yp));
      S.yarn.setAttribute('transform', `rotate(${t * 20})`);
    }
    // loose thread drops to notebook
    const th = seg(t, 17.3, 17.85);
    show(S.thread, th > 0 && t < 18.75);
    if (th > 0) {
      const a = [480, 935], b = [240, 1358];
      const e = lp(a, b, E.out(th));
      S.thread.setAttribute('d', `M${a[0]} ${a[1]} C${a[0] - 20} ${a[1] + 160}, ${e[0] + 90} ${e[1] - 140}, ${e[0]} ${e[1]}`);
    }
  }
};

function blobPath(cx, cy, rx, ry, n) {
  let d = '';
  for (let i = 0; i <= n; i++) {
    const a0 = i / n * Math.PI * 2, a1 = (i + .5) / n * Math.PI * 2, a2 = (i + 1) / n * Math.PI * 2;
    const p0 = [cx + Math.cos(a0) * rx, cy + Math.sin(a0) * ry];
    const c = [cx + Math.cos(a1) * rx * 1.22, cy + Math.sin(a1) * ry * 1.22];
    const p2 = [cx + Math.cos(a2) * rx, cy + Math.sin(a2) * ry];
    if (i === 0) d += `M${p0[0].toFixed(1)} ${p0[1].toFixed(1)}`;
    if (i < n) d += ` Q${c[0].toFixed(1)} ${c[1].toFixed(1)} ${p2[0].toFixed(1)} ${p2[1].toFixed(1)}`;
  }
  return d + 'Z';
}
function yarnPath(cx, cy, R) {
  let d = '';
  for (let k = 0; k < 520; k++) {
    const a = k * .23;
    const phi = k * .037;
    const r = R * (.55 + .45 * Math.sin(k * .071 + 1));
    const x = cx + r * Math.cos(a) * Math.cos(phi) - r * .3 * Math.sin(a * 1.3);
    const y = cy + r * Math.sin(a) * (.8 + .2 * Math.sin(phi * 2));
    d += (k ? ' L' : 'M') + x.toFixed(1) + ' ' + y.toFixed(1);
  }
  return d;
}
