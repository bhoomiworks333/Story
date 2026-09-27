// Small deterministic helpers shared by every module. Nothing here may depend on wall-clock time or Math.random,
// because every frame must be a pure function of t.
export function rng(seed = 1) {
  let s = seed >>> 0;
  return () => {
    s += 0x6d2b79f5;
    let t = s;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
export const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const lerp = (a, b, u) => a + (b - a) * u;
export const smooth = (u) => { u = clamp(u); return u * u * (3 - 2 * u); };
export const smoother = (u) => { u = clamp(u); return u * u * u * (u * (u * 6 - 15) + 10); };
export const easeOut = (u) => 1 - Math.pow(1 - clamp(u), 3);
export const easeIn = (u) => Math.pow(clamp(u), 3);
export const easeInOut = (u) => { u = clamp(u); return u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2; };
export const range = (t, a, b) => clamp((t - a) / (b - a));
// fade in over [a, a+fi], hold, fade out over [b-fo, b]
export const window01 = (t, a, b, fi = 0.3, fo = 0.3) => Math.min(range(t, a, a + fi), 1 - range(t, b - fo, b));

// 2D value noise + fbm, deterministic
function hash2(x, y, seed) {
  let h = (x * 374761393 + y * 668265263 + seed * 982451653) | 0;
  h = Math.imul(h ^ (h >>> 13), 1274126177);
  return ((h ^ (h >>> 16)) >>> 0) / 4294967296;
}
export function vnoise(x, y, seed = 0, period = 0) {
  const xi = Math.floor(x), yi = Math.floor(y);
  const xf = x - xi, yf = y - yi;
  const w = (v) => (period ? ((v % period) + period) % period : v);
  const a = hash2(w(xi), w(yi), seed), b = hash2(w(xi + 1), w(yi), seed);
  const c = hash2(w(xi), w(yi + 1), seed), d = hash2(w(xi + 1), w(yi + 1), seed);
  const u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf);
  return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
}
export function fbm(x, y, oct = 4, seed = 0, period = 0) {
  let s = 0, amp = 0.5, f = 1, n = 0;
  for (let i = 0; i < oct; i++) {
    s += amp * vnoise(x * f, y * f, seed + i * 17, period ? period * f : 0);
    n += amp; amp *= 0.5; f *= 2;
  }
  return s / n;
}
