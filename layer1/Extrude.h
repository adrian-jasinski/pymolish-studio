
/* 
A* -------------------------------------------------------------------
B* This file contains source code for the PyMOL computer program
C* copyright 1998-2000 by Warren Lyford Delano of DeLano Scientific. 
D* -------------------------------------------------------------------
E* It is unlawful to modify or remove this copyright notice.
F* -------------------------------------------------------------------
G* Please see the accompanying LICENSE file for further information. 
H* -------------------------------------------------------------------
I* Additional authors of this source file include:
-* 
-* 
-*
Z* -------------------------------------------------------------------
*/
#ifndef _H_Extrude
#define _H_Extrude

#include <memory>

#include "Basis.h"

struct PyMOLGlobals;
struct ObjectMolecule;
class CGO;

struct CExtrude {
  PyMOLGlobals* G{};
  int N{}; /* number of points in the extrusion segment */

  // arrays, not vectors: sized for the worst case and left unfilled, and
  // const functions write the scratch arrays tv and tn
  std::unique_ptr<float[]> p;        /* points */
  std::unique_ptr<float[]> n;        /* normals (3x3f) at each point */
  std::unique_ptr<float[]> c;        /* colors */
  std::unique_ptr<float[]> alpha;    /* alpha values*/
  std::unique_ptr<unsigned int[]> i; /* atom indices */

  float r{};
  /* scale factors for variable-width extrusions (single point) */
  std::unique_ptr<float[]> sf;

  std::unique_ptr<float[]> sv;
  std::unique_ptr<float[]> tv;
  std::unique_ptr<float[]> sn;
  std::unique_ptr<float[]> tn;
  int Ns;
};

CExtrude *ExtrudeNew(PyMOLGlobals * G);

CExtrude *ExtrudeCopyPointsNormalsColors(CExtrude * orig);

int ExtrudeAllocPointsNormalsColors(CExtrude * I, int n);
void ExtrudeTruncate(CExtrude * I, int n);

void ExtrudeFree(CExtrude * I);

void ExtrudeShiftToAxis(CExtrude*, float radius, int sampling);
int ExtrudeCircle(CExtrude * I, int n, float size);
int ExtrudeRectangle(CExtrude * I, float width, float length, int mode);
int ExtrudeOval(CExtrude * I, int n, float width, float length);

int ExtrudeComputePuttyScaleFactors(CExtrude * I, ObjectMolecule * obj,
				    int transform,
				    float mean, float stdev, float min, float max,
				    float power, float range,
				    float min_scale, float max_scale, int smooth_window);

void ExtrudeBuildNormals1f(CExtrude * I);
void ExtrudeBuildNormals2f(CExtrude * I);
int ExtrudeComputeTangents(CExtrude * I);
int ExtrudeCylindersToCGO(CExtrude * I, CGO *cgo, float tube_radius);
int ExtrudeCGOSurfaceTube(const CExtrude* I, CGO* cgo, cCylCap cap,
    const float* color_override, bool use_spheres, int dash = 0);
int ExtrudeCGOSurfaceVariableTube(const CExtrude * I, CGO * cgo, cCylCap cap);

int ExtrudeCGOSurfacePolygon(const CExtrude * I, CGO * cgo, cCylCap cap, const float *color_override);
int ExtrudeCGOSurfacePolygonTaper(const CExtrude * I, CGO * cgo,
                                   int sampling, const float *color_override);
int ExtrudeCGOSurfaceStrand(const CExtrude * I, CGO * cgo, int sampling,
                             const float *color_override);
int ExtrudeDumbbell1(CExtrude * I, float width, float length, int mode);
void ExtrudeDumbbellEdge(CExtrude * I, int samp, int sign, float length);

#endif
