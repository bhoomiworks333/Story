// Arena reel. Claude edits this file, never index.html.
// Times are seconds in the CUT recording. Layout: split the whole time,
// pixel-art akhada on top (1080x960), Prashant's face below (1080x960),
// one caption bar on the seam.
(function () {
  // ---------------------------------------------------------------- look
  const LW = 270, LH = 240, S = 4;            // logical pixel canvas, drawn 4x
  const C = {
    ink: '#141414', y: '#FFD600', paper: '#fffaf0', red: '#d33b2c', orange: '#e8862a', green: '#3f9a4a',
    blue: '#2f6fd6', purple: '#8e44c9', teal: '#1f9e9a',
    g1: '#8a8f98', g2: '#b7bcc4', g3: '#5d626b',
    wall: '#b4643c', wall2: '#8f4a2a', wall3: '#c97b4e',
    pit: '#c86a3f', pit2: '#a9542f', pit3: '#dc8c5b',
    leaf: '#3f7a3a', leaf2: '#5c9b48', trunk: '#6b4226', brass: '#c9a227',
  };
  const BASE = { k: '#1b1b1b', s: '#b8754a', d: '#8e5535', m: '#2a1a12', w: '#ffffff', W: '#f4f1ea', P: '#3a3a48', B: '#101010', Y: '#f2c230', O: '#b8860b', L: C.red };

  const css = `
  @font-face{font-family:PS;src:url(fonts/press-start-2p-latin-400-normal.woff2)}
  @font-face{font-family:IN;font-weight:500;src:url(fonts/inter-latin-500-normal.woff2)}
  @font-face{font-family:IN;font-weight:700;src:url(fonts/inter-latin-700-normal.woff2)}
  @font-face{font-family:IN;font-weight:800;src:url(fonts/inter-latin-800-normal.woff2)}
  @font-face{font-family:IN;font-weight:900;src:url(fonts/inter-latin-900-normal.woff2)}
  @font-face{font-family:JB;font-weight:400;src:url(fonts/jetbrains-mono-latin-400-normal.woff2)}
  @font-face{font-family:JB;font-weight:700;src:url(fonts/jetbrains-mono-latin-700-normal.woff2)}
  html,body,#video{background:#141414}
  #face.split{left:0;top:960px;width:1080px;height:960px;border-radius:0;box-shadow:none;object-position:50% 50%}
  #stage.split{height:960px;background:#141414}
  #zw{position:absolute;left:0;top:0;width:1080px;height:960px;transform-origin:50% 50%}
  #px{position:absolute;left:0;top:0;width:1080px;height:960px;image-rendering:pixelated}
  #ov,#ov2{position:absolute;left:0;top:0;width:1080px;height:960px}
  .t{position:absolute;white-space:pre;line-height:1}
  .chip{background:#141414;padding:14px 18px 8px}
  #cap{top:913px}
  #cap .pill{background:#141414;color:#fff;border-radius:14px;padding:14px 30px 16px;font-family:IN;font-weight:800;font-size:58px;letter-spacing:-0.01em;box-shadow:0 0 0 4px #141414,0 14px 30px -10px rgba(0,0,0,.6)}
  #cap .hl{background:#FFD600;color:#141414;border-radius:10px;padding:2px 14px 4px;margin:0 -8px;display:inline-block}
  #hook{top:200px;left:50px;right:50px}
  #hook .box{background:#141414;color:#fff;font-family:IN;font-weight:900;font-size:72px;white-space:nowrap;border-radius:16px;padding:30px 40px 34px;box-shadow:10px 10px 0 #FFD600;letter-spacing:-0.025em;line-height:1.08}
  #hook .y{color:#FFD600}`;
  document.head.insertAdjacentHTML('beforeend', `<style>${css}</style>`);
  ['16px PS', '500 16px IN', '700 16px IN', '800 16px IN', '900 16px IN', '400 16px JB', '700 16px JB'].forEach(f => document.fonts.load(f));

  // ---------------------------------------------------------------- helpers (own names: the engine owns clamp/prog/...)
  const cl = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const pr = (t, a, b) => cl((t - a) / (b - a));
  const eo = p => 1 - Math.pow(1 - p, 3);
  const R = Math.round;
  const bounce = p => {
    if (p >= 1) return 1; const n = 7.5625, d = 2.75; let x = p;
    if (x < 1 / d) return n * x * x;
    if (x < 2 / d) return n * (x -= 1.5 / d) * x + .75;
    if (x < 2.5 / d) return n * (x -= 2.25 / d) * x + .9375;
    return n * (x -= 2.625 / d) * x + .984375;
  };
  const rng = seed => { let s = seed >>> 0; return () => (s = (s * 1664525 + 1013904223) >>> 0) / 4294967296; };
  const Wd = i => WORDS[i].s;                 // start of spoken word i in words.js

  let X, OV, OV2;                             // canvas ctx, overlay html lists
  const rect = (x, y, w, h, c) => { X.fillStyle = c; X.fillRect(R(x), R(y), R(w), R(h)); };
  const disc = (cx, cy, r, c) => { for (let dy = -r; dy <= r; dy++) { const w = R(Math.sqrt(r * r - dy * dy)); rect(cx - w, cy + dy, 2 * w, 1, c); } };
  const ring = (cx, cy, r, th, c) => { for (let dy = -r; dy <= r; dy++) for (let dx = -r; dx <= r; dx++) { const d = Math.sqrt(dx * dx + dy * dy); if (d <= r && d > r - th) rect(cx + dx, cy + dy, 1, 1, c); } };
  function box(x, y, w, h, fill, o = {}) {      // pixel panel: hard shadow + 2px ink border
    if (o.shadow !== false) rect(x + 4, y + 4, w, h, o.sh || C.ink);
    rect(x, y, w, h, o.border || C.ink); rect(x + 2, y + 2, w - 4, h - 4, fill);
  }
  function T(x, y, s, o = {}) {               // text at logical x,y (centre by default)
    const al = o.align || 'c', tx = al === 'c' ? '-50%' : al === 'r' ? '-100%' : '0';
    let st = `left:${R(x * S)}px;top:${R(y * S)}px;font-family:${o.font || 'PS'};font-weight:${o.weight || 400};font-size:${o.size || 32}px;color:${o.color || C.ink};transform:translate(${tx},-50%) ${o.tf || ''};`;
    if (o.op != null) st += `opacity:${o.op};`;
    if (o.shadow) st += `text-shadow:${o.shadow};`;
    if (o.style) st += o.style;
    (o.layer || OV).push(`<div class="t${o.chip ? ' chip' : ''}" style="${st}">${s}</div>`);
  }
  const SHD = '5px 5px 0 #141414';

  // ---------------------------------------------------------------- sprites (12 wide)
  const SP = {
    front: ['....kkkk....', '...kkkkkk...', '...ssssss...', '...skssks...', '...smmmms...', '....ssss....', '.ssssssssss.', 'ssssssssssss',
      'ss.ssssss.ss', 'ss.ssssss.ss', 'dd.LLLLLL.dd', '...LLLLLL...', '...ss..ss...', '...ss..ss...', '...ss..ss...', '..kkk..kkk..'],
    side: ['.....kkkk...', '....kkkkkk..', '....kkssss..', '....ksssks..', '....sssmms..', '.....sssss..', '...ssssssss.', '..ssssssssss',
      '..ssssss.sss', '...sssss....', '...LLLLLL...', '...LLLLLL...', '...ss..ss...', '..ss....ss..', '..ss....ss..', '.kkk....kkk.'],
    up: ['s..........s', 's...kkkk...s', 's..kkkkkk..s', 's..ssssss..s', 's..skssks..s', 'ss.smmmms.ss', '.ss.ssss.ss.', '..ssssssss..',
      '..ssssssss..', '...ssssss...', '...LLLLLL...', '...LLLLLL...', '...ss..ss...', '...ss..ss...', '...ss..ss...', '..kkk..kkk..'],
    ref: ['....kkkk....', '...kkkkkk...', '...ssssss...', '...skssks...', '...ssmmss...', '....ssss....', '..WWWWWWWW..', '.WWWWWWWWWW.',
      '.sWWWWWWWWs.', '.sWWWWWWWWs.', '..WWWWWWWW..', '..PPPPPPPP..', '...PP..PP...', '...PP..PP...', '...PP..PP...', '..kkk..kkk..'],
    trophy: ['.YYYYYYYYYY.', 'YYYYYYYYYYYY', 'Y.YYYYYYYY.Y', 'Y.YYYYYYYY.Y', '.YYYYYYYYYY.', '..YYYYYYYY..', '...YYYYYY...', '....YYYY....',
      '.....YY.....', '.....YY.....', '...OOOOOO...', '..OOOOOOOO..'],
  };
  const greyOf = hex => { const n = parseInt(hex.slice(1), 16), r = n >> 16, g = (n >> 8) & 255, b = n & 255; const l = R(.3 * r + .59 * g + .11 * b); const v = R(l * .5 + 150 * .5); return `rgb(${v},${v},${v + 6})`; };
  function sprite(name, x, y, o = {}) {
    const rows = SP[name], sc = o.sc || 1, pal = Object.assign({}, BASE, o.pal || {});
    if (o.L) pal.L = o.L;
    const h = rows.length, w = rows[0].length;
    if (o.outline !== false) {                // 1px ink outline so bodies read against the mud
      X.fillStyle = o.grey ? '#4a4a50' : C.ink;
      for (let r = 0; r < h; r++) for (let c = 0; c < w; c++) {
        if (rows[r][c] === '.') continue;
        const cx = o.flip ? w - 1 - c : c;
        if (o.rot) X.fillRect(R(x + (h - 1 - r) * sc) - 1, R(y + cx * sc) - 1, sc + 2, sc + 2);
        else X.fillRect(R(x + cx * sc) - 1, R(y + r * sc) - 1, sc + 2, sc + 2);
      }
    }
    for (let r = 0; r < h; r++) for (let c = 0; c < w; c++) {
      const ch = rows[r][c]; if (ch === '.') continue;
      X.fillStyle = o.grey ? greyOf(pal[ch]) : pal[ch];
      const cx = o.flip ? w - 1 - c : c;
      if (o.rot) X.fillRect(R(x + (h - 1 - r) * sc), R(y + cx * sc), sc, sc);
      else X.fillRect(R(x + cx * sc), R(y + r * sc), sc, sc);
    }
    if (o.blind && !o.rot) { rect(x + 2 * sc, y + 3 * sc, 8 * sc, sc, '#101010'); rect(x + (o.flip ? 0 : 10) * sc, y + 4 * sc, 2 * sc, sc, '#101010'); }
  }

  // ---------------------------------------------------------------- the akhada (drawn once)
  let BG = null;
  function makeBG() {
    const c = document.createElement('canvas'); c.width = LW; c.height = LH;
    const keep = X; X = c.getContext('2d');
    ['#f6c07a', '#f8ca89', '#fad498', '#fbdda8'].forEach((col, i) => rect(0, i * 15, LW, 15, col));
    disc(218, 30, 13, '#fde9bd');
    // peepal tree behind the wall
    rect(30, 26, 9, 40, C.trunk); rect(24, 50, 6, 3, C.trunk);
    [[34, 18, 22, C.leaf], [16, 30, 14, C.leaf], [54, 30, 15, C.leaf], [30, 10, 13, C.leaf2], [44, 24, 11, C.leaf2], [20, 22, 9, C.leaf2]].forEach(([x, y, r, col]) => disc(x, y, r, col));
    // mud wall with brick courses
    rect(0, 56, LW, 56, C.wall); rect(0, 56, LW, 4, C.wall3);
    for (let row = 0; row < 6; row++) { const yy = 62 + row * 8; rect(0, yy + 7, LW, 1, C.wall2); for (let x = (row % 2) * 9; x < LW; x += 18) rect(x, yy, 1, 7, C.wall2); }
    // two gadas leaning on the wall
    [[236, 66], [248, 70]].forEach(([x, y]) => { rect(x, y + 6, 3, 38, C.trunk); disc(x + 1, y + 4, 6, C.brass); rect(x - 2, y + 1, 2, 2, '#e8c757'); });
    // the pit
    rect(0, 112, LW, 128, C.pit); rect(0, 112, LW, 3, C.pit2);
    const r = rng(7);
    for (let i = 0; i < 420; i++) { const x = R(r() * LW), y = 116 + R(r() * 124); rect(x, y, r() < .5 ? 2 : 1, 1, r() < .55 ? C.pit2 : C.pit3); }
    X = keep; return c;
  }
  const ground = () => X.drawImage(BG, 0, 0);
  const dim = a => rect(0, 0, LW, LH, `rgba(20,20,20,${a})`);

  // grid of 100 small wrestlers
  const gx = i => 10 + (i % 10) * 25.4, gy = i => 60 + Math.floor(i / 10) * 16;
  const PERM = (() => { const a = [...Array(100).keys()], r = rng(42); for (let i = 99; i > 0; i--) { const j = Math.floor(r() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; })();
  const TINT = i => `hsl(${(i * 37) % 360},62%,48%)`;

  // ---------------------------------------------------------------- scenes
  function graves(t, t0) {
    ground();
    [[18, .05], [107, .55], [196, 1.05]].forEach(([x, ts]) => {
      const p = eo(pr(t, t0 + ts, t0 + ts + .28)); if (p <= 0) return;
      const h = 72, base = 214, top = base - h * p;
      X.save(); X.beginPath(); X.rect(0, 0, LW, base); X.clip();
      rect(x, top + 8, 56, h - 8, C.g1); rect(x + 3, top + 4, 50, 4, C.g1); rect(x + 8, top + 1, 40, 3, C.g1); rect(x + 16, top, 24, 1, C.g1);
      rect(x, top + 8, 3, h - 8, C.g2); rect(x + 53, top + 8, 3, h - 8, C.g3); rect(x + 40, top + 30, 1, 8, C.g3); rect(x + 41, top + 38, 1, 6, C.g3);
      X.restore();
      rect(x - 6, base - 2, 68, 6, C.pit2); rect(x - 2, base - 4, 60, 3, C.pit2);
      if (p > .7) { T(x + 28, top + 24, 'RIP', { size: 40, color: '#2b2e35' }); T(x + 28, top + 48, 'BAD\nANSWER', { size: 18, color: '#2b2e35', style: 'text-align:center;line-height:1.3' }); }
    });
  }

  function chat(t) {
    ground(); dim(.35);
    box(18, 52, 234, 172, C.paper); rect(20, 54, 230, 14, '#eadcc0'); rect(20, 68, 230, 2, C.ink);
    [[26, '#d33b2c'], [33, '#e8b02a'], [40, '#3f9a4a']].forEach(([x, c]) => rect(x, 59, 4, 4, c));
    T(135, 61.5, 'CLAUDE', { size: 18, color: '#6b5b45' });
    box(104, 76, 140, 22, '#efe3cb', { shadow: false, border: '#cbb999' });
    T(238, 87.5, 'Write my pricing headline', { font: 'IN', weight: 700, size: 30, align: 'r' });
    const presses = [Wd(7), Wd(8) + .1, Wd(10)];
    const n = presses.filter(p => t >= p).length, last = n ? presses[n - 1] : -9;
    const fade = eo(pr(t, last + .06, last + .26));
    box(26, 106, 218, 54, '#ffffff', { shadow: false, border: '#cbb999' });
    T(34, 133, '"Unlock your potential with\nplans that grow with you!"', { font: 'IN', weight: 500, size: 32, align: 'l', op: n ? fade : 1, style: 'line-height:1.25' });
    const down = t - last < .14 ? 1 : 0;
    box(26, 172 + down, 108, 22, down ? C.y : '#f0e6d2', { shadow: !down });
    T(80, 184 + down, '↻ TRY AGAIN', { size: 18 });
    if (n) T(196, 183, `TRY #${n}`, { size: 30, color: C.red, tf: `scale(${1 + .25 * (1 - eo(pr(t, last, last + .18)))})` });
    if (t >= Wd(10) + .12) T(135, 133, 'SAME REPLY', { size: 40, color: C.red, tf: `rotate(-8deg) scale(${1.4 - .4 * eo(pr(t, Wd(10) + .12, Wd(10) + .3))})`, style: 'border:6px solid #d33b2c;padding:14px 18px 8px;background:rgba(255,250,240,.92)' });
  }

  function crowd(t, n, dropFrom, opts = {}) {
    for (let k = 0; k < n; k++) {
      const i = PERM[k];
      let dy = 0;
      if (dropFrom) { const ti = dropFrom(k); dy = -70 * (1 - bounce(pr(t, ti, ti + .26))); if (t < ti) continue; }
      sprite('front', gx(i), gy(i) + dy, { L: opts.tint ? TINT(i) : C.red });
    }
  }

  function versions(t) {
    ground();
    const a = Wd(11), b = Wd(16);
    const n = t < a ? 1 : Math.min(100, 1 + Math.floor(99 * Math.pow(pr(t, a, b), 1.9)));
    crowd(t, n, k => (k === 0 ? 3.62 : a + Math.pow(k / 99, 1 / 1.9) * (b - a)));
    T(135, 47, `×${n}`, { size: 56, color: C.y, chip: true });
  }

  const IMG = (src, x, y, w, h, extra = '') => OV.push(`<img src="assets/${src}" style="position:absolute;left:${R(x)}px;top:${R(y)}px;width:${w}px;height:${h}px;${extra}">`);
  function repo(t) {
    ground(); dim(.4);
    const a = Wd(18);
    if (t < a) return;
    const p = bounce(pr(t, a, a + .35)), oy = R((1 - p) * -200 / S) * S;
    X.save(); X.translate(0, oy / S);
    box(12, 56, 246, 162, '#ffffff'); rect(14, 58, 242, 14, '#eef1f4'); rect(14, 72, 242, 2, C.ink);
    [[20, '#d33b2c'], [27, '#e8b02a'], [34, '#3f9a4a']].forEach(([x, c]) => rect(x, 63, 4, 4, c));
    X.restore();
    T(135, 65 + oy / S, 'github.com/Jakeschincariol/arena-skill', { font: 'JB', weight: 400, size: 22, color: '#57606a' });
    IMG('repo-name.png', 80, 312 + oy, 660, 100);
    const sp = eo(pr(t, a + .45, a + .65));
    IMG('repo-star.png', 80, 424 + oy, 490, 120, `transform:scale(${1 + .08 * Math.sin(sp * Math.PI)});transform-origin:0 50%;outline:${sp > 0 ? 8 : 0}px solid #FFD600;outline-offset:6px;border-radius:12px`);
    IMG('repo-about-760.png', 80, 556 + oy, 700, 293);
  }

  function title(t) {
    ground();
    rect(92, 34, 86, 80, C.wall2); rect(96, 38, 78, 76, C.wall3); disc(135, 66, 24, '#3b2016'); rect(111, 66, 48, 48, '#3b2016');
    rect(92, 30, 86, 6, C.wall); [[96, C.red], [168, C.y]].forEach(([x, c]) => { rect(x, 6, 2, 26, C.trunk); rect(x + 2, 6, 12, 8, c); });
    const a = Wd(26);
    if (t >= a) {
      const p = eo(pr(t, a, a + .2)), sh = t < a + .3 ? R(Math.sin(t * 90) * 4) : 0;
      T(135 + sh / 4, 140, 'ARENA', { size: 112, color: C.y, shadow: '8px 8px 0 #141414', tf: `scale(${2 - p})`, op: cl(p * 2) });
      T(135, 176, '/arena · free Claude Code skill', { size: 20, color: '#fff', chip: true, op: eo(pr(t, a + .2, a + .4)) });
    }
  }

  function terminal(t, text, t1, t2, hiFrom) {
    rect(0, 0, LW, LH, '#1d1d22');
    box(14, 56, 242, 150, '#0d0d10', { border: '#3a3a44', sh: '#000' });
    [[22, '#ff5f57'], [30, '#febc2e'], [38, '#28c840']].forEach(([x, c]) => rect(x, 63, 4, 4, c));
    T(135, 65.5, 'claude-code — ~/startup', { font: 'JB', size: 20, color: '#8b8b96' });
    rect(16, 74, 238, 1, '#2a2a33');
    const n = R(text.length * pr(t, t1, t2)), typed = text.slice(0, n);
    let html = typed;
    if (hiFrom != null && n > hiFrom[0]) html = typed.slice(0, hiFrom[0]) + `<span style="background:#FFD600;color:#141414">${typed.slice(hiFrom[0], Math.min(n, hiFrom[1]))}</span>` + typed.slice(Math.min(n, hiFrom[1]));
    const cur = (Math.floor(t * 3) % 2 === 0 || n < text.length) ? '<span style="background:#e6e6e6;color:#e6e6e6">_</span>' : '';
    T(24, 92, `<span style="color:#d97757">&gt;</span> ${html}${cur}`, { font: 'JB', weight: 700, size: 38, color: '#f2f2f2', align: 'l', style: 'white-space:normal;width:880px;line-height:1.4;transform:translate(0,0)' });
  }

  function cards(t) {
    ground(); dim(.25);
    const a = Wd(32), split = Wd(38);
    if (t < split) {
      const p = bounce(pr(t, a, a + .3));
      const oy = (1 - p) * -150;
      box(56, 80 + oy, 158, 84, C.paper);
      T(70, 94 + oy, 'TASK', { size: 18, color: '#fff', align: 'l', style: 'background:#d33b2c;padding:8px 10px 4px' });
      T(70, 128 + oy, 'Write the headline\nfor my pricing page', { font: 'IN', weight: 800, size: 40, align: 'l', style: 'line-height:1.2' });
      return;
    }
    const p = eo(pr(t, split, split + .38));
    for (let i = 0; i < 100; i++) {
      const tx = gx(i) - 2, ty = gy(i) + 1, x = 125 + (tx - 125) * p, y = 115 + (ty - 115) * p;
      rect(x + 1, y + 1, 17, 13, C.ink); rect(x, y, 17, 13, C.ink); rect(x + 1, y + 1, 15, 11, C.paper);
      rect(x + 3, y + 4, 9, 1, '#9a8f7c'); rect(x + 3, y + 7, 11, 1, '#9a8f7c'); rect(x + 3, y + 2, 4, 1, C.red);
    }
    const s = Wd(39) + .3;
    if (t >= s) T(135, 140, 'IDENTICAL ×100', { size: 44, color: C.red, tf: `rotate(-8deg) scale(${1.5 - .5 * eo(pr(t, s, s + .16))})`, style: 'border:7px solid #d33b2c;padding:16px 20px 8px;background:rgba(255,250,240,.94)' });
  }

  function strategies(t) {
    ground();
    const list = [[Wd(41), 'REASONING', 'FIRST\nPRINCIPLES', C.blue], [Wd(43), 'WORKFLOW', 'DRAFT,\nCRITIQUE,\nREWRITE', C.green], [Wd(47), 'STRATEGY', 'EDGE CASES\nFIRST', C.purple]];
    list.forEach(([ts, kind, label, col], i) => {
      const cx = 45 + i * 90;
      sprite('up', cx - 18, 150, { sc: 3, L: col });
      if (t < ts) return;
      const p = bounce(pr(t, ts, ts + .3)), oy = (1 - p) * -120;
      box(cx - 41, 62 + oy, 82, 80, C.paper); rect(cx - 39, 64 + oy, 78, 14, col);
      T(cx, 71.5 + oy, kind, { font: 'IN', weight: 800, size: 26, color: '#fff' });
      T(cx, 110 + oy, label, { size: 22, style: 'text-align:center;line-height:1.45' });
    });
    if (t >= Wd(48)) T(135, 47, '2,160 DIFFERENT CARDS', { size: 22, color: C.y, chip: true, op: eo(pr(t, Wd(48), Wd(48) + .15)) });
  }

  function faceoff(t) {
    ground();
    const a = Wd(51), lunge = eo(pr(t, a, a + .16)) * 14 - (t > a + .16 ? eo(pr(t, a + .16, a + .5)) * 6 : 0);
    const shake = t > a + .1 && t < a + .35 ? R(Math.sin(t * 120) * 2) : 0;
    sprite('side', 34 + lunge + shake, 132, { sc: 4, L: C.blue });
    sprite('side', 188 - lunge - shake, 132, { sc: 4, L: C.red, flip: true });
    if (t < a) T(135, 150, 'VS', { size: 64, color: C.y, shadow: SHD, tf: `scale(${1 + .2 * Math.sin(t * 14)})` });
    else if (t < a + .3) { for (let k = 0; k < 8; k++) { const ang = k * Math.PI / 4; rect(135 + Math.cos(ang) * 14 - 2, 150 + Math.sin(ang) * 14 - 2, 4, 4, C.y); } }
    const tag = (ts, x0, y0, x1, y1, lvl, col, txt) => {
      if (t < ts) return; const p = eo(pr(t, ts, ts + .3));
      T(x0 + (x1 - x0) * p, y0 + (y1 - y0) * p, `<span style="background:${col};color:#fff;padding:8px 10px 4px;margin-right:12px">${lvl}</span>${txt}`,
        { size: 26, tf: `rotate(${(1 - p) * 12 * (x1 > x0 ? 1 : -1)}deg)`, style: 'background:#fffaf0;border:5px solid #141414;padding:10px 14px 6px;box-shadow:5px 5px 0 #141414' });
    };
    tag(Wd(52), 200, 130, 108, 76, 'FATAL', C.red, 'NO PROOF');
    tag(Wd(53) + .1, 70, 140, 160, 104, 'MAJOR', C.orange, 'TOO GENERIC');
  }

  function judge(t) {
    ground();
    rect(18, 160, 30, 3, C.pit2); rect(222, 160, 30, 3, C.pit2);
    sprite('front', 20, 132, { sc: 2, L: C.blue }); sprite('front', 226, 132, { sc: 2, L: C.red, flip: true });
    sprite('ref', 72, 124, { sc: 4 });
    rect(114, 150, 10, 4, BASE.s);
    const a = Wd(56);
    if (t < a) return;
    const p = bounce(pr(t, a, a + .3)), oy = (1 - p) * -60;
    box(124, 64 + oy, 110, 96, '#ffffff'); rect(126, 66 + oy, 106, 16, C.ink);
    T(179, 74.5 + oy, 'JUDGE', { size: 20, color: C.y });
    T(179, 100 + oy, 'ROUND 1', { size: 30 });
    if (t >= Wd(58)) T(179, 124 + oy, '50 BOUTS', { size: 24, color: C.red, op: eo(pr(t, Wd(58), Wd(58) + .12)) });
    if (t >= Wd(59)) T(179, 145 + oy, '100 → 50', { font: 'JB', weight: 700, size: 30, op: eo(pr(t, Wd(59), Wd(59) + .12)) });
  }

  const KO = [50, 25, 13, 7, 4, 2, 1];
  const koT = k => Wd(60) + k * (Wd(65) - Wd(60)) / 6;      // 50 on "until" ... 1 on "standing"
  function winnerScene(t, frozen) {
    ground();
    const a = Wd(65), tt = frozen ? a + .7 : t;
    const p = bounce(pr(tt, a, a + .35)), oy = (1 - p) * 30;
    sprite('up', 105, 114 + oy, { sc: 5, L: C.y });
    sprite('trophy', 111, 62 + oy, { sc: 4 });
    rect(115, 66 + oy, 4, 4, '#fff6c8');
    const r = rng(9);
    for (let i = 0; i < 46; i++) { const x = r() * LW, sp = 40 + r() * 60, y = -10 + ((tt - a) * sp + r() * 240) % 250; rect(x, y, 3, 3, [C.y, C.red, C.blue, '#fff', C.green][i % 5]); }
    T(135, 47, 'LEFT: <span style="color:#FFD600">1</span>', { size: 44, color: '#fff', chip: true, tf: `scale(${1 + .4 * (1 - eo(pr(tt, a, a + .2)))})` });
  }
  function knockout(t) {
    if (t >= Wd(65)) return winnerScene(t, false);
    ground();
    let k = -1; for (let j = 0; j < KO.length; j++) if (t >= koT(j)) k = j;
    const alive = k < 0 ? 100 : KO[k];
    for (let r = 0; r < 100; r++) {
      const i = PERM[r];
      if (r < alive) sprite('front', gx(i), gy(i), { L: TINT(i) });
      else sprite('front', gx(i) - 2, gy(i) + 4, { rot: true, grey: true, L: TINT(i) });
    }
    if (k >= 0) T(135, 47, `LEFT: ${alive}`, { size: 44, color: '#fff', chip: true, tf: `scale(${1 + .25 * (1 - eo(pr(t, koT(k), koT(k) + .12)))})` });
  }

  function freeze(t) {
    winnerScene(t, true);
    const a = Wd(66), z = 1 + .55 * eo(pr(t, a, a + .55));
    document.getElementById('zw').style.transform = `scale(${z})`;
    document.getElementById('zw').style.transformOrigin = `${135 * S}px ${98 * S}px`;
    if (t >= a) {
      const on = Math.floor((t - a) * 3.5) % 2 === 0;
      T(135, 196, '⚠ NOBODY TELLS YOU', { size: 30, color: on ? C.ink : '#fff', layer: OV2, style: `background:${on ? C.y : '#141414'};padding:16px 20px 10px;box-shadow:6px 6px 0 #141414` });
    }
  }

  function freeSkill(t) {
    ground(); dim(.3);
    const a = Wd(71), p = bounce(pr(t, a, a + .35)), sw = Math.sin((t - a) * 7) * 6 * Math.exp(-(t - a) * 2.2);
    if (t < a) return;
    X.save(); X.translate(135 * 1, 50); X.rotate(sw * Math.PI / 180 * (p)); X.translate(-135, -50);
    rect(134, 40, 2, 34 - (1 - p) * 30, C.ink);
    box(70, 74 - (1 - p) * 40, 130, 76, C.y); disc(84, 88 - (1 - p) * 40, 4, C.ink); disc(84, 88 - (1 - p) * 40, 2, C.pit);
    X.restore();
    if (t >= Wd(74)) T(138, 112, 'FREE', { size: 72, tf: `rotate(${sw}deg) scale(${1.5 - .5 * eo(pr(t, Wd(74), Wd(74) + .15))})` });
    if (t >= Wd(74) + .15) T(135, 176, 'MIT · no signup · no API key', { font: 'IN', weight: 800, size: 34, color: '#fff', chip: true });
  }

  function fullRun(t) {
    ground(); crowd(t, 100, null);
    if (t >= Wd(77)) T(135, 47, t >= Wd(80) ? 'FULL RUN: <span style="color:#FFD600">100</span>' : 'FULL RUN', { size: 40, color: '#fff', chip: true });
  }

  function gauge(t) {
    ground(); dim(.55);
    const a = Wd(82), b = Wd(84) + .1, p = eo(pr(t, a, b));
    const lvl = 1 - .93 * p, col = lvl > .5 ? C.green : lvl > .22 ? C.orange : C.red;
    T(135, 70, 'CLAUDE LIMITS', { size: 30, color: '#fff' });
    box(28, 84, 206, 50, '#2a2a2a', { border: '#f2f2f2' }); rect(234, 98, 8, 22, '#f2f2f2');
    const flash = lvl < .22 && Math.floor(t * 8) % 2 === 0;
    rect(32, 88, R(198 * lvl), 42, flash ? '#ff6b5b' : col);
    for (let x = 32; x < 230; x += 22) rect(x, 88, 1, 42, 'rgba(0,0,0,.25)');
    T(135, 162, `${R(595 * p)} CALLS`, { size: 64, color: C.y, shadow: SHD });
    if (t >= Wd(83)) T(135, 196, 'one full run of 100', { font: 'IN', weight: 800, size: 34, color: '#fff' });
  }

  function table(t) {
    ground(); dim(.35);
    const a = 27.1, p = eo(pr(t, a, a + .2)), oy = R((1 - p) * 20) * S;
    box(12, 56, 246, 162, '#ffffff');
    T(28, 72 + oy / S, 'README → What it costs', { font: 'IN', weight: 800, size: 34, color: '#57606a', align: 'l' });
    IMG('readme-cost.png', 70, 340 + oy, 940, 452);
    const hl = (ts, row, col) => { if (t < ts) return; const q = eo(pr(t, ts, ts + .15)); OV.push(`<div style="position:absolute;left:66px;top:${R(340 + oy + row * 75.6)}px;width:948px;height:76px;background:${col};mix-blend-mode:multiply;outline:6px solid #141414;opacity:${q}"></div>`); };
    hl(a + .15, 1, 'rgba(255,214,0,.85)');
    hl(27.9, 4, 'rgba(120,220,140,.7)');
  }

  function everyday(t) {
    ground(); dim(.2);
    [['EMAIL', Wd(91)], ['CAPTION', Wd(91) + .2], ['BUG FIX', Wd(92)]].forEach(([s, ts], i) => {
      if (t < ts) return;
      const p = bounce(pr(t, ts, ts + .3)), cx = 48 + i * 87, oy = (1 - p) * -100;
      box(cx - 38, 96 + oy, 76, 70, C.paper);
      if (i === 0) { rect(cx - 16, 112 + oy, 32, 20, C.ink); rect(cx - 14, 114 + oy, 28, 16, '#fff'); for (let k = 0; k < 8; k++) { rect(cx - 13 + k * 2, 115 + k + oy, 2, 1, C.ink); rect(cx + 11 - k * 2, 115 + k + oy, 2, 1, C.ink); } }
      if (i === 1) { rect(cx - 16, 112 + oy, 32, 3, C.ink); rect(cx - 16, 119 + oy, 26, 3, C.ink); rect(cx - 16, 126 + oy, 20, 3, C.ink); }
      if (i === 2) { disc(cx, 122 + oy, 9, C.green); rect(cx - 2, 108 + oy, 4, 4, C.green); for (let k = -1; k <= 1; k++) { rect(cx - 15, 120 + k * 5 + oy, 6, 2, C.ink); rect(cx + 9, 120 + k * 5 + oy, 6, 2, C.ink); } }
      T(cx, 152 + oy, s, { size: 20 });
    });
  }

  function quickRing(t) {
    ground();
    const a = Wd(96) + .02, p = eo(pr(t, a, a + .3));
    if (t < a) { crowd(t, 100, null); }
    const w = 252 - 82 * p, h = 178 - 30 * p, x = 135 - w / 2, y = 62 + (1 - p) * -4;
    for (const [dx, col] of [[0, '#f4ede0'], [3, C.red], [6, '#f4ede0']]) { rect(x + dx, y + dx, w - 2 * dx, 2, col); rect(x + dx, y + h - dx - 2, w - 2 * dx, 2, col); rect(x + dx, y + dx, 2, h - 2 * dx, col); rect(x + w - dx - 2, y + dx, 2, h - 2 * dx, col); }
    [[x, y], [x + w - 4, y], [x, y + h - 4], [x + w - 4, y + h - 4]].forEach(([px, py]) => rect(px - 2, py - 2, 8, 8, C.ink));
    if (t >= a) for (let i = 0; i < 16; i++) { const ti = a + i * .012; if (t < ti) continue; sprite('front', 135 - 64 + (i % 4) * 34 - 12 + 12, y + 8 + Math.floor(i / 4) * 34, { sc: 2, L: TINT(i * 6) }); }
    if (t >= Wd(97)) T(135, 47, t >= Wd(98) ? '<span style="color:#FFD600">16</span> AGENTS · 91 CALLS' : '<span style="color:#FFD600">16</span> AGENTS', { size: 38, color: '#fff', chip: true, tf: `scale(${1.4 - .4 * eo(pr(t, Wd(97), Wd(97) + .15))})` });
  }

  function checkMark(x, y) { [[0, 3], [1, 4], [2, 5], [3, 4], [4, 3], [5, 2], [6, 1], [7, 0]].forEach(([dx, dy]) => rect(x + dx, y + dy, 2, 2, C.green)); }
  function taskMd(t) {
    ground(); dim(.3);
    box(30, 56, 210, 156, '#ffffff'); rect(32, 58, 206, 16, '#eef1f4'); rect(32, 74, 206, 2, C.ink);
    T(40, 66.5, 'task.md', { font: 'JB', weight: 700, size: 28, align: 'l' });
    [['Goal: pricing page headline', Wd(101)], ['For: solo founders', Wd(103)], ['Rule: plain words, under 10', Wd(104)]].forEach(([s, ts], i) => {
      if (t < ts) return;
      const y = 96 + i * 26;
      checkMark(40, y - 4);
      T(56, y, s, { font: 'JB', weight: 700, size: 30, align: 'l', op: eo(pr(t, ts, ts + .12)) });
    });
    if (t >= Wd(105)) T(180, 190, 'CLEAR', { size: 30, color: C.green, tf: `rotate(-6deg) scale(${1.4 - .4 * eo(pr(t, Wd(105), Wd(105) + .15))})`, style: 'border:5px solid #3f9a4a;padding:10px 14px 4px;background:#fff' });
  }

  function blind(t) {
    ground();
    const a = Wd(108);
    box(14, 60, 120, 92, t >= a ? '#c9c9c9' : C.paper);
    rect(16, 62, 116, 12, t >= a ? '#a9a9a9' : '#eadcc0');
    T(74, 68.5, 'YOUR CHAT', { size: 16, color: t >= a ? '#6b6b6b' : C.ink });
    for (let k = 0; k < 5; k++) rect(24 + (k % 2) * 30, 82 + k * 13, 70 - (k % 2) * 30, 7, t >= a ? '#ababab' : (k % 2 ? '#efe3cb' : '#e0e6ee'));
    if (t >= a) { const p = eo(pr(t, a, a + .15)); const r = R(30 * (1.3 - .3 * p)); ring(74, 106, r, 5, C.red); for (let k = -r + 6; k < r - 6; k++) rect(74 + k * .7 - 2, 106 + k * .7 - 2, 5, 5, C.red); }
    const bt = Wd(107);
    [0, 1, 2].forEach(i => sprite('front', 146 + i * 38, 128, { sc: 3, L: [C.blue, C.green, C.purple][i], blind: t >= bt }));
  }

  function onlyTask(t) {
    ground(); dim(.62);
    const a = Wd(112);
    X.fillStyle = 'rgba(255,240,170,.22)'; X.beginPath(); X.moveTo(120, 0); X.lineTo(150, 0); X.lineTo(205, 120); X.lineTo(65, 120); X.closePath(); X.fill();
    box(80, 64, 110, 56, '#ffffff', { border: C.y, sh: '#7a6a10' });
    T(135, 80, 'task.md', { font: 'JB', weight: 700, size: 30 });
    T(135, 102, 'the only thing\nthey see', { font: 'IN', weight: 800, size: 24, style: 'text-align:center;line-height:1.2' });
    [0, 1, 2].forEach(i => {
      const x = 46 + i * 70;
      sprite('front', x, 150, { sc: 3, L: [C.blue, C.green, C.purple][i], blind: true });
      for (let k = 0; k < 6; k++) { const f = (k / 6 + (t - a) * 1.5) % 1, px = 135 + (x + 18 - 135) * f, py = 122 + (150 - 122) * f; rect(px - 1, py - 1, 2, 2, C.y); }
    });
    if (t >= a) T(135, 47, 'ONLY THE TASK', { size: 36, color: C.y, chip: true });
  }

  function link(t) {
    ground(); dim(.35);
    const a = Wd(118), p = bounce(pr(t, a, a + .3)), oy = (1 - p) * -80;
    if (t < a) return;
    [[-18, -6], [18, 6]].forEach(([dx, dy]) => { const cx = 135 + dx, cy = 108 + dy + oy; box(cx - 22, cy - 12, 44, 24, C.y, { shadow: false }); rect(cx - 14, cy - 4, 28, 8, C.pit); });
    T(135, 160 + oy / 2, 'WANT THE LINK?', { size: 34, color: '#fff', chip: true });
  }

  function comment(t) {
    ground(); dim(.35);
    const a = Wd(121) - .02;
    box(14, 64, 242, 112, '#ffffff', { shadow: true });
    T(28, 80, 'Comments', { font: 'IN', weight: 800, size: 34, align: 'l' });
    rect(22, 92, 226, 1, '#dbdbdb');
    disc(32, 110, 7, '#c9c9c9'); disc(32, 108, 3, '#9a9a9a'); rect(27, 113, 10, 3, '#9a9a9a');
    box(46, 100, 168, 22, '#ffffff', { shadow: false, border: '#dbdbdb' });
    const word = 'ARENA';
    const n = R(5 * pr(t, Wd(122) - .02, Wd(122) + .28));
    const typed = word.slice(0, n), caret = Math.floor(t * 3) % 2 ? '|' : '&nbsp;';
    T(52, 111.5, n ? `<b>${typed}</b>${n < 5 ? caret : ''}` : `<span style="color:#8e8e8e">Add a comment…</span>${caret}`, { font: 'IN', weight: 500, size: 36, align: 'l' });
    const posted = t >= Wd(123) + .05;
    T(222, 111.5, 'Post', { font: 'IN', weight: posted ? 800 : 700, size: 32, color: n === 5 ? '#0095f6' : '#b2dffc', align: 'l' });
    if (posted) T(28, 146, `<b>you</b>&nbsp;&nbsp;ARENA`, { font: 'IN', weight: 500, size: 32, align: 'l', op: eo(pr(t, Wd(123) + .05, Wd(123) + .2)) });
    const d = Wd(124);
    if (t >= d) {
      const p = bounce(pr(t, d, d + .3));
      box(70, 186 + (1 - p) * 30, 180, 30, C.y);
      T(160, 201 + (1 - p) * 30, 'DM: here’s the link →', { font: 'IN', weight: 800, size: 32 });
    }
  }

  const SCENES = [
    [0, 2.2, t => graves(t, 0)],
    [2.2, 3.62, chat],
    [3.62, 5.9, versions],
    [5.9, 7.9, repo],
    [7.9, 8.85, title],
    [8.85, 10.15, t => terminal(t, '/arena Write the headline for my pricing page', 8.95, 9.85)],
    [10.15, 12.4, cards],
    [12.4, 14.8, strategies],
    [14.8, 17.0, faceoff],
    [17.0, 18.9, judge],
    [18.9, 21.0, knockout],
    [21.0, 22.9, freeze],
    [22.9, 24.2, freeSkill],
    [24.2, 25.8, fullRun],
    [25.8, 27.1, gauge],
    [27.1, 28.5, table],
    [28.5, 29.5, everyday],
    [29.5, 30.7, t => terminal(t, '/arena --quick write the headline for my pricing page', 29.6, 30.45, [7, 14])],
    [30.7, 32.4, quickRing],
    [32.4, 34.2, taskMd],
    [34.2, 35.5, blind],
    [35.5, 37.0, onlyTask],
    [37.0, 37.88, link],
    [37.88, 40.37, comment],
    [40.37, 99, t => graves(t, 40.37)],
  ];
  window.SCENES = SCENES;

  // ---------------------------------------------------------------- captions: 2-3 words, one bar on the seam
  const PHRASES = [
    'If Claude keeps', 'giving you', 'bad answers,', 'stop asking', 'it again.', 'Make', '*100 versions', 'of it', 'compete instead.',
    "It's a free", 'skill for', 'Claude Code', 'called', '*Arena.', 'You give it', 'one task,', 'it hands', 'that exact task', 'to 100', 'sub-agents',
    'and each one', 'tackles it', 'in a', 'different way.', 'Then they', 'attack each', "other's answers.", 'A judge', 'scores every', 'round',
    'until', 'one answer is', '*left standing.', 'One thing', 'nobody tells you,', 'the skill', 'is free,', 'but the full', 'run of 100', 'makes almost',
    '*600 calls', 'on your', 'Claude limits.', 'So for', 'everyday stuff,', 'use quick mode.', "That's", '*16 agents', 'only.', 'And make', 'your task clear',
    'because', 'the agents', "*can't see your chat,", 'only the task', 'you give them.', 'Want the link?', 'Comment', "*'ARENA'", "and I'll", 'send it to you.', 'Because trust me.',
  ];
  let GROUPS = null;
  function buildGroups() {
    GROUPS = []; let i = 0;
    for (const ph of PHRASES) {
      const hl = ph[0] === '*', toks = ph.replace(/^\*/, '').split(' ');
      const ws = WORDS.slice(i, i + toks.length);
      toks.forEach((tk, j) => { if (!ws[j] || ws[j].w !== tk) throw new Error(`caption phrase "${ph}" does not match words.js at word ${i + j} (${ws[j] && ws[j].w})`); });
      GROUPS.push({ hl, ws, s: ws[0].s, e: ws[ws.length - 1].e, text: toks.join(' ') }); i += toks.length;
    }
    if (i !== WORDS.length) throw new Error(`captions cover ${i} of ${WORDS.length} words`);
  }
  function myCaptionAt(t) {
    if (!GROUPS) buildGroups();
    const k = GROUPS.findIndex((g, j) => { const nx = GROUPS[j + 1]; const end = Math.min(g.e + .4, nx ? nx.s - .03 : Infinity); return t >= g.s - .05 && t < end; });
    if (k < 0) return [];
    const g = GROUPS[k];
    return g.hl ? [{ w: `<span class="hl">${g.text}</span>`, s: g.s, e: g.e }] : g.ws;
  }
  document.addEventListener('DOMContentLoaded', () => { window.captionAt = myCaptionAt; });

  // ---------------------------------------------------------------- the one beat
  window.VIDEO = {
    fps: 30,
    duration: 41.3,       // length of cut-audio.wav
    faceFrames: 1239,     // JPGs in face/
    capWords: 3,
    hook: ['Stop re-asking Claude', 'Make <span class="y">100</span> of it fight'],
    hookEnd: 2.2,
    sfx: { bell: Wd0(49), pop: [Wd0(18), Wd0(65)], warn: Wd0(66) },   // for the sound mix
    beats: [{
      start: 0, end: 99, layout: 'split',
      html: `<div id="zw"><canvas id="px" width="${LW}" height="${LH}"></canvas><div id="ov"></div></div><div id="ov2"></div>`,
      draw(lt, el, t) {
        if (!BG) BG = makeBG();
        const cv = el.querySelector('#px'); X = cv.getContext('2d'); X.imageSmoothingEnabled = false;
        X.setTransform(1, 0, 0, 1, 0, 0); X.clearRect(0, 0, LW, LH);
        el.querySelector('#zw').style.transform = 'none';
        OV = []; OV2 = [];
        const sc = SCENES.find(s => t >= s[0] && t < s[1]) || SCENES[SCENES.length - 1];
        sc[2](t);
        el.querySelector('#ov').innerHTML = OV.join('');
        el.querySelector('#ov2').innerHTML = OV2.join('');
        // seam line between the halves
        X.setTransform(1, 0, 0, 1, 0, 0); rect(0, LH - 1, LW, 1, C.ink);
      },
    }],
  };
  function Wd0(i) { return WORDS[i].s; }
})();
