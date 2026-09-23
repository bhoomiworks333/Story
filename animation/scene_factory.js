// SCENE 6: one connected system, many moving parts.
const Factory = {
  build(parent) {
    const S = this;
    S.root = G(parent, { filter: 'url(#rough)' });
    const w = S.root;
    el('rect', { x: -10, y: -10, width: 1100, height: 1940, fill: P('#221E47', .5) }, w);
    for (let i = 0; i < 40; i++) el('circle', { cx: rnd(i * 4) * 1080, cy: rnd(i * 4 + 1) * 900, r: 2 + rnd(i + 2) * 3, fill: '#F2C94C', opacity: .8 }, w);
    el('path', { d: 'M100 170 a50 50 0 1 0 60 70 a42 42 0 1 1 -60 -70z', fill: P('#F4E7C4') }, w);
    S.slide = G(w);
    const sl = S.slide;
    // threads from the logo to each part
    S.threads = [[560, 860], [430, 1200], [960, 1040], [210, 760]].map(([x, y]) => {
      const p = el('path', { d: `M540 400 C540 560, ${x} ${y - 250}, ${x} ${y}`, fill: 'none', stroke: C.purple, 'stroke-width': 6, 'stroke-dasharray': '2 14', 'stroke-linecap': 'round' }, w);
      p.L = p.getTotalLength(); return p;
    });
    // torn hills + building
    cut('path', { d: 'M-20 1000 C200 940, 400 1010, 600 960 C800 910, 950 980, 1100 950 L1100 1940 L-20 1940Z' }, sl, '#2E2860', 6);
    const bld = G(sl);
    cut('path', { d: 'M20 1300 L20 700 L200 610 L380 700 L380 1300Z' }, bld, '#4B3F8C', 7);
    scribbleText(bld, 40, 720, 330, 560, '#C9C0F0', .18, 11, 22);
    S.windows = [];
    for (let r = 0; r < 3; r++) for (let c = 0; c < 2; c++) S.windows.push(cut('rect', { x: 80 + c * 140, y: 760 + r * 150, width: 80, height: 90, rx: 4 }, bld, '#F2C94C', 5));
    cut('rect', { x: 150, y: 560, width: 50, height: 110 }, bld, '#3A3070', 5);
    S.smoke = [0, 1, 2].map(() => cut('circle', { r: 26 }, bld, '#8F88B8', 4));
    // conveyor
    cut('rect', { x: 280, y: 1180, width: 640, height: 44, rx: 22 }, sl, '#3A3552', 6);
    S.rollers = [];
    for (let x = 310; x < 910; x += 60) S.rollers.push(el('circle', { cx: x, cy: 1202, r: 12, fill: '#8C86A8' }, sl));
    for (const x of [320, 600, 880]) cut('rect', { x: x - 10, y: 1224, width: 20, height: 120 }, sl, '#3A3552', 4);
    // boxes
    S.boxes = [0, 1, 2, 3, 4].map(i => {
      const b = G(sl);
      cut('rect', { x: -44, y: -80, width: 88, height: 80, rx: 4 }, b, '#C89559', 5);
      el('path', { d: 'M-44 -56 L44 -56 M0 -80 L0 -56', stroke: '#9A6A36', 'stroke-width': 4 }, b);
      b.face = G(b);
      el('circle', { cx: -12, cy: -30, r: 5, fill: C.ink }, b.face); el('circle', { cx: 12, cy: -30, r: 5, fill: C.ink }, b.face);
      if (i === 2) {
        el('path', { d: 'M18 -80 L28 -62 L40 -80', fill: '#6E4A26', stroke: '#6E4A26', 'stroke-width': 4 }, b);
        b.sad = el('path', { d: 'M-8 -12 Q0 -18 8 -12', fill: 'none', stroke: C.ink, 'stroke-width': 3.5, 'stroke-linecap': 'round' }, b.face);
      }
      return b;
    });
    // sensor on the belt
    S.sensor = G(sl, { transform: 'translate(430 1240)' });
    cut('rect', { x: -30, y: 0, width: 60, height: 44, rx: 8 }, S.sensor, '#7C8FA6', 5);
    S.led = el('circle', { cx: 0, cy: 20, r: 10, fill: '#7CE39A' }, S.sensor);
    S.waves = el('path', { d: 'M-40 -8 Q0 -30 40 -8 M-56 -20 Q0 -50 56 -20', fill: 'none', stroke: '#7CE39A', 'stroke-width': 4 }, S.sensor);
    // camera-eye on a pole
    S.eyeG = G(sl, { transform: 'translate(560 900)' });
    cut('rect', { x: -8, y: 0, width: 16, height: 190 }, S.eyeG, '#5E6E84', 4);
    S.beam = el('path', { d: 'M-30 20 L-110 280 L110 280 L30 20Z', fill: '#FFF3B0', opacity: .18 }, S.eyeG);
    cut('path', { d: 'M-70 0 Q0 -60 70 0 Q0 60 -70 0Z' }, S.eyeG, '#FFFDF6', 6);
    S.iris = el('circle', { cx: 0, cy: 0, r: 22, fill: C.purple }, S.eyeG);
    S.pupil = el('circle', { cx: 0, cy: 0, r: 10, fill: C.ink }, S.eyeG);
    S.lid = el('path', { fill: '#5E6E84' }, S.eyeG);
    S.bang = el('text', { x: 90, y: -30, 'font-family': 'Nunito', 'font-weight': 800, 'font-size': 90, fill: '#F2C94C' }, S.eyeG);
    S.bang.textContent = '!';
    // robot arm
    S.robot = G(sl);
    cut('rect', { x: 930, y: 1180, width: 110, height: 160, rx: 10 }, S.robot, '#5E6E84', 6);
    S.up = limb(S.robot, '#E07B39', 44);
    S.fore = limb(S.robot, '#E9955A', 36);
    S.joint = cut('circle', { r: 26 }, S.robot, '#F2C94C', 5);
    S.grip = G(S.robot);
    el('path', { d: 'M-26 0 L-26 40 M26 0 L26 40 M-30 0 L30 0', stroke: '#3A3552', 'stroke-width': 12, 'stroke-linecap': 'round' }, S.grip);
    S.rface = G(S.robot);
    cut('circle', { r: 34 }, S.rface, '#E07B39', 5);
    el('circle', { cx: -10, cy: -4, r: 5, fill: C.ink }, S.rface); el('circle', { cx: 10, cy: -4, r: 5, fill: C.ink }, S.rface);
    S.rsm = el('path', { d: 'M-8 8 Q0 14 8 8', fill: 'none', stroke: C.ink, 'stroke-width': 3 }, S.rface);
    // repair bin (front)
    S.bin = G(sl, { transform: 'translate(760 1420)' });
    cut('path', { d: 'M-80 -60 L80 -60 L66 40 L-66 40Z' }, S.bin, '#2F8C86', 6);
    el('path', { d: 'M-24 -20 l14 14 l30 -30', fill: 'none', stroke: '#FBF4E4', 'stroke-width': 8, 'stroke-linecap': 'round' }, S.bin);
    S.planes = [makePlane(w), makePlane(w)];
  },

  render(t) {
    const S = this;
    const up = E.out(seg(t, 41.2, 41.9));
    S.slide.setAttribute('transform', `translate(0 ${(1 - up) * 700})`);
    S.threads.forEach((p, i) => { const q = E.out(seg(t, 41.7 + i * .1, 42.2 + i * .1)); p.setAttribute('stroke-dashoffset', (-t * 40).toFixed(1)); p.setAttribute('opacity', q); });
    S.smoke.forEach((s, i) => { const k = ((t * .5) + i / 3) % 1; tf(s, { x: 175 + k * 40, y: 540 - k * 160, s: .5 + k }); s.setAttribute('opacity', 1 - k); });
    S.windows.forEach((wn, i) => wn.setAttribute('opacity', (Math.sin(t * 2 + i * 1.7) > -.6 ? 1 : .5)));

    // belt: moves, stops when the eye spots the dent, resumes after the robot fixes it
    const v = 130;
    const stopA = 43.1, stopB = 43.5, goA = 45.5, goB = 45.9;
    const dist = t2 => {
      // integral of velocity profile
      let d = 0; const dt = .02;
      for (let x = 41.0; x < t2; x += dt) {
        let vv = v;
        if (x > stopA) vv = v * (1 - seg(x, stopA, stopB));
        if (x > goA) vv = v * seg(x, goA, goB);
        d += vv * dt;
      }
      return d;
    };
    const D = dist(t);
    S.rollers.forEach((r, i) => r.setAttribute('transform', `rotate(${D * 3} ${310 + i * 60} 1202)`));
    const beltDent = 330 + D - 10;
    const dentPos = [t > 44.9 ? 619 : beltDent, 1180];
    // eye scanning
    const spot = t > 42.85;
    const lx = spot ? clamp((dentPos[0] - 560) / 200, -1, 1) : Math.sin(t * 3) * .8;
    S.iris.setAttribute('cx', lx * 26); S.iris.setAttribute('cy', spot ? 14 : 12);
    S.pupil.setAttribute('cx', lx * 26); S.pupil.setAttribute('cy', spot ? 14 : 12);
    const wide = spot ? 1 : .6;
    S.lid.setAttribute('d', `M-72 0 Q0 ${-60 * (1 - wide) - 62} 72 0 Q0 ${-60 * wide} -72 0Z`);
    const bangP = E.back(seg(t, 42.85, 43.1)) * (1 - seg(t, 44.2, 44.4));
    S.bang.setAttribute('opacity', clamp(bangP)); S.bang.setAttribute('transform', `translate(${90 * (1 - bangP)} 0) scale(${bangP})`);
    S.beam.setAttribute('opacity', spot && t < 44.3 ? .32 : .14);
    // sensor
    const alert = t > 42.9 && t < 45.6;
    S.led.setAttribute('fill', alert ? (Math.sin(t * 20) > 0 ? '#F2A33A' : '#F2C94C') : '#7CE39A');
    S.waves.setAttribute('stroke', alert ? '#F2A33A' : '#7CE39A');
    S.waves.setAttribute('opacity', .4 + Math.sin(t * 8) * .4);

    // messages: eye -> logo -> robot
    const legs = [[[560, 860], [540, 400], 43.0, 43.55], [[540, 400], [960, 1040], 44.0, 44.55]];
    S.planes.forEach((pl, k) => {
      const [A, B, a, b] = legs[k];
      const p = seg(t, a, b);
      show(pl, p > 0 && p < 1);
      const f = E.inOut(p);
      const x = lerp(A[0], B[0], f) + Math.sin(f * Math.PI) * 80 * (k ? 1 : -1), y = lerp(A[1], B[1], f);
      const ang = Math.atan2(B[1] - A[1], B[0] - A[0]) * 180 / Math.PI;
      tf(pl, { x, y, r: ang, s: 1.3 });
    });

    // robot IK: shoulder at (985 1100)
    const sh = [985, 1110];
    const rest = [880, 900], box = [dentPos ? dentPos[0] : 700, 1090], lift = [760, 900], bin = [760, 1300];
    let tg = rest;
    const k1 = E.inOut(seg(t, 44.5, 44.9)), k2 = E.inOut(seg(t, 44.95, 45.25)), k3 = E.inOut(seg(t, 45.25, 45.55)), k4 = E.inOut(seg(t, 45.6, 46.0));
    tg = lp(rest, [619, 1090], k1);
    if (k2 > 0) tg = lp([619, 1090], lift, k2);
    if (k3 > 0) tg = lp(lift, bin, k3);
    if (k4 > 0) tg = lp(bin, rest, k4);
    tg = [tg[0] + Math.sin(t * 2) * 6, tg[1] + Math.cos(t * 2.3) * 6];
    const L1 = 230, L2 = 220;
    const dx = tg[0] - sh[0], dy = tg[1] - sh[1];
    const d = Math.min(Math.hypot(dx, dy), L1 + L2 - 1);
    const a = Math.atan2(dy, dx);
    const cosB = (L1 * L1 + d * d - L2 * L2) / (2 * L1 * d);
    const el1 = a + Math.acos(clamp(cosB, -1, 1));
    const elbow = [sh[0] + Math.cos(el1) * L1, sh[1] + Math.sin(el1) * L1];
    const hand = [sh[0] + Math.cos(a) * d, sh[1] + Math.sin(a) * d];
    S.up([sh, elbow]); S.fore([elbow, hand]);
    tf(S.joint, { x: elbow[0], y: elbow[1] });
    tf(S.grip, { x: hand[0], y: hand[1] - 10 });
    tf(S.rface, { x: sh[0], y: sh[1] });
    S.rsm.setAttribute('d', t > 45.5 ? 'M-10 6 Q0 18 10 6' : 'M-8 8 Q0 14 8 8');
    const grabPt = t < 45.55 ? hand : [760, 1300 + seg(t, 45.55, 45.8) * 40];
    const grabT = 44.9;
    S.boxes.forEach((b, i) => {
      let x = 330 + (i - 2) * 230 + D + (-10), y = 1180;
      if (i === 2) {
        if (t > grabT) { const g = grabPt; x = g[0]; y = g[1] + 80; }
        b.sad.setAttribute('d', t > 45.6 ? 'M-8 -14 Q0 -8 8 -14' : 'M-8 -12 Q0 -18 8 -12');
      }
      const vis = x > 250 && x < 1100;
      show(b, vis || (i === 2 && t > grabT));
      tf(b, { x, y: y - Math.abs(Math.sin(D / 30 + i)) * 3 });
    });
    if (t > 45.55) show(S.boxes[2], seg(t, 45.55, 45.8) < 1);
  }
};
