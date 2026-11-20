// "GTA 7 by Monday": a 3D low-poly skit. Every frame is a pure function of time: renderAt(t).
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

const W = 1080, H = 1920;
const DATA = await (await fetch('vo/lines.json')).json();
const LINES = DATA.lines;
const TOTAL = DATA.total;
window.TOTAL = TOTAL;

// ---------- renderer ----------
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(1);
renderer.setSize(W, H);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
document.getElementById('wrap').prepend(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color('#1a0f26');
scene.fog = new THREE.Fog('#1a0f26', 9, 22);
const camera = new THREE.PerspectiveCamera(30, W / H, 0.05, 60);

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(W / 2, H / 2), 0.45, 0.5, 0.86);
composer.addPass(bloom);
composer.addPass(new OutputPass());

// ---------- helpers ----------
const std = (color, o = {}) => new THREE.MeshStandardMaterial({ color, roughness: .75, metalness: 0, ...o });
const flat = (color, o = {}) => std(color, { flatShading: true, ...o });
const glow = (color, i = 2) => new THREE.MeshStandardMaterial({ color: '#000', emissive: color, emissiveIntensity: i });
function mesh(geo, mat, parent, pos = [0, 0, 0], rot = [0, 0, 0], scl = [1, 1, 1], shadow = true) {
  const m = new THREE.Mesh(geo, mat);
  m.position.set(...pos); m.rotation.set(...rot); m.scale.set(...scl);
  m.castShadow = shadow; m.receiveShadow = shadow;
  parent.add(m); return m;
}
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const ease = x => { x = clamp(x); return x * x * (3 - 2 * x); };
const back = x => { x = clamp(x); const c = 2.2; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
const lerp = (a, b, k) => a + (b - a) * k;
function hash(n) { const s = Math.sin(n * 127.1) * 43758.5453; return s - Math.floor(s); }

function canvasTex(w, h, draw) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  const g = c.getContext('2d'); draw(g, w, h);
  const tx = new THREE.CanvasTexture(c); tx.colorSpace = THREE.SRGBColorSpace; tx.anisotropy = 4;
  tx.userData = { c, g, draw }; return tx;
}

// ---------- room ----------
const room = new THREE.Group(); scene.add(room);
const wallMat = flat('#3a2350');
mesh(new THREE.PlaneGeometry(14, 8), wallMat, room, [0, 2.5, -2.3]);
mesh(new THREE.PlaneGeometry(14, 10), flat('#24152f'), room, [0, -0.9, 0], [-Math.PI / 2, 0, 0]);
mesh(new THREE.PlaneGeometry(8, 8), flat('#301c42'), room, [-4.2, 2.5, 0], [0, Math.PI / 2, 0]);
mesh(new THREE.PlaneGeometry(8, 8), flat('#301c42'), room, [4.2, 2.5, 0], [0, -Math.PI / 2, 0]);

// window with city
const winX = -1.3, winY = 1.75, winW = 2.2, winH = 1.9;
const frameMat = flat('#20142c');
// wall with a hole: build four panels around the window
room.remove(room.children[0]);
const wz = -2.3;
mesh(new THREE.PlaneGeometry(14, 8), wallMat, room, [0, 2.5 + 0, wz - 0.001]).visible = false;
const L = -7, R = 7, B = -1.5, T = 6.5;
const panel = (x0, x1, y0, y1) => mesh(new THREE.PlaneGeometry(x1 - x0, y1 - y0), wallMat, room, [(x0 + x1) / 2, (y0 + y1) / 2, wz]);
panel(L, winX - winW / 2, B, T); panel(winX + winW / 2, R, B, T);
panel(winX - winW / 2, winX + winW / 2, winY + winH / 2, T); panel(winX - winW / 2, winX + winW / 2, B, winY - winH / 2);
for (const [x, y, w, h] of [[winX, winY + winH / 2, winW + .12, .1], [winX, winY - winH / 2, winW + .2, .12], [winX - winW / 2, winY, .1, winH], [winX + winW / 2, winY, .1, winH], [winX, winY, .05, winH], [winX, winY + .1, winW, .05]])
  mesh(new THREE.BoxGeometry(w, h, .12), frameMat, room, [x, y, wz + .02]);

const sky = mesh(new THREE.PlaneGeometry(30, 16), new THREE.MeshBasicMaterial({ color: '#2b1250' }), room, [0, 4, -14], [0, 0, 0], [1, 1, 1], false);
sky.material.map = canvasTex(64, 256, (g, w, h) => { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, '#120a2e'); gr.addColorStop(.6, '#4b1d6b'); gr.addColorStop(1, '#a8417a'); g.fillStyle = gr; g.fillRect(0, 0, w, h); });
mesh(new THREE.SphereGeometry(.7, 24, 16), new THREE.MeshBasicMaterial({ color: '#fff3d6' }), room, [-2.2, 4.4, -12.5], [0, 0, 0], [1, 1, 1], false);
const winTex = canvasTex(128, 256, (g, w, h) => {
  g.fillStyle = '#1b1030'; g.fillRect(0, 0, w, h);
  for (let y = 6; y < h; y += 14) for (let x = 6; x < w; x += 14) {
    const r = hash(x * 3.1 + y * 7.7);
    g.fillStyle = r > .55 ? (r > .85 ? '#ffd27a' : '#ffb35c') : (r > .4 ? '#6b4fa0' : '#2a1a40');
    g.fillRect(x, y, 7, 8);
  }
});
winTex.wrapS = winTex.wrapT = THREE.RepeatWrapping;
for (let i = 0; i < 22; i++) {
  const h = 2 + hash(i) * 6, w = .7 + hash(i + 9) * 1.1, x = -6 + i * .6 + hash(i + 3) * .3, z = -7 - hash(i + 5) * 4;
  const t = winTex.clone(); t.needsUpdate = true; t.repeat.set(w, h / 2); t.offset.set(hash(i + 1), hash(i + 2));
  const m = new THREE.MeshStandardMaterial({ color: '#241638', emissive: '#ffffff', emissiveMap: t, emissiveIntensity: .75, map: t });
  mesh(new THREE.BoxGeometry(w, h, 1), m, room, [x, -1 + h / 2, z], [0, 0, 0], [1, 1, 1], false);
}

// neon strip + string lights
mesh(new THREE.CylinderGeometry(.025, .025, 4.5, 8), glow('#c14dff', 3.2), room, [1.6, 3.15, -2.2], [0, 0, 1.35], [1, 1, 1], false);
mesh(new THREE.CylinderGeometry(.02, .02, 3.0, 8), glow('#ff4fb8', 2.6), room, [-3.9, 2.9, -1.0], [Math.PI / 2, 0, 0], [1, 1, 1], false);
for (let i = 0; i < 26; i++) {
  const x = -4 + i * .32, y = 3.55 - Math.sin(i / 25 * Math.PI) * .25 - (i % 5) * .0;
  mesh(new THREE.SphereGeometry(.04, 8, 6), glow('#ffd58a', 2.4), room, [x, y, -2.2], [0, 0, 0], [1, 1, 1], false);
}

// code screen on wall
const CODE = [
  ['#c678dd', 'const '], ['#e5c07b', 'gta7'], ['#abb2bf', ' = '], ['#61afef', 'build'], ['#abb2bf', '({'], null,
  ['#abb2bf', '  budget: '], ['#98c379', '"₹500"'], ['#abb2bf', ','], null,
  ['#abb2bf', '  deadline: '], ['#98c379', '"Monday"'], ['#abb2bf', ','], null,
  ['#abb2bf', '  laptopRAM: '], ['#d19a66', '8'], ['#5c6370', ' // pray'], null,
  ['#abb2bf', '  map: '], ['#98c379', '"one street"'], ['#abb2bf', ','], null,
  ['#abb2bf', '});'], null, null,
  ['#5c6370', '// TODO: make it fun'], null,
  ['#c678dd', 'while'], ['#abb2bf', ' ('], ['#d19a66', 'true'], ['#abb2bf', ') {'], null,
  ['#abb2bf', '  '], ['#61afef', 'ship'], ['#abb2bf', '();'], null, ['#abb2bf', '}'],
];
const codeTex = canvasTex(640, 480, (g, w, h) => {
  g.fillStyle = '#16121f'; g.fillRect(0, 0, w, h);
  g.fillStyle = '#231c31'; g.fillRect(0, 0, w, 40);
  ['#ff5f57', '#febc2e', '#28c840'].forEach((c, i) => { g.fillStyle = c; g.beginPath(); g.arc(24 + i * 24, 20, 7, 0, 7); g.fill(); });
  g.fillStyle = '#8a7fa0'; g.font = '600 18px monospace'; g.fillText('build-with-prashant / gta7.js', 110, 27);
  g.font = '600 24px monospace'; let x = 24, y = 82;
  for (const tk of CODE) { if (!tk) { x = 24; y += 34; continue; } g.fillStyle = tk[0]; g.fillText(tk[1], x, y); x += g.measureText(tk[1]).width; }
});
const scr = new THREE.Group(); room.add(scr); scr.position.set(1.55, 1.75, -2.25);
mesh(new RoundedBoxGeometry(2.05, 1.58, .08, 3, .04), flat('#0e0b14'), scr);
mesh(new THREE.PlaneGeometry(1.95, 1.46), new THREE.MeshStandardMaterial({ map: codeTex, emissive: '#fff', emissiveMap: codeTex, emissiveIntensity: .85, color: '#000' }), scr, [0, 0, .045], [0, 0, 0], [1, 1, 1], false);
// sticky note
const note = canvasTex(256, 256, (g, w, h) => { g.fillStyle = '#ffe36e'; g.fillRect(0, 0, w, h); g.fillStyle = '#4a3a10'; g.font = '700 44px "Comic Sans MS", Nunito'; g.fillText('GTA 7', 50, 100); g.font = '700 34px Nunito'; g.fillText('due: Monday', 22, 170); });
mesh(new THREE.PlaneGeometry(.38, .38), new THREE.MeshStandardMaterial({ map: note, roughness: .9 }), scr, [-.86, -.55, .06], [0, 0, .12], [1, 1, 1], false);

// ---------- desk ----------
const deskY = .55;
const desk = new THREE.Group(); scene.add(desk);
mesh(new RoundedBoxGeometry(3.6, .12, 1.5, 3, .04), flat('#6b3f4a'), desk, [0, deskY - .06, .25]);
for (const x of [-1.65, 1.65]) mesh(new THREE.BoxGeometry(.1, 1.5, 1.3), flat('#4d2c37'), desk, [x, deskY - .8, .25]);
// keyboard with rgb strip
const kb = mesh(new RoundedBoxGeometry(.62, .04, .2, 2, .015), flat('#1d1626'), desk, [-.45, deskY + .02, .62], [0, .35, 0]);
const rgb = mesh(new THREE.BoxGeometry(.6, .012, .015), glow('#3cf2c8', 2.4), kb, [0, .02, .1], [0, 0, 0], [1, 1, 1], false);
// mug
const mug = new THREE.Group(); desk.add(mug); mug.position.set(-1.3, deskY, .55);
mesh(new THREE.CylinderGeometry(.08, .07, .17, 14), flat('#f2e9df'), mug, [0, .085, 0]);
mesh(new THREE.TorusGeometry(.05, .014, 6, 12), flat('#f2e9df'), mug, [.09, .09, 0], [0, 0, 0]);
mesh(new THREE.CircleGeometry(.072, 14), flat('#b07a4a'), mug, [0, .15, 0], [-Math.PI / 2, 0, 0]);
// plant
const plant = new THREE.Group(); desk.add(plant); plant.position.set(1.4, deskY, -.2);
mesh(new THREE.CylinderGeometry(.11, .08, .18, 8), flat('#d9744f'), plant, [0, .09, 0]);
for (let i = 0; i < 6; i++) mesh(new THREE.IcosahedronGeometry(.09, 0), flat('#4fae6a'), plant, [Math.cos(i) * .07, .25 + (i % 3) * .07, Math.sin(i * 2) * .06], [i, i * 2, 0], [1, 1.6, .6]);

// laptop (in front of Prashant, screen facing him)
const laptop = new THREE.Group(); desk.add(laptop);
laptop.position.set(-.6, deskY, .38); laptop.rotation.y = .38; laptop.scale.setScalar(.72);
mesh(new RoundedBoxGeometry(.62, .03, .42, 2, .012), flat('#a9a3b6'), laptop, [0, .015, 0]);
const lid = new THREE.Group(); laptop.add(lid); lid.position.set(0, .03, .2); lid.rotation.x = .25;
mesh(new RoundedBoxGeometry(.62, .42, .025, 2, .012), flat('#a9a3b6'), lid, [0, .21, 0]);
mesh(new RoundedBoxGeometry(.11, .11, .01, 2, .02), glow('#996eff', .9), lid, [0, .23, .014]);
let lapState = { p: 0 };
const lapTex = canvasTex(512, 340, (g, w, h) => {
  const p = lapState.p;
  g.fillStyle = '#f4f4f8'; g.fillRect(0, 0, w, h);
  g.fillStyle = '#dcdbe6'; g.fillRect(0, 0, w, 36);
  g.fillStyle = '#fff'; g.fillRect(60, 8, 180, 28);
  g.fillStyle = '#555'; g.font = '600 15px Nunito'; g.fillText('New Tab', 80, 28);
  g.save(); g.translate(w / 2, 150); g.rotate(p * 9);
  g.lineWidth = 12; g.strokeStyle = '#4285f4'; g.beginPath(); g.arc(0, 0, 40, 0, 4.4); g.stroke(); g.restore();
  g.fillStyle = '#333'; g.font = '800 28px Nunito'; g.textAlign = 'center';
  g.fillText('Opening Chrome…', w / 2, 240);
  g.fillStyle = '#ddd'; g.fillRect(96, 262, 320, 18);
  g.fillStyle = '#4285f4'; g.fillRect(96, 262, 320 * (.02 + .01 * p), 18);
  g.fillStyle = '#888'; g.font = '700 20px Nunito'; g.fillText('2%  ·  about 2 business days left', w / 2, 312);
});
const lapScreen = mesh(new THREE.PlaneGeometry(.58, .38), new THREE.MeshStandardMaterial({ map: lapTex, emissive: '#fff', emissiveMap: lapTex, emissiveIntensity: .42, color: '#000' }), lid, [0, .21, -.014], [0, Math.PI, 0], [1, 1, 1], false);

// ---------- Prashant ----------
const SKIN = '#c98d63', HAIR = '#1b1412', BEARD = '#3b2a22';
function buildPrashant() {
  const root = new THREE.Group();
  const body = new THREE.Group(); root.add(body);
  // torso: grey tee + navy overshirt
  mesh(new THREE.CapsuleGeometry(.27, .32, 6, 14), flat('#2d3a5c'), body, [0, .42, 0], [0, 0, 0], [1.08, 1, .78]);
  mesh(new THREE.CylinderGeometry(.13, .2, .3, 12, 1, true), flat('#8e8e96'), body, [0, .6, .07], [-.15, 0, 0], [1, 1, .6]);
  mesh(new THREE.CylinderGeometry(.075, .085, .14, 10), flat(SKIN), body, [0, .74, 0]);
  // arms resting forward onto desk
  for (const s of [-1, 1]) {
    const arm = mesh(new THREE.CapsuleGeometry(.075, .32, 4, 10), flat('#2d3a5c'), body, [s * .3, .4, .17], [1.15, 0, s * -.15]);
    mesh(new THREE.SphereGeometry(.068, 10, 8), flat(SKIN), body, [s * .26, .33, .42]);
  }
  const head = new THREE.Group(); root.add(head); head.position.set(0, 1.08, 0);
  const r = .32;
  mesh(new THREE.IcosahedronGeometry(r, 4), flat(SKIN), head, [0, 0, 0], [0, 0, 0], [1, 1.02, .97]);
  for (const s of [-1, 1]) mesh(new THREE.SphereGeometry(.06, 10, 8), flat(SKIN), head, [s * r * .97, -.02, 0], [0, 0, 0], [.6, 1, .9]);
  // hair: cap + tuft
  const hm = flat(HAIR, { roughness: .9 });
  mesh(new THREE.SphereGeometry(r * 1.07, 22, 14, 0, Math.PI * 2, 0, 1.3), hm, head, [0, .015, -.01], [-.32, 0, 0]);
  mesh(new THREE.SphereGeometry(r * 1.05, 22, 14, Math.PI * .1, Math.PI * .8, 0.9, 1.0), hm, head, [0, 0, -.02], [0, Math.PI, 0]);
  const tuft = [[-.12, .26, .17, .12], [.0, .3, .19, .14], [.12, .27, .15, .12], [.05, .33, .08, .13], [-.06, .34, .05, .12], [.17, .21, .13, .09], [-.18, .2, .14, .09]];
  for (const [x, y, z, s] of tuft) mesh(new THREE.IcosahedronGeometry(s, 1), hm, head, [x, y, z], [x * 3, y, z], [1.2, .75, 1]);
  for (const s of [-1, 1]) mesh(new THREE.IcosahedronGeometry(.09, 1), hm, head, [s * .27, .1, -.02], [0, 0, 0], [.6, 1.3, 1.2]);
  // beard + moustache (trimmed)
  const bm = flat(BEARD, { roughness: 1 });
  mesh(new THREE.SphereGeometry(r * 1.015, 26, 14, Math.PI / 2 - 1.15, 2.3, 2.08, .9), bm, head, [0, 0, 0], [0, 0, 0], [1, 1.02, .97]);
  const must = mesh(new THREE.CapsuleGeometry(.022, .09, 4, 8), bm, head, [0, -.095, r * .95], [0, 0, Math.PI / 2], [1, 1, .7]);
  // eyes
  const eyes = [], hl = [];
  for (const s of [-1, 1]) {
    const e = mesh(new THREE.SphereGeometry(.042, 14, 10), std('#100c0c', { roughness: .25 }), head, [s * .105, .015, r * .93], [0, 0, 0], [1, 1.15, .5], false);
    mesh(new THREE.SphereGeometry(.013, 8, 6), new THREE.MeshBasicMaterial({ color: '#fff' }), e, [.012, .018, .04], [0, 0, 0], [1, 1, 1], false);
    eyes.push(e);
  }
  // brows
  const brows = [];
  for (const s of [-1, 1]) brows.push(mesh(new THREE.CapsuleGeometry(.014, .055, 4, 6), hm, head, [s * .105, .12, r * .93], [0, 0, Math.PI / 2], [1, 1, .7], false));
  // glasses: rounded rect rims
  const gm = std('#151218', { roughness: .4 });
  const rim = (() => {
    const sh = new THREE.Shape(); const w = .085, h = .062, rr = .025;
    const rr_ = (p, w, h, r) => { p.moveTo(-w + r, -h); p.lineTo(w - r, -h); p.quadraticCurveTo(w, -h, w, -h + r); p.lineTo(w, h - r); p.quadraticCurveTo(w, h, w - r, h); p.lineTo(-w + r, h); p.quadraticCurveTo(-w, h, -w, h - r); p.lineTo(-w, -h + r); p.quadraticCurveTo(-w, -h, -w + r, -h); };
    rr_(sh, w, h, rr); const hole = new THREE.Path(); rr_(hole, w - .014, h - .014, rr - .01); sh.holes.push(hole);
    return new THREE.ExtrudeGeometry(sh, { depth: .012, bevelEnabled: false });
  })();
  const glasses = new THREE.Group(); head.add(glasses); glasses.position.set(0, .015, r * .99);
  for (const s of [-1, 1]) {
    mesh(rim, gm, glasses, [s * .105, 0, 0], [0, s * -.12, 0], [1, 1, 1], false);
    mesh(new THREE.BoxGeometry(.012, .012, .2), gm, glasses, [s * .19, .03, -.1], [0, s * .15, 0], [1, 1, 1], false);
  }
  mesh(new THREE.BoxGeometry(.04, .012, .012), gm, glasses, [0, .025, .006], [0, 0, 0], [1, 1, 1], false);
  // mouth: open ellipse + smile arc
  const mouth = mesh(new THREE.CircleGeometry(.04, 18), std('#4a1622', { roughness: .6 }), head, [0, -.135, r * .985], [-.25, 0, 0], [1, .3, 1], false);
  const tongue = mesh(new THREE.CircleGeometry(.025, 14), std('#e06a7a'), mouth, [0, -.018, .002], [0, 0, 0], [1, .6, 1], false);
  const smile = mesh(new THREE.TorusGeometry(.04, .009, 6, 16, Math.PI), std('#4a1622'), head, [0, -.12, r * .98], [-.25, 0, Math.PI], [1, 1, 1], false);
  // blush
  for (const s of [-1, 1]) mesh(new THREE.CircleGeometry(.035, 14), new THREE.MeshBasicMaterial({ color: '#ff7f8f', transparent: true, opacity: .35 }), head, [s * .17, -.06, r * .86], [0, s * .55, 0], [1, .65, 1], false);
  return { root, head, body, eyes, brows, mouth, smile, tongue, glasses };
}
const P = buildPrashant(); scene.add(P.root);
P.root.position.set(-.75, .1, -.15); P.root.rotation.y = .38;

// ---------- Stacky (AlfaStack-purple cube buddy) ----------
function buildStacky() {
  const root = new THREE.Group(); const bob = new THREE.Group(); root.add(bob);
  const S = .62;
  const body = mesh(new RoundedBoxGeometry(S, S * .9, S * .85, 6, .15), std('#996eff', { roughness: .55 }), bob, [0, S * .45 + .07, 0]);
  // subtle stack stripes (nod to the logo)
  for (const y of [-.12, .02]) mesh(new RoundedBoxGeometry(S * 1.005, .018, S * .855, 2, .009), std('#7f55ec', { roughness: .6 }), body, [0, y - .1, 0], [0, 0, 0], [1, 1, 1], false);
  for (const [x, z] of [[-.18, -.14], [.18, -.14], [-.18, .14], [.18, .14]]) mesh(new THREE.CapsuleGeometry(.045, .03, 4, 8), std('#7a4fe6'), bob, [x, .05, z]);
  const arms = [];
  for (const s of [-1, 1]) arms.push(mesh(new THREE.CapsuleGeometry(.045, .07, 4, 8), std('#8a60f5'), body, [s * (S / 2 + .02), -.06, .05], [0, 0, s * .5]));
  // antenna
  const ant = new THREE.Group(); body.add(ant); ant.position.set(.08, S * .45, 0);
  mesh(new THREE.CylinderGeometry(.01, .012, .14, 6), std('#5c3bb8'), ant, [0, .07, 0]);
  const bulb = mesh(new THREE.SphereGeometry(.035, 12, 8), glow('#ffd36e', 2.5), ant, [0, .16, 0], [0, 0, 0], [1, 1, 1], false);
  const face = new THREE.Group(); body.add(face); face.position.set(0, .03, S * .425 + .002);
  const black = std('#0b0910', { roughness: .2 });
  const eyes = [], flats = [], happy = [];
  for (const s of [-1, 1]) {
    const e = mesh(new THREE.CapsuleGeometry(.036, .06, 6, 12), black, face, [s * .12, .02, 0], [0, 0, 0], [1, 1, .35], false);
    mesh(new THREE.SphereGeometry(.014, 8, 6), new THREE.MeshBasicMaterial({ color: '#fff' }), e, [.012, .035, .03], [0, 0, 0], [1, 1, 1], false);
    eyes.push(e);
    flats.push(mesh(new THREE.CapsuleGeometry(.018, .07, 4, 8), black, face, [s * .12, .02, 0], [0, 0, Math.PI / 2], [1, 1, .35], false));
    happy.push(mesh(new THREE.TorusGeometry(.045, .014, 6, 16, Math.PI), black, face, [s * .12, .0, 0], [0, 0, 0], [1, 1, .4], false));
  }
  for (const s of [-1, 1]) mesh(new THREE.CircleGeometry(.045, 16), new THREE.MeshBasicMaterial({ color: '#ff8fb8', transparent: true, opacity: .45 }), face, [s * .2, -.07, .004], [0, 0, 0], [1, .6, 1], false);
  return { root, bob, body, eyes, flats, happy, arms, ant, bulb };
}
const S = buildStacky(); scene.add(S.root);
S.root.position.set(.8, deskY, .25); S.root.rotation.y = -.5;

// ---------- auto-rickshaw toy ----------
function buildAuto() {
  const g = new THREE.Group(); const k = .55;
  const gr = flat('#2fa84f'), yl = flat('#ffd23f'), bk = flat('#16121c');
  mesh(new RoundedBoxGeometry(.34 * k, .16 * k, .2 * k, 2, .03 * k), gr, g, [0, .12 * k, 0]);
  mesh(new RoundedBoxGeometry(.12 * k, .2 * k, .18 * k, 2, .04 * k), gr, g, [.17 * k, .2 * k, 0]);
  mesh(new RoundedBoxGeometry(.38 * k, .05 * k, .24 * k, 2, .02 * k), yl, g, [0, .36 * k, 0]);
  for (const [x, z] of [[-.08, -.09], [-.08, .09]]) mesh(new THREE.CylinderGeometry(.012 * k, .012 * k, .16 * k, 5), bk, g, [x * k, .28 * k, z * k]);
  mesh(new THREE.BoxGeometry(.02 * k, .1 * k, .16 * k), new THREE.MeshStandardMaterial({ color: '#bfe8ff', transparent: true, opacity: .5 }), g, [.2 * k, .3 * k, 0]);
  for (const [x, z] of [[.22, 0], [-.12, .11], [-.12, -.11]]) mesh(new THREE.CylinderGeometry(.05 * k, .05 * k, .035 * k, 12), bk, g, [x * k, .05 * k, z * k], [Math.PI / 2, 0, 0]);
  mesh(new THREE.SphereGeometry(.02 * k, 8, 6), glow('#fff6c8', 3), g, [.24 * k, .2 * k, 0], [0, 0, 0], [1, 1, 1], false);
  return g;
}
const auto = buildAuto(); scene.add(auto); auto.visible = false;
// puff for spawn
const puff = new THREE.Group(); scene.add(puff);
for (let i = 0; i < 8; i++) mesh(new THREE.IcosahedronGeometry(.05, 0), flat('#ffffff'), puff, [Math.cos(i) * .08, .02 * i % .05, Math.sin(i) * .08], [i, i, 0], [1, 1, 1], false);

// ---------- lights ----------
const hemi = new THREE.HemisphereLight('#8a6cff', '#2a1530', .65); scene.add(hemi);
const key = new THREE.SpotLight('#ffd9b8', 26, 12, .7, .6, 1.4); key.position.set(1.8, 3.4, 3.2); key.target.position.set(0, .8, 0);
key.castShadow = true; key.shadow.mapSize.set(1024, 1024); key.shadow.bias = -.0005; scene.add(key, key.target);
const rim1 = new THREE.PointLight('#d35bff', 7, 6, 1.6); rim1.position.set(1.8, 2.6, -1.6); scene.add(rim1);
const rim2 = new THREE.PointLight('#ff5fa8', 4, 6, 1.6); rim2.position.set(-3, 2.2, -.6); scene.add(rim2);
const fill = new THREE.PointLight('#7fb8ff', 2.2, 6, 1.6); fill.position.set(-1.5, 1.4, 2.5); scene.add(fill);
const screenGlow = new THREE.PointLight('#cfe0ff', 1.6, 2.2, 1.8); screenGlow.position.set(-.3, .9, .35); scene.add(screenGlow);
const lightsAll = [hemi, key, rim1, rim2, fill, screenGlow];
const baseI = lightsAll.map(l => l.intensity);

// ---------- timeline ----------
function lineAt(t) { let cur = null; for (const L of LINES) if (t >= L.start - .12) cur = L; return cur || LINES[0]; }
function speaking(t) { for (const L of LINES) if (t >= L.start && t < L.start + L.dur) return { L, k: L.env[Math.min(L.env.length - 1, Math.floor((t - L.start) * 30))] || 0 }; return null; }

// per-line expressions
const PEX = { 0: 'curious', 2: 'think', 3: 'grin', 5: 'proud', 7: 'proud', 9: 'plead', 11: 'plead', 13: 'puppy', 15: 'grin', 17: 'soft', 19: 'grin' };
const SEX = { 4: 'wide', 6: 'squint', 10: 'flat', 12: 'flat', 14: 'think', 16: 'flat', 18: 'happy', 20: 'flat' };
function exprFor(map, idx) { let e = 'neutral'; for (let i = 0; i <= idx; i++) if (map[i] !== undefined) e = map[i]; return e; }

// camera presets: [pos, target]
const head = () => P.root.localToWorld(P.head.position.clone());
function from(target, dir, dist, up = 0) { const d = new THREE.Vector3(...dir).normalize(); const t = new THREE.Vector3(...target); return [[t.x + d.x * dist, t.y + d.y * dist + up, t.z + d.z * dist], [t.x, t.y, t.z]]; }
const PH = [-.75, 1.2, -.15], SC = [.8, .86, .25];
const SH = {
  P: () => from([PH[0], PH[1] - .1, PH[2]], [.22, .12, 1], 3.0),
  Pclose: () => from([PH[0], PH[1] - .02, PH[2]], [.3, .16, 1], 2.15),
  S: () => from([SC[0] - .1, SC[1] + .04, SC[2]], [-.32, .2, 1], 2.7),
  Sclose: () => from([SC[0], SC[1] + .02, SC[2]], [-.4, .12, 1], 1.85),
  Shappy: () => from([SC[0], SC[1] + .03, SC[2]], [-.36, .15, 1], 2.05),
  wide: () => [[.05, 1.65, 5.3], [0, .95, -.2]],
  laptop: () => { const p = lapScreen.getWorldPosition(new THREE.Vector3()); const n = new THREE.Vector3(0, 0, 1).applyQuaternion(lapScreen.getWorldQuaternion(new THREE.Quaternion())); return [[p.x + n.x * .95, p.y + .16, p.z + n.z * .95], [p.x, p.y + .1, p.z]]; },
  auto: () => [[.3, 1.02, 1.5], [.14, .76, .6]],
};
const v3 = a => new THREE.Vector3(...a);

window.renderAt = function (t) {
  const L = lineAt(t);
  const idx = L.i;
  const sp = speaking(t);
  const shotStart = L.start - .12, st = t - shotStart;

  // ---- camera: shot + slow push + tiny handheld drift
  const [p0, tg] = SH[L.shot]();
  const pos = v3(p0), tgt = v3(tg);
  const dir = pos.clone().sub(tgt);
  const push = L.shot === 'wide' ? .07 : .045;
  pos.sub(dir.multiplyScalar(push * Math.min(st, 4)));
  pos.x += Math.sin(t * .7) * .012; pos.y += Math.sin(t * .9 + 1) * .008;
  // punch-in on the second "No."
  if (idx === 12) pos.lerp(tgt, .12 * back(st / .25));
  camera.position.copy(pos); camera.lookAt(tgt);
  camera.fov = 40; camera.updateProjectionMatrix();

  P.root.visible = L.shot !== 'laptop';
  // ---- Prashant
  const pSp = sp && sp.L.who === 'P' ? sp.k : 0;
  const pe = exprFor(PEX, idx);
  const blinkP = (t % 3.7) < .1 || ((t + 1.3) % 5.3) < .09;
  P.eyes.forEach((e, i) => {
    let sy = 1.15, sx = 1;
    if (pe === 'puppy') { sx = 1.25; sy = 1.4; }
    if (pe === 'think') sy = .55;
    if (pe === 'grin') sy = .9;
    if (blinkP) sy = .12;
    e.scale.set(sx, sy, .5);
    e.position.x = (i ? 1 : -1) * .105 + (pe === 'think' ? .015 : 0);
    e.position.y = .015 + (pe === 'think' ? .012 : 0);
  });
  const browUp = { curious: .02, think: -.005, grin: .018, proud: .01, plead: .025, puppy: .03, soft: .008, neutral: 0 }[pe] || 0;
  const browTilt = { curious: .15, think: -.2, plead: .35, puppy: .4, grin: -.1 }[pe] || 0;
  P.brows.forEach((b, i) => { const s = i ? 1 : -1; b.position.y = .12 + browUp + pSp * .01; b.rotation.z = Math.PI / 2 + s * browTilt; });
  const open = pSp > .08 ? .25 + pSp * 1.0 : 0;
  P.mouth.visible = open > 0; P.mouth.scale.set(.85 + pSp * .25, Math.max(.2, open), 1);
  P.smile.visible = open === 0; P.smile.scale.setScalar(['grin', 'proud', 'soft'].includes(pe) ? 1.15 : .7);
  P.smile.rotation.z = ['grin', 'proud', 'soft', 'puppy'].includes(pe) ? Math.PI : (pe === 'think' ? 0 : Math.PI);
  P.smile.position.y = pe === 'think' ? -.155 : -.12;
  const nod = Math.sin(t * 9) * pSp * .04;
  P.head.rotation.set(-.04 + nod + (pe === 'think' ? -.08 : 0), Math.sin(t * .6) * .05 + (pe === 'think' ? -.15 : 0), (pe === 'puppy' ? .14 : pe === 'curious' ? .08 : 0) + Math.sin(t * .8) * .02);
  P.body.position.y = Math.sin(t * 1.6) * .006;

  // ---- Stacky
  const sSp = sp && sp.L.who === 'S' ? sp.k : 0;
  const se = exprFor(SEX, idx);
  const blinkS = (t % 4.1) < .1 || ((t + 2.2) % 6.7) < .09;
  const showFlat = se === 'flat' || blinkS && se !== 'happy';
  S.eyes.forEach((e, i) => {
    e.visible = !showFlat && se !== 'happy';
    let sx = 1, sy = 1;
    if (se === 'wide') { const k = back((t - LINES[4].start + .1) / .3); sx = 1 + .35 * k; sy = 1 + .45 * k; }
    if (se === 'squint') { sy = .62; }
    if (se === 'think') { e.position.y = .045; e.position.x = (i ? 1 : -1) * .12 + .03; } else { e.position.y = .02; e.position.x = (i ? 1 : -1) * .12; }
    e.rotation.z = se === 'squint' ? (i ? -.35 : .35) : 0;
    e.scale.set(sx, sy, .35);
  });
  S.flats.forEach(f => f.visible = showFlat);
  S.happy.forEach(h => h.visible = se === 'happy');
  const sAge = t - (sp && sp.L.who === 'S' ? sp.L.start : 0);
  S.bob.scale.set(1 + sSp * .035, 1 - sSp * .05 + Math.sin(t * 2.2) * .008, 1 + sSp * .035);
  S.bob.position.y = Math.abs(Math.sin(t * 8)) * sSp * .02;
  S.bob.rotation.z = se === 'wide' ? .08 * Math.sin(clamp((t - LINES[4].start) / .4) * Math.PI) : (se === 'think' ? .07 : 0);
  S.bob.rotation.y = Math.sin(t * .5) * .05;
  S.arms.forEach((a, i) => a.rotation.z = (i ? 1 : -1) * (.5 + (se === 'happy' ? .9 : 0) + sSp * .3 * Math.sin(t * 10 + i)));
  S.ant.rotation.z = Math.sin(t * 3) * .12 + sSp * .2 * Math.sin(t * 13);
  S.bulb.material.emissiveIntensity = 2 + Math.sin(t * 4) * .6;

  // ---- laptop texture
  lapState.p = t; if (Math.abs(t - LINES[8].start) < 4) { const g = lapTex.userData.g; lapTex.userData.draw(g, 512, 340); lapTex.needsUpdate = true; }

  // ---- auto-rickshaw: spawns on "Shipped.", drives in left-turning circles
  const ta = t - LINES[16].start;
  auto.visible = ta > 0;
  if (ta > 0) {
    const sc = back(ta / .35);
    const ang = ta * 1.6;
    const cx = .12, cz = .62, rr = .17;
    auto.position.set(cx + Math.cos(ang) * rr, deskY + Math.abs(Math.sin(ta * 22)) * .004, cz - Math.sin(ang) * rr);
    auto.rotation.y = ang + Math.PI;
    auto.scale.setScalar(.001 + sc);
  }
  puff.visible = ta > 0 && ta < .55;
  if (puff.visible) { puff.position.set(.29, deskY + .03, .62); puff.children.forEach((c, i) => { const k = ta / .55; c.position.set(Math.cos(i * .8) * .25 * k, .05 + .08 * k * (i % 3), Math.sin(i * .8) * .25 * k); c.scale.setScalar((1 - k) * 1.4); }); }

  // ---- lights out at the end
  const off = t - (LINES[20].start + LINES[20].dur + .25);
  const lk = off > 0 ? Math.max(.06, 1 - off / .08) : 1;
  lightsAll.forEach((l, i) => l.intensity = baseI[i] * lk);
  S.bulb.material.emissiveIntensity *= off > 0 ? 1.4 : 1;

  // ---- caption
  const cap = document.getElementById('cap');
  const capL = sp ? sp.L : (t >= L.start ? L : null);
  const show = capL && t < capL.start + capL.dur + .25;
  cap.textContent = show ? capL.text : '';
  const ca = show ? clamp((t - capL.start) / .12) : 0;
  cap.style.opacity = ca; cap.style.transform = `scale(${.92 + .08 * back(ca)})`;
  cap.style.color = capL && capL.who === 'S' ? '#fff' : '#fff';

  composer.render();
};
window.ready = true;
renderAt(0.5);
