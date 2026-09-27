// Low-poly but properly proportioned people (≈1.65 m) with a 6-pose walk cycle, rendered as instanced meshes.
// Clothing follows the Harappan evidence: unstitched cotton (dhoti-like lower cloth, shawl over one shoulder), bangles.
import * as THREE from 'three';
import { Acc, potGeom } from './geo.js';

const SKIN = [0.36, 0.22, 0.14], HAIR = [0.06, 0.045, 0.035], CLOTH = [1, 1, 1];
export const POSES = 6;

// variant 0: bare torso + lower cloth, 1: shawl over the torso, 2: full wrap (women), carry: pot on head, arm raised
export function figureGeom(pose, variant, carry = false) {
  const A = new Acc();
  const ph = (pose / POSES) * Math.PI * 2, sw = Math.sin(ph) * 0.42, lift = Math.max(0, Math.cos(ph)) * 0.05;
  const limb = (x, y, z, len, r0, r1, rotX, col) => {
    const g = new THREE.CylinderGeometry(r0, r1, len, 7); g.translate(0, -len / 2, 0); g.rotateX(rotX); g.translate(x, y, z); A.add(g, col);
  };
  // legs from the hip, opposite phase; skin below the cloth
  limb(-0.08, 0.86, 0, 0.86, 0.06, 0.045, sw, SKIN);
  limb(0.08, 0.86, 0, 0.86, 0.06, 0.045, -sw, SKIN);
  const lowerLen = variant === 2 ? 0.78 : 0.5;
  { const g = new THREE.CylinderGeometry(0.17, variant === 2 ? 0.22 : 0.2, lowerLen, 12); g.translate(0, 1.0 - lowerLen / 2, 0); A.add(g, CLOTH); }
  { const g = new THREE.CylinderGeometry(0.2, 0.165, 0.5, 12); g.scale(1, 1, 0.72); g.translate(0, 1.2, 0); A.add(g, variant === 0 ? SKIN : CLOTH); }
  { const g = new THREE.SphereGeometry(0.2, 12, 6, 0, Math.PI * 2, 0, Math.PI / 2); g.scale(1.08, 0.35, 0.75); g.translate(0, 1.44, 0); A.add(g, variant === 0 ? SKIN : CLOTH); }
  if (variant === 1) { const g = new THREE.BoxGeometry(0.1, 0.62, 0.3); g.rotateZ(0.55); g.translate(0.02, 1.2, 0.0); A.add(g, CLOTH); } // shawl diagonal
  // arms swing against the legs; with a pot, the right arm steadies it
  limb(-0.23, 1.42, 0, 0.62, 0.045, 0.038, -sw * 0.8, SKIN);
  if (carry) { const g = new THREE.CylinderGeometry(0.04, 0.035, 0.5, 7); g.translate(0, 0.25, 0); g.rotateZ(-0.35); g.translate(0.23, 1.42, 0); A.add(g, SKIN); }
  else limb(0.23, 1.42, 0, 0.62, 0.045, 0.038, sw * 0.8, SKIN);
  { const g = new THREE.CylinderGeometry(0.05, 0.06, 0.1, 8); g.translate(0, 1.5, 0); A.add(g, SKIN); }
  { const g = new THREE.SphereGeometry(0.105, 14, 10); g.scale(0.92, 1.08, 1); g.translate(0, 1.6, 0.005); A.add(g, SKIN); }
  { const g = new THREE.SphereGeometry(0.112, 14, 8, 0, Math.PI * 2, 0, Math.PI * 0.55); g.translate(0, 1.615, -0.012); A.add(g, HAIR); }
  if (variant === 2) { const g = new THREE.SphereGeometry(0.06, 8, 6); g.translate(0, 1.6, -0.12); A.add(g, HAIR); } // hair bun
  if (carry) { const g = potGeom(); g.scale(0.32, 0.3, 0.32); g.translate(0, 1.7, 0); A.add(g, [0.62, 0.3, 0.18]); }
  const geo = A.geometry(); geo.translate(0, lift, 0);
  return geo;
}

// A crowd: walkers(i) -> {x, z, yaw, moving, phase}; returns update(t)
export function buildCrowd(G, specs) {
  const mat = new THREE.MeshStandardMaterial({ roughness: 0.9, vertexColors: true });
  // instance colour dyes only the cloth (vertex colour white), never skin, hair or the pot
  mat.onBeforeCompile = (sh) => {
    sh.vertexShader = sh.vertexShader.replace('#include <color_vertex>',
      'vColor = vec3(1.0); vColor *= color;\n#ifdef USE_INSTANCING_COLOR\n if (color.r > 0.9) vColor *= instanceColor;\n#endif');
  };
  const kinds = [];
  for (let v = 0; v < 3; v++) for (const carry of [false, true]) {
    const meshes = [];
    for (let p = 0; p < POSES; p++) {
      const m = new THREE.InstancedMesh(figureGeom(p, v, carry), mat, specs.length);
      m.castShadow = m.receiveShadow = true; m.frustumCulled = false; G.add(m); meshes.push(m);
    }
    kinds.push({ v, carry, meshes });
  }
  // pack only the visible instances into each pose mesh (zero-scaled instances still cost full draw time)
  const col = new THREE.Color();
  for (const k of kinds) for (const m of k.meshes) m.setColorAt(0, col.set(0xffffff));
  const M = new THREE.Matrix4(), Q = new THREE.Quaternion(), P = new THREE.Vector3(), S = new THREE.Vector3(), Y = new THREE.Vector3(0, 1, 0);
  return function update(t) {
    for (const k of kinds) for (const m of k.meshes) m.userData.n = 0;
    specs.forEach((s) => {
      const st = s.at(t);
      const pose = st.moving ? Math.floor(((st.dist / 1.25) % 1 + 1) % 1 * POSES) : 0;
      P.set(st.x, st.y || 0, st.z); Q.setFromAxisAngle(Y, st.yaw); S.setScalar(s.scale);
      M.compose(P, Q, S);
      const k = kinds.find((k) => k.v === s.variant && k.carry === s.carry), m = k.meshes[pose], n = m.userData.n++;
      m.setMatrixAt(n, M); m.setColorAt(n, col.set(s.cloth));
    });
    for (const k of kinds) for (const m of k.meshes) {
      m.count = m.userData.n; m.instanceMatrix.needsUpdate = true; if (m.instanceColor) m.instanceColor.needsUpdate = true;
    }
  };
}
