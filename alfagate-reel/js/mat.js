// Materials: world-space triplanar PBR (so bricks keep their real size on any box), water, and the sky dome.
import * as THREE from 'three';

let macro = null;
export function setMacro(t) { macro = t; }

// side: {map, bump, tile} used on walls; top: same, used on faces pointing up (roofs, floors, ground).
export function triMat({ side, top = side, bumpScale = 1.2, roughness = 0.92, groundDark = 0.7, tint = 0xffffff, macroAmt = 0.35 }) {
  const m = new THREE.MeshStandardMaterial({ color: tint, roughness, metalness: 0, vertexColors: true });
  m.onBeforeCompile = (sh) => {
    m.userData.shader = sh;
    Object.assign(sh.uniforms, {
      tSide: { value: side.map }, tSideB: { value: side.bump }, sSide: { value: 1 / side.tile },
      tTop: { value: top.map }, tTopB: { value: top.bump }, sTop: { value: 1 / top.tile },
      tMacro: { value: macro }, uBump: { value: bumpScale }, uGround: { value: groundDark }, uMacro: { value: macroAmt },
    });
    sh.vertexShader = sh.vertexShader
      .replace('#include <common>', '#include <common>\nvarying vec3 vWP; varying vec3 vWN;')
      .replace('#include <project_vertex>', '#include <project_vertex>\n vWP = (modelMatrix * vec4(transformed, 1.0)).xyz; vWN = normalize(mat3(modelMatrix) * objectNormal);');
    sh.fragmentShader = sh.fragmentShader
      .replace('#include <common>', `#include <common>
varying vec3 vWP; varying vec3 vWN;
uniform sampler2D tSide, tSideB, tTop, tTopB, tMacro; uniform float sSide, sTop, uBump, uGround, uMacro;
vec3 perturbTri(vec3 p, vec3 n, vec2 dH, float fd) {
  vec3 sx = normalize(dFdx(p)), sy = normalize(dFdy(p));
  vec3 r1 = cross(sy, n), r2 = cross(n, sx); float det = dot(sx, r1) * fd;
  vec3 g = sign(det) * (dH.x * r1 + dH.y * r2); return normalize(abs(det) * n - g);
}`)
      .replace('#include <map_fragment>', `
  vec3 an = abs(vWN); vec2 tuv; bool isTop = false;
  if (an.y > an.x && an.y > an.z) { tuv = vWP.xz; isTop = vWN.y > 0.0; }
  else if (an.x > an.z) tuv = vec2(vWP.z * sign(vWN.x), vWP.y);
  else tuv = vec2(-vWP.x * sign(vWN.z), vWP.y);
  vec4 tcol; float triH;
  if (isTop) { tcol = texture2D(tTop, tuv * sTop); triH = texture2D(tTopB, tuv * sTop).r; }
  else { tcol = texture2D(tSide, tuv * sSide); triH = texture2D(tSideB, tuv * sSide).r; }
  vec2 mac = texture2D(tMacro, vWP.xz * 0.0137 + vWP.y * 0.004).rg;
  tcol.rgb *= mix(1.0, 0.72 + 0.56 * mac.r, uMacro);
  tcol.rgb *= mix(uGround, 1.0, smoothstep(0.0, 1.4, vWP.y)) ;
  diffuseColor *= tcol;`)
      .replace('#include <normal_fragment_maps>', `#include <normal_fragment_maps>
  normal = perturbTri(-vViewPosition, normal, vec2(dFdx(triH), dFdy(triH)) * uBump * 0.35, faceDirection);`);
  };
  m.customProgramCacheKey = () => 'tri' + side.map.uuid + top.map.uuid;
  return m;
}

// Water: dark body colour, sky reflection from the environment map, flowing normals.
export function waterMat(normal, { color = 0x2a2a1c, flow = [0, 0.25], scale = 1.5, strength = 0.6, rough = 0.06, env = 0.6 } = {}) {
  const m = new THREE.MeshPhysicalMaterial({ color, roughness: rough, metalness: 0, clearcoat: 0.7, clearcoatRoughness: 0.04, envMapIntensity: env });
  m.normalMap = normal; m.normalScale = new THREE.Vector2(strength, strength);
  m.userData.time = { value: 0 };
  m.onBeforeCompile = (sh) => {
    sh.uniforms.uTime = m.userData.time; sh.uniforms.uFlow = { value: new THREE.Vector2(...flow) }; sh.uniforms.uScale = { value: scale };
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec3 vWP2;')
      .replace('#include <project_vertex>', '#include <project_vertex>\n vWP2 = (modelMatrix * vec4(transformed,1.0)).xyz;');
    sh.fragmentShader = sh.fragmentShader
      .replace('#include <common>', '#include <common>\nvarying vec3 vWP2; uniform float uTime, uScale; uniform vec2 uFlow;')
      .replace('#include <normal_fragment_maps>', `
  vec2 wuv = vWP2.xz / uScale;
  vec3 n1 = texture2D(normalMap, wuv + uFlow * uTime).xyz * 2.0 - 1.0;
  vec3 n2 = texture2D(normalMap, wuv * 0.63 + vec2(0.37, 0.11) + uFlow.yx * uTime * 0.55).xyz * 2.0 - 1.0;
  vec3 nn = normalize(vec3((n1.xy + n2.xy) * normalScale, 1.0));
  normal = normalize(tbnFromNormal(normal, nn));`)
      .replace('#include <clipping_planes_pars_fragment>', `#include <clipping_planes_pars_fragment>
vec3 tbnFromNormal(vec3 n, vec3 t) { vec3 up = abs(n.y) < 0.99 ? vec3(0.,1.,0.) : vec3(1.,0.,0.);
  vec3 T = normalize(cross(up, n)); vec3 B = cross(n, T); return T * t.x + B * t.y + n * t.z; }`);
  };
  m.customProgramCacheKey = () => 'water' + flow.join() + scale;
  return m;
}

// Sky dome with a sun glow; colours are uniforms so each shot can re-light it.
export function skyMat() {
  return new THREE.ShaderMaterial({
    side: THREE.BackSide, depthWrite: false, fog: false,
    uniforms: {
      zenith: { value: new THREE.Color() }, horizon: { value: new THREE.Color() }, ground: { value: new THREE.Color() },
      sunDir: { value: new THREE.Vector3(0, 1, 0) }, sunCol: { value: new THREE.Color() }, glow: { value: 1 },
    },
    vertexShader: `varying vec3 vD; void main(){ vD = normalize(position); vec4 p = projectionMatrix * modelViewMatrix * vec4(position,1.); gl_Position = p.xyww; }`,
    fragmentShader: `varying vec3 vD; uniform vec3 zenith, horizon, ground, sunDir, sunCol; uniform float glow;
      void main(){ float h = vD.y;
        vec3 c = h > 0. ? mix(horizon, zenith, pow(clamp(h,0.,1.), 0.55)) : mix(horizon, ground, clamp(-h*6.,0.,1.));
        float s = max(dot(normalize(vD), normalize(sunDir)), 0.);
        c += sunCol * (pow(s, 12.) * 0.35 + pow(s, 400.) * 3.0) * glow;
        gl_FragColor = vec4(c, 1.);
        #include <tonemapping_fragment>
        #include <colorspace_fragment>
      }`,
  });
}
