
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
#ifndef _H_RepSurface
#define _H_RepSurface

#include "PyMOLGlobals.h"

struct Rep;
struct CoordSet;

Rep *RepSurfaceNew(CoordSet * cset, int state);

/// A surface of at least this many atoms is built on a thread of its own
/// when it is wanted for the window (SceneBuildsInBackground)
constexpr int cSurfaceBuildMinAtoms = 5000;

/**
 * Takes the results of the surfaces that were built in the background, on
 * the main thread: those that are ready, or with `wait` all of them.
 * @return true if a surface got its triangles
 */
bool RepSurfaceFinishBuilds(PyMOLGlobals* G, bool wait);

#define cRepSurface_by_flags       0
#define cRepSurface_all            1
#define cRepSurface_heavy_atoms    2
#define cRepSurface_vis_only       3
#define cRepSurface_vis_heavy_only 4

#endif
