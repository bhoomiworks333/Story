// Every frame is a pure function of t: renderAt(t) draws the 3D shot (if any) and the 2D overlay.
import { createWorld } from './world.js';
import { SHOTS, shotAt, DUR } from './shots.js';
import { createOverlay } from './overlay.js';

const gl = document.getElementById('gl'), ov = document.getElementById('ov');
const fonts = ['400 20px Inter', '500 20px Inter', '600 20px Inter', '700 20px Inter', '700 20px Manrope', '800 20px Manrope', '20px Kalam', '800 20px Manrope', '500 20px Inter'];
await Promise.all(['700 20px Manrope', '800 20px Manrope', '400 20px Inter', '500 20px Inter', '600 20px Inter', '700 20px Inter'].map((f) => document.fonts.load(f, '₹')));
await Promise.all(fonts.map((f) => document.fonts.load(f)));
const world = await createWorld(gl);
const overlay = await createOverlay(ov, world);

window.DUR = DUR; window.world = world;
window.renderAt = (t) => {
  const s = shotAt(t), u = (t - s.a) / (s.b - s.a);
  if (s.kind === '3d') { gl.style.visibility = 'visible'; world.render({ id: s.id, ...s.cam(t, u) }); }
  else gl.style.visibility = 'hidden';
  overlay.draw(t, s, u);
  return s.id;
};
window.ready = true;
