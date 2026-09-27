// Present-day close-up set (x=0, z=-6000): the security desk with the visitor register, a phone, a steel tumbler,
// the committee laptop with the accounts sheet, sticky notes. A second set (x=+3) holds the phone for the app shot.
import * as THREE from 'three';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { painted } from './tex.js';
import { makeRegister, makeSheet, drawChat, drawLock, drawApp, PH } from './screens.js';
import { range, clamp, fbm } from './util.js';

export const STUDIO = new THREE.Vector3(0, 0, -6000);
export const APPSET = new THREE.Vector3(3, 0, -6000);
export const REG_POS = new THREE.Vector3(0, 0, 0), PHONE_POS = new THREE.Vector3(0.43, 0, 0.1), LAPTOP_POS = new THREE.Vector3(-0.66, 0, -0.06);
const PAGE = { w: 0.62, h: 0.434 };

export function buildStudio(scene, icon) {
  const G = new THREE.Group(); G.position.copy(STUDIO); scene.add(G);
  const std = (o) => new THREE.MeshStandardMaterial(o);

  // desk: worn laminate
  const wood = painted(1024, (c, N, R) => {
    c.fillStyle = '#6b4a31'; c.fillRect(0, 0, N, N);
    for (let y = 0; y < N; y += 2) { const v = fbm(0, y / 40, 3, 4) * 40 - 20 + fbm(y / 7, 0, 2, 9) * 14; c.fillStyle = `rgba(${v > 0 ? 255 : 0},${v > 0 ? 220 : 0},${v > 0 ? 170 : 0},${Math.abs(v) / 180})`; c.fillRect(0, y, N, 2); }
    for (let i = 0; i < 120; i++) { c.strokeStyle = `rgba(230,210,180,${0.05 + R() * 0.1})`; c.lineWidth = 1; c.beginPath(); const x = R() * N, y = R() * N; c.moveTo(x, y); c.lineTo(x + (R() - 0.5) * 200, y + (R() - 0.5) * 30); c.stroke(); }
    for (let i = 0; i < 8; i++) { c.strokeStyle = 'rgba(40,25,15,0.12)'; c.lineWidth = 10 + R() * 20; c.beginPath(); c.arc(R() * N, R() * N, 30 + R() * 30, 0, 7); c.stroke(); } // tea rings
  }, { seed: 61, grain: 0.1 });
  wood.repeat.set(2, 1.3);
  const desk = new THREE.Mesh(new THREE.PlaneGeometry(2.6, 1.7), std({ map: wood, roughness: 0.45 })); desk.rotation.x = -Math.PI / 2; desk.position.set(-0.2, 0, -0.1); desk.receiveShadow = true; G.add(desk);
  const wallTex = painted(512, (c, N, R) => { const g = c.createLinearGradient(0, 0, 0, N); g.addColorStop(0, '#9fb3a6'); g.addColorStop(1, '#7f9486'); c.fillStyle = g; c.fillRect(0, 0, N, N);
    c.fillStyle = '#f6f1e3'; c.fillRect(N * 0.55, N * 0.25, N * 0.2, N * 0.28); c.fillStyle = '#e9d9a8'; c.fillRect(N * 0.6, N * 0.3, N * 0.1, N * 0.12); }, { seed: 62 });
  const wall = new THREE.Mesh(new THREE.PlaneGeometry(4, 2.4), std({ map: wallTex, roughness: 0.9 })); wall.position.set(0, 0.9, -0.95); G.add(wall);
  const tube = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.04, 0.04), new THREE.MeshBasicMaterial({ color: 0xffffff })); tube.position.set(-0.3, 1.8, -0.9); G.add(tube);

  // register
  const reg = makeRegister();
  const regTex = new THREE.CanvasTexture(reg.canvas); regTex.colorSpace = THREE.SRGBColorSpace; regTex.anisotropy = 8;
  const pg = new THREE.PlaneGeometry(PAGE.w, PAGE.h, 60, 4); pg.rotateX(-Math.PI / 2);
  const pp = pg.attributes.position;
  for (let i = 0; i < pp.count; i++) { const x = pp.getX(i), a = Math.abs(x) / (PAGE.w / 2); pp.setY(i, 0.021 * Math.pow(Math.sin(Math.min(1, a * 3) * Math.PI / 2), 0.6) - 0.004 * a * a); }
  pg.computeVertexNormals();
  const pages = new THREE.Mesh(pg, std({ map: regTex, roughness: 0.85, color: 0xc9c2b4 })); pages.position.copy(REG_POS).setY(0.022); pages.castShadow = pages.receiveShadow = true;
  const block = new THREE.Mesh(new THREE.BoxGeometry(PAGE.w + 0.01, 0.022, PAGE.h + 0.01), std({ color: 0xe7dfca, roughness: 0.9 })); block.position.copy(REG_POS).setY(0.011);
  const cover = new THREE.Mesh(new THREE.BoxGeometry(PAGE.w + 0.03, 0.004, PAGE.h + 0.025), std({ color: 0x5c1f1a, roughness: 0.7 })); cover.position.copy(REG_POS).setY(0.002);
  block.castShadow = block.receiveShadow = cover.receiveShadow = true;
  const regG = new THREE.Group(); regG.add(pages, block, cover); regG.rotation.y = 0.05; G.add(regG);
  // ballpoint pen (tip placed on the live entry every frame)
  const pen = new THREE.Group();
  const body = new THREE.Mesh(new THREE.CylinderGeometry(0.0042, 0.0042, 0.13, 16), std({ color: 0xdfe6ef, roughness: 0.25, transparent: true, opacity: 0.92 })); body.position.y = 0.075;
  const refill = new THREE.Mesh(new THREE.CylinderGeometry(0.0012, 0.0012, 0.12, 8), std({ color: 0x1d2a8b })); refill.position.y = 0.07;
  const cap = new THREE.Mesh(new THREE.CylinderGeometry(0.0045, 0.0045, 0.012, 16), std({ color: 0x1d2a8b, roughness: 0.4 })); cap.position.y = 0.141;
  const tipc = new THREE.Mesh(new THREE.ConeGeometry(0.0042, 0.012, 16), std({ color: 0xe0e0e0, metalness: 0.9, roughness: 0.25 })); tipc.rotation.x = Math.PI; tipc.position.y = 0.006;
  pen.add(body, refill, cap, tipc); pen.traverse((o) => { if (o.isMesh) o.castShadow = true; });
  regG.add(pen);

  // phone lying on the desk
  const phoneTexCv = document.createElement('canvas'); phoneTexCv.width = PH.W; phoneTexCv.height = PH.H;
  const phoneTex = new THREE.CanvasTexture(phoneTexCv); phoneTex.colorSpace = THREE.SRGBColorSpace; phoneTex.anisotropy = 8;
  const makePhone = (tex, env = 0.35, glow = 0.8) => {
    const g = new THREE.Group();
    const bodyM = new THREE.Mesh(new RoundedBoxGeometry(0.0745, 0.0085, 0.1605, 6, 0.0035), std({ color: 0x1b1d22, metalness: 0.7, roughness: 0.3 }));
    bodyM.position.y = 0.00425; bodyM.castShadow = true;
    const scr = new THREE.Mesh(new THREE.PlaneGeometry(0.0695, 0.1505), new THREE.MeshStandardMaterial({ color: 0x000000, emissive: 0xffffff, emissiveMap: tex, emissiveIntensity: glow, roughness: 0.12, metalness: 0, envMapIntensity: env }));
    scr.rotation.x = -Math.PI / 2; scr.position.y = 0.0093;
    const bezel = new THREE.Mesh(new RoundedBoxGeometry(0.0725, 0.0004, 0.1585, 2, 0.0005), std({ color: 0x050505, roughness: 0.1 })); bezel.position.y = 0.0084;
    g.add(bodyM, bezel, scr); g.userData.screen = scr; return g;
  };
  const phone = makePhone(phoneTex); phone.position.copy(PHONE_POS); phone.rotation.y = -0.22; G.add(phone);

  // steel tumbler with chai
  const tum = new THREE.Mesh(new THREE.LatheGeometry([[0, 0], [0.028, 0], [0.03, 0.004], [0.036, 0.09], [0.037, 0.092], [0.034, 0.092], [0.033, 0.01]].map(([r, y]) => new THREE.Vector2(r, y)), 32),
    std({ color: 0xd8d8d8, metalness: 1, roughness: 0.22, side: THREE.DoubleSide }));
  const chai = new THREE.Mesh(new THREE.CircleGeometry(0.0335, 32), std({ color: 0x9a6a3e, roughness: 0.2 })); chai.rotation.x = -Math.PI / 2; chai.position.y = 0.055;
  const tumG = new THREE.Group(); tumG.add(tum, chai); tumG.position.set(-0.3, 0, -0.22); tum.castShadow = true; G.add(tumG);

  // laptop with the accounts sheet
  const sheetTex = new THREE.CanvasTexture(makeSheet()); sheetTex.colorSpace = THREE.SRGBColorSpace; sheetTex.anisotropy = 8;
  const alu = std({ color: 0x9a9da3, metalness: 0.8, roughness: 0.35 });
  const lap = new THREE.Group();
  const base = new THREE.Mesh(new RoundedBoxGeometry(0.32, 0.014, 0.22, 3, 0.004), alu); base.position.y = 0.007; base.castShadow = true;
  const keys = new THREE.Mesh(new THREE.PlaneGeometry(0.27, 0.1), std({ color: 0x222326, roughness: 0.8 })); keys.rotation.x = -Math.PI / 2; keys.position.set(0, 0.0142, -0.02);
  const lid = new THREE.Group(); lid.position.set(0, 0.014, -0.11); lid.rotation.x = -0.28;
  const lidM = new THREE.Mesh(new RoundedBoxGeometry(0.32, 0.215, 0.006, 3, 0.003), alu); lidM.position.set(0, 0.1075, -0.003); lidM.castShadow = true;
  const lcd = new THREE.Mesh(new THREE.PlaneGeometry(0.3, 0.1875), new THREE.MeshStandardMaterial({ color: 0x000000, emissive: 0xffffff, emissiveMap: sheetTex, emissiveIntensity: 0.5, roughness: 0.2 }));
  lcd.position.set(0, 0.11, 0.0002);
  lid.add(lidM, lcd); lap.add(base, keys, lid); lap.position.copy(LAPTOP_POS); lap.rotation.y = 0.32; G.add(lap);
  // sticky notes and receipts
  const note = (txt, col, x, z, rot, seed) => {
    const t = painted(256, (c, N, R) => { c.fillStyle = col; c.fillRect(0, 0, N, N); c.fillStyle = 'rgba(0,0,0,0.06)'; c.fillRect(0, 0, N, 22);
      c.font = '34px Kalam'; c.fillStyle = '#1d2a6b'; txt.split('\n').forEach((l, i) => c.fillText(l, 16, 80 + i * 44)); }, { seed, grain: 0.05 });
    const m = new THREE.Mesh(new THREE.PlaneGeometry(0.076, 0.076), std({ map: t, roughness: 0.9 })); m.rotation.set(-Math.PI / 2, 0, rot); m.position.set(x, 0.0008 + seed * 0.00001, z); m.receiveShadow = true; G.add(m);
  };
  note('Lift B -\n3rd complaint!!', '#f7e36b', -0.52, 0.16, 0.2, 71);
  note('Plumber\n₹1,200 ??\nwho paid', '#f9b3c4', -0.42, 0.24, -0.15, 72);
  note('Tanker bill\nmissing', '#f7e36b', -0.66, 0.24, 0.05, 73);
  const rcpt = painted(256, (c, N, R) => { c.fillStyle = '#f4f2ec'; c.fillRect(0, 0, N, N); c.fillStyle = '#888'; for (let y = 30; y < N; y += 18) c.fillRect(20, y, 80 + R() * 130, 5); }, { seed: 74, grain: 0.04 });
  for (let i = 0; i < 4; i++) { const m = new THREE.Mesh(new THREE.PlaneGeometry(0.07, 0.14), std({ map: rcpt, roughness: 0.9 })); m.rotation.set(-Math.PI / 2, 0, i * 0.5 - 0.6); m.position.set(-0.25 + i * 0.03, 0.0005 + i * 0.0003, 0.2 + (i % 2) * 0.02); m.receiveShadow = true; G.add(m); }

  // ---- app set: phone upright in front of a softly lit lobby
  const A = new THREE.Group(); A.position.copy(APPSET); scene.add(A);
  const appCv = document.createElement('canvas'); appCv.width = PH.W; appCv.height = PH.H;
  const appTex = new THREE.CanvasTexture(appCv); appTex.colorSpace = THREE.SRGBColorSpace; appTex.anisotropy = 8;
  const phone2 = makePhone(appTex, 0.06, 1.0); phone2.rotation.set(Math.PI / 2 - 0.16, 0, 0); phone2.position.set(0, 0.09, 0); A.add(phone2);
  const lobby = painted(1024, (c, N, R) => {
    const g = c.createLinearGradient(0, 0, 0, N); g.addColorStop(0, '#2b2330'); g.addColorStop(0.6, '#4a3a3e'); g.addColorStop(1, '#6b5448'); c.fillStyle = g; c.fillRect(0, 0, N, N);
    for (let i = 0; i < 40; i++) { const x = R() * N, y = R() * N * 0.7, r = 20 + R() * 60; const gg = c.createRadialGradient(x, y, 0, x, y, r);
      const w = R() < 0.7 ? '255,210,150' : '190,170,255'; gg.addColorStop(0, `rgba(${w},0.55)`); gg.addColorStop(0.7, `rgba(${w},0.25)`); gg.addColorStop(1, `rgba(${w},0)`); c.fillStyle = gg; c.beginPath(); c.arc(x, y, r, 0, 7); c.fill(); }
  }, { seed: 81, grain: 0.03 });
  const bg = new THREE.Mesh(new THREE.PlaneGeometry(3.2, 2.4), new THREE.MeshBasicMaterial({ map: lobby })); bg.position.set(0, 0.5, -1.6); A.add(bg);
  const marble = painted(512, (c, N, R) => { c.fillStyle = '#e9e6e1'; c.fillRect(0, 0, N, N); for (let i = 0; i < 30; i++) { c.strokeStyle = `rgba(120,115,110,${0.05 + R() * 0.1})`; c.lineWidth = 1 + R() * 2; c.beginPath(); let x = R() * N, y = 0; c.moveTo(x, y); while (y < N) { x += (R() - 0.5) * 40; y += 20; c.lineTo(x, y); } c.stroke(); } }, { seed: 82 });
  const top = new THREE.Mesh(new THREE.PlaneGeometry(2, 1.2), std({ map: marble, roughness: 0.25 })); top.rotation.x = -Math.PI / 2; top.position.set(0, 0, -0.2); top.receiveShadow = true; A.add(top);

  const pctx = phoneTexCv.getContext('2d'), actx = appCv.getContext('2d');
  // update(t, shotId): draw screens and place the pen
  function update(t, id) {
    // writing progress over the register shot; finished afterwards
    const wu = clamp((t - 16.7) / 1.8);
    const { tip, W, H } = reg.draw(wu);
    regTex.needsUpdate = true;
    const px = (tip[0] / W - 0.5) * PAGE.w, pz = (tip[1] / H - 0.5) * PAGE.h;
    const writing = t < 18.6;
    const wob = writing ? Math.sin(t * 38) * 0.0015 : 0;
    if (writing) { pen.position.set(REG_POS.x + px + wob, 0.023 + Math.max(0, Math.sin(t * 19)) * 0.0012, REG_POS.z + pz); pen.rotation.set(-0.55, 0, -0.5); }
    else { pen.position.set(0.2, 0.026, 0.12); pen.rotation.set(Math.PI / 2, 0, 1.2); }
    // phone screen by shot
    if (id === 'chat') drawChat(pctx, 1 + (t - 18.6) * 4.2);
    else if (id === 'flood') drawLock(pctx, (t - 22.8) * 13, t);
    else if (id === 'question') {
      const on = range(t, 26.5, 26.7) * (1 - range(t, 28.6, 29.0));
      if (on > 0) drawLock(pctx, 12, t, on); else { pctx.fillStyle = '#000'; pctx.fillRect(0, 0, PH.W, PH.H); }
    } else if (id === 'register' || id === 'ledger') { pctx.fillStyle = '#000'; pctx.fillRect(0, 0, PH.W, PH.H); }
    phoneTex.needsUpdate = true;
    if (id === 'app') { drawApp(actx, t - 33.9, icon); appTex.needsUpdate = true; }
  }
  return { update, phone, phone2 };
}
