// Characters and props. All built around a local origin; animate with tf() / set().
const C = {
  skin: '#C98E62', skinDark: '#A8704A', hair: '#1D1719', blush: '#EE8A86',
  mustard: '#EDB441', grey: '#8D8C92', greyLight: '#B9B8BE', khaki: '#B99D6C',
  navy: '#27335E', teal: '#2F8C86', terracotta: '#D5664A', pink: '#E9868B',
  cream: '#F7EEDA', wood: '#A2653D', woodDark: '#7A4A2C', red: '#D8413A',
  purple: '#996EFF', indigo: '#221E47', shirtBlue: '#93BCD0', ink: '#1E1A22',
};

// ---------- faces ----------
// stage: kid | teen | college | adult | father | generic
function makeHead(parent, cfg = {}) {
  const st = cfg.stage || 'kid';
  const g = G(parent);
  const inner = G(g);
  const skin = cfg.skin || C.skin;
  const adultish = st === 'adult' || st === 'father';
  const rx = st === 'kid' ? 94 : st === 'teen' ? 90 : adultish ? 90 : 90;
  const ry = st === 'kid' ? 98 : st === 'teen' ? 104 : adultish ? 110 : 106;

  // back hair
  const hairCol = cfg.hair || C.hair;
  if (st !== 'father' && st !== 'generic') {
    cut('ellipse', { cx: 0, cy: -40, rx: rx + 16, ry: ry * .9 }, inner, hairCol);
  } else if (st === 'father') {
    cut('ellipse', { cx: 0, cy: -44, rx: rx + 8, ry: ry * .74 }, inner, hairCol);
  } else {
    cut('ellipse', { cx: 0, cy: -40, rx: rx + 8, ry: ry * .78 }, inner, hairCol);
  }
  // ears
  cut('ellipse', { cx: -rx + 2, cy: 10, rx: 17, ry: 22 }, inner, skin, 5);
  cut('ellipse', { cx: rx - 2, cy: 10, rx: 17, ry: 22 }, inner, skin, 5);
  // face
  cut('ellipse', { cx: 0, cy: 6, rx, ry }, inner, skin);
  // blush
  el('ellipse', { cx: -rx * .6, cy: 38, rx: 17, ry: 14, fill: C.blush, opacity: .85 }, inner);
  el('ellipse', { cx: rx * .6, cy: 38, rx: 17, ry: 14, fill: C.blush, opacity: .85 }, inner);

  // beard (adult prashant)
  if (st === 'adult') {
    el('path', { d: `M${-rx + 4} 0 C${-rx + 2} 80, -46 ${ry + 14}, 0 ${ry + 18} C46 ${ry + 14}, ${rx - 2} 80, ${rx - 4} 0 C${rx - 12} 52, 56 82, 30 76 C14 70, -14 70, -30 76 C-56 82, ${-rx + 12} 52, ${-rx + 4} 0Z`, fill: P('#2A2224'), opacity: .92 }, inner);
    el('path', { d: 'M-34 52 C-20 36, 20 36, 34 52 C20 47, -20 47, -34 52Z', fill: P('#221B1D') }, inner);
  }
  if (st === 'father') {
    el('path', { d: 'M-42 56 C-26 30, 26 30, 42 56 C30 50, 12 46, 0 50 C-12 46, -30 50, -42 56Z', fill: P('#241C1E') }, inner);
  }
  // nose
  el('path', { d: 'M-6 28 Q0 34 6 28', fill: 'none', stroke: C.skinDark, 'stroke-width': 4, 'stroke-linecap': 'round' }, inner);

  // eyes group
  const eyes = G(inner);
  const eyeDots = [], eyeArcs = [];
  for (const sx of [-1, 1]) {
    const eg = G(eyes, { transform: `translate(${sx * 33} 6)` });
    const dot = el('ellipse', { cx: 0, cy: 0, rx: 8.5, ry: 11, fill: C.ink }, eg);
    el('circle', { cx: 2.5, cy: -4, r: 2.6, fill: '#fff', opacity: .9 }, eg);
    const arc = el('path', { d: 'M-11 3 Q0 -9 11 3', fill: 'none', stroke: C.ink, 'stroke-width': 5, 'stroke-linecap': 'round' }, eg);
    eyeDots.push(eg); eyeArcs.push(arc);
  }
  // brows
  const brows = [];
  for (const sx of [-1, 1]) {
    brows.push(el('path', { d: 'M-12 0 Q0 -5 12 0', fill: 'none', stroke: C.ink, 'stroke-width': adultish ? 6 : 4.5, 'stroke-linecap': 'round' }, inner));
  }
  // mouth
  const mouthY = st === 'adult' ? 60 : st === 'father' ? 66 : 52;
  const mouth = el('path', { fill: '#6B2230', stroke: '#6B2230', 'stroke-width': 4, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, inner);
  const mouths = {
    o: `M-6 ${mouthY} a6 7 0 1 0 12 0 a6 7 0 1 0 -12 0`,
    smile: st === 'adult' ? `M-22 ${mouthY - 4} Q0 ${mouthY + 14} 22 ${mouthY - 4} Q0 ${mouthY + 6} -22 ${mouthY - 4}` : `M-14 ${mouthY - 3} Q0 ${mouthY + 10} 14 ${mouthY - 3} Q0 ${mouthY + 4} -14 ${mouthY - 3}`,
    grin: `M-18 ${mouthY - 4} Q0 ${mouthY + 18} 18 ${mouthY - 4} Z`,
    flat: `M-9 ${mouthY} L9 ${mouthY}`,
    pout: `M-7 ${mouthY + 2} Q0 ${mouthY - 4} 7 ${mouthY + 2}`,
    talk: `M-12 ${mouthY - 3} Q0 ${mouthY + 14} 12 ${mouthY - 3} Z`,
  };

  // front hair
  if (st === 'kid' || st === 'teen' || st === 'college' || st === 'adult') {
    const dy = ry - 100, k = st === 'kid' ? 1 : .96;
    const Y = v => (v < -70 ? v - dy : v).toFixed(1);
    const fr = `M${-rx - 8} 5 C${-rx - 20} -60, -92 ${Y(-122)}, -40 ${Y(-138)}
      C-8 ${Y(-152)}, 42 ${Y(-160)}, 80 ${Y(-142)} C106 ${Y(-128)}, ${rx + 24} ${Y(-96)}, ${rx + 14} -60
      C${rx + 20} -40, ${rx + 14} -12, ${rx + 8} 5
      C${rx + 2} -26, ${rx - 8} -44, 64 ${-54 * k} C50 ${-40 * k}, 26 ${-44 * k}, 16 ${-62 * k}
      C0 ${-46 * k}, -26 ${-48 * k}, -34 ${-64 * k} C-50 ${-48 * k}, -72 ${-48 * k}, -80 ${-56 * k}
      C${-rx} -40, ${-rx - 6} -20, ${-rx - 8} 5Z`;
    cut('path', { d: fr }, inner, C.hair);
    // wave strands
    el('path', { d: `M-30 ${Y(-120)} C0 ${Y(-140)}, 50 ${Y(-142)}, 84 ${Y(-118)}`, fill: 'none', stroke: '#4A4046', 'stroke-width': 4, 'stroke-linecap': 'round', opacity: .8 }, inner);
    el('path', { d: `M-70 ${Y(-84)} C-50 ${Y(-112)}, -10 ${Y(-116)}, 20 ${Y(-104)}`, fill: 'none', stroke: '#4A4046', 'stroke-width': 3.5, 'stroke-linecap': 'round', opacity: .7 }, inner);
    el('path', { d: `M40 -60 C52 ${Y(-84)}, 80 ${Y(-90)}, 96 ${Y(-74)}`, fill: 'none', stroke: '#4A4046', 'stroke-width': 3.5, 'stroke-linecap': 'round', opacity: .7 }, inner);
  } else if (st === 'father') {
    const fr = `M${-rx - 4} -6 C${-rx - 10} -80, -50 ${-ry - 22}, 10 ${-ry - 18} C70 ${-ry - 20}, ${rx + 12} -70, ${rx + 4} -6
      C${rx - 6} -40, 70 -58, 40 -66 C10 -70, -20 -72, -36 -84 C-50 -66, -80 -52, ${-rx - 4} -6Z`;
    cut('path', { d: fr }, inner, C.hair);
    // grey temples
    el('path', { d: `M${-rx - 2} -8 C${-rx - 4} -30, ${-rx + 4} -44, ${-rx + 12} -52`, fill: 'none', stroke: '#9A9699', 'stroke-width': 7, 'stroke-linecap': 'round' }, inner);
    el('path', { d: `M${rx + 2} -8 C${rx + 4} -30, ${rx - 4} -44, ${rx - 12} -52`, fill: 'none', stroke: '#9A9699', 'stroke-width': 7, 'stroke-linecap': 'round' }, inner);
    // reading glasses pushed up on head
    const rg = G(inner, { transform: `translate(0 ${-ry + 2})` });
    for (const sx of [-1, 1]) el('rect', { x: sx * 30 - 22, y: -14, width: 44, height: 28, rx: 10, fill: '#fff', 'fill-opacity': .25, stroke: '#3A2A22', 'stroke-width': 5 }, rg);
    el('path', { d: 'M-8 -2 Q0 -8 8 -2', fill: 'none', stroke: '#3A2A22', 'stroke-width': 5 }, rg);
    // pen behind ear
    const pen = G(inner, { transform: `translate(${rx + 2} -8) rotate(-68)` });
    cut('rect', { x: -30, y: -5, width: 52, height: 10, rx: 3 }, pen, '#2F6DB5', 3);
    el('path', { d: 'M22 -5 L32 0 L22 5Z', fill: '#E8C9A0' }, pen);
  } else if (cfg.hairStyle === 'bun') {
    cut('circle', { cx: 0, cy: -ry - 20, r: 38 }, inner, hairCol);
    cut('path', { d: `M${-rx - 6} 10 C${-rx - 12} -80, -40 ${-ry - 14}, 0 ${-ry - 12} C40 ${-ry - 14}, ${rx + 12} -80, ${rx + 6} 10 C${rx - 10} -30, 40 -64, 0 -66 C-40 -64, ${-rx + 10} -30, ${-rx - 6} 10Z` }, inner, hairCol);
  } else if (cfg.hairStyle === 'cap') {
    cut('path', { d: `M${-rx - 6} -20 C${-rx} -110, ${rx} -110, ${rx + 6} -20 Z` }, inner, cfg.capColor || C.terracotta);
    cut('path', { d: `M${rx - 20} -26 L${rx + 60} -18 L${rx + 50} -6 L${rx - 20} -10Z` }, inner, cfg.capColor || C.terracotta, 5);
  } else {
    cut('path', { d: `M${-rx - 4} 0 C${-rx - 8} -70, -50 ${-ry - 16}, 0 ${-ry - 14} C50 ${-ry - 16}, ${rx + 8} -70, ${rx + 4} 0 C${rx - 8} -34, 50 -60, 10 -60 C-30 -58, ${-rx + 8} -40, ${-rx - 4} 0Z` }, inner, hairCol);
  }

  // glasses
  let glasses = null;
  if (st === 'college' || st === 'adult') {
    glasses = G(inner);
    for (const sx of [-1, 1]) el('rect', { x: sx * 34 - 27, y: -13, width: 54, height: 40, rx: 9, fill: '#fff', 'fill-opacity': .18, stroke: '#18141A', 'stroke-width': 6.5 }, glasses);
    el('path', { d: 'M-7 0 Q0 -5 7 0', fill: 'none', stroke: '#18141A', 'stroke-width': 6 }, glasses);
    el('path', { d: `M-61 -2 L${-rx + 2} -6 M61 -2 L${rx - 2} -6`, stroke: '#18141A', 'stroke-width': 6 }, glasses);
  }

  const face = {
    g, inner, glasses,
    set(s = {}) {
      const lx = s.lookX || 0, ly = s.lookY || 0, blink = s.blink || 0;
      const happy = s.happy || 0;
      eyes.setAttribute('transform', `translate(${lx * 9} ${ly * 7})`);
      eyeDots.forEach((eg, i) => {
        const base = `translate(${(i ? 1 : -1) * 33} 6)`;
        eg.setAttribute('transform', base + ` scale(1 ${Math.max(.08, 1 - blink)})`);
        eg.children[0].setAttribute('opacity', happy > .5 ? 0 : 1);
        eg.children[1].setAttribute('opacity', happy > .5 || blink > .5 ? 0 : .9);
        eyeArcs[i].setAttribute('opacity', happy > .5 ? 1 : 0);
      });
      const br = s.brow || 0; // + raise, - frown
      brows.forEach((b, i) => {
        const sx = i ? 1 : -1;
        const tilt = -br * 10 * sx * -1;
        b.setAttribute('transform', `translate(${sx * 33 + lx * 6} ${-24 - br * 8 + ly * 4}) rotate(${(s.frown ? sx * 12 : 0) + tilt * .3})`);
      });
      mouth.setAttribute('d', mouths[s.mouth || 'smile']);
      const isLine = ['flat', 'pout'].includes(s.mouth);
      mouth.setAttribute('fill', isLine || s.mouth === 'smile' ? (s.mouth === 'smile' ? '#6B2230' : 'none') : '#6B2230');
      tf(inner, { r: s.tilt || 0, x: s.dx || 0, y: s.dy || 0, sx: 1 + (s.squash || 0), sy: 1 - (s.squash || 0) });
    }
  };
  face.set({});
  return face;
}

// striped tee helper
function tee(parent, d, base, stripe, clipId) {
  const g = G(parent);
  cut('path', { d }, g, base);
  const cp = el('clipPath', { id: clipId }, DEFS);
  el('path', { d }, cp);
  const sg = G(g, { 'clip-path': `url(#${clipId})` });
  for (let y = -400; y < 200; y += 34) flat('rect', { x: -200, y, width: 400, height: 15 }, sg, stripe);
  return g;
}

let _clip = 0;
// ---------- Prashant full figures ----------
// pose 'sit' (kid on stool, chin on fists, notebook on lap) or 'desk' (upper body behind a desk; origin = desk top)
function makePrashant(parent, stage, pose) {
  const g = G(parent);
  const body = G(g);
  const o = { g, stage, pose };
  const sid = 'clip' + (_clip++);
  if (pose === 'sit') {
    // stool
    const stool = G(body);
    cut('rect', { x: -110, y: 0, width: 220, height: 28, rx: 8 }, stool, C.wood);
    cut('path', { d: 'M-90 26 L-110 170 L-86 170 L-60 26Z' }, stool, C.woodDark, 5);
    cut('path', { d: 'M90 26 L110 170 L86 170 L60 26Z' }, stool, C.woodDark, 5);
    cut('rect', { x: -96, y: 110, width: 192, height: 14 }, stool, C.woodDark, 4);
    // legs (swing)
    o.legs = [];
    for (const sx of [-1, 1]) {
      const lg = G(body, { transform: `translate(${sx * 40} 0)` });
      cut('rect', { x: -19, y: -10, width: 38, height: 130, rx: 18 }, lg, C.skin, 6);
      // chappal
      cut('path', { d: 'M-26 118 Q0 108 26 118 L28 136 Q0 142 -28 136Z' }, lg, '#6E4630', 5);
      el('path', { d: 'M-12 116 L0 126 L12 116', fill: 'none', stroke: '#C9A26D', 'stroke-width': 5 }, lg);
      // plaster on knee (left)
      if (sx < 0) { const pl = cut('rect', { x: -12, y: 30, width: 24, height: 12, rx: 4, transform: 'rotate(-20)' }, lg, '#E8C79B', 3); }
      o.legs.push(lg);
    }
    // shorts
    cut('path', { d: 'M-88 -70 L88 -70 L96 16 L8 22 L0 4 L-8 22 L-96 16Z' }, body, C.khaki);
    // tee
    tee(body, 'M-78 -214 C-40 -226, 40 -226, 78 -214 L128 -178 L112 -120 L88 -132 L92 -56 L-92 -56 L-88 -132 L-112 -120 L-128 -178Z', C.mustard, C.grey, sid);
    // notebook on lap (open)
    o.nb = G(body, { transform: 'translate(0 -52)' });
    o.nbOpen = G(o.nb);
    cut('path', { d: 'M-96 -18 L0 -8 L96 -18 L100 22 L0 30 L-100 22Z' }, o.nbOpen, C.cream, 6);
    el('path', { d: 'M0 -8 L0 30', stroke: '#C9B89A', 'stroke-width': 3 }, o.nbOpen);
    for (let i = 0; i < 3; i++) el('path', { d: `M-80 ${-4 + i * 9} L-14 ${2 + i * 9} M14 ${2 + i * 9} L80 ${-4 + i * 9}`, stroke: '#7FA7C9', 'stroke-width': 2, opacity: .6 }, o.nbOpen);
    o.nbClosed = G(o.nb);
    cut('path', { d: 'M-70 -14 L70 -14 L74 26 L-74 26Z' }, o.nbClosed, C.teal, 6);
    el('path', { d: 'M-40 6 l6 -12 l6 12 l-13 -8 h14z', fill: '#F2C94C' }, o.nbClosed);
    // arms: elbows on notebook, fists under chin
    o.armL = limb(body, C.skin, 34);
    o.armR = limb(body, C.skin, 34);
    // sleeves over upper arm
    o.slL = cut('path', { d: 'M-26 -22 L26 -18 L20 22 L-22 20Z' }, body, C.mustard, 6);
    o.slR = cut('path', { d: 'M-26 -18 L26 -22 L22 20 L-20 22Z' }, body, C.mustard, 6);
    o.fistL = cut('circle', { r: 24 }, body, C.skin, 6);
    o.fistR = cut('circle', { r: 24 }, body, C.skin, 6);
    o.headG = G(g, { transform: 'translate(0 -318)' });
    o.head = makeHead(o.headG, { stage });
    o.pose = (p = {}) => {
      const t = p.t || 0;
      const swing = p.swing ?? 1;
      o.legs.forEach((lg, i) => lg.setAttribute('transform', `translate(${i ? 40 : -40} 0) rotate(${Math.sin(t * 5.5 + i * 2.2) * 14 * swing})`));
      const chin = p.chin ?? 1; // 1 = fists under chin, 0 = hands holding notebook
      const headLift = p.headDy || 0;
      const fl = lp([-70, -80], [-38, -216], chin), fr = lp([70, -80], [38, -216], chin);
      o.armL([[-92, -190], [-86, -82], fl]);
      o.armR([[92, -190], [86, -82], fr]);
      o.slL.setAttribute('transform', 'translate(-94 -168) rotate(8)');
      o.slR.setAttribute('transform', 'translate(94 -168) rotate(-8)');
      tf(o.fistL, { x: fl[0], y: fl[1] }); tf(o.fistR, { x: fr[0], y: fr[1] });
      o.headG.setAttribute('transform', `translate(0 ${-318 + headLift}) rotate(${p.headTilt || 0})`);
      const closed = p.nbClosed || 0;
      show(o.nbOpen, closed < .5); show(o.nbClosed, closed >= .5);
      o.head.set(p.face || {});
    };
  } else {
    // desk pose: torso ends at y=0 (desk top covers). head at -330
    const cloth = { kid: C.mustard, teen: '#9C9BA2', college: '#5E7FA8', adult: C.navy }[stage];
    if (stage === 'kid') {
      tee(body, 'M-80 -222 C-40 -234, 40 -234, 80 -222 L130 -184 L112 -126 L90 -138 L94 20 L-94 20 L-90 -138 L-112 -126 L-130 -184Z', C.mustard, C.grey, sid);
    } else if (stage === 'teen') {
      cut('path', { d: 'M-96 -226 C-50 -240, 50 -240, 96 -226 L118 20 L-118 20Z' }, body, cloth);
      cut('path', { d: 'M-30 -238 L0 -206 L30 -238 L18 -246 L0 -226 L-18 -246Z' }, body, '#C9C8CE', 5);
      for (let i = 0; i < 3; i++) el('circle', { cx: 0, cy: -180 + i * 50, r: 5, fill: '#6B6A70' }, body);
      cut('rect', { x: 40, y: -190, width: 36, height: 30, rx: 4 }, body, '#85848A', 4);
    } else if (stage === 'college') {
      // checked shirt over grey tee
      cut('path', { d: 'M-96 -226 C-50 -240, 50 -240, 96 -226 L118 20 L-118 20Z' }, body, cloth);
      const cp = el('clipPath', { id: sid }, DEFS); el('path', { d: 'M-96 -226 C-50 -240, 50 -240, 96 -226 L118 20 L-118 20Z' }, cp);
      const ck = G(body, { 'clip-path': `url(#${sid})`, opacity: .45 });
      for (let x = -130; x < 130; x += 40) el('rect', { x, y: -260, width: 14, height: 300, fill: '#E7E1D2' }, ck);
      for (let y = -250; y < 30; y += 40) el('rect', { x: -130, y, width: 260, height: 14, fill: '#1F3350' }, ck);
      cut('path', { d: 'M-44 -236 L0 -228 L44 -236 L30 20 L-30 20Z' }, body, C.grey, 5);
    } else {
      // adult: grey collared shirt + navy textured blazer
      cut('path', { d: 'M-104 -226 C-56 -242, 56 -242, 104 -226 L124 20 L-124 20Z' }, body, C.navy);
      const tx = G(body, { opacity: .25 });
      for (let i = 0; i < 40; i++) el('circle', { cx: -110 + rnd(i) * 220, cy: -220 + rnd(i + 50) * 230, r: 2, fill: '#9AA6D6' }, tx);
      cut('path', { d: 'M-40 -234 L0 -150 L40 -234 L30 20 L-30 20Z' }, body, C.grey, 5);
      cut('path', { d: 'M-40 -236 L-6 -200 L-22 -176Z M40 -236 L6 -200 L22 -176Z' }, body, '#A4A3AA', 4);
      cut('path', { d: 'M-44 -234 L-6 -120 L-60 -40 L-72 -200Z M44 -234 L6 -120 L60 -40 L72 -200Z' }, body, '#1E284C', 5);
    }
    const armCol = stage === 'kid' ? C.skin : cloth;
    o.armL = limb(body, armCol, 40);
    o.armR = limb(body, armCol, 40);
    o.hL = cut('ellipse', { rx: 24, ry: 20 }, body, C.skin, 6);
    o.hR = cut('ellipse', { rx: 24, ry: 20 }, body, C.skin, 6);
    if (stage === 'kid') {
      o.slL = cut('path', { d: 'M-26 -22 L26 -18 L20 22 L-22 20Z', transform: 'translate(-106 -176) rotate(14)' }, body, C.mustard, 6);
      o.slR = cut('path', { d: 'M-26 -18 L26 -22 L22 20 L-20 22Z', transform: 'translate(106 -176) rotate(-14)' }, body, C.mustard, 6);
    }
    o.headG = G(g, { transform: 'translate(0 -330)' });
    o.head = makeHead(o.headG, { stage });
    o.pose = (p = {}) => {
      const t = p.t || 0;
      const type = p.typing ? Math.sin(t * 22) * 6 : 0, type2 = p.typing ? Math.sin(t * 19 + 1) * 6 : 0;
      const hl = p.hL || [-70, -18 + type], hr = p.hR || [70, -18 + type2];
      o.armL([[-100, -196], [-128, -70], hl]);
      o.armR([[100, -196], [128, -70], hr]);
      tf(o.hL, { x: hl[0], y: hl[1] }); tf(o.hR, { x: hr[0], y: hr[1] });
      o.headG.setAttribute('transform', `translate(${p.headDx || 0} ${-330 + (p.headDy || 0)}) rotate(${p.headTilt || 0})`);
      o.head.set(p.face || {});
    };
  }
  o.pose({});
  return o;
}

// ---------- Father (behind counter; origin = counter top) ----------
function makeFather(parent) {
  const g = G(parent);
  const o = { g };
  const body = G(g);
  cut('path', { d: 'M-118 -248 C-60 -266, 60 -266, 118 -248 L140 20 L-140 20Z' }, body, C.shirtBlue);
  // collar + pocket + pens
  cut('path', { d: 'M-40 -262 L0 -222 L40 -262 L26 -270 L0 -244 L-26 -270Z' }, body, '#B7D3E0', 5);
  cut('rect', { x: 36, y: -200, width: 48, height: 44, rx: 5 }, body, '#84AFC4', 4);
  el('rect', { x: 46, y: -218, width: 7, height: 26, fill: '#D8413A' }, body);
  el('rect', { x: 60, y: -222, width: 7, height: 30, fill: '#1E1A22' }, body);
  for (let i = 0; i < 4; i++) el('circle', { cx: 0, cy: -200 + i * 55, r: 5, fill: '#5E8BA2' }, body);
  // sleeves
  o.slL = cut('ellipse', { rx: 40, ry: 32 }, body, C.shirtBlue, 6);
  o.slR = cut('ellipse', { rx: 40, ry: 32 }, body, C.shirtBlue, 6);
  o.armL = limb(body, C.skin, 36);
  o.armR = limb(body, C.skin, 36);
  o.watch = cut('rect', { x: -18, y: -10, width: 36, height: 20, rx: 5 }, body, '#3C3C44', 3);
  o.hL = cut('ellipse', { rx: 26, ry: 22 }, body, C.skin, 6);
  o.hR = cut('ellipse', { rx: 26, ry: 22 }, body, C.skin, 6);
  // handset (held)
  o.handset = G(body);
  cut('path', { d: 'M-16 -62 C-34 -60, -34 -40, -18 -36 L-10 36 C-30 40, -30 60, -12 62 L10 58 L6 -58Z' }, o.handset, '#2E2A33', 5);
  // pen (held)
  o.pen = G(body);
  cut('rect', { x: -5, y: -40, width: 10, height: 50, rx: 3 }, o.pen, '#2F6DB5', 3);
  o.headG = G(g, { transform: 'translate(0 -356)' });
  o.head = makeHead(o.headG, { stage: 'father', skin: '#C08559' });
  o.pose = (p = {}) => {
    const t = p.t || 0;
    // right hand: phone at ear (1) or on counter (0)
    const ph = p.phone ?? 0;
    const hr = lp([110, -30], [96, -360], ph);
    const er = lp([150, -110], [170, -230], ph);
    o.armR([[112, -222], er, hr]);
    tf(o.hR, { x: hr[0], y: hr[1] });
    tf(o.slR, { x: 118, y: -222, r: -20 });
    show(o.handset, ph > .05);
    tf(o.handset, { x: hr[0] - 16, y: hr[1] + 10, r: lerp(40, -8, ph), s: .9 });
    // left hand: writing (w) with jitter, or gesturing
    const wr = p.write || 0;
    const scrib = wr ? [Math.sin(t * 17) * 14 + Math.sin(t * 5) * 20, Math.cos(t * 23) * 5] : [0, 0];
    let hl = p.hL || [-60 + scrib[0], -12 + scrib[1]];
    const el2 = p.eL || [-160, -100];
    o.armL([[-112, -222], el2, hl]);
    tf(o.hL, { x: hl[0], y: hl[1] });
    tf(o.watch, { x: lerp(el2[0], hl[0], .8), y: lerp(el2[1], hl[1], .8), r: 20 });
    tf(o.slL, { x: -118, y: -222, r: 20 });
    show(o.pen, wr > 0);
    tf(o.pen, { x: hl[0] + 8, y: hl[1] - 8, r: 25 });
    o.headG.setAttribute('transform', `translate(${p.headDx || 0} ${-356 + (p.headDy || 0)}) rotate(${p.headTilt || 0})`);
    o.head.set(p.face || {});
  };
  o.pose({});
  return o;
}

// ---------- simple customers ----------
function makePerson(parent, cfg) {
  const g = G(parent);
  cut('path', { d: `M-100 -200 C-50 -216, 50 -216, 100 -200 L120 ${cfg.long ? 400 : 40} L-120 ${cfg.long ? 400 : 40}Z` }, g, cfg.cloth);
  if (cfg.dupatta) cut('path', { d: 'M-100 -200 C-60 -150, 60 -90, 110 -30 L120 10 C60 -60, -40 -120, -110 -150Z' }, g, cfg.dupatta, 5);
  const hg = G(g, { transform: 'translate(0 -300)' });
  const head = makeHead(hg, { stage: 'generic', skin: cfg.skin, hair: cfg.hair || C.hair, hairStyle: cfg.hairStyle, capColor: cfg.capColor });
  if (cfg.mustache) el('path', { d: 'M-30 50 C-16 36, 16 36, 30 50 C16 46, -16 46, -30 50Z', fill: '#2A2224' }, head.inner);
  return { g, head, hg };
}

// ---------- props ----------
function makePhone(parent) {
  const g = G(parent);
  const o = { g };
  cut('path', { d: 'M-70 0 L-56 -60 C-40 -74, 40 -74, 56 -60 L70 0Z' }, g, '#C8423B');
  el('circle', { cx: 0, cy: -34, r: 20, fill: '#F4E7D0' }, g);
  for (let i = 0; i < 8; i++) { const a = i / 8 * Math.PI * 2; el('circle', { cx: Math.cos(a) * 13, cy: -34 + Math.sin(a) * 13, r: 3, fill: '#7A2A26' }, g); }
  el('path', { d: 'M40 -10 C80 0, 70 40, 110 30', fill: 'none', stroke: '#2E2A33', 'stroke-width': 5 }, g);
  o.hs = G(g);
  cut('path', { d: 'M-66 -70 C-70 -96, -50 -100, -40 -86 L40 -86 C50 -100, 70 -96, 66 -70 L52 -66 C46 -76, 40 -76, 36 -72 L-36 -72 C-40 -76, -46 -76, -52 -66Z' }, o.hs, '#A8342E', 5);
  o.lines = G(g, { stroke: '#2B2340', 'stroke-width': 6, 'stroke-linecap': 'round', fill: 'none' });
  el('path', { d: 'M-96 -90 L-118 -108 M-104 -60 L-130 -64 M96 -90 L118 -108 M104 -60 L130 -64' }, o.lines);
  o.set = (t, ringing) => {
    if (ringing) {
      const j = Math.sin(t * 60);
      tf(o.hs, { y: -Math.abs(Math.sin(t * 30)) * 16, r: j * 6 });
      o.lines.setAttribute('opacity', (Math.sin(t * 30) > 0 ? 1 : .2));
      tf(o.g, { x: o.x, y: o.y, r: Math.sin(t * 50) * 3, s: o.s || 1 });
    } else {
      tf(o.hs, {}); o.lines.setAttribute('opacity', 0); tf(o.g, { x: o.x, y: o.y, s: o.s || 1 });
    }
  };
  return o;
}

function makeLedger(parent, color = '#6A3E7C') {
  const g = G(parent);
  const o = { g };
  o.l = G(g); o.r = G(g);
  cut('path', { d: 'M0 0 L-110 -16 L-110 40 L0 50Z' }, o.l, C.cream, 6);
  cut('path', { d: 'M0 0 L110 -16 L110 40 L0 50Z' }, o.r, C.cream, 6);
  for (let i = 0; i < 4; i++) {
    el('path', { d: `M-96 ${-4 + i * 11} L-14 ${6 + i * 11}`, stroke: '#9C8ABF', 'stroke-width': 2 }, o.l);
    el('path', { d: `M14 ${6 + i * 11} L96 ${-4 + i * 11}`, stroke: '#9C8ABF', 'stroke-width': 2 }, o.r);
  }
  el('path', { d: 'M-110 40 L0 50 L110 40 L110 48 L0 58 L-110 48Z', fill: P(color) }, g);
  return o;
}

// small critters with dot eyes
function makeCritter(parent, kind) {
  const g = G(parent);
  const o = { g, kind };
  o.legs = G(g);
  o.lL = el('path', { stroke: C.ink, 'stroke-width': 5, 'stroke-linecap': 'round', fill: 'none' }, o.legs);
  o.lR = el('path', { stroke: C.ink, 'stroke-width': 5, 'stroke-linecap': 'round', fill: 'none' }, o.legs);
  o.body = G(g);
  let eyeY = -46, legY = 0;
  if (kind === 'paper') {
    cut('path', { d: 'M-34 -100 L22 -100 L36 -86 L36 0 L-34 0Z' }, o.body, '#FFFDF5', 5);
    for (let i = 0; i < 4; i++) el('path', { d: `M-24 ${-80 + i * 14} L24 ${-80 + i * 14}`, stroke: '#8FA9C8', 'stroke-width': 3 }, o.body);
    eyeY = -30;
  } else if (kind === 'box') {
    cut('rect', { x: -48, y: -84, width: 96, height: 84, rx: 4 }, o.body, '#C89559');
    el('path', { d: 'M-48 -60 L48 -60 M0 -84 L0 -60', stroke: '#9A6A36', 'stroke-width': 4 }, o.body);
    eyeY = -34;
  } else if (kind === 'gear') {
    let d = '';
    for (let i = 0; i < 16; i++) { const a = i / 16 * Math.PI * 2, r = i % 2 ? 44 : 56; d += (i ? 'L' : 'M') + (Math.cos(a) * r).toFixed(1) + ' ' + (-50 + Math.sin(a) * r).toFixed(1); }
    o.gear = cut('path', { d: d + 'Z' }, o.body, '#3E9C95');
    eyeY = -52;
  } else if (kind === 'coin') {
    cut('circle', { cx: 0, cy: -50, r: 48 }, o.body, '#E9B43F');
    el('text', { x: 0, y: -12, 'text-anchor': 'middle', 'font-size': 30, 'font-family': 'Nunito', 'font-weight': 800, fill: '#A87414' }, o.body).textContent = '₹';
    eyeY = -64;
  } else if (kind === 'tag') {
    cut('path', { d: 'M-40 -96 L20 -96 L50 -50 L20 -4 L-40 -4Z' }, o.body, '#E77C6E');
    el('circle', { cx: 24, cy: -50, r: 8, fill: '#FBF4E4' }, o.body);
    eyeY = -54;
  } else if (kind === 'person') {
    cut('path', { d: 'M-40 0 C-40 -50, 40 -50, 40 0Z' }, o.body, '#D5664A');
    cut('circle', { cx: 0, cy: -70, r: 30 }, o.body, '#C98E62');
    el('path', { d: 'M-30 -78 C-30 -106, 30 -106, 30 -78 C20 -92, -20 -92, -30 -78Z', fill: C.hair }, o.body);
    eyeY = -68;
  } else if (kind === 'machine') {
    cut('rect', { x: -50, y: -86, width: 100, height: 86, rx: 10 }, o.body, '#7C8FA6');
    cut('rect', { x: 18, y: -120, width: 20, height: 36 }, o.body, '#5E6E84', 4);
    cut('circle', { cx: -22, cy: -22, r: 12 }, o.body, '#F2C94C', 3);
    o.puff = cut('circle', { cx: 28, cy: -140, r: 14 }, o.body, '#E6E1D6', 4);
    eyeY = -60;
  }
  o.eyes = G(g);
  el('ellipse', { cx: -13, cy: eyeY, rx: 5.5, ry: 7, fill: C.ink }, o.eyes);
  el('ellipse', { cx: 13, cy: eyeY, rx: 5.5, ry: 7, fill: C.ink }, o.eyes);
  o.smile = el('path', { d: `M-8 ${eyeY + 14} Q0 ${eyeY + 20} 8 ${eyeY + 14}`, fill: 'none', stroke: C.ink, 'stroke-width': 3.5, 'stroke-linecap': 'round', opacity: 0 }, o.eyes);
  o.set = (p = {}) => {
    const t = p.t || 0, walk = p.walk || 0;
    const a = Math.sin(t * 14) * 16 * walk;
    o.lL.setAttribute('d', `M-16 -4 L${-18 + a * .6} 22`);
    o.lR.setAttribute('d', `M16 -4 L${18 - a * .6} 22`);
    show(o.legs, !p.noLegs);
    if (o.gear) o.gear.setAttribute('transform', `rotate(${(p.spin || 0)} 0 -50)`);
    if (o.puff) { const k = (t * 1.3) % 1; o.puff.setAttribute('transform', `translate(${k * 10} ${-k * 30}) scale(${.6 + k})`); o.puff.setAttribute('opacity', 1 - k); }
    o.eyes.setAttribute('transform', `translate(${(p.lookX || 0) * 6} ${(p.lookY || 0) * 5}) scale(1 ${p.blink ? .15 : 1})`);
    o.smile.setAttribute('opacity', p.smile ? 1 : 0);
    tf(o.g, { x: p.x || 0, y: (p.y || 0) - Math.abs(Math.sin(t * 7)) * 10 * walk - (p.hop || 0), r: p.r || 0, s: p.s ?? 1, sx: (p.s ?? 1) * (p.flip ? -1 : 1) });
  };
  return o;
}

function makePlane(parent, color = '#FFFDF5') {
  const g = G(parent);
  cut('path', { d: 'M40 0 L-30 -22 L-14 0 L-30 20Z' }, g, color, 4);
  el('path', { d: 'M40 0 L-14 0', stroke: '#BFB6A6', 'stroke-width': 2 }, g);
  return g;
}
