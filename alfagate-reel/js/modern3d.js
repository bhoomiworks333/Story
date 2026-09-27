// A present-day Indian gated residential society (x = -3000): towers, internal roads laid out like the ancient
// First Street / cross street (so the top-down match cut lines up), parking, a pool, the gate with a guard cabin.
import * as THREE from 'three';
import { Acc } from './geo.js';
import { triMat } from './mat.js';
import { painted } from './tex.js';
import { rng, fbm } from './util.js';

export const MOD = new THREE.Vector3(-3000, 0, 0);

function facade() { // one tile = 6 m: two floors, two 3 m bays
  const map = painted(1024, (c, N, R) => {
    const m = N / 6;
    c.fillStyle = '#e9e1d4'; c.fillRect(0, 0, N, N);
    for (let f = 0; f < 2; f++) for (let b = 0; b < 2; b++) {
      const x = b * 3 * m, y = f * 3 * m;
      c.fillStyle = '#d9cfbf'; c.fillRect(x, y + 2.75 * m, 3 * m, 0.25 * m);             // slab band
      const g = c.createLinearGradient(0, y + 0.7 * m, 0, y + 2.4 * m);
      g.addColorStop(0, '#6f8597'); g.addColorStop(1, '#394955');
      c.fillStyle = g; c.fillRect(x + 0.5 * m, y + 0.8 * m, 2.0 * m, 1.6 * m);            // glazing
      c.fillStyle = 'rgba(255,255,255,0.25)'; c.fillRect(x + 0.5 * m, y + 0.8 * m, 2.0 * m, 0.08 * m);
      c.fillStyle = '#cfc6b8'; c.fillRect(x + 1.47 * m, y + 0.8 * m, 0.06 * m, 1.6 * m);  // mullion
      c.fillStyle = '#b9b2a6'; c.fillRect(x + 0.35 * m, y + 2.4 * m, 2.3 * m, 0.12 * m);  // sill
      if (R() < 0.35) { c.fillStyle = '#e0b37a'; c.fillRect(x + 0.6 * m, y + 1.0 * m, 0.7 * m, 1.3 * m); } // curtains
      c.strokeStyle = '#8c8c8c'; c.lineWidth = 3; c.strokeRect(x + 0.4 * m, y + 1.7 * m, 2.2 * m, 0.7 * m); // balcony rail
    }
    // monsoon stains running down from every slab and sill
    for (let i = 0; i < 70; i++) { const x = R() * N, y = R() * N, h = 40 + R() * 260; const g = c.createLinearGradient(0, y, 0, y + h);
      g.addColorStop(0, 'rgba(70,64,56,0.28)'); g.addColorStop(1, 'rgba(70,64,56,0)'); c.fillStyle = g; c.fillRect(x, y, 3 + R() * 10, h); }
  }, { seed: 43, grain: 0.07 });
  return { map, bump: painted(64, (c) => { c.fillStyle = '#808080'; c.fillRect(0, 0, 64, 64); }, { grain: 0, srgb: false }), tile: 6 };
}
function flat(col, tile, seed, extra) {
  const map = painted(512, (c, N, R) => { c.fillStyle = col; c.fillRect(0, 0, N, N); if (extra) extra(c, N, R); }, { seed, grain: 0.12 });
  return { map, bump: painted(64, (c) => { c.fillStyle = '#808080'; c.fillRect(0, 0, 64, 64); }, { grain: 0, srgb: false }), tile };
}

export function buildModern(scene) {
  const G = new THREE.Group(); G.position.copy(MOD); scene.add(G);
  const R = rng(77);
  const fac = facade(), roof = flat('#9d988e', 5, 44, (c, N, R) => { for (let i = 0; i < 40; i++) { c.fillStyle = `rgba(${60 + R() * 40},${58 + R() * 30},${50},${0.1 + R() * 0.2})`; c.beginPath(); c.ellipse(R() * N, R() * N, 20 + R() * 80, 15 + R() * 60, R() * 3, 0, 7); c.fill(); } }), asphalt = flat('#55565a', 6, 45, (c, N, R) => { for (let i = 0; i < 50; i++) { c.fillStyle = `rgba(${R() < 0.5 ? 30 : 110},${R() < 0.5 ? 30 : 105},${R() < 0.5 ? 32 : 100},0.18)`; c.beginPath(); c.ellipse(R() * N, R() * N, 10 + R() * 50, 8 + R() * 30, R() * 3, 0, 7); c.fill(); } }), grass = flat('#66704a', 8, 46, (c, N, R) => {
    for (let i = 0; i < 60; i++) { c.fillStyle = `rgba(${120 + R() * 30},${105 + R() * 20},${80},${0.15 + R() * 0.25})`; c.beginPath(); c.ellipse(R() * N, R() * N, 10 + R() * 40, 8 + R() * 30, R() * 3, 0, 7); c.fill(); }
    for (let i = 0; i < 5000; i++) { c.fillStyle = `hsl(${65 + R() * 30},${18 + R() * 18}%,${24 + R() * 16}%)`; c.fillRect(R() * N, R() * N, 2, 2); }
  }), paving = flat('#b8b0a3', 3, 47, (c, N) => { c.strokeStyle = '#9a9286'; c.lineWidth = 2; for (let i = 0; i <= N; i += N / 8) { c.beginPath(); c.moveTo(i, 0); c.lineTo(i, N); c.moveTo(0, i); c.lineTo(N, i); c.stroke(); } });
  const towerMat = triMat({ side: fac, top: roof, bumpScale: 0, roughness: 0.7, groundDark: 0.9, macroAmt: 0.15 });
  const groundMat = triMat({ side: paving, top: grass, bumpScale: 0, groundDark: 1, macroAmt: 0.4 });
  const roadMat = triMat({ side: asphalt, top: asphalt, bumpScale: 0, groundDark: 1, macroAmt: 0.3, roughness: 0.85 });
  const paveMat = triMat({ side: paving, top: paving, bumpScale: 0, groundDark: 1, macroAmt: 0.2 });
  const plain = new THREE.MeshStandardMaterial({ roughness: 0.6, vertexColors: true });
  const glass = new THREE.MeshStandardMaterial({ color: 0x1c242c, roughness: 0.15, metalness: 0.6 });

  const gg = new THREE.PlaneGeometry(1600, 1600); gg.rotateX(-Math.PI / 2);
  gg.setAttribute('color', new THREE.BufferAttribute(new Float32Array(gg.attributes.position.count * 3).fill(1), 3));
  const ground = new THREE.Mesh(gg, groundMat); ground.receiveShadow = true; G.add(ground);

  const towers = new Acc(), roads = new Acc(), pave = new Acc(), misc = new Acc(), gl = new Acc();
  const X0 = -85, X1 = 85, Z0 = -125, Z1 = 125;
  // outer city roads and neighbours so the frame edges are not empty
  roads.aabb(-500, 0, Z1 + 6, 500, 0.05, Z1 + 20).aabb(-500, 0, Z0 - 20, 500, 0.05, Z0 - 6);
  roads.aabb(X1 + 8, 0, -500, X1 + 22, 0.05, 500).aabb(X0 - 22, 0, -500, X0 - 8, 0.05, 500);
  for (let i = 0; i < 70; i++) {
    const x = (R() - 0.5) * 900, z = (R() - 0.5) * 900;
    if (x > X0 - 30 && x < X1 + 30 && z > Z0 - 30 && z < Z1 + 30) continue;
    const w = 18 + R() * 20, h = 12 + R() * 40; const t = 0.8 + R() * 0.25;
    towers.aabb(x, 0, z, x + w, h, z + w * (0.7 + R() * 0.6), [t, t, t * 0.98]);
  }
  // boundary wall and gate
  const wallT = [0.93, 0.9, 0.86];
  misc.aabb(X0, 0, Z0, X1, 2.4, Z0 + 0.3, wallT).aabb(X0, 0, Z0, X0 + 0.3, 2.4, Z1, wallT).aabb(X1 - 0.3, 0, Z0, X1, 2.4, Z1, wallT);
  misc.aabb(X0, 0, Z1 - 0.3, -7, 2.4, Z1, wallT).aabb(7, 0, Z1 - 0.3, X1, 2.4, Z1, wallT);
  misc.aabb(-8, 0, Z1 - 1, -6, 4.2, Z1 + 1, [0.85, 0.82, 0.78]).aabb(6, 0, Z1 - 1, 8, 4.2, Z1 + 1, [0.85, 0.82, 0.78]); // gate pillars
  misc.aabb(8.5, 0, Z1 - 4.5, 11.5, 2.8, Z1 - 1.5, [0.95, 0.95, 0.95]).aabb(8.3, 2.8, Z1 - 4.7, 11.7, 3.0, Z1 - 1.3, [0.3, 0.45, 0.6]); // guard cabin
  misc.aabb(-6, 1.0, Z1 - 0.05, 6, 1.15, Z1 + 0.05, [0.85, 0.15, 0.12]); // boom barrier
  // internal roads: main road (like First Street) and a cross road
  roads.aabb(-4, 0, Z0 + 5, 4, 0.04, Z1 + 6).aabb(X0 + 5, 0, -3.5, X1 - 5, 0.04, 3.5).aabb(X0 + 5, 0, Z0 + 5, X1 - 5, 0.04, Z0 + 11).aabb(X0 + 5, 0, Z0 + 5, X0 + 11, 0.04, Z1 - 5).aabb(X1 - 11, 0, Z0 + 5, X1 - 5, 0.04, Z1 - 5);
  for (let z = Z0 + 8; z < Z1; z += 6) misc.aabb(-0.08, 0.041, z, 0.08, 0.045, z + 3, [0.95, 0.95, 0.95]); // centre line
  // towers: 3 each side of the main road
  const tw = [];
  for (const sx of [-1, 1]) for (const z of [-88, -38, 38]) tw.push([sx * 38, z, 48 + Math.floor(R() * 5) * 3]);
  for (const [x, z, h] of tw) {
    pave.aabb(x - 16, 0, z - 16, x + 16, 0.08, z + 16);
    towers.aabb(x - 12, 0, z - 12, x + 12, h, z + 12);
    towers.aabb(x - 3, h, z - 3, x + 3, h + 3.5, z + 3, [0.9, 0.9, 0.9]); // lift machine room
    for (let i = 0; i < 6; i++) misc.cyl(x - 9 + (i % 3) * 2.4, h, z + 7 + Math.floor(i / 3) * 2.4, 0.95, 0.95, 1.9, 16, [0.08, 0.08, 0.09]); // black water tanks
    for (let i = 0; i < 4; i++) gl.box(x + 3 + (i % 2) * 4, h + 0.4, z - 8 + Math.floor(i / 2) * 3.4, 3.6, 0.1, 2.8, [1, 1, 1], 0);
    misc.aabb(x - 12.3, h, z - 12.3, x + 12.3, h + 1.1, z - 11.9, [0.9, 0.88, 0.84]).aabb(x - 12.3, h, z + 11.9, x + 12.3, h + 1.1, z + 12.3, [0.9, 0.88, 0.84]);
  }
  // clubhouse + pool near the gate
  towers.aabb(22, 0, 70, 52, 8, 92, [1, 0.98, 0.95]);
  pave.aabb(-60, 0, 62, -14, 0.08, 104);
  const pool = new THREE.PlaneGeometry(26, 12); pool.rotateX(-Math.PI / 2); pool.translate(-37, 0.12, 83);
  // parking: cars along the cross road and in the visitor lot
  const carCols = [[0.92, 0.92, 0.92], [0.7, 0.72, 0.74], [0.35, 0.36, 0.38], [0.12, 0.12, 0.13], [0.6, 0.1, 0.08], [0.15, 0.25, 0.45], [0.85, 0.85, 0.82]];
  const car = (x, z, rot) => {
    const c = carCols[Math.floor(R() * carCols.length)];
    misc.box(x, 0.2, z, 1.8, 0.75, 4.2, c, rot); gl.box(x, 0.95, z, 1.55, 0.5, 2.2, [1, 1, 1], rot);
  };
  for (let x = X0 + 16; x < X1 - 16; x += 2.8) { if (Math.abs(x) < 9) continue; if (R() < 0.8) car(x, -6.8, 0); if (R() < 0.8) car(x, 6.8, 0); }
  for (let z = Z0 + 18; z < Z1 - 20; z += 2.8) { if (R() < 0.7) car(X0 + 14, z, Math.PI / 2); if (R() < 0.7) car(X1 - 14, z, Math.PI / 2); }
  for (let x = 14; x < 60; x += 2.8) for (const z of [104, 111]) if (R() < 0.75) car(x, z, 0);
  // trees
  const trees = new Acc(), blob = new THREE.IcosahedronGeometry(1, 2);
  const tree = (x, z, s) => {
    trees.cyl(x, 0, z, 0.15 * s, 0.25 * s, 2.6 * s, 6, [0.3, 0.24, 0.18]);
    for (let i = 0; i < 5; i++) {
      const g = blob.clone(); const p = g.attributes.position;
      for (let j = 0; j < p.count; j++) { const v = new THREE.Vector3().fromBufferAttribute(p, j); v.multiplyScalar(0.8 + fbm(v.x * 2 + i, v.y * 2 + z, 2, 9) * 0.45); p.setXYZ(j, v.x, v.y * 0.75, v.z); }
      g.computeVertexNormals();
      const a = R() * 6.28, r = R() * 1.2 * s, k = 0.8 + R() * 0.35;
      trees.geom(g, x + Math.cos(a) * r, 3 * s + R() * s, z + Math.sin(a) * r, (1.1 + R() * 0.7) * s, 0, [0.2 * k, 0.33 * k, 0.12 * k]);
    }
  };
  for (let z = Z0 + 14; z < Z1 - 6; z += 9) { tree(-7, z + R() * 2, 1 + R() * 0.3); tree(7, z + R() * 2, 1 + R() * 0.3); }
  for (let i = 0; i < 40; i++) { const x = X0 + 4 + R() * (X1 - X0 - 8), z = Z0 + 4 + R() * (Z1 - Z0 - 8); if (Math.abs(x) < 10) continue; if (tw.some(([tx, tz]) => Math.abs(x - tx) < 18 && Math.abs(z - tz) < 18)) continue; tree(x, z, 0.9 + R() * 0.5); }

  G.add(towers.mesh(towerMat), roads.mesh(roadMat, { cast: false }), pave.mesh(paveMat, { cast: false }), misc.mesh(plain), gl.mesh(glass), trees.mesh(new THREE.MeshStandardMaterial({ roughness: 1, vertexColors: true })));
  const poolMesh = new THREE.Mesh(pool, new THREE.MeshPhysicalMaterial({ color: 0x3aa6b8, roughness: 0.08, clearcoat: 1 }));
  G.add(poolMesh);
  // one car driving in through the gate
  const mover = new THREE.Group();
  const body = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.75, 4.2), new THREE.MeshStandardMaterial({ color: 0xe8e8e8, roughness: 0.4 })); body.position.y = 0.58;
  const cab = new THREE.Mesh(new THREE.BoxGeometry(1.55, 0.5, 2.2), glass); cab.position.y = 1.2;
  mover.add(body, cab); mover.traverse((o) => { if (o.isMesh) o.castShadow = true; }); G.add(mover);
  return { group: G, update(t) { mover.position.set(-2, 0, 150 - (t - 14) * 6); } };
}
