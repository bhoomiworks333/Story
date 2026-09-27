// Renderer, lighting presets, post-processing and camera placement for the 3D shots.
import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { BokehPass } from 'three/addons/postprocessing/BokehPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import * as TX from './tex.js';
import { setMacro, skyMat } from './mat.js';
import { buildAncient } from './ancient.js';
import { buildModern } from './modern3d.js';
import { buildStudio } from './studio.js';

export const W = 1080, H = 1920;

const PRESETS = {
  ancient: { zenith: 0x6a8fba, horizon: 0xf2cd9c, ground: 0xb08a66, sunCol: 0xffc98a, sun: 3.6, sunLight: 0xffd29e,
    hemiSky: 0xa9c0de, hemiGround: 0x9a7252, hemi: 1.0, fog: 0xe0bf95, env: 0.8, exposure: 1.0,
    grade: { lift: [0.035, 0.022, 0.01], gain: [1.05, 0.99, 0.9], sat: 0.9, contrast: 1.08 } },
  modern: { zenith: 0x7c9cc0, horizon: 0xd3dbe2, ground: 0x7d8590, sunCol: 0xfff1dc, sun: 2.6, sunLight: 0xfff4e8,
    hemiSky: 0xbcd0e6, hemiGround: 0x6b6f75, hemi: 0.8, fog: 0xc6d0d9, env: 0.7, exposure: 0.95,
    grade: { lift: [0.01, 0.015, 0.025], gain: [0.96, 0.99, 1.03], sat: 0.72, contrast: 1.04 } },
};

PRESETS.studio = { zenith: 0x2a2d31, horizon: 0x33373b, ground: 0x222222, sunCol: 0x000000, sun: 2.3, sunLight: 0xeef3ff,
  hemiSky: 0xdfe8f0, hemiGround: 0x3a3028, hemi: 0.45, fog: 0x000000, env: 0.45, exposure: 1.0, envKey: 'modern',
  grade: { lift: [0.0, 0.006, 0.016], gain: [0.96, 1.0, 1.04], sat: 0.86, contrast: 1.1 } };
PRESETS.studioWarm = { ...PRESETS.studio, sun: 2.4, sunLight: 0xfff0dc, hemi: 0.6, env: 0.8, exposure: 1.05,
  grade: { lift: [0.01, 0.006, 0.0], gain: [1.02, 1.0, 0.98], sat: 0.95, contrast: 1.06 } };

const GradeShader = {
  uniforms: { tDiffuse: { value: null }, lift: { value: new THREE.Vector3() }, gain: { value: new THREE.Vector3(1, 1, 1) },
    sat: { value: 1 }, contrast: { value: 1 }, vig: { value: 0.35 } },
  vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.); }',
  fragmentShader: `uniform sampler2D tDiffuse; uniform vec3 lift, gain; uniform float sat, contrast, vig; varying vec2 vUv;
    void main(){ vec3 c = texture2D(tDiffuse, vUv).rgb;
      c = (c - 0.5) * contrast + 0.5;
      float l = dot(c, vec3(0.2126,0.7152,0.0722)); c = mix(vec3(l), c, sat);
      c = c * gain + lift * (1.0 - c);
      vec2 d = (vUv - 0.5) * vec2(0.75, 1.0); c *= 1.0 - vig * smoothstep(0.25, 0.75, length(d));
      gl_FragColor = vec4(clamp(c, 0., 1.), 1.); }`,
};

export async function createWorld(canvas) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
  renderer.setPixelRatio(1); renderer.setSize(W, H, false);
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.outputColorSpace = THREE.SRGBColorSpace;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(40, W / H, 0.1, 4000);
  const sky = new THREE.Mesh(new THREE.SphereGeometry(3000, 32, 16), skyMat()); sky.frustumCulled = false; sky.renderOrder = -1;
  scene.add(sky);
  const sun = new THREE.DirectionalLight(0xffffff, 3); sun.castShadow = true;
  sun.shadow.mapSize.set(4096, 4096); sun.shadow.bias = -0.0004; sun.shadow.normalBias = 0.04;
  scene.add(sun, sun.target);
  const hemi = new THREE.HemisphereLight(0xffffff, 0x444444, 0.6); scene.add(hemi);
  scene.fog = new THREE.FogExp2(0xffffff, 0.002);

  setMacro(TX.macroNoise());
  const T = {
    brick: TX.brick(3), mudWall: TX.mud(17, [178, 140, 104]), brick2: TX.brick(8, { dust: 0.2, hue: 15 }), mud: TX.mud(7), earth: TX.earth(11),
    earthPale: TX.earth(13, [186, 164, 132]), stone: TX.stone(19), waterN: TX.waterNormal(31),
  };
  const ancient = buildAncient(scene, T);
  const modern = buildModern(scene, T);
  const icon = new Image(); icon.src = 'assets/alfagate_icon.png'; await icon.decode();
  const studio = buildStudio(scene, icon);

  // environment maps for reflections, one per preset, rendered from the sky alone
  const pmrem = new THREE.PMREMGenerator(renderer);
  const envs = {};
  for (const k of ['ancient', 'modern']) {
    applySky(k, new THREE.Vector3(-0.85, 0.5, 0.3));
    const s = new THREE.Scene(); const sk = sky.clone(); s.add(sk);
    envs[k] = pmrem.fromScene(s, 0, 0.1, 4000).texture;
  }

  const composer = new EffectComposer(renderer, new THREE.WebGLRenderTarget(W, H, { type: THREE.HalfFloatType, samples: 4 }));
  composer.setPixelRatio(1); composer.setSize(W, H);
  composer.addPass(new RenderPass(scene, camera));
  const bokeh = new BokehPass(scene, camera, { focus: 10, aperture: 0.002, maxblur: 0.01 }); composer.addPass(bokeh);
  const bloom = new UnrealBloomPass(new THREE.Vector2(W / 2, H / 2), 0.22, 0.5, 0.9); composer.addPass(bloom);
  composer.addPass(new OutputPass());
  const grade = new ShaderPass(GradeShader); composer.addPass(grade);

  function applySky(k, sunDir) {
    const p = PRESETS[k], u = sky.material.uniforms;
    u.zenith.value.set(p.zenith); u.horizon.value.set(p.horizon); u.ground.value.set(p.ground);
    u.sunCol.value.set(p.sunCol); u.sunDir.value.copy(sunDir);
  }

  // shot: { preset, sunDir, pos, look, fov, up?, fog, dof?: {focus, aperture, maxblur}, shadow: {center, size}, t }
  function render(shot) {
    const p = PRESETS[shot.preset];
    applySky(shot.preset, shot.sunDir);
    sky.material.uniforms.glow.value = shot.glow ?? 1;
    sky.position.copy(shot.pos);
    scene.environment = envs[p.envKey || shot.preset]; scene.environmentIntensity = p.env;
    renderer.toneMappingExposure = shot.exposure ?? p.exposure;
    scene.fog.color.set(p.fog); scene.fog.density = shot.fog;
    sun.color.set(p.sunLight); sun.intensity = p.sun * (shot.sunMul ?? 1);
    hemi.color.set(p.hemiSky); hemi.groundColor.set(p.hemiGround); hemi.intensity = p.hemi;
    const c = shot.shadow.center, s = shot.shadow.size;
    sun.target.position.copy(c); sun.position.copy(c).addScaledVector(shot.sunDir.clone().normalize(), s * 2);
    Object.assign(sun.shadow.camera, { left: -s, right: s, top: s, bottom: -s, near: 1, far: s * 4 });
    sun.shadow.camera.updateProjectionMatrix();
    camera.fov = shot.fov; camera.up.copy(shot.up || new THREE.Vector3(0, 1, 0));
    camera.near = shot.near ?? 0.1; camera.far = shot.far ?? 4000;
    camera.position.copy(shot.pos); camera.lookAt(shot.look); camera.updateProjectionMatrix();
    bokeh.uniforms.nearClip.value = camera.near; bokeh.uniforms.farClip.value = camera.far;
    bloom.strength = shot.bloom ?? 0.22;
    if (shot.dof) { bokeh.enabled = true; Object.assign(bokeh.uniforms.focus, { value: shot.dof.focus }); bokeh.uniforms.aperture.value = shot.dof.aperture; bokeh.uniforms.maxblur.value = shot.dof.maxblur; }
    else bokeh.enabled = false;
    const g = { ...p.grade, ...(shot.grade || {}) };
    grade.uniforms.lift.value.set(...g.lift); grade.uniforms.gain.value.set(...g.gain);
    grade.uniforms.sat.value = g.sat; grade.uniforms.contrast.value = g.contrast; grade.uniforms.vig.value = shot.vig ?? 0.38;
    // draw only the set this shot uses: hidden sets skip both the camera and the shadow pass
    const set = shot.preset === 'modern' ? 'modern' : shot.preset.startsWith('studio') ? (shot.id === 'app' ? 'app' : 'desk') : shot.id === 'reservoir' ? 'dhola' : 'city';
    ancient.group.visible = set === 'city'; ancient.dhola.group.visible = set === 'dhola'; modern.group.visible = set === 'modern';
    studio.desk.visible = set === 'desk'; studio.appSet.visible = set === 'app';
    for (const w of ancient.waters) w.userData.time.value = shot.t;
    ancient.people.update(shot.t); ancient.carts.update(shot.t); modern.update(shot.t); studio.update(shot.t, shot.id);
    composer.render();
  }
  return { render, camera, scene, ancient, modern, studio, icon, glCanvas: canvas };
}
