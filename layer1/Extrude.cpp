
/* 
A* -------------------------------------------------------------------
B* This file contains source code for the PyMOL computer program
C* copyright 1998-2000 by Warren Lyford Delano of DeLano Scientific. 
D* -------------------------------------------------------------------
E* It is unlawful to modify or remove this copyright notice.
F* -------------------------------------------------------------------
G* Please see the accompanying LICENSE file for further information. 
H* --------------------------------------------------\-----------------
I* Additional authors of this source file include:
-* Cameron Mura
-* 
-*
Z* -------------------------------------------------------------------
*/

#include"os_predef.h"
#include"os_std.h"
#include"os_gl.h"

#include"Extrude.h"
#include"Base.h"
#include"Err.h"
#include"Setting.h"
#include"Feedback.h"
#include "MemoryDebug.h"
#include "CGO.h"
#include "AtomInfo.h"
#include "ObjectMolecule.h"

#include "pymol/algorithm.h"

static
void ExtrudeInit(PyMOLGlobals * G, CExtrude * I);

#define CopyArray(dst,src,type,count) memcpy(dst,src,sizeof(type)*(count))

CExtrude *ExtrudeCopyPointsNormalsColors(CExtrude * orig)
{
  int ok = true;
  auto I = new CExtrude();
  CHECKOK(ok, I);
  if (ok)
    ExtrudeInit(orig->G, I);

  if (ok)
    ok &= ExtrudeAllocPointsNormalsColors(I, orig->N);

  if (ok){
    CopyArray(I->p.get(), orig->p.get(), float, 3 * I->N);
    CopyArray(I->n.get(), orig->n.get(), float, 9 * I->N);
    CopyArray(I->c.get(), orig->c.get(), float, 3 * I->N);
    CopyArray(I->alpha.get(), orig->alpha.get(), float, I->N);
    CopyArray(I->i.get(), orig->i.get(), unsigned int, I->N);
    CopyArray(I->sf.get(), orig->sf.get(), float, I->N);      /* PUTTY: scale factors */
  } else {
    ExtrudeFree(I);
    I = nullptr;
  }
  return (I);
}

void ExtrudeInit(PyMOLGlobals * G, CExtrude * I)
{
  I->G = G;

  I->N = 0;
  I->Ns = 0;                    /* number of shape points */
}

int ExtrudeCircle(CExtrude * I, int n, float size)
{
  int a;
  float *v, *vn;
  int ok = true;
  PRINTFD(I->G, FB_Extrude)
    " ExtrudeCircle-DEBUG: entered.\n" ENDFD;
  /*
  if(n > 50)
  n = 50;*/

  I->sv.reset(new float[3 * (n + 1)]);
  I->sn.reset(new float[3 * (n + 1)]);
  I->tv.reset(new float[3 * (n + 1)]);
  I->tn.reset(new float[3 * (n + 1)]);

  if (ok){
    I->Ns = n;
    I->r = size;
    
    v = I->sv.get();
    vn = I->sn.get();
    
    for(a = 0; a <= n; a++) {
      *(vn++) = 0.0;
      *(vn++) = (float) cos(a * 2 * PI / n);
      *(vn++) = (float) sin(a * 2 * PI / n);
      *(v++) = 0.0;
      *(v++) = (float) cos(a * 2 * PI / n) * size;
      *(v++) = (float) sin(a * 2 * PI / n) * size;
    }
  }

  PRINTFD(I->G, FB_Extrude)
    " ExtrudeCircle-DEBUG: exiting...\n" ENDFD;
  return ok;
}

int ExtrudeOval(CExtrude * I, int n, float width, float length)
{
  int a;
  float *v, *vn;
  int ok = true;

  PRINTFD(I->G, FB_Extrude)
    " ExtrudeOval-DEBUG: entered.\n" ENDFD;

  /*  if(n > 50)
      n = 50;*/

  I->sv.reset(new float[3 * (n + 1)]);
  I->sn.reset(new float[3 * (n + 1)]);
  I->tv.reset(new float[3 * (n + 1)]);
  I->tn.reset(new float[3 * (n + 1)]);
  I->Ns = n;

  v = I->sv.get();
  vn = I->sn.get();

  for(a = 0; a <= n; a++) {
    *(vn++) = 0.0;
    *(vn++) = (float) cos(a * 2 * PI / n) * length;
    *(vn++) = (float) sin(a * 2 * PI / n) * width;
    *(v++) = 0.0;
    *(v++) = (float) cos(a * 2 * PI / n) * width;
    *(v++) = (float) sin(a * 2 * PI / n) * length;
  }

  PRINTFD(I->G, FB_Extrude)
    " ExtrudeOval-DEBUG: exiting...\n" ENDFD;
  return ok;
}

int ExtrudeRectangle(CExtrude * I, float width, float length, int mode)
{
  float *v, *vn;
  int ok = true;

  PRINTFD(I->G, FB_Extrude)
    " ExtrudeRectangle-DEBUG: entered...\n" ENDFD;

  switch (mode) {
  case 0:
    I->Ns = 8;
    break;
  default:
    I->Ns = 4;
    break;
  }

  I->sv.reset(new float[3 * (I->Ns + 1)]);
  I->sn.reset(new float[3 * (I->Ns + 1)]);
  I->tv.reset(new float[3 * (I->Ns + 1)]);
  I->tn.reset(new float[3 * (I->Ns + 1)]);

  v = I->sv.get();
  vn = I->sn.get();

  if((!mode) || (mode == 1)) {
    *(vn++) = 0.0;
    *(vn++) = 1.0;
    *(vn++) = 0.0;
    *(vn++) = 0.0;
    *(vn++) = 1.0;
    *(vn++) = 0.0;
    *(v++) = 0.0;
    *(v++) = (float) cos(PI / 4) * width;
    *(v++) = (float) -sin(PI / 4) * length;
    *(v++) = 0.0;
    *(v++) = (float) cos(PI / 4) * width;
    *(v++) = (float) sin(PI / 4) * length;
  }

  if((!mode) || (mode == 2)) {
    *(vn++) = 0.0;
    *(vn++) = 0.0;
    *(vn++) = 1.0;
    *(vn++) = 0.0;
    *(vn++) = 0.0;
    *(vn++) = 1.0;
    *(v++) = 0.0;
    *(v++) = (float) cos(PI / 4) * width;
    *(v++) = (float) sin(PI / 4) * length;
    *(v++) = 0.0;
    *(v++) = (float) -cos(PI / 4) * width;
    *(v++) = (float) sin(PI / 4) * length;
  }

  if((!mode) || (mode == 1)) {
    *(vn++) = 0.0;
    *(vn++) = -1.0;
    *(vn++) = 0.0;
    *(vn++) = 0.0;
    *(vn++) = -1.0;
    *(vn++) = 0.0;
    *(v++) = 0.0;
    *(v++) = (float) -cos(PI / 4) * width;
    *(v++) = (float) sin(PI / 4) * length;
    *(v++) = 0.0;
    *(v++) = (float) -cos(PI / 4) * width;
    *(v++) = (float) -sin(PI / 4) * length;
  }

  if((!mode) || (mode == 2)) {

    *(vn++) = 0.0;
    *(vn++) = 0.0;
    *(vn++) = -1.0;
    *(vn++) = 0.0;
    *(vn++) = 0.0;
    *(vn++) = -1.0;
    *(v++) = 0.0;
    *(v++) = (float) -cos(PI / 4) * width;
    *(v++) = (float) -sin(PI / 4) * length;
    *(v++) = 0.0;
    *(v++) = (float) cos(PI / 4) * width;
    *(v++) = (float) -sin(PI / 4) * length;
  }

  PRINTFD(I->G, FB_Extrude)
    " ExtrudeRectangle-DEBUG: exiting...\n" ENDFD;
  return ok;
}

int ExtrudeDumbbell1(CExtrude * I, float width, float length, int mode)
{
  float *v, *vn;
  int ok = true;

  PRINTFD(I->G, FB_Extrude)
    " ExtrudeDumbbell1-DEBUG: entered...\n" ENDFD;

  switch (mode) {
  case 0:
    I->Ns = 4;
    break;
  default:
    I->Ns = 2;
    break;

  }

  I->sv.reset(new float[3 * (I->Ns + 1)]);
  I->sn.reset(new float[3 * (I->Ns + 1)]);
  I->tv.reset(new float[3 * (I->Ns + 1)]);
  I->tn.reset(new float[3 * (I->Ns + 1)]);

  v = I->sv.get();
  vn = I->sn.get();

  if((!mode) || (mode == 1)) {  /* top */
    *(vn++) = 0.0;
    *(vn++) = 1.0;
    *(vn++) = 0.0;
    *(vn++) = 0.0;
    *(vn++) = 1.0;
    *(vn++) = 0.0;
    *(v++) = 0.0;
    *(v++) = (float) cos(PI / 4) * width;
    *(v++) = (float) -sin(PI / 4) * length;
    *(v++) = 0.0;
    *(v++) = (float) cos(PI / 4) * width;
    *(v++) = (float) sin(PI / 4) * length;
  }

  if((!mode) || (mode == 2)) {  /* bottom */
    *(vn++) = 0.0;
    *(vn++) = -1.0;
    *(vn++) = 0.0;
    *(vn++) = 0.0;
    *(vn++) = -1.0;
    *(vn++) = 0.0;
    *(v++) = 0.0;
    *(v++) = (float) -cos(PI / 4) * width;
    *(v++) = (float) sin(PI / 4) * length;
    *(v++) = 0.0;
    *(v++) = (float) -cos(PI / 4) * width;
    *(v++) = (float) -sin(PI / 4) * length;
  }

  PRINTFD(I->G, FB_Extrude)
    " ExtrudeDumbbell1-DEBUG: exiting...\n" ENDFD;
  return ok;
}

void ExtrudeDumbbellEdge(CExtrude * I, int samp, int sign, float length)
{
  int a;
  float *n, *p, f, disp;

  PRINTFD(I->G, FB_Extrude)
    " ExtrudeDumbbellEdge-DEBUG: entered.\n" ENDFD;
  disp = (float) (sign * sin(PI / 4) * length);
  p = I->p.get();
  n = I->n.get();
  for(a = 0; a < I->N; a++) {
    if(a <= samp)
      f = disp * smooth((a / ((float) samp)), 2);
    else if(a >= (I->N - samp))
      f = disp * smooth(((I->N - a - 1) / ((float) samp)), 2);
    else
      f = disp;
    n += 6;
    (*p++) += *(n++) * f;
    (*p++) += *(n++) * f;
    (*p++) += *(n++) * f;
  }
  PRINTFD(I->G, FB_Extrude)
    " ExtrudeDumbbellEdge-DEBUG: exiting...\n" ENDFD;

}


CExtrude *ExtrudeNew(PyMOLGlobals * G)
{
  auto I = new CExtrude();
  ExtrudeInit(G, I);
  return (I);
}

void ExtrudeBuildNormals1f(CExtrude * I)
{
  int a;
  float *v;

  PRINTFD(I->G, FB_Extrude)
    " ExtrudeBuildNormals1f-DEBUG: entered.\n" ENDFD;

  if(I->N) {
    get_system1f3f(I->n.get(), I->n.get() + 3, I->n.get() + 6);   /* first is arbitrary */
    v = I->n.get() + 9;
    for(a = 1; a < I->N; a++) {
      copy3f(v - 6, v + 3);
      get_system2f3f(v, v + 3, v + 6);  /* the rest are relative to first */
      v += 9;
    }
  }

  PRINTFD(I->G, FB_Extrude)
    " ExtrudeBuildNormals1f-DEBUG: exiting...\n" ENDFD;

}

void ExtrudeBuildNormals2f(CExtrude * I)
{
  int a;
  float *v;
  PRINTFD(I->G, FB_Extrude)
    " ExtrudeBuildNormals2f-DEBUG: entered.\n" ENDFD;

  if(I->N) {
    v = I->n.get();
    for(a = 0; a < I->N; a++) {
      get_system2f3f(v, v + 3, v + 6);
      v += 9;
    }
  }

  PRINTFD(I->G, FB_Extrude)
    " ExtrudeBuildNormals2f-DEBUG: entering...\n" ENDFD;

}

/**
 * Approximate a helix center trace.
 *
 * - shifts points to the helix center
 * - smoothes the points curve (low-pass filter)
 *
 * @pre I has helix geometry
 * @post I has linear geometry along helix axis
 * @post I has normals
 *
 * @param[in,out] I data structure to modify in-place.
 * @param radius Cylindrical helix radius (for optimizing end points)
 * @param sampling Samples per residue
 */
void ExtrudeShiftToAxis(CExtrude* I, float radius, int sampling)
{
  assert(I->N > 1);

  constexpr float loop_radius = 0.2f;
  const int smooth_cycles =
      SettingGet<int>(I->G, cSetting_cartoon_smooth_cylinder_cycles);
  const int smooth_window =
      SettingGet<int>(I->G, cSetting_cartoon_smooth_cylinder_window);

  float p_start[3];
  float p_end[3];

  // original start and end points
  copy3(I->p.get(), p_start);
  copy3(I->p.get() + (I->N - 1) * 3, p_end);

  ExtrudeBuildNormals2f(I);

  // Because segments have open ends, we don't have ideal helix normals for the
  // first and last position. We can reconstruct the desired normals from the
  // next position by an ideal rotation.
  if (I->N > 2) {

    // ideal rotation from one alpha helix residue to the next
    static float const residue_rotation[9] = {
        0.224, -0.809, -0.544, 0.809, -0.157, 0.567, -0.544, -0.567, 0.619};
    static float const residue_rotation_inv[9] = {
        0.224, 0.809, -0.544, -0.809, -0.157, -0.567, -0.544, 0.567, 0.619};

    multiply33f33f(residue_rotation_inv, //
        I->n.get() + 9 * sampling, I->n.get());
    multiply33f33f(residue_rotation, //
        I->n.get() + 9 * (I->N - 1 - sampling), I->n.get() + 9 * (I->N - 1));
  }

  // move points to helix axes
  for (int a = 0; a < I->N; ++a) {
    float* point = I->p.get() + a * 3;
    const float* normal = I->n.get() + a * 9 + 3;

    // distance to move point (distance between C-alpha atom and helix axis)
    float factor = 2.3;

    // keep end points close enough to adjacent segments so they overlap
    if (a == 0 || a + 1 == I->N) {
      factor = std::min(factor, radius - loop_radius);
    }

    float tmp[3];
    scale3f(normal, -factor, tmp);
    add3f(point, tmp, point);
  }

  // window averaging of point positions
  if (I->N > 2 && smooth_window > 0) {
    int const w2 = sampling * smooth_window;

    for (int i = 0; i < smooth_cycles; ++i) {
      std::vector<float> smoothed((I->N - 2) * 3);

      for (int a = 1; a + 1 < I->N; ++a) {
        float* avg = smoothed.data() + (a - 1) * 3;

        for (int j = -w2; j <= w2; ++j) {
          int const k = std::clamp(a + j, 0, I->N - 1);
          add3f(I->p.get() + k * 3, avg, avg);
        }

        scale3f(avg, 1. / (2 * w2 + 1), avg);
      }

      std::copy(smoothed.begin(), smoothed.end(), I->p.get() + 3);
    }
  }

  ExtrudeComputeTangents(I);
  ExtrudeBuildNormals1f(I);

  // extend tips for better geometry overlap with adjacent segments
  auto const push_out_tip = [&](int index, float const* pos_orig,
                                int direction) {
    float const protrusion = loop_radius * 2;
    float const* normal = I->n.get() + index * 9;
    float* pos = I->p.get() + index * 3;
    float offset[3];
    subtract3f(pos_orig, pos, offset);
    float const len = project3f(offset, normal, offset) * direction;
    if (len > -protrusion) {
      scale3f(normal, (len + protrusion) * direction, offset);
      add3f(pos, offset, pos);
    }
  };

  push_out_tip(0, p_start, -1);
  push_out_tip(I->N - 1, p_end, 1);
}


int ExtrudeComputeTangents(CExtrude * I)
{
  float *v1, *v;
  int a;
  int ok = true;

  PRINTFD(I->G, FB_Extrude)
    " ExtrudeComputeTangents-DEBUG: entered.\n" ENDFD;

  std::vector<float> nv(I->N * 3);

  v = nv.data();
  v1 = I->p.get() + 3;

  for(a = 1; a < I->N; a++) {
    subtract3f(v1, v1 - 3, v);
    normalize3f(v);
    v += 3;
    v1 += 3;
  }

  /* compute tangents */

  v = nv.data();
  v1 = I->n.get();

  *(v1++) = *(v++);             /* first segment */
  *(v1++) = *(v++);
  *(v1++) = *(v++);
  v1 += 6;

  for(a = 1; a < (I->N - 1); a++) {

    add3f(v, (v - 3), v1);
    normalize3f(v1);
    v1 += 9;
    v += 3;
  }

  *(v1++) = *(v - 3);           /* last segment */
  *(v1++) = *(v - 2);
  *(v1++) = *(v - 1);

  PRINTFD(I->G, FB_Extrude)
    " ExtrudeComputeTangents-DEBUG: exiting...\n" ENDFD;
  return ok;
}


/**
 * Draw flat cap on a tube cartoon (loop, oval, etc.)
 *
 * I: tube instance
 * cgo: CGO to add to
 * index: sampling index in `I`
 * inv_dir: inverse direction of normal if true
 * color: RGB color or nullptr to use color from `I`
 */
static
void TubeCapFlat(const CExtrude * I, CGO * cgo, int index, bool inv_dir, const float * color) {
  const float * vertex = I->p.get() + 3 * index;
  const float * base33 = I->n.get() + 9 * index;
  const float * normal = base33;
  float tmp3f[3];
  int b_end = -1, b_incr = -1;

  if (inv_dir) {
    copy3f(normal, tmp3f);
    invert3f(tmp3f);
    normal = tmp3f;
  } else {
    b_end = I->Ns * 2 + 1;
    b_incr = 1;
  }

  CGOBegin(cgo, GL_TRIANGLE_FAN);
  CGOColorv(cgo, color ? color : (I->c.get() + 3 * index));
  CGOAlpha(cgo, I->alpha[index]);
  CGOPickColor(cgo, I->i[index], cPickableAtom);
  CGONormalv(cgo, normal); // (tmp3f again free to use)
  CGOVertexv(cgo, vertex); // center

  // Indexing trickery: going in a loop, visiting first index twice to
  // close the loop. Iterating backwards in case of `inv_dir`.
  for (int b = I->Ns; b != b_end; b += b_incr) {
    transform33Tf3f(base33, I->sv.get() + (b % I->Ns) * 3, tmp3f);
    add3f(vertex, tmp3f, tmp3f);
    CGOVertexv(cgo, tmp3f);
  }

  CGOEnd(cgo);
  CGOPickColor(cgo, -1, cPickableNoPick);
}

/**
 * I: tube instance
 * cgo: CGO to add to
 * cap: 0: no caps, 1: flat caps, 2: round caps
 * color_override: RGB color or nullptr to use color from `I`
 * use_spheres: do round caps with spheres instead of triangles
 * dash: if > 0, skip every segment which is a multiple of `dash`
 */
int ExtrudeCGOSurfaceTube(const CExtrude* I, CGO* cgo, cCylCap cap,
    const float* color_override, bool use_spheres, int dash)
{
  int a, b;
  unsigned int *i;
  float *v;
  float *n;
  float *c;
  const float *alpha;
  float *sv, *sn, *tv, *tn, *tv1, *tn1;
  int start, stop;
  int ok = true;
  PRINTFD(I->G, FB_Extrude)
    " ExtrudeCGOSurfaceTube-DEBUG: entered.\n" ENDFD;

  if(I->N && I->Ns) {
    std::vector<float> TV(3 * (I->Ns + 1) * I->N);
    std::vector<float> TN(3 * (I->Ns + 1) * I->N);
    /* compute transformed shape vertices */

    if (ok){
      tn = TN.data();
      tv = TV.data();
      
      sv = I->sv.get();
      sn = I->sn.get();
      for(b = 0; b <= I->Ns; b++) {
	if(b == I->Ns) {
	  sv = I->sv.get();
	  sn = I->sn.get();
	}
	v = I->p.get();
	n = I->n.get();
	
	for(a = 0; a < I->N; a++) {
	  transform33Tf3f(n, sv, tv);
	  add3f(v, tv, tv);
	  tv += 3;
	  transform33Tf3f(n, sn, tn);
	  tn += 3;
	  n += 9;
	  v += 3;
	}
	sv += 3;
	sn += 3;
      }
      
      start = I->Ns / 4;
      stop = 3 * I->Ns / 4;
    }

    // first loop: axial, for dashes (skipping segments)
    for (int a_start = 0, a_incr = (dash ? dash : I->N);
        a_start < I->N - 1;
        a_start += a_incr) {

      int a_end = a_start + a_incr;
      if (a_end > I->N)
        a_end = I->N;

      // second loop: circumferential, setting up axial triangle strips
      for(b = 0; ok && b < I->Ns; b++) {
	if(SettingGetGlobal_i(I->G, cSetting_cartoon_debug) < 1.5)
	  ok &= CGOBegin(cgo, GL_TRIANGLE_STRIP);
	else {
	  ok &= CGOBegin(cgo, GL_LINE_STRIP);
	}
	if (ok){
          c = I->c.get() + a_start * 3;
          alpha = I->alpha.get() + a_start;
          i = I->i.get() + a_start;

          tv = TV.data() + 3 * (a_start + b * I->N);
          tn = TN.data() + 3 * (a_start + b * I->N);

          tv1 = tv + 3 * I->N;
          tn1 = tn + 3 * I->N;

          // third loop: axial, segments within one "dash"
          for(a = a_start; ok && a < a_end; ++a) {
	    if(color_override && (b > start) && (b < stop))
	      ok &= CGOColorv(cgo, color_override);
	    else
	      ok &= CGOColorv(cgo, c);
        if (ok){
          ok &= CGOAlpha(cgo, *alpha);
        }
	    if (ok)
	      ok &= CGOPickColor(cgo, *i, cPickableAtom);
	    if (ok)
	      ok &= CGONormalv(cgo, tn);
	    if (ok)
	      ok &= CGOVertexv(cgo, tv);
	    tn += 3;
	    tv += 3;
	    if (ok)
	      ok &= CGONormalv(cgo, tn1);
	    if (ok)
	      ok &= CGOVertexv(cgo, tv1);
	    tn1 += 3;
	    tv1 += 3;
	    c += 3;
        alpha++;
	    i++;
	  }
	}
	if (ok)
	  ok &= CGOEnd(cgo);
	if (ok)
	  ok &= CGOPickColor(cgo, -1, cPickableNoPick);
      }

      if (cap == cCylCap::Flat) {
        TubeCapFlat(I, cgo, a_start, true, color_override);
        TubeCapFlat(I, cgo, a_end - 1, false, color_override);
      }
    }

    if (ok){
    switch (cap) {
    case cCylCap::Round:
      {
	float p0[3], p1[3], p2[3], z1, z2, normal[3], vertex1[3];
	float c, d, prev, x, y, *v1, nEdge = I->Ns, nEdgeH = 2.f * floor(I->Ns/2.f);

	if (ok){
	  n = I->n.get();
	  v = I->p.get();
	  sv = I->sv.get();
	  tv = I->tv.get();
	  for(b = 0; b < I->Ns; b++) {
	    transform33Tf3f(n, sv, tv);
	    add3f(v, tv, tv);
	    sv += 3;
	    tv += 3;
	  }
	  
	  copy3f(I->n.get(), p0);
	  invert3f(p0);
	  transform33Tf3f(I->n.get(), I->sv.get(), p1);
	  cross_product3f(p0, p1, p2);
	  normalize3f(p1);
	  normalize3f(p2);
	}
	if (ok){
	  if(color_override)
	    ok &= CGOColorv(cgo, color_override);
	  else
	    ok &= CGOColorv(cgo, I->c.get());
	}
    if (ok){
      ok &= CGOAlpha(cgo, I->alpha[0]);
    }
	if (ok)
	  ok &= CGOPickColor(cgo, I->i[0], cPickableAtom);
	if (ok){
        v = I->p.get();
	if (use_spheres){
	  ok &= CGOSphere(cgo, v, I->r); // this matches the Cylinder
	} else {
	  /* If we don't use spheres, then we need to have the rounded cap
	   * line up with the geometry perfectly.  We generate the cap using 
	   * spheracle coordinates, then for the last line (i.e., last=true)
	   * we use the coordinates from the geometry (i.e., exactly 
	   * how they were genereated from I->n and I->sv).  This is so that 
	   * the vertices line up perfectly. */
	  nEdge = I->Ns;
	  ok &= CGOBegin(cgo, GL_TRIANGLE_STRIP);
	  z1 = z2 = 1.f;
	  prev = 1.f;
	  v1 = v;
	  tv = I->tv.get();
	  for (c = 1; ok && c <= (nEdgeH/2); c++){
	    short last = (c + 1) > (nEdgeH/2);
	    z1 = z2;
	    z2 = (float) cos((c) * PI / ((float)nEdgeH));
	    for (d = 0; d <= nEdge; d++){
	      x = (float) cos((d) * 2 * PI / (float)nEdge) * sin((c-prev) * PI / (float)nEdgeH);
	      y = (float) sin((d) * 2 * PI / (float)nEdge) * sin((c-prev) * PI / (float)nEdgeH);
	      normal[0] = p1[0] * x + p2[0] * y + p0[0] * z1;
	      normal[1] = p1[1] * x + p2[1] * y + p0[1] * z1;
	      normal[2] = p1[2] * x + p2[2] * y + p0[2] * z1;
	      vertex1[0] = v1[0] + normal[0] * I->r;
	      vertex1[1] = v1[1] + normal[1] * I->r;
	      vertex1[2] = v1[2] + normal[2] * I->r;
	      normalize3f(normal);
	      ok &= CGONormalv(cgo, normal);	  
	      if (ok)
		ok &= CGOVertexv(cgo, vertex1);
	      
	      if (ok){
	      if (last){
		float *vert = tv + 3*(((int)(nEdge-d))%((int)nEdge));
		subtract3f(vert, v, normal);
		ok &= CGONormalv(cgo, normal);
		if (ok)
		  ok &= CGOVertexv(cgo, vert);
	      } else {
		x = (float) cos((d) * 2 * PI / (float)nEdge) * sin((c) * PI / (float)nEdgeH);
		y = (float) sin((d) * 2 * PI / (float)nEdge) * sin((c) * PI / (float)nEdgeH);
		normal[0] = p1[0] * x + p2[0] * y + p0[0] * z2;
		normal[1] = p1[1] * x + p2[1] * y + p0[1] * z2;
		normal[2] = p1[2] * x + p2[2] * y + p0[2] * z2;
		vertex1[0] = v1[0] + normal[0] * I->r;
		vertex1[1] = v1[1] + normal[1] * I->r;
		vertex1[2] = v1[2] + normal[2] * I->r;
		normalize3f(normal);
		ok &= CGONormalv(cgo, normal);	  
		if (ok)
		  ok &= CGOVertexv(cgo, vertex1);
	      }
	      }
	    }
	  }
	  if (ok)
	    ok &= CGOEnd(cgo);
	  if (ok)
	    ok &= CGOPickColor(cgo, -1, cPickableNoPick);
	}

	if (ok){
	  n = I->n.get() + 9 * (I->N - 1);
	  v = I->p.get() + 3 * (I->N - 1);
	  sv = I->sv.get();
	  tv = I->tv.get();
	  for(b = 0; b < I->Ns; b++) {
	    transform33Tf3f(n, sv, tv);
	    add3f(v, tv, tv);
	    sv += 3;
	    tv += 3;
	  }
	  
	  copy3f(n, p0);
	  transform33Tf3f(n, I->sv.get(), p1);
	  cross_product3f(p0, p1, p2);
	  normalize3f(p1);
	  normalize3f(p2);
	  
	  if(color_override)
	    ok &= CGOColorv(cgo, color_override);
	  else
	    ok &= CGOColorv(cgo, I->c.get() + 3 * (I->N - 1));
	}
    if (ok){
      ok &= CGOAlpha(cgo, I->alpha[I->N - 1]);
    }
	if (ok)
	  ok &= CGOPickColor(cgo, I->i[I->N - 1], cPickableAtom);

	if (ok){
	if (use_spheres){
	  ok &= CGOSphere(cgo, v, I->r); // this matches the Cylinder
	} else {
	  /* If we don't use spheres, then we need to have the rounded cap
	   * line up with the geometry perfectly.  We generate the cap using 
	   * spheracle coordinates, then for the last line (i.e., last=true)
	   * we use the coordinates from the geometry (i.e., exactly 
	   * how they were genereated from I->n and I->sv).  This is so that 
	   * the vertices line up perfectly. */
	  nEdge = I->Ns;
	  ok &= CGOBegin(cgo, GL_TRIANGLE_STRIP);
	  z1 = z2 = 1.f;
	  prev = 1.f;
	  v1 = v;
	  tv = I->tv.get();
	  for (c = 1; ok && c <= (nEdgeH/2); c++){
	    short last = (c + 1) > (nEdgeH/2);
	    z1 = z2;
	    z2 = (float) cos((c) * PI / ((float)nEdgeH));
	    for (d = 0; d <= nEdge; d++){
	      x = (float) cos((d) * 2 * PI / (float)nEdge) * sin((c-prev) * PI / (float)nEdgeH);
	      y = (float) sin((d) * 2 * PI / (float)nEdge) * sin((c-prev) * PI / (float)nEdgeH);
	      normal[0] = p1[0] * x + p2[0] * y + p0[0] * z1;
	      normal[1] = p1[1] * x + p2[1] * y + p0[1] * z1;
	      normal[2] = p1[2] * x + p2[2] * y + p0[2] * z1;
	      vertex1[0] = v1[0] + normal[0] * I->r;
	      vertex1[1] = v1[1] + normal[1] * I->r;
	      vertex1[2] = v1[2] + normal[2] * I->r;
	      normalize3f(normal);
	      ok &= CGONormalv(cgo, normal);	  
	      if (ok)
		ok &= CGOVertexv(cgo, vertex1);
	      
	      if (ok){
	      if (last){
		float *vert = tv + 3*(((int)(d))%((int)nEdge));
		subtract3f(vert, v, normal);
		ok &= CGONormalv(cgo, normal);
		if (ok)
		  ok &= CGOVertexv(cgo, vert);
	      } else {
		x = (float) cos((d) * 2 * PI / (float)nEdge) * sin((c) * PI / (float)nEdgeH);
		y = (float) sin((d) * 2 * PI / (float)nEdge) * sin((c) * PI / (float)nEdgeH);
		normal[0] = p1[0] * x + p2[0] * y + p0[0] * z2;
		normal[1] = p1[1] * x + p2[1] * y + p0[1] * z2;
		normal[2] = p1[2] * x + p2[2] * y + p0[2] * z2;
		vertex1[0] = v1[0] + normal[0] * I->r;
		vertex1[1] = v1[1] + normal[1] * I->r;
		vertex1[2] = v1[2] + normal[2] * I->r;
		normalize3f(normal);
		ok &= CGONormalv(cgo, normal);	  
		if (ok)
		  ok &= CGOVertexv(cgo, vertex1);
	      }
	      }
	    }
	  }
	  if (ok)
	    ok &= CGOEnd(cgo);
	  if (ok)
	    ok &= CGOPickColor(cgo, -1, cPickableNoPick);
	}
	}
	}
      }
      break;
    }
    }
  }

  PRINTFD(I->G, FB_Extrude)
    " ExtrudeCGOSurfaceTube-DEBUG: exiting...\n" ENDFD;
  return ok;
}

int ExtrudeCylindersToCGO(CExtrude * I, CGO * cgo, float tube_radius){
  float *v1, *c1, midc[3], axis[3];
  const float *alpha;
  int a;
  unsigned int *i;
  int ok = true;

  PRINTFD(I->G, FB_Extrude)
    " ExtrudeCylindersToCGO-DEBUG: entered.\n" ENDFD;

  v1 = I->p.get() + 3;
  c1 = I->c.get() + 3;
  alpha = I->alpha.get() + 1;
  i = I->i.get() + 1;
  
  int cap = (cCylShaderBothCapsRound | cCylShaderInterpColor);
  for(a = 1; a < I->N; a++) {
    average3f(c1-3, c1, midc);
    ok &= CGOPickColor(cgo, *(i-1), cPickableAtom);
    subtract3f(v1, v1-3, axis);
    CGOColorv(cgo, c1-3);
    CGOAlpha(cgo, *(alpha-1));
    Pickable pickcolor2 = { *i, cPickableAtom };
    cgo->add<cgo::draw::shadercylinder2ndcolor>(cgo, v1-3, axis, tube_radius, cap, c1, &pickcolor2);
    v1 += 3;
    c1 += 3;
    alpha++;
    i++;
    cap = cCylShaderCap2Round | cCylShaderInterpColor;
  }
  if (ok)
    ok &= CGOPickColor(cgo, 0, cPickableNoPick);

  PRINTFD(I->G, FB_Extrude)
    " ExtrudeCylindersToCGO-DEBUG: exiting...\n" ENDFD;
  return ok;
}

int ExtrudeCGOSurfaceVariableTube(const CExtrude* I, CGO* cgo, cCylCap cap)
{
  int a, b;
  unsigned int *i;
  float *v;
  float *n;
  float *c;
  const float *alpha;
  float *sv, *sn, *tv, *tn, *tv1, *tn1, *an;
  float v0[3];
  float *sf;                    /* PUTTY: scale factor from ExtrudeMakeSausLUT() */
  int ok = true;
  PRINTFD(I->G, FB_Extrude)
    " ExtrudeCGOSurfaceTube-DEBUG: entered.\n" ENDFD;

  if(I->N && I->Ns) {

    std::vector<float> TV(3 * (I->Ns + 1) * I->N);
    std::vector<float> TN(3 * (I->Ns + 1) * I->N);
    std::vector<float> AN(3 * I->N);        /* normals adjusted for changing widths */

    /* compute transformed shape vertices */

    tv = TV.data();

    sv = I->sv.get();
    for(b = 0; b <= I->Ns; b++) {
      if(b == I->Ns) {
        sv = I->sv.get();
      }

      n = I->n.get();                 /* NOTE: n is not a counter -- it's a 3x3 coordinate system! */
      v = I->p.get();
      sf = I->sf.get();               /* PUTTY: scale factors */

      for(a = 0; a < I->N; a++) {
        transform33Tf3f(n, sv, tv);

        *(tv) *= *sf;
        *(tv + 1) *= *sf;
        *(tv + 2) *= *sf;

        add3f(v, tv, tv);
        tv += 3;
        v += 3;
        sf++;
        n += 9;
      }
      sv += 3;
    }

    /* compute transformed normals, taking into account changing radii */

    tn = TN.data();
    tv = TV.data();

    sn = I->sn.get();
    for(b = 0; b <= I->Ns; b++) {

      float d1, d2, r0, r1, r2, x1, x2;

      if(b == I->Ns) {
        sn = I->sn.get();
      }

      an = AN.data();
      v = I->p.get();

      for(a = 0; a < I->N; a++) {
        if((a > 0) && (a < (I->N - 1))) {
          /* compute rises */

          r0 = (float) diff3f(v, tv);
          r1 = (float) (diff3f(v - 3, tv - 3) - r0);
          r2 = (float) (diff3f(v + 3, tv + 3) - r0);

          /* compute runs */

          d1 = (float) diff3f(v - 3, v);
          d2 = (float) diff3f(v + 3, v);

          /* compute x-to-yz weights */

          x1 = r1 / d1;
          x2 = -r2 / d2;

          if(a == 1) {
            an[-3] = x1;
            an[-2] = sn[1];
            an[-1] = sn[2];
            normalize3f(an - 3);
          } else if(a == I->N - 2) {
            an[3] = x2;
            an[4] = sn[1];
            an[5] = sn[2];
            normalize3f(an + 3);
          }
          an[0] = (x1 + x2) / 2.0F;
          an[1] = sn[1];
          an[2] = sn[2];
          normalize3f(an);
        }
        tv += 3;
        v += 3;
        an += 3;
      }

      n = I->n.get();                 /* NOTE: n is not a counter -- it's a 3x3 coordinate system! */
      an = AN.data();

      for(a = 0; a < I->N; a++) {
        transform33Tf3f(n, an, tn);
        tn += 3;
        an += 3;
        n += 9;
      }
      sn += 3;
    }

    /* fill in each strip separately */

    tv = TV.data();
    tn = TN.data();

    tv1 = TV.data() + 3 * I->N;
    tn1 = TN.data() + 3 * I->N;

    for(b = 0; b < I->Ns; b++) {
      if(SettingGetGlobal_i(I->G, cSetting_cartoon_debug) < 1.5)
        CGOBegin(cgo, GL_TRIANGLE_STRIP);
      else {
        CGOBegin(cgo, GL_LINE_STRIP);
      }
      c = I->c.get();
      alpha = I->alpha.get();
      i = I->i.get();
      for(a = 0; a < I->N; a++) {
        CGOColorv(cgo, c);
        CGOAlpha(cgo, *alpha);
        CGOPickColor(cgo, *i, cPickableAtom);
        CGONormalv(cgo, tn);
        CGOVertexv(cgo, tv);
        tn += 3;
        tv += 3;
        CGONormalv(cgo, tn1);
        CGOVertexv(cgo, tv1);
        tn1 += 3;
        tv1 += 3;
        c += 3;
        alpha++;
        i++;
      }
      CGOEnd(cgo);
      CGOPickColor(cgo, -1, cPickableNoPick);
    }

    if(ok && SettingGetGlobal_i(I->G, cSetting_cartoon_debug) > 3.5) {

      tv = TV.data();
      tn = TN.data();

      tv1 = TV.data() + 3 * I->N;
      tn1 = TN.data() + 3 * I->N;

      for(b = 0; b < I->Ns; b++) {
        float vv[3];
	  CGOBegin(cgo, GL_LINES);
	  c = I->c.get();
      alpha = I->alpha.get();
	  i = I->i.get();
	  for(a = 0; a < I->N; a++) {
	    CGOColorv(cgo, c);
        CGOAlpha(cgo, *alpha);
	    copy3f(tn, vv);
	    scale3f(vv, 0.3F, vv);
	    add3f(vv, tv, vv);
	    CGONormalv(cgo, tn);
	    CGOVertexv(cgo, tv);
	    CGOVertexv(cgo, vv);
	    tn += 3;
	    tv += 3;
	    copy3f(tn1, vv);
	    scale3f(vv, 0.3F, vv);
	    add3f(vv, tv1, vv);
	    CGONormalv(cgo, tn1);
	    CGOVertexv(cgo, tv1);
	    CGOVertexv(cgo, vv);
	    tn1 += 3;
	    tv1 += 3;
	    c += 3;
        alpha++;
	    i++;
	  }
	  CGOEnd(cgo);
      }
    }

    if(ok && cap != cCylCap::None) {

      n = I->n.get();
      v = I->p.get();
      sf = I->sf.get();

      sv = I->sv.get();
      tv = I->tv.get();
      for(b = 0; b < I->Ns; b++) {
        transform33Tf3f(n, sv, tv);

        *(tv) *= *sf;
        *(tv + 1) *= *sf;
        *(tv + 2) *= *sf;

        add3f(v, tv, tv);
        sv += 3;
        tv += 3;
      }
      CGOBegin(cgo, GL_TRIANGLE_FAN);
      copy3f(I->n.get(), v0);
      invert3f(v0);
      CGOColorv(cgo, I->c.get());
      CGOAlpha(cgo, I->alpha[0]);
      CGOPickColor(cgo, I->i[0], cPickableAtom);
      CGONormalv(cgo, v0);
      if (ok) {
	CGOVertexv(cgo, v);
	/* trace shape */
	CGOVertexv(cgo, I->tv.get());
	for(b = I->Ns - 1; b >= 0; b--) {
	  CGOVertexv(cgo, I->tv.get() + b * 3);
	}
	CGOEnd(cgo);
	n = I->n.get() + 9 * (I->N - 1);
	v = I->p.get() + 3 * (I->N - 1);
	sf = I->sf.get() + (I->N - 1);  /* PUTTY */
	
	sv = I->sv.get();
	tv = I->tv.get();
	for(b = 0; b < I->Ns; b++) {
	  transform33Tf3f(n, sv, tv);
	  
	  *(tv) *= *(sf);
	  *(tv + 1) *= *(sf);
	  *(tv + 2) *= *(sf);
	  
	  add3f(v, tv, tv);
	  sv += 3;
	  tv += 3;
	}
	
	CGOBegin(cgo, GL_TRIANGLE_FAN);
	CGOColorv(cgo, I->c.get() + 3 * (I->N - 1));
    CGOAlpha(cgo, I->alpha[I->N - 1]);
	CGOPickColor(cgo, I->i[I->N - 1], cPickableAtom);
	CGONormalv(cgo, n);
	CGOVertexv(cgo, v);
	/* trace shape */
	for(b = 0; b < I->Ns; b++) {
	  CGOVertexv(cgo, I->tv.get() + b * 3);
	}
	CGOVertexv(cgo, I->tv.get());
	CGOEnd(cgo);
      }
      CGOPickColor(cgo, -1, cPickableNoPick);
    }
    
    PRINTFD(I->G, FB_Extrude)
      " ExtrudeCGOSurfaceTube-DEBUG: exiting...\n" ENDFD;
  }
  return ok;
}

int ExtrudeCGOSurfacePolygon(const CExtrude * I, CGO * cgo, cCylCap cap, const float *color_override)
{
  int a, b;
  unsigned int *i;
  float *v;
  float *n;
  float *c;
  const float *alpha;
  float *sv, *sn, *tv, *tn, *tv1, *tn1;
  float v0[3];
  int ok = true;

  PRINTFD(I->G, FB_Extrude)
    " ExtrudeCGOSurfacePolygon-DEBUG: entered.\n" ENDFD;

  if(I->N && I->Ns) {

    std::vector<float> TV(3 * (I->Ns + 1) * I->N);
    std::vector<float> TN(3 * (I->Ns + 1) * I->N);
    /* compute transformed shape vertices */

    if (ok){
      tn = TN.data();
      tv = TV.data();
      
      sv = I->sv.get();
      sn = I->sn.get();
      for(b = 0; b <= I->Ns; b++) {
	if(b == I->Ns) {
	  sv = I->sv.get();
	  sn = I->sn.get();
	}
	v = I->p.get();
	n = I->n.get();
	
	for(a = 0; a < I->N; a++) {
	  transform33Tf3f(n, sv, tv);
	  add3f(v, tv, tv);
	  tv += 3;
	  transform33Tf3f(n, sn, tn);
	  tn += 3;
	  n += 9;
	  v += 3;
	}
	sv += 3;
	sn += 3;
      }
      
      /* fill in each strip separately */
      
      tv = TV.data();
      tn = TN.data();
      
      tv1 = TV.data() + 3 * I->N;
      tn1 = TN.data() + 3 * I->N;
    }
    for(b = 0; ok && b < I->Ns; b += 2) {
      if(SettingGetGlobal_i(I->G, cSetting_cartoon_debug) < 1.5)
        ok &= CGOBegin(cgo, GL_TRIANGLE_STRIP);
      else {
        ok &= CGOBegin(cgo, GL_LINE_STRIP);
      }
      if(ok && color_override)
        ok &= CGOColorv(cgo, color_override);
      c = I->c.get();
      alpha = I->alpha.get();
      i = I->i.get();
      for(a = 0; ok && a < I->N; a++) {
        if(!color_override)
          ok &= CGOColorv(cgo, c);
        if (ok){
          ok &= CGOAlpha(cgo, *alpha);
        }
        if (ok)
	  ok &= CGOPickColor(cgo, *i, cPickableAtom);
	if (ok)
	  ok &= CGONormalv(cgo, tn);
	if (ok)
	  ok &= CGOVertexv(cgo, tv);
        tn += 3;
        tv += 3;
	if (ok)
	  ok &= CGONormalv(cgo, tn1);
	if (ok)
	  ok &= CGOVertexv(cgo, tv1);
        tn1 += 3;
        tv1 += 3;
        c += 3;
        alpha++;
        i++;
      }
      tv += 3 * I->N;
      tn += 3 * I->N;
      tv1 += 3 * I->N;
      tn1 += 3 * I->N;
      if (ok)
	ok &= CGOEnd(cgo);
      if (ok)
	ok &= CGOPickColor(cgo, -1, cPickableNoPick);
    }

    if(ok && cap != cCylCap::None) {

      if(color_override)
        ok &= CGOColorv(cgo, color_override);

      if (ok){
	n = I->n.get();
	v = I->p.get();
	
	sv = I->sv.get();
	tv = I->tv.get();
	for(b = 0; b < I->Ns; b++) {
	  transform33Tf3f(n, sv, tv);
	  add3f(v, tv, tv);
	  sv += 3;
	  tv += 3;
	}
      }
      if (ok)
	ok &= CGOBegin(cgo, GL_TRIANGLE_FAN);
      if (ok){
	copy3f(I->n.get(), v0);
	invert3f(v0);
	if(!color_override)
	  ok &= CGOColorv(cgo, I->c.get());
    if (ok){
      ok &= CGOAlpha(cgo, I->alpha[0]);
    }
	if (ok)
	  ok &= CGOPickColor(cgo, I->i[0], cPickableAtom);
	if (ok)
	  ok &= CGONormalv(cgo, v0);
      }
      if (ok)
	ok &= CGOVertexv(cgo, v);
      /* trace shape */
      if (ok)
	ok &= CGOVertexv(cgo, I->tv.get());
      for(b = I->Ns - 1; ok && b >= 0; b--) {
        ok &= CGOVertexv(cgo, I->tv.get() + b * 3);
      }
      if (ok)
	ok &= CGOEnd(cgo);
      if (ok)
	ok &= CGOPickColor(cgo, -1, cPickableNoPick);
      if (ok){
	n = I->n.get() + 9 * (I->N - 1);
	v = I->p.get() + 3 * (I->N - 1);
	
	sv = I->sv.get();
	tv = I->tv.get();
	for(b = 0; b < I->Ns; b++) {
	  transform33Tf3f(n, sv, tv);
	  add3f(v, tv, tv);
	  sv += 3;
	  tv += 3;
	}
      }
      if (ok)
	ok &= CGOBegin(cgo, GL_TRIANGLE_FAN);
      if(ok && !color_override)
        ok &= CGOColorv(cgo, I->c.get() + 3 * (I->N - 1));
      if (ok){
        ok &= CGOAlpha(cgo, I->alpha[I->N - 1]);
      }
      if (ok)
	ok &= CGOPickColor(cgo, I->i[I->N - 1], cPickableAtom);
      if (ok)
	ok &= CGONormalv(cgo, n);
      if (ok)
	ok &= CGOVertexv(cgo, v);
      /* trace shape */
      for(b = 0; ok && b < I->Ns; b++) {
        ok &= CGOVertexv(cgo, I->tv.get() + b * 3);
      }
      if (ok)
	ok &= CGOVertexv(cgo, I->tv.get());
      if (ok)
	ok &= CGOEnd(cgo);
      if (ok)
	ok &= CGOPickColor(cgo, -1, cPickableNoPick);
    }
  }

  PRINTFD(I->G, FB_Extrude)
    " ExtrudeCGOSurfacePolygon-DEBUG: exiting...\n" ENDFD;
  return ok;
}

int ExtrudeCGOSurfacePolygonTaper(const CExtrude * I, CGO * cgo, int sampling,
				  const float *color_override)
{
  int a, b;
  unsigned int *i;
  float *v;
  float *n;
  float *c;
  const float *alpha;
  float *sv, *sn, *tv, *tn, *tv1, *tn1;
  float s0[3];
  float f;
  int subN;
  int ok = true;

  subN = I->N - sampling;

  PRINTFD(I->G, FB_Extrude)
    " ExtrudeCGOSurfacePolygonTaper-DEBUG: entered.\n" ENDFD;

  if(I->N && I->Ns) {

    std::vector<float> TV(3 * (I->Ns + 1) * I->N);
    std::vector<float> TN(3 * (I->Ns + 1) * I->N);
    /* compute transformed shape vertices */

    if (ok){
    tn = TN.data();
    tv = TV.data();

    sv = I->sv.get();
    sn = I->sn.get();
    for(b = 0; b <= I->Ns; b++) {
      if(b == I->Ns) {
        sv = I->sv.get();
        sn = I->sn.get();
      }
      v = I->p.get();
      n = I->n.get();

      for(a = 0; a < I->N; a++) {
        if((a >= sampling) && (a < subN)) {

          transform33Tf3f(n, sv, tv);
          add3f(v, tv, tv);
          tv += 3;
          transform33Tf3f(n, sn, tn);
          tn += 3;
          n += 9;
          v += 3;
        } else {
          copy3f(sv, s0);

          if(a >= subN) {
            f = ((I->N - a - 1) / ((float) sampling));
          } else if(a < sampling) {
            f = (a / ((float) sampling));
          } else
            f = 1.0;
          f = smooth(f, 2);
          s0[2] *= f;

          transform33Tf3f(n, s0, tv);
          add3f(v, tv, tv);
          tv += 3;
          transform33Tf3f(n, sn, tn);
          tn += 3;
          n += 9;
          v += 3;

        }
      }
      sv += 3;
      sn += 3;
    }

    /* fill in each strip separately */

    tv = TV.data();
    tn = TN.data();

    tv1 = TV.data() + 3 * I->N;
    tn1 = TN.data() + 3 * I->N;
    }
    for(b = 0; ok && b < I->Ns; b += 2) {
      if (ok){
	if(SettingGetGlobal_i(I->G, cSetting_cartoon_debug) < 1.5)
	  ok &= CGOBegin(cgo, GL_TRIANGLE_STRIP);
	else {
	  ok &= CGOBegin(cgo, GL_LINE_STRIP);
	}
      }
      if(ok && color_override)
        ok &= CGOColorv(cgo, color_override);
      c = I->c.get();
      alpha = I->alpha.get();
      i = I->i.get();
      for(a = 0; ok && a < I->N; a++) {
        if(!color_override)
          ok &= CGOColorv(cgo, c);
        if (ok){
          ok &= CGOAlpha(cgo, *alpha);
        }
        if (ok)
	  ok &= CGOPickColor(cgo, *i, cPickableAtom);
        if (ok)
	  ok &= CGONormalv(cgo, tn);
	if (ok)
	  ok &= CGOVertexv(cgo, tv);
        tn += 3;
        tv += 3;
	if (ok)
	  ok &= CGONormalv(cgo, tn1);
	if (ok)
	  ok &= CGOVertexv(cgo, tv1);
        tn1 += 3;
        tv1 += 3;
        c += 3;
        alpha++;
        i++;
      }
      if (ok){
	tv += 3 * I->N;
	tn += 3 * I->N;
	tv1 += 3 * I->N;
	tn1 += 3 * I->N;
	CGOEnd(cgo);
	CGOPickColor(cgo, -1, cPickableNoPick);
      }
    }

  }

  PRINTFD(I->G, FB_Extrude)
    " ExtrudeCGOSurfacePolygonTaper-DEBUG: exiting...\n" ENDFD;
  return ok;
}

int ExtrudeCGOSurfaceStrand(const CExtrude * I, CGO * cgo, int sampling, const float *color_override)
{
  int a, b;
  unsigned int *i;
  float *v;
  float *n;
  float *c;
  const float *alpha;
  float *sv, *sn, *tv, *tn, *tv1, *tn1;
  float v0[3], n0[3], s0[3], z[3] = { 1.0, 0.0, 1.0 };
  int subN;
  int ok = true;
  subN = I->N - sampling;

  PRINTFD(I->G, FB_Extrude)
    " ExtrudeCGOSurfaceStrand-DEBUG: entered.\n" ENDFD;

  if(I->N && I->Ns) {

    std::vector<float> TV(3 * (I->Ns + 1) * I->N);
    std::vector<float> TN(3 * (I->Ns + 1) * I->N);
    /* compute transformed shape vertices */

    if (ok){
      tn = TN.data();
      tv = TV.data();
      sv = I->sv.get();
      sn = I->sn.get();
      for(b = 0; b <= I->Ns; b++) {
	if(b == I->Ns) {
	  sv = I->sv.get();
	  sn = I->sn.get();
	}
	v = I->p.get();
	n = I->n.get();
	for(a = 0; a < I->N; a++) {
	  copy3f(sv, s0);
	  if(a == subN) {
	    scale3f(s0, 0.50F, s0);
	  }
	  transform33Tf3f(n, s0, tv);
	  add3f(v, tv, tv);
	  tv += 3;
	  transform33Tf3f(n, sn, tn);
	  tn += 3;
	  n += 9;
	  v += 3;
	}
	sv += 3;
	sn += 3;
      }

      /* fill in each strip of arrow separately */
      
      tv = TV.data();
      tn = TN.data();
      
      tv1 = TV.data() + 3 * I->N;
      tn1 = TN.data() + 3 * I->N;
    }

    for(b = 0; ok && b < I->Ns; b += 2) {
      if(SettingGetGlobal_i(I->G, cSetting_cartoon_debug) < 1.5)
        ok &= CGOBegin(cgo, GL_TRIANGLE_STRIP);
      else {
        ok &= CGOBegin(cgo, GL_LINE_STRIP);
      }
      c = I->c.get();
      alpha = I->alpha.get();
      i = I->i.get();
      for(a = 0; ok && a < I->N; a++) {
        if(a < subN) {
	  if(color_override && ((b == 2) || (b == 3) || (b == 6) || (b == 7)))
	    ok &= CGOColorv(cgo, color_override);
	  else
	    ok &= CGOColorv(cgo, c);
      if (ok){
        ok &= CGOAlpha(cgo, *alpha);
      }
	  if (ok)
	    ok &= CGOPickColor(cgo, *i, cPickableAtom);
	  if (ok)
	    ok &= CGONormalv(cgo, tn);
	  if (ok)
	    ok &= CGOVertexv(cgo, tv);
        }
        tn += 3;
        tv += 3;
        if(ok && a < subN) {
          ok &= CGONormalv(cgo, tn1);
	  if (ok)
	    ok &= CGOVertexv(cgo, tv1);
        }
        tn1 += 3;
        tv1 += 3;
        c += 3;
        alpha++;
        i++;
      }
      tv += 3 * I->N;
      tn += 3 * I->N;
      tv1 += 3 * I->N;
      tn1 += 3 * I->N;
      if (ok)
	ok &= CGOEnd(cgo);
      if (ok)
	ok &= CGOPickColor(cgo, -1, cPickableNoPick);
    }

    if(ok) {

      n = I->n.get();
      v = I->p.get();

      sv = I->sv.get();
      tv = I->tv.get();
      for(b = 0; b < I->Ns; b++) {
        transform33Tf3f(n, sv, tv);
        add3f(v, tv, tv);
        sv += 3;
        tv += 3;
      }

      copy3f(I->n.get(), v0);
      invert3f(v0);
      if (ok){
	if(color_override)
	  ok &= CGOColorv(cgo, color_override);
	else
	  ok &= CGOColorv(cgo, I->c.get());
       }
      if(ok){
        ok &= CGOAlpha(cgo, I->alpha[0]);
      }
      if (ok)
	ok &= CGOPickColor(cgo, I->i[0], cPickableAtom);

      if (ok)
	ok &= CGOBegin(cgo, GL_TRIANGLE_STRIP);
      if (ok)
	ok &= CGONormalv(cgo, v0);

      ok &= CGOVertexv(cgo, I->tv.get() + 6 * 3);
      ok &= CGOVertexv(cgo, I->tv.get() + 4 * 3);
      ok &= CGOVertexv(cgo, I->tv.get() + 0 * 3);
      ok &= CGOVertexv(cgo, I->tv.get() + 2 * 3);
      if (ok)
	ok &= CGOEnd(cgo);
      if (ok)
	ok &= CGOPickColor(cgo, -1, cPickableNoPick);
    }

    /* now do the arrow part */

    tn = TN.data();
    tv = TV.data();

    sv = I->sv.get();
    sn = I->sn.get();
    if (ok){
      for(b = 0; b <= I->Ns; b++) {
	if(b == I->Ns) {
	  sv = I->sv.get();
	  sn = I->sn.get();
	}
	v = I->p.get();
	n = I->n.get();
	
	for(a = 0; a < I->N; a++) {
	  copy3f(sv, s0);
	  s0[2] = s0[2] * ((1.5F * ((I->N - 1) - a)) / sampling);
	  transform33Tf3f(n, s0, tv);
	  add3f(v, tv, tv);
	  tv += 3;
	  copy3f(sn, n0);
	  if(fabs(dot_product3f(sn, z)) > R_SMALL4) {
	    n0[0] += 0.4F;
	    normalize3f(n0);
	  }
	  transform33Tf3f(n, n0, tn);
	  tn += 3;
	  n += 9;
	  v += 3;
	}
	sv += 3;
	sn += 3;
      }
    }

    tv = TV.data();
    tn = TN.data();

    tv1 = TV.data() + 3 * I->N;
    tn1 = TN.data() + 3 * I->N;

    for(b = 0; ok && b < I->Ns; b += 2) {
      if (ok){
	if(SettingGetGlobal_i(I->G, cSetting_cartoon_debug) < 1.5)
	  ok &= CGOBegin(cgo, GL_TRIANGLE_STRIP);
	else {
	  ok &= CGOBegin(cgo, GL_LINE_STRIP);
	}
      }
      c = I->c.get();
      alpha = I->alpha.get();
      i = I->i.get();
      for(a = 0; ok && a < I->N; a++) {
        if(a >= (subN - 1)) {
          if(color_override && ((b == 2) || (b == 3) || (b == 6) || (b == 7)))
            ok &= CGOColorv(cgo, color_override);
          else
            ok &= CGOColorv(cgo, c);
        if (ok){
          ok &= CGOAlpha(cgo, *alpha);
        }
	  if (ok)
	    ok &= CGOPickColor(cgo, *i, cPickableAtom);
          if (ok)
	    ok &= CGONormalv(cgo, tn);
	  if (ok)
	    ok &= CGOVertexv(cgo, tv);
        }
        tn += 3;
        tv += 3;
        if(ok && a >= (subN - 1)) {
          ok &= CGONormalv(cgo, tn1);
	  if (ok)
	    ok &= CGOVertexv(cgo, tv1);
        }
        tn1 += 3;
        tv1 += 3;
        c += 3;
        alpha++;
        i++;
      }
      tv += 3 * I->N;
      tn += 3 * I->N;
      tv1 += 3 * I->N;
      tn1 += 3 * I->N;
      if (ok)
	ok &= CGOEnd(cgo);
      if (ok)
	ok &= CGOPickColor(cgo, -1, cPickableNoPick);
    }

    n = I->n.get() + 9 * (subN - 1);
    v = I->p.get() + 3 * (subN - 1);
    sv = I->sv.get();
    tv = I->tv.get();
    if (ok){
      for(b = 0; b < I->Ns; b++) {
	copy3f(sv, s0);
	s0[2] = s0[2] * ((s0[2] < 0.f) ? -1.f : 1.5F) ;
	transform33Tf3f(n, s0, tv);
	add3f(v, tv, tv);
	sv += 3;
	tv += 3;
      }
    }

    // Back end/flat surface of the arrow, 
    // now split into two pieces, one for each side
    copy3f(n, v0);
    invert3f(v0);
    if (ok){
      if(color_override)
	ok &= CGOColorv(cgo, color_override);
      else
	ok &= CGOColorv(cgo, I->c.get() + 3 * (subN - 1));
    }
    if (ok){
      ok &= CGOAlpha(cgo, I->alpha[(subN - 1)]);
    }
    if (ok)
      ok &= CGOPickColor(cgo, I->i[(subN - 1)], cPickableAtom);

    // draw first side
    tv = I->tv.get();
    if (ok)
      ok &= CGOBegin(cgo, GL_TRIANGLE_STRIP);
    if (ok)
      ok &= CGONormalv(cgo, v0);
    ok &= CGOVertexv(cgo, I->tv.get() + 6 * 3);
    ok &= CGOVertexv(cgo, I->tv.get() + 4 * 3);
    ok &= CGOVertexv(cgo, I->tv.get() + 0 * 3);
    ok &= CGOVertexv(cgo, I->tv.get() + 2 * 3);
    if (ok)
      ok &= CGOEnd(cgo);

    // switch vertices to other side of flat surface of arrow
    sv = I->sv.get();
    tv = I->tv.get();
    if (ok){
      for(b = 0; b < I->Ns; b++) {
	copy3f(sv, s0);
	s0[2] = s0[2] * ((s0[2] < 0.f) ? 1.f : -1.5F) ;
	transform33Tf3f(n, s0, tv);
	add3f(v, tv, tv);
	sv += 3;
	tv += 3;
      }
    }
    // draw other side
    if (ok)
      ok &= CGOBegin(cgo, GL_TRIANGLE_STRIP);
    if (ok)
      ok &= CGONormalv(cgo, v0);
    ok &= CGOVertexv(cgo, I->tv.get() + 0 * 3);
    ok &= CGOVertexv(cgo, I->tv.get() + 2 * 3);
    ok &= CGOVertexv(cgo, I->tv.get() + 6 * 3);
    ok &= CGOVertexv(cgo, I->tv.get() + 4 * 3);
    if (ok)
      ok &= CGOEnd(cgo);

    if (ok)
      ok &= CGOPickColor(cgo, -1, cPickableNoPick);

  }

  PRINTFD(I->G, FB_Extrude)
    " ExtrudeCGOSurfaceStrand-DEBUG: exiting...\n" ENDFD;
  return ok;
}

int ExtrudeComputePuttyScaleFactors(CExtrude * I, ObjectMolecule * obj, int transform,
				    float mean, float stdev, float min, float max,
				    float power, float range,
				    float min_scale, float max_scale, int window)
{
  float *sf;
  int a;
  unsigned int *i;
  AtomInfoType *at;
  float scale = 1.0F;
  float data_range = max - min;
  int ok = true;

  if(I->N && I->Ns) {
    int invalid = false;
    i = I->i.get();
    sf = I->sf.get();

    /* guard against invalid inputs that would imply division by zero */

    switch (transform) {
    case cPuttyTransformNormalizedNonlinear:
    case cPuttyTransformNormalizedLinear:
      /* depend on stdev */
      if(stdev < R_SMALL8)
        invalid = true;
      break;
    }
    switch (transform) {
    case cPuttyTransformNormalizedNonlinear:
    case cPuttyTransformRelativeNonlinear:
    case cPuttyTransformScaledNonlinear:
    case cPuttyTransformNormalizedLinear:
    case cPuttyTransformRelativeLinear:
    case cPuttyTransformScaledLinear:
      /* depend on range */

      if(fabs(range) < R_SMALL8)
        invalid = true;
      break;
    }
    switch (transform) {
    case cPuttyTransformRelativeNonlinear:
    case cPuttyTransformRelativeLinear:
      /* depend on data_range */
      if(fabs(data_range) < R_SMALL8)
        invalid = true;
      break;
    }

    if(!invalid) {
      for(a = 0; a < I->N; a++) {
        at = obj->AtomInfo + (*i);
        switch (transform) {
        case cPuttyTransformNormalizedNonlinear:
          /* normalized by Z-score, with the range affecting the distribution width */
          scale = (range + (at->b - mean) / stdev) / range;
          if(scale < 0.0F)
            scale = 0.0F;
          scale = (float) pow(scale, power);
          break;
        case cPuttyTransformRelativeNonlinear:
          scale = (at->b - min) / (data_range * range);
          if(scale < 0.0F)
            scale = 0.0F;
          scale = (float) pow(scale, power);
          *sf = scale;
          break;
        case cPuttyTransformScaledNonlinear:
          scale = at->b / range;
          if(scale < 0.0F)
            scale = 0.0F;
          scale = (float) pow(scale, power);
          *sf = scale;
          break;
        case cPuttyTransformAbsoluteNonlinear:
          scale = at->b;
          if(scale < 0.0F)
            scale = 0.0F;
          scale = (float) pow(scale, power);
          *sf = scale;
          break;
        case cPuttyTransformNormalizedLinear:
          /* normalized by Z-score, with the range affecting the distribution width */
          scale = (range + (at->b - mean) / stdev) / range;
          if(scale < 0.0F)
            scale = 0.0F;
          break;
        case cPuttyTransformRelativeLinear:
          scale = (at->b - min) / (data_range * range);
          if(scale < 0.0F)
            scale = 0.0F;
          *sf = scale;
          break;
        case cPuttyTransformScaledLinear:
          scale = at->b / range;
          if(scale < 0.0F)
            scale = 0.0F;
          *sf = scale;
          break;
        case cPuttyTransformAbsoluteLinear:
          scale = at->b;
          if(scale < 0.0F)
            scale = 0.0F;
          *sf = scale;
          break;
        case cPuttyTransformImpliedRMS:
          if(scale < 0.0F)
            scale = 0.0F;
          scale = (float) (sqrt1d(at->b / 8.0) / PI);
          break;
        }
        if((scale < min_scale) && (min_scale >= 0.0))
          scale = min_scale;
        if((scale > max_scale) && (max_scale >= 0.0))
          scale = max_scale;
        *(sf++) = scale;
        i++;
      }
    } else {
      PRINTFB(I->G, FB_RepCartoon, FB_Warnings)
        " Extrude-Warning: invalid putty settings (division by zero)\n" ENDFB(I->G);
      for(a = 0; a < I->N; a++) {
        *sf = 0.5F;
        sf++;
      }
    }

    PRINTFB(I->G, FB_RepCartoon, FB_Blather)
      " Putty: mean %8.3f stdev %8.3f min %8.3f max %8.3f\n",
      mean, stdev,
      mean + (pow(min_scale, 1.0F / power) * range - range) * stdev,
      mean + (pow(max_scale, 1.0F / power) * range - range) * stdev ENDFB(I->G);
    /* now compute window average */

    {
      std::vector<float> SF(I->N);
      int w, ww;
      float accum;
      int cnt;

      sf = I->sf.get();

      if (ok){
	for(a = 1; a < (I->N - 1); a++) {
	  accum = 0.0F;
	  cnt = 0;
	  for(w = -window; w <= window; w++) {
	    ww = w + a;
	    if(ww < 0)
	      ww = 0;
	    else if(ww > (I->N - 1))
	      ww = I->N - 1;
	    accum += sf[ww];
	    cnt++;
	  }
	  SF[a] = accum / cnt;
	}
	for(a = 1; a < I->N - 1; a++)
	  sf[a] = SF[a];
      }
    }
  }
  return (ok);
}


void ExtrudeTruncate(CExtrude * I, int n)
{

  I->N = n;
  /* should free RAM here... */
}

int ExtrudeAllocPointsNormalsColors(CExtrude * I, int n)
{
  int ok = true;
  if(I->N < n) {
    /* reset */
    I->p.reset(new float[3 * (n + 1)]);
    I->n.reset(new float[9 * (n + 1)]);
    I->c.reset(new float[3 * (n + 1)]);
    I->alpha.reset(new float[n + 1]);
    I->i.reset(new unsigned int[3 * (n + 1)]);
    I->sf.reset(new float[n + 1]);        /* PUTTY: scale factors */
  }
  I->N = n;
  return ok;
}

void ExtrudeFree(CExtrude * I)
{
  delete I;
}
