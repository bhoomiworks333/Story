// Reconstructions: Mohenjo-daro lower town + citadel (origin) and the Dholavira reservoir (x = +3000).
// Grounded in the archaeology: grid of main streets, blank walls on main streets with doors on side lanes, courtyard
// houses of fired brick, brick-lined street drains with covers and open inspection points, wells, the Great Bath on a
// raised citadel mound, bullock carts. Deliberately absent: temples, palaces, horses, iron, the later Buddhist stupa.
import * as THREE from 'three';
import { Acc, potGeom } from './geo.js';
import { buildCrowd } from './figures.js';
import { triMat, waterMat } from './mat.js';
import * as TX from './tex.js';
import { rng, fbm } from './util.js';

export const DHOLA = new THREE.Vector3(3000, 0, 0);
export const STREETS = { ns: [[0, 9], [-85, 5.5], [85, 5.5]], ew: [[0, 8], [-95, 5.5], [95, 5.5]], x: [-170, 170], z: [-190, 190] };
export const DRAIN_X = 4.5 - 0.6;    // centre of the east drain of First Street
export const HERO_OPEN = [28.5, 40]; // uncovered stretch of that drain, where the close-up is shot

export function buildAncient(scene, T) {
  const R = rng(101);
  const wallMat = triMat({ side: T.brick, top: T.mud, bumpScale: 1.4 });
  const plasterMat = triMat({ side: T.mudWall, top: T.mud, bumpScale: 1.0 });
  const drainMat = triMat({ side: T.brick2, top: T.brick2, bumpScale: 1.6, groundDark: 0.85 });
  const groundMat = triMat({ side: T.earth, top: T.earth, bumpScale: 0.8, groundDark: 1, macroAmt: 0.55 });
  const darkMat = new THREE.MeshStandardMaterial({ color: 0x140d08, roughness: 1 });
  const woodMat = new THREE.MeshStandardMaterial({ color: 0x5a3b22, roughness: 0.85 });
  const potMat = new THREE.MeshStandardMaterial({ color: 0xa4502e, roughness: 0.75, vertexColors: true });
  const water = waterMat(T.waterN, { color: 0x14140e, flow: [0, 0.35], scale: 0.9, strength: 0.28, rough: 0.03, env: 1.4 });
  const G = new THREE.Group(); scene.add(G);

  // ground (2.4 km) with slight undulation far from the city
  const gg = new THREE.PlaneGeometry(2400, 2400, 120, 120); gg.rotateX(-Math.PI / 2);
  const gp = gg.attributes.position;
  for (let i = 0; i < gp.count; i++) {
    const x = gp.getX(i), z = gp.getZ(i), d = Math.max(0, Math.hypot(x * 0.8, z * 0.7) - 330);
    gp.setY(i, -0.05 + Math.min(1, d / 200) * (fbm(x / 180, z / 180, 3, 5) - 0.5) * 14);
  }
  gg.computeVertexNormals();
  const ground = new THREE.Mesh(gg, groundMat); ground.receiveShadow = true;
  ground.geometry.setAttribute('color', new THREE.BufferAttribute(new Float32Array(gp.count * 3).fill(1), 3));
  G.add(ground);

  let walls = new Acc(); const brickWalls = walls, plasterWalls = new Acc(); const dark = new Acc(), wood = new Acc(), drains = new Acc(), pots = new Acc();
  const pot = potGeom();
  const tint = () => { const l = 0.86 + R() * 0.24; return [l * (1 + (R() - 0.5) * 0.06), l, l * (1 - R() * 0.05)]; };

  // ---- blocks between streets
  const cuts = (list, lo, hi) => {
    const s = [...list].sort((a, b) => a[0] - b[0]); const out = []; let a = lo;
    for (const [c, w] of s) { out.push([a, c - w / 2]); a = c + w / 2; }
    out.push([a, hi]); return out;
  };
  const bx = cuts(STREETS.ns, STREETS.x[0], STREETS.x[1]), bz = cuts(STREETS.ew, STREETS.z[0], STREETS.z[1]);
  const onMain = (x0, x1, z0, z1) => ({ // which lot edges face a main street (no doors there)
    w: STREETS.ns.some(([c, w]) => Math.abs(x0 - (c + w / 2)) < 0.1), e: STREETS.ns.some(([c, w]) => Math.abs(x1 - (c - w / 2)) < 0.1),
    n: STREETS.ew.some(([c, w]) => Math.abs(z0 - (c + w / 2)) < 0.1), s: STREETS.ew.some(([c, w]) => Math.abs(z1 - (c - w / 2)) < 0.1),
  });

  function house(x0, x1, z0, z1) {
    const w = x1 - x0, d = z1 - z0, t = tint();
    walls = R() < 0.28 ? plasterWalls : brickWalls;
    const main = onMain(x0, x1, z0, z1);
    if (R() < 0.05) { // open work yard with a well
      walls.aabb(x0, 0, z0, x1, 1.6, z0 + 0.5, t).aabb(x0, 0, z1 - 0.5, x1, 1.6, z1, t);
      well((x0 + x1) / 2, (z0 + z1) / 2); return;
    }
    const H = () => (R() < 0.5 ? 3.6 : 6.8) + (R() - 0.5) * 0.4;
    const rd = 3 + R() * 1.2;
    const strips = (w < 9.5 || d < 9.5)
      ? [[x0, z0, x1, z1, H()]]
      : [[x0, z0, x1, z0 + rd, H()], [x0, z1 - rd, x1, z1, H()], [x0, z0 + rd, x0 + rd, z1 - rd, H()], [x1 - rd, z0 + rd, x1, z1 - rd, H()]];
    for (const [a, b, c, e, h] of strips) {
      walls.aabb(a, 0, b, c, h, e, t);
      // parapet along the strip's outer edges
      const p = 0.45, k = 0.3;
      walls.aabb(a, h, b, c, h + p, b + k, t).aabb(a, h, e - k, c, h + p, e, t);
      walls.aabb(a, h, b, a + k, h + p, e, t).aabb(c - k, h, b, c, h + p, e, t);
      if (R() < 0.12) walls.aabb(a + 0.6, h, b + 0.6, a + 2.8, h + 2.3, b + 2.6, t); // stair head room on the roof
      if (R() < 0.35) pots.geom(pot, a + 1 + R() * (c - a - 2), h, b + 1 + R() * (e - b - 2), 0.5 + R() * 0.3, 0, [1, 0.9 + R() * 0.2, 0.9]);
    }
    if (strips.length === 4) {
      walls.aabb(x0 + rd, 0, z0 + rd, x1 - rd, 0.06, z1 - rd, t); // courtyard floor
      if (R() < 0.3) well(x0 + rd + 1.2, z0 + rd + 1.2);
      for (let i = 0; i < 3; i++) if (R() < 0.6) pots.geom(pot, x0 + rd + 0.6 + R() * (w - 2 * rd - 1.2), 0.06, z0 + rd + 0.6 + R() * (d - 2 * rd - 1.2), 0.55 + R() * 0.3, 0, [1, 0.9, 0.85]);
    }
    // one door on a lane-facing side (never on a main street), windows sparingly
    const sides = ['n', 's', 'e', 'w'].filter((s) => !main[s]);
    const side = sides[Math.floor(R() * sides.length)] || 'n';
    const along = (s) => (s === 'n' || s === 's' ? [x0 + 1.5, x1 - 1.5] : [z0 + 1.5, z1 - 1.5]);
    const [lo, hi] = along(side); const u = lo + R() * Math.max(0, hi - lo);
    const dw = 1.0, dh = 2.0, pr = 0.04;
    if (side === 'n') { dark.aabb(u - dw / 2, 0, z0 - pr, u + dw / 2, dh, z0 + 0.01); wood.aabb(u - 0.8, dh, z0 - 0.1, u + 0.8, dh + 0.16, z0 + 0.02); }
    if (side === 's') { dark.aabb(u - dw / 2, 0, z1 - 0.01, u + dw / 2, dh, z1 + pr); wood.aabb(u - 0.8, dh, z1 - 0.02, u + 0.8, dh + 0.16, z1 + 0.1); }
    if (side === 'w') { dark.aabb(x0 - pr, 0, u - dw / 2, x0 + 0.01, dh, u + dw / 2); wood.aabb(x0 - 0.1, dh, u - 0.8, x0 + 0.02, dh + 0.16, u + 0.8); }
    if (side === 'e') { dark.aabb(x1 - 0.01, 0, u - dw / 2, x1 + pr, dh, u + dw / 2); wood.aabb(x1 - 0.02, dh, u - 0.8, x1 + 0.1, dh + 0.16, u + 0.8); }
    if (R() < 0.4) { // small high window slits
      const y = 2.7 + R() * 2; const s2 = sides[Math.floor(R() * sides.length)] || 'n';
      const [l2, h2] = along(s2); const v = l2 + R() * Math.max(0, h2 - l2);
      if (s2 === 'n') dark.aabb(v - 0.25, y, z0 - pr, v + 0.25, y + 0.35, z0 + 0.01);
      if (s2 === 's') dark.aabb(v - 0.25, y, z1 - 0.01, v + 0.25, y + 0.35, z1 + pr);
      if (s2 === 'w') dark.aabb(x0 - pr, y, v - 0.25, x0 + 0.01, y + 0.35, v + 0.25);
      if (s2 === 'e') dark.aabb(x1 - 0.01, y, v - 0.25, x1 + pr, y + 0.35, v + 0.25);
    }
  }
  function well(x, z) {
    walls.cyl(x, 0, z, 0.75, 0.8, 0.75, 20, [0.95, 0.95, 0.95], false);
    dark.cyl(x, 0.76, z, 0.55, 0.55, 0.01, 20);
  }
  function split(x0, x1, z0, z1, depth) {
    const w = x1 - x0, d = z1 - z0;
    if ((w < 17 && d < 17) || depth > 7) { house(x0, x1, z0, z1); return; }
    const lane = depth < 2 ? 3 : depth < 3 ? 2.2 : 0; // lanes between the first subdivisions, party walls deeper down
    if (w >= d) { const m = x0 + w * (0.38 + R() * 0.24); split(x0, m - lane / 2, z0, z1, depth + 1); split(m + lane / 2, x1, z0, z1, depth + 1); }
    else { const m = z0 + d * (0.38 + R() * 0.24); split(x0, x1, z0, m - lane / 2, depth + 1); split(x0, x1, m + lane / 2, z1, depth + 1); }
  }
  for (const [x0, x1] of bx) for (const [z0, z1] of bz) split(x0, x1, z0, z1, 0);
  walls = brickWalls;

  // ---- street drains along both sides of the main streets, with covers and open inspection points
  const waterParts = [];
  function drainLine(axis, c, a0, a1) {
    // axis 'z': runs along z at x=c
    const cw = 0.45, kw = 0.25, kh = 0.3;
    const B = (u0, u1, v0, v1, y0, y1, tt) => axis === 'z' ? drains.aabb(v0, y0, u0, v1, y1, u1, tt) : drains.aabb(u0, y0, v0, u1, y1, v1, tt);
    B(a0, a1, c - cw / 2 - kw, c - cw / 2, -0.05, kh, [1, 1, 1]);
    B(a0, a1, c + cw / 2, c + cw / 2 + kw, -0.05, kh, [1, 1, 1]);
    B(a0, a1, c - cw / 2, c + cw / 2, -0.05, 0.04, [0.8, 0.8, 0.8]);
    for (let u = a0; u < a1; u += 0.62) {
      const heroOpen = axis === 'z' && Math.abs(c - DRAIN_X) < 0.01 && u > HERO_OPEN[0] && u < HERO_OPEN[1];
      if (heroOpen || ((u - a0) % 14 < 1.3 && u - a0 > 2)) continue;
      const t = 0.85 + R() * 0.3;
      B(u + 0.01, u + 0.6, c - cw / 2 - 0.12, c + cw / 2 + 0.12, kh, kh + 0.075, [t, t * 0.97, t * 0.94]);
    }
    const len = a1 - a0, wg = new THREE.PlaneGeometry(axis === 'z' ? cw : len, axis === 'z' ? len : cw);
    wg.rotateX(-Math.PI / 2); wg.translate(axis === 'z' ? c : (a0 + a1) / 2, 0.13, axis === 'z' ? (a0 + a1) / 2 : c);
    waterParts.push(wg);
  }
  const segs = (lo, hi, crossings) => cuts(crossings, lo, hi);
  for (const [c, w] of STREETS.ns.filter((s) => s[1] > 6)) for (const side of [-1, 1]) for (const [a0, a1] of segs(STREETS.z[0], STREETS.z[1], STREETS.ew)) drainLine('z', c + side * (w / 2 - 0.6), a0 + 0.3, a1 - 0.3);
  for (const [c, w] of STREETS.ew.filter((s) => s[1] > 6)) for (const side of [-1, 1]) for (const [a0, a1] of segs(STREETS.x[0], STREETS.x[1], STREETS.ns)) drainLine('x', c + side * (w / 2 - 0.6), a0 + 0.3, a1 - 0.3);
  // soak pit next to the hero opening, and pots by the wall
  for (let i = 0; i < 5; i++) pots.geom(pot, 4.95 + (i % 2) * 0.35, 0, 41 + i * 0.55 + R() * 0.2, 0.45 + R() * 0.25, R() * 3, [1, 0.85 + R() * 0.2, 0.8]);

  // ---- citadel mound with the Great Bath (west)
  const cit = { x0: -340, x1: -225, z0: -130, z1: 70, h: 12 };
  for (let i = 0; i < 6; i++) { // battered (stepped) brick mound
    const k = i * 1.1, hh = cit.h / 6;
    walls.aabb(cit.x0 + k, i * hh, cit.z0 + k, cit.x1 - k, (i + 1) * hh, cit.z1 - k, [0.95, 0.93, 0.9]);
  }
  const by = cit.h, bcx = -282, bcz = -20;
  // Great Bath: 12 × 7 m tank, 2.4 m deep, steps at both short ends, inside a courtyard with cells
  walls.aabb(bcx - 16, by, bcz - 13, bcx + 16, by + 3.2, bcz - 11, [1, 1, 1]).aabb(bcx - 16, by, bcz + 11, bcx + 16, by + 3.2, bcz + 13, [1, 1, 1]);
  walls.aabb(bcx - 16, by, bcz - 11, bcx - 14, by + 3.2, bcz + 11, [1, 1, 1]).aabb(bcx + 14, by, bcz - 11, bcx + 16, by + 3.2, bcz + 11, [1, 1, 1]);
  for (let i = -3; i <= 3; i++) walls.aabb(bcx + i * 3.6 - 0.4, by, bcz - 9.8, bcx + i * 3.6 + 0.4, by + 3, bcz - 9, [1, 1, 1]); // colonnade piers
  for (let i = -3; i <= 3; i++) walls.aabb(bcx + i * 3.6 - 0.4, by, bcz + 9, bcx + i * 3.6 + 0.4, by + 3, bcz + 9.8, [1, 1, 1]);
  drains.aabb(bcx - 7.5, by + 0.0, bcz - 4.5, bcx + 7.5, by + 0.35, bcz - 3.5).aabb(bcx - 7.5, by, bcz + 3.5, bcx + 7.5, by + 0.35, bcz + 4.5);
  drains.aabb(bcx - 7.5, by, bcz - 3.5, bcx - 6.5, by + 0.35, bcz + 3.5).aabb(bcx + 6.5, by, bcz - 3.5, bcx + 7.5, by + 0.35, bcz + 3.5);
  const bathW = new THREE.PlaneGeometry(13, 7); bathW.rotateX(-Math.PI / 2); bathW.translate(bcx, by + 0.2, bcz); waterParts.push(bathW);
  // granary / platform blocks and buildings on the mound
  for (let i = 0; i < 26; i++) {
    const x = cit.x0 + 12 + R() * (cit.x1 - cit.x0 - 24), z = cit.z0 + 12 + R() * (cit.z1 - cit.z0 - 24);
    if (Math.abs(x - bcx) < 20 && Math.abs(z - bcz) < 17) continue;
    walls.aabb(x, by, z, x + 8 + R() * 10, by + 3 + R() * 3.5, z + 8 + R() * 10, tint());
  }

  // ---- trees (sparse, mostly outside the grid), fields and the river to the east
  const trees = new Acc(), treeMat = new THREE.MeshStandardMaterial({ roughness: 1, vertexColors: true });
  const blob = new THREE.IcosahedronGeometry(1, 2);
  function tree(x, z, s) {
    trees.cyl(x, 0, z, 0.18 * s, 0.3 * s, 3.2 * s, 7, [0.32, 0.24, 0.17]);
    for (let i = 0; i < 7; i++) {
      const g = blob.clone(); const p = g.attributes.position;
      for (let j = 0; j < p.count; j++) { const v = new THREE.Vector3().fromBufferAttribute(p, j); v.multiplyScalar(0.8 + fbm(v.x * 2 + i, v.y * 2 + x, 2, 3) * 0.5); p.setXYZ(j, v.x, v.y * 0.7, v.z); }
      g.computeVertexNormals();
      const a = R() * 6.28, r = R() * 1.8 * s;
      const gcol = 0.8 + R() * 0.3;
      trees.geom(g, x + Math.cos(a) * r, 3.4 * s + R() * 1.6 * s, z + Math.sin(a) * r, (1.3 + R() * 0.9) * s, 0, [0.29 * gcol, 0.33 * gcol, 0.16 * gcol]);
    }
  }
  for (let i = 0; i < 90; i++) {
    let x = (R() - 0.5) * 900, z = (R() - 0.5) * 900;
    if (x > -350 && x < 180 && z > -200 && z < 200) continue;
    tree(x, z, 1 + R() * 0.6);
  }
  for (const [x, z] of [[-40, 60], [60, -40], [120, 130], [-120, -60], [30, 150]]) tree(x + 0.5, z + 0.5, 0.9);

  const fields = new Acc(), fieldMat = new THREE.MeshStandardMaterial({ roughness: 1, vertexColors: true });
  for (let i = 0; i < 70; i++) {
    const x = 260 + R() * 320, z = -500 + R() * 1000, w = 30 + R() * 60, d = 30 + R() * 70, g = R();
    fields.box(x, 0.02 + R() * 0.02, z, w, 0.05, d, g < 0.5 ? [0.36, 0.38, 0.2] : g < 0.8 ? [0.55, 0.47, 0.28] : [0.45, 0.42, 0.24]);
  }
  const river = new THREE.PlaneGeometry(320, 3000); river.rotateX(-Math.PI / 2); river.translate(760, 0.1, 0);
  const riverMesh = new THREE.Mesh(river, waterMat(T.waterN, { color: 0x4a4636, flow: [0, 0.02], scale: 30, strength: 0.25, rough: 0.12 }));

  G.add(brickWalls.mesh(wallMat), plasterWalls.mesh(plasterMat), dark.mesh(darkMat, { cast: false }), wood.mesh(woodMat), drains.mesh(drainMat), pots.mesh(potMat),
    trees.mesh(treeMat), fields.mesh(fieldMat, { cast: false }), riverMesh);
  const wm = new THREE.Group(); for (const g of waterParts) wm.add(new THREE.Mesh(g, water));
  G.add(wm);

  const people = buildPeople(G, T, rng(7));
  const carts = buildCarts(G);
  const dhola = buildDholavira(scene, T);
  return { group: G, waters: [water, riverMesh.material, ...dhola.waters], people: { update: (t) => { people.update(t); dhola.update(t); } }, carts, dhola };
}

// ---- people walking the streets (and a few standing at doorways), cleared away from the drain close-up
function buildPeople(G, T, R) {
  const cloth = [0xefe6d3, 0xe6dac2, 0xf3ecdd, 0xd9c8a8, 0xc9a77c, 0xa8563a, 0xb98b5a];
  const specs = [];
  const heroCam = (x, z, t) => t > 7.4 && t < 10.1 && Math.hypot(x - DRAIN_X, z - 30) < 9;
  for (let i = 0; i < 460; i++) {
    const pick = R(); let axis, c0, a0, a1;
    if (pick < 0.5) { const s = STREETS.ns[Math.floor(R() * 3)]; axis = 'z'; c0 = s[0] + (R() - 0.5) * (s[1] - 3.4); a0 = STREETS.z[0]; a1 = STREETS.z[1]; }
    else { const s = STREETS.ew[Math.floor(R() * 3)]; axis = 'x'; c0 = s[0] + (R() - 0.5) * (s[1] - 3.4); a0 = STREETS.x[0]; a1 = STREETS.x[1]; }
    const v = (1.0 + R() * 0.45) * (R() < 0.5 ? -1 : 1), off = R() * 400, L = a1 - a0;
    const at = (t) => { const d = off + v * t; const u = ((d % L) + L) % L + a0;
      return axis === 'z' ? { x: c0, z: u, yaw: v > 0 ? 0 : Math.PI, moving: true, dist: Math.abs(d) } : { x: u, z: c0, yaw: v > 0 ? Math.PI / 2 : -Math.PI / 2, moving: true, dist: Math.abs(d) }; };
    let bad = false; for (let t = 7.4; t < 10.1; t += 0.2) { const p = at(t); if (heroCam(p.x, p.z, t)) bad = true; }
    if (bad) continue;
    const variant = R() < 0.3 ? 2 : R() < 0.5 ? 1 : 0;
    specs.push({ at, variant, carry: R() < 0.14, cloth: cloth[Math.floor(R() * cloth.length)], scale: variant === 2 ? 0.94 : 0.98 + R() * 0.08 });
  }
  // people in the far background of the drain shot: standing, talking, one walking away
  for (const [x, z, yaw, variant] of [[-1.5, 52, 1.2, 1], [-0.9, 53, -1.9, 0], [-2.8, 61, 0.4, 2], [1.6, 70, 3.0, 1]]) {
    specs.push({ at: () => ({ x, z, yaw, moving: false }), variant, carry: false, cloth: cloth[Math.floor(R() * cloth.length)], scale: 1 });
  }
  specs.push({ at: (t) => ({ x: 2.2, z: 44 + (t - 7.6) * 1.1, yaw: 0, moving: true, dist: t * 1.1 }), variant: 2, carry: true, cloth: 0xa8563a, scale: 0.95 });
  const update = buildCrowd(G, specs);
  return { update };
}

// ---- bullock carts on First Street (solid wheels, zebu oxen, as in the terracotta cart models)
function buildCarts(G) {
  const wood = new THREE.MeshStandardMaterial({ color: 0x6b4a2c, roughness: 0.9 });
  const ox = new THREE.MeshStandardMaterial({ color: 0xcfc5b5, roughness: 0.95 });
  const carts = [];
  const specs = [[-1.8, -60, 0.8], [2.0, 120, -0.7], [-1.5, 160, 0.9], [1.6, 20, -0.75]];
  for (const [x, z0, v] of specs) {
    const g = new THREE.Group();
    const bed = new THREE.Mesh(new THREE.BoxGeometry(1.3, 0.12, 1.9), wood); bed.position.y = 0.72;
    const s1 = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.35, 1.9), wood); s1.position.set(-0.62, 0.95, 0);
    const s2 = s1.clone(); s2.position.x = 0.62;
    const pole = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.1, 2.4), wood); pole.position.set(0, 0.8, 2.0);
    g.add(bed, s1, s2, pole);
    for (const sx of [-0.78, 0.78]) { const wh = new THREE.Mesh(new THREE.CylinderGeometry(0.55, 0.55, 0.12, 20), wood); wh.rotation.z = Math.PI / 2; wh.position.set(sx, 0.55, 0); g.add(wh); }
    for (const sx of [-0.45, 0.45]) {
      const body = new THREE.Mesh(new THREE.CapsuleGeometry(0.33, 1.1, 6, 12), ox); body.rotation.x = Math.PI / 2; body.position.set(sx, 1.05, 3.2);
      const hump = new THREE.Mesh(new THREE.SphereGeometry(0.2, 10, 8), ox); hump.position.set(sx, 1.42, 3.55);
      const head = new THREE.Mesh(new THREE.BoxGeometry(0.24, 0.3, 0.5), ox); head.position.set(sx, 1.1, 4.1);
      g.add(body, hump, head);
      for (const [lx, lz] of [[-0.15, 2.8], [0.15, 2.8], [-0.15, 3.6], [0.15, 3.6]]) { const l = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.05, 0.8), ox); l.position.set(sx + lx, 0.4, lz); g.add(l); }
    }
    g.traverse((o) => { if (o.isMesh) { o.castShadow = true; o.receiveShadow = true; } });
    G.add(g); carts.push({ g, x, z0, v });
  }
  return { update(t) { for (const c of carts) { c.g.position.set(c.x, 0, c.z0 + c.v * t); c.g.rotation.y = c.v > 0 ? 0 : Math.PI; } } };
}

// ---- Dholavira: a stone-cut, terraced reservoir fed by a stone channel, on pale Kutch ground
function buildDholavira(scene, T) {
  const O = DHOLA, G = new THREE.Group(); G.position.copy(O); scene.add(G);
  const stoneMat = triMat({ side: T.stone, top: T.stone, bumpScale: 2 });
  const groundMat = triMat({ side: T.stone, top: T.earthPale, bumpScale: 0.8, groundDark: 1, macroAmt: 0.5 });
  const A = new Acc(), R = rng(55);
  const L = 36, W = 14, D = 2.7; // half-length, half-width of top rim; terrace depth
  // ground with a hole for the reservoir
  const sh = new THREE.Shape(); sh.moveTo(-900, -900); sh.lineTo(900, -900); sh.lineTo(900, 900); sh.lineTo(-900, 900);
  const hole = new THREE.Path(); hole.moveTo(-L, -W); hole.lineTo(-L, W); hole.lineTo(L, W); hole.lineTo(L, -W); sh.holes.push(hole);
  const gg = new THREE.ShapeGeometry(sh); gg.rotateX(-Math.PI / 2);
  gg.setAttribute('color', new THREE.BufferAttribute(new Float32Array(gg.attributes.position.count * 3).fill(1), 3));
  const ground = new THREE.Mesh(gg, groundMat); ground.receiveShadow = true; G.add(ground);
  for (let i = 0; i < 3; i++) {
    const l = L - i * 2.2, w = W - i * 2.2, y0 = -(i + 1) * D, y1 = -i * D, k = 1.2;
    A.aabb(-l - k, y0, -w - k, l + k, y1, -w).aabb(-l - k, y0, w, l + k, y1, w + k);
    A.aabb(-l - k, y0, -w, -l, y1, w).aabb(l, y0, -w, l + k, y1, w);
    const nl = l - 2.2, nw = w - 2.2; // ledge floor between this terrace and the next
    A.aabb(-l, y0 - 0.3, -w, l, y0, -nw).aabb(-l, y0 - 0.3, nw, l, y0, w).aabb(-l, y0 - 0.3, -nw, -nl, y0, nw).aabb(nl, y0 - 0.3, -nw, l, y0, nw);
  }
  A.aabb(-L + 6.6, -3 * D - 0.4, -W + 6.6, L - 6.6, -3 * D, W - 6.6);
  for (let k = 0; k < 27; k++) A.aabb(-L + 0.2 + k * 0.42, -3 * D, W - 2.1, -L + 0.2 + k * 0.42 + 0.44, -k * 0.3, W - 0.05); // stair along the north wall
  // inlet channel from the west, stone-lined
  for (const s of [-1, 1]) A.aabb(-L - 60, -0.1, s * 0.9 - 0.3, -L - 1, 0.35, s * 0.9 + 0.3);
  A.aabb(-L - 60, -0.1, -0.6, -L - 1, 0.02, 0.6);
  // rim walls / later settlement hints
  for (let i = 0; i < 14; i++) { const x = (R() - 0.5) * 200, z = 30 + R() * 90; A.aabb(x, 0, z, x + 6 + R() * 8, 1 + R() * 2.2, z + 5 + R() * 8, [0.95, 0.95, 0.95]); }
  G.add(A.mesh(stoneMat));
  const w1 = waterMat(T.waterN, { color: 0x283a3a, flow: [0.004, 0.01], scale: 6, strength: 0.35, rough: 0.04 });
  const wg = new THREE.PlaneGeometry(2 * L, 2 * W); wg.rotateX(-Math.PI / 2); wg.translate(0, -6.1, 0);
  const w2 = waterMat(T.waterN, { color: 0x2a3432, flow: [0.25, 0], scale: 1.2, strength: 0.5 });
  const cg = new THREE.PlaneGeometry(59, 1.2); cg.rotateX(-Math.PI / 2); cg.translate(-L - 30.5, 0.16, 0);
  G.add(new THREE.Mesh(wg, w1), new THREE.Mesh(cg, w2));
  // a few people: on the stair with pots, on the rim, one walking along the inlet channel
  const updateFigs = buildCrowd(G, [
    { at: (t) => ({ x: -L + 3 + (t - 11.8) * 0.5, y: -Math.min(26, (3 + (t - 11.8) * 0.5) / 0.42) * 0.3 + 0.0, z: W - 1.1, yaw: Math.PI / 2, moving: true, dist: t * 0.5 }), variant: 2, carry: true, cloth: 0xe6dac2, scale: 0.95 },
    { at: () => ({ x: -L + 9.4, y: -3.9, z: W - 1.2, yaw: -Math.PI / 2, moving: false }), variant: 1, carry: false, cloth: 0xa8563a, scale: 1 },
    { at: (t) => ({ x: -L - 20 + (t - 11.8) * 1.1, z: 2.2, yaw: Math.PI / 2, moving: true, dist: t * 1.1 }), variant: 0, carry: false, cloth: 0xefe6d3, scale: 1 },
    { at: () => ({ x: -L - 4, z: W + 3, yaw: 0.3, moving: false }), variant: 2, carry: true, cloth: 0xd9c8a8, scale: 0.95 },
    { at: () => ({ x: -L - 3.2, z: W + 3.6, yaw: 2.6, moving: false }), variant: 1, carry: false, cloth: 0xc9a77c, scale: 1 },
  ]);
  return { waters: [w1, w2], update: updateFigs, group: G };
}
