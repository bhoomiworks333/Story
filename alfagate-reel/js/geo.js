// Geometry accumulator: collect boxes/cylinders with per-vertex tint, merge into one mesh per material.
import * as THREE from 'three';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

export class Acc {
  constructor() { this.parts = []; }
  add(g, tint = [1, 1, 1]) {
    g = g.index ? g.toNonIndexed() : g;
    for (const k of Object.keys(g.attributes)) if (!['position', 'normal', 'uv'].includes(k)) g.deleteAttribute(k);
    const n = g.attributes.position.count, c = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) c.set(tint, i * 3);
    g.setAttribute('color', new THREE.BufferAttribute(c, 3));
    this.parts.push(g);
    return this;
  }
  // box with its bottom at y0
  box(cx, y0, cz, w, h, d, tint, rotY = 0) {
    if (w <= 0 || h <= 0 || d <= 0) return this;
    const g = new THREE.BoxGeometry(w, h, d);
    g.translate(0, h / 2, 0); if (rotY) g.rotateY(rotY); g.translate(cx, y0, cz);
    return this.add(g, tint);
  }
  // axis-aligned box from min/max corners
  aabb(x0, y0, z0, x1, y1, z1, tint) { return this.box((x0 + x1) / 2, y0, (z0 + z1) / 2, x1 - x0, y1 - y0, z1 - z0, tint); }
  cyl(cx, y0, cz, rt, rb, h, seg = 16, tint, open = false) {
    const g = new THREE.CylinderGeometry(rt, rb, h, seg, 1, open); g.translate(cx, y0 + h / 2, cz); return this.add(g, tint);
  }
  geom(g, x, y, z, s = 1, rotY = 0, tint) {
    g = g.clone(); g.scale(s, s, s); if (rotY) g.rotateY(rotY); g.translate(x, y, z); return this.add(g, tint);
  }
  geometry() { const g = mergeGeometries(this.parts, false); this.parts = []; return g; }
  mesh(mat, { cast = true, receive = true } = {}) {
    if (!this.parts.length) return new THREE.Group();
    const m = new THREE.Mesh(mergeGeometries(this.parts, false), mat);
    m.castShadow = cast; m.receiveShadow = receive; m.matrixAutoUpdate = false;
    this.parts = [];
    return m;
  }
}

// Terracotta pot profile (LatheGeometry), unit height.
export function potGeom(seed = 0) {
  const pts = [[0, 0], [0.18, 0.02], [0.34, 0.2], [0.42, 0.45], [0.36, 0.72], [0.2, 0.86], [0.18, 0.93], [0.24, 1]];
  return new THREE.LatheGeometry(pts.map(([r, y]) => new THREE.Vector2(r * (1 + (seed % 3) * 0.08), y)), 14);
}
