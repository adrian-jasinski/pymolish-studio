#ifndef PYMOL_WEBGL
#version 120
#else
precision highp float;
#endif

/*
 * The halo of "glow" (15p): what is drawn, blurred, in a buffer 176 rows
 * high at any size of the picture (CShaderMgr::bindGlow). Three stages,
 * each one screen-filling rectangle (SceneRenderAA); fxaa.fs lays the
 * result around the molecule.
 *
 * 0: the picture times its cover, and the cover: 1 where something was
 *    drawn, found in the depth, so the background does not glow.
 * 1, 2: a bell curve of 13 points along x, then along y.
 */

uniform sampler2D colorTex;
uniform sampler2D depthTex;
uniform int stage;
uniform vec2 reach; // 0: a quarter of a halo texel; 1, 2: point to point

varying vec2 texcoordAttr;

void main()
{
  vec2 at = texcoordAttr;
  vec4 sum = vec4(0.);
  if (stage == 0) {
    // the centres of the four quarters of this texel of the halo
    for (int i = 0; i < 4; ++i) {
      vec2 p = at + reach * (vec2(mod(float(i), 2.), float(i / 2)) * 2. - 1.);
      float cover = texture2D(depthTex, p).r < 1. ? 1. : 0.;
      sum += vec4(texture2D(colorTex, p).rgb * cover, cover);
    }
    gl_FragColor = sum / 4.;
  } else {
    float total = 0.;
    for (int i = -6; i <= 6; ++i) {
      float weight = exp(-float(i * i) / 18.);
      sum += weight * texture2D(colorTex, at + reach * float(i));
      total += weight;
    }
    gl_FragColor = sum / total;
  }
}
