#ifndef PYMOL_WEBGL
#version 120
#else
precision highp float;
#endif

/*
 * Smooth edges in the viewport ("antialias_shader" 1): fast approximate
 * anti-aliasing after T. Lottes, in its short form. Where the brightness
 * changes sharply, the pixel is mixed with its neighbors along the edge.
 * One pass over the finished picture (SceneRenderAA).
 */

uniform sampler2D colorTex;
uniform vec2 inv_dimensions;

varying vec2 texcoordAttr;

float brightness(vec2 at)
{
  return dot(texture2D(colorTex, at).rgb, vec3(0.299, 0.587, 0.114));
}

void main()
{
  vec2 at = texcoordAttr;
  vec4 here = texture2D(colorTex, at);
  float m = dot(here.rgb, vec3(0.299, 0.587, 0.114));
  float nw = brightness(at + vec2(-1., -1.) * inv_dimensions);
  float ne = brightness(at + vec2(1., -1.) * inv_dimensions);
  float sw = brightness(at + vec2(-1., 1.) * inv_dimensions);
  float se = brightness(at + vec2(1., 1.) * inv_dimensions);
  float darkest = min(m, min(min(nw, ne), min(sw, se)));
  float lightest = max(m, max(max(nw, ne), max(sw, se)));

  // along the edge: across the direction in which the brightness changes
  vec2 along = vec2((sw + se) - (nw + ne), (nw + sw) - (ne + se));
  float least = max((nw + ne + sw + se) * 0.03125, 0.0078125);
  along = clamp(along / (min(abs(along.x), abs(along.y)) + least), -8., 8.) *
          inv_dimensions;

  vec3 near = 0.5 * (texture2D(colorTex, at - along / 6.).rgb +
                     texture2D(colorTex, at + along / 6.).rgb);
  vec3 far = 0.5 * near + 0.25 * (texture2D(colorTex, at - along / 2.).rgb +
                                  texture2D(colorTex, at + along / 2.).rgb);
  float reached = dot(far, vec3(0.299, 0.587, 0.114));
  // the wide mix left the range of the neighborhood: it crossed the edge
  gl_FragColor =
      vec4((reached < darkest || reached > lightest) ? near : far, here.a);
}
