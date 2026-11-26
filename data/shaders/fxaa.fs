#ifndef PYMOL_WEBGL
#version 120
#else
precision highp float;
#endif

/*
 * The finished picture on its way to the screen (SceneRenderAA), in one
 * pass.
 *
 * Smooth edges ("antialias_shader" 1): fast approximate anti-aliasing
 * after T. Lottes, in its short form. Where the brightness changes
 * sharply, the pixel is mixed with its neighbors along the edge.
 *
 * Outline ("ray_trace_mode" 1 to 3 while "viewport_outline" is on): a line
 * where the picture lies behind its neighbors by more than a slope
 * explains, found in the depth. It falls on the far side of a step: beside
 * an atom on the atom behind it, around the molecule on the background.
 */

uniform sampler2D colorTex;
uniform vec2 inv_dimensions;
uniform bool smooth_edges;

uniform int outline; // ray_trace_mode: 1, 3 lines on the picture, 2 lines alone
uniform sampler2D depthTex; // of the finished picture
uniform sampler2D opaqueTex; // before what is see-through was drawn
uniform vec4 view; // front, back, orthoscopic?, A per pixel (at depth 1 unless so)
uniform vec3 line_color;
uniform vec3 fill_color;
uniform float line_width; // pixels

uniform float glow; // "glow": how much of the halo, 0 none
uniform sampler2D glowTex; // what is drawn, blurred (glow.fs)

varying vec2 texcoordAttr;

float brightness(vec2 at)
{
  return dot(texture2D(colorTex, at).rgb, vec3(0.299, 0.587, 0.114));
}

// distance from the eye in A
float depth(sampler2D tex, vec2 at)
{
  float d = texture2D(tex, at).r;
  return view.z > 0.5 ? view.x + d * (view.y - view.x)
                      : view.x * view.y / (view.y - d * (view.y - view.x));
}

// How far `z`, the depth at `at`, is behind the two neighbors on a line
// through it: nothing on a slope, the height of a step on its far side.
float behind(sampler2D tex, vec2 at, float z, vec2 step)
{
  return 2. * z - depth(tex, at - step) - depth(tex, at + step);
}

// 1 where a line is, 0 where none
float line(sampler2D tex, vec2 at)
{
  float z = depth(tex, at);
  vec2 x = vec2(line_width, 0.) * inv_dimensions;
  vec2 y = vec2(0., line_width) * inv_dimensions;
  float step = max(max(behind(tex, at, z, x), behind(tex, at, z, y)),
      max(behind(tex, at, z, 0.7 * (x + y)), behind(tex, at, z, 0.7 * (x - y))));
  // the crease between two atoms that touch is no line, at any zoom: the
  // least step grows with what a pixel covers
  float least = 0.5 + 4. * line_width * (view.z > 0.5 ? view.w : view.w * z);
  return smoothstep(least, 2. * least, step);
}

// No step near `at`: most of the picture, and there the rest is skipped.
bool level(sampler2D tex, vec2 at)
{
  float z = depth(tex, at);
  vec2 x = vec2(line_width + 1., 0.) * inv_dimensions;
  vec2 y = vec2(0., line_width + 1.) * inv_dimensions;
  float far = max(
      max(abs(depth(tex, at - x) - z), abs(depth(tex, at + x) - z)),
      max(abs(depth(tex, at - y) - z), abs(depth(tex, at + y) - z)));
  x *= 0.7;
  y *= 0.7;
  far = max(far, max(max(abs(depth(tex, at - x - y) - z),
                         abs(depth(tex, at + x + y) - z)),
                     max(abs(depth(tex, at - x + y) - z),
                         abs(depth(tex, at + x - y) - z))));
  return far < 0.25;
}

// How much of a line is at `at`, smoothed: a pixel beside the line gets a
// quarter of it.
float drawn(sampler2D tex, vec2 at)
{
  if (level(tex, at))
    return 0.;
  return min(1., 0.5 * line(tex, at) +
      0.25 * (line(tex, at + vec2(inv_dimensions.x, 0.)) +
              line(tex, at - vec2(inv_dimensions.x, 0.)) +
              line(tex, at + vec2(0., inv_dimensions.y)) +
              line(tex, at - vec2(0., inv_dimensions.y))));
}

void main()
{
  vec2 at = texcoordAttr;
  vec4 here = texture2D(colorTex, at);
  vec3 color = here.rgb;
  if (smooth_edges) {
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
    color = (reached < darkest || reached > lightest) ? near : far;
  }
  float alpha = here.a;
  // a line drawing: what is drawn has the color of the background
  if (outline == 2 && texture2D(depthTex, at).r < 1.)
    color = fill_color;
  if (outline != 0) {
    float lines = drawn(depthTex, at);
    // behind a see-through surface: what lies inside has its outline too
    if (texture2D(opaqueTex, at).r != texture2D(depthTex, at).r)
      lines = max(lines, drawn(opaqueTex, at));
    color = mix(color, line_color, lines);
    alpha = max(alpha, lines); // on a see-through background too
  }
  // a halo in the colors of what is drawn, around it: on the background
  // only, so the molecule itself stays as it is
  if (glow > 0. && texture2D(depthTex, at).r == 1.) {
    vec4 halo = texture2D(glowTex, at);
    float much = glow * min(1., 2. * halo.a);
    color = mix(color, halo.rgb / max(halo.a, 0.004), much);
    alpha = max(alpha, much);
  }
  gl_FragColor = vec4(color, alpha);
}
