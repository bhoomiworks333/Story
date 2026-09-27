// Edit decision list. Times in seconds (24 fps master). 3D shots return camera/light setups; 2D shots are drawn by overlay.js.
import * as THREE from 'three';
import { smoother, easeInOut, lerp } from './util.js';
import { DRAIN_X, DHOLA } from './ancient.js';
import { MOD } from './modern3d.js';
import { STUDIO as S0, APPSET } from './studio.js';

const V = (x, y, z) => new THREE.Vector3(x, y, z);
const SUN_A = V(-0.85, 0.5, 0.3).normalize();
const SUN_M = V(-0.5, 0.75, -0.35).normalize();
const L = (a, b, u) => a.clone().lerp(b, u);
const SUN_S = V(0.35, 0.85, 0.4).normalize();
const S = (x, y, z) => S0.clone().add(V(x, y, z));
const shake = (t, amp, f = 1) => V(Math.sin(t * 13.1 * f) + Math.sin(t * 7.3 * f + 1), Math.sin(t * 11.7 * f + 2), Math.sin(t * 9.1 * f + 3) + Math.sin(t * 5.3 * f)).multiplyScalar(amp);
const studio = (o) => ({ preset: 'studio', sunDir: SUN_S, fog: 0, near: 0.01, far: 30, shadow: { center: S0.clone(), size: 1.0 }, glow: 0, vig: 0.45, ...o });
// small organic camera drift so nothing feels locked-off
const drift = (t, amp = 0.04, f = 0.35) => V(Math.sin(t * f * 6.1) * amp, Math.sin(t * f * 4.3 + 1) * amp * 0.6, Math.sin(t * f * 5.2 + 2) * amp);

export const DUR = 43.8;
export const SHOTS = [
  { id: 'aerial', a: 0, b: 7.6, kind: '3d', cam(t, u) {
    const e = smoother(u * 0.92 + 0.04);
    return { preset: 'ancient', sunDir: SUN_A, pos: L(V(230, 150, 300), V(70, 46, 118), e).add(drift(t, 0.3)), look: L(V(-70, 0, -40), V(-40, 2, -45), e),
      fov: 42, fog: lerp(0.0015, 0.0009, e), shadow: { center: L(V(-20, 0, -20), V(0, 0, 0), e), size: 260 }, t };
  } },
  { id: 'drain', a: 7.6, b: 9.9, kind: '3d', cam(t, u) {
    const e = easeInOut(u);
    return { preset: 'ancient', sunDir: SUN_A, pos: V(DRAIN_X, 0.95, lerp(26.4, 28.2, e)).add(drift(t, 0.008)), look: V(DRAIN_X - 0.05, 0.02, 37),
      fov: 36, fog: 0.004, dof: { focus: lerp(4.6, 3.8, e), aperture: 0.01, maxblur: 0.012 }, shadow: { center: V(0, 0, 36), size: 30 }, t, exposure: 1.0 };
  } },
  { id: 'street', a: 9.9, b: 11.8, kind: '3d', cam(t, u) {
    const e = easeInOut(u);
    return { preset: 'ancient', sunDir: SUN_A, pos: V(-1.2, lerp(11, 9.5, e), lerp(-58, -44, e)).add(drift(t, 0.05)), look: V(0.5, 2.5, 80),
      fov: 40, fog: 0.0035, shadow: { center: V(0, 0, 10), size: 90 }, t };
  } },
  { id: 'reservoir', a: 11.8, b: 14.2, kind: '3d', cam(t, u) {
    const e = easeInOut(u);
    return { preset: 'ancient', sunDir: SUN_A, pos: DHOLA.clone().add(L(V(32, 10, -21), V(22, 8.5, -22), e)).add(drift(t, 0.04)), look: DHOLA.clone().add(V(-20, -6, 7)),
      fov: 44, fog: 0.0028, shadow: { center: DHOLA.clone(), size: 70 }, t };
  } },
  { id: 'topA', a: 14.2, b: 15.2, kind: '3d', cam(t, u) {
    const e = smoother(u);
    return { preset: 'ancient', sunDir: SUN_A, pos: V(0, lerp(215, 245, e), 0.01), look: V(0, 0, 0), up: V(0, 0, -1),
      fov: 40, fog: 0.0012, shadow: { center: V(0, 0, 0), size: 200 }, t };
  } },
  { id: 'topM', a: 15.2, b: 16.6, kind: '3d', cam(t, u) {
    const e = smoother(u);
    return { preset: 'modern', sunDir: SUN_M, pos: MOD.clone().add(V(0, lerp(245, 265, e), 0.01)), look: MOD.clone(), up: V(0, 0, -1),
      fov: 40, fog: 0.0009, shadow: { center: MOD.clone(), size: 200 }, t };
  } },
  { id: 'register', a: 16.6, b: 18.6, kind: '3d', cam(t, u) {
    const x = lerp(0.04, 0.2, u);
    return studio({ pos: S(x + 0.06, 0.2, 0.15).add(shake(t, 0.0012)), look: S(x, 0.02, 0.0), fov: 34, dof: { focus: 0.25, aperture: 0.35, maxblur: 0.018 }, t });
  } },
  { id: 'chat', a: 18.6, b: 20.6, kind: '3d', cam(t, u) {
    return studio({ pos: S(0.46, lerp(0.26, 0.23, u), 0.2).add(shake(t, 0.0015)), look: S(0.43, 0, 0.085), fov: 36, dof: { focus: 0.26, aperture: 0.3, maxblur: 0.015 }, t });
  } },
  { id: 'ledger', a: 20.6, b: 22.8, kind: '3d', cam(t, u) {
    const e = easeInOut(u);
    return studio({ pos: L(S(-0.585, 0.17, 0.17), S(-0.47, 0.26, 0.45), e).add(shake(t, 0.002)), look: L(S(-0.705, 0.115, -0.195), S(-0.56, 0.0, 0.18), e), fov: 38,
      dof: { focus: lerp(0.38, 0.3, e), aperture: 0.12, maxblur: 0.012 }, t });
  } },
  { id: 'flood', a: 22.8, b: 23.8, kind: '3d', cam(t, u) {
    return studio({ pos: S(0.44, lerp(0.2, 0.17, u), 0.14).add(shake(t, 0.0015 + u * 0.004, 1.6)), look: S(0.43, 0, 0.095), fov: 36, dof: { focus: 0.2, aperture: 0.3, maxblur: 0.015 }, t });
  } },
  { id: 'question', a: 23.8, b: 29.6, kind: '3d', cam(t, u) {
    const e = smoother(u);
    return studio({ pos: L(S(0.62, 0.62, 0.78), S(0.5, 0.3, 0.36), e), look: L(S(0.3, 0, 0.05), S(0.43, 0, 0.1), e), fov: 36, sunMul: lerp(1, 0.55, e),
      dof: { focus: lerp(0.95, 0.3, e), aperture: 0.1, maxblur: 0.012 }, t });
  } },
  { id: 'gridA', a: 29.6, b: 31.8, kind: '3d', cam(t, u) {
    const e = smoother(u);
    return { preset: 'ancient', sunDir: SUN_A, pos: V(0, lerp(250, 300, e), 0.01), look: V(0, 0, 0), up: V(0, 0, -1),
      fov: 40, fog: 0.0012, shadow: { center: V(0, 0, 0), size: 220 }, t };
  } },
  { id: 'gridMorph', a: 31.8, b: 33.9, kind: '2d' },
  { id: 'app', a: 33.9, b: 37.6, kind: '3d', cam(t, u) {
    const e = easeInOut(u), a = lerp(-0.28, 0.1, e), d = lerp(0.36, 0.31, e);
    return studio({ preset: 'studioWarm', sunDir: V(-0.4, 0.8, 0.6).normalize(), pos: APPSET.clone().add(V(Math.sin(a) * d, 0.13, Math.cos(a) * d)), look: APPSET.clone().add(V(0, 0.09, 0)),
      fov: 32, shadow: { center: APPSET.clone(), size: 1.0 }, dof: { focus: d, aperture: 0.06, maxblur: 0.01 }, vig: 0.3, bloom: 0, grade: { contrast: 1.14, sat: 1.0 }, t });
  } },
  { id: 'brand', a: 37.6, b: DUR, kind: '2d' },
];

// Voiceover placement (line index -> start time). Durations come from vo/vo.json.
export const VO_AT = [0.4, 7.75, 10.0, 11.9, 16.75, 18.7, 20.7, 24.0, 26.6, 29.7, 34.1, 37.8];

export function shotAt(t) { return SHOTS.find((s) => t >= s.a && t < s.b) || SHOTS[SHOTS.length - 1]; }
