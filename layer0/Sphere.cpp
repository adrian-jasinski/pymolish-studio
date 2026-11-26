

/* 
A* -------------------------------------------------------------------
B* This file contains source code for the PyMOL computer program
C* Copyright (c) Schrodinger, LLC. 
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

#include"os_predef.h"
#include"os_std.h"
#include"os_gl.h"

#include"Base.h"
#include"Sphere.h"
#include"Vector.h"
#include"Err.h"

#include"MemoryDebug.h"



static const int mesh[30][2] = {
  {0, 3},
  {0, 4},
  {0, 5},
  {0, 8},
  {0, 11},
  {1, 2},
  {1, 6},
  {1, 7},
  {1, 8},
  {1, 11},
  {2, 6},
  {2, 7},
  {2, 9},
  {2, 10},
  {3, 4},
  {3, 5},
  {3, 9},
  {3, 10},
  {4, 7},
  {4, 8},
  {4, 9},
  {5, 6},
  {5, 10},
  {5, 11},
  {6, 10},
  {6, 11},
  {7, 8},
  {7, 9},
  {8, 11},
  {9, 10}
};

#include"SphereData.h"



void SphereInit(PyMOLGlobals * G)
{
  CSphere *I = (G->Sphere = new CSphere());

  I->Array.resize(Sphere_NSpheres);

  {
    int i;
    for (i=0; i<Sphere_NSpheres; i++){
      I->Array[i].area = &Sphere_area[Sphere_dot_start[i]];
      I->Array[i].dot = &Sphere_dot[Sphere_dot_start[i]];
      I->Array[i].StripLen = &Sphere_StripLen[Sphere_StripLen_start[i]];
      I->Array[i].Sequence = &Sphere_Sequence[Sphere_Sequence_start[i]];
      I->Array[i].NStrip = Sphere_NStrip[i];
      I->Array[i].NVertTot = Sphere_NVertTot[i];
      I->Array[i].nDot = Sphere_nDot[i];
      I->Array[i].Tri = &Sphere_Tri[Sphere_Tri_start[i]];
      I->Array[i].NTri = Sphere_NTri[i];
      
      if (i){
	I->Array[i].Mesh = nullptr;
	I->Array[i].NMesh = 0;
      } else {
	I->Array[i].Mesh = (int *) (void *) mesh;
	I->Array[i].NMesh = 30;
      }
      I->Sphere[i] = &I->Array[i];
    }
  }

}


void SphereFree(PyMOLGlobals * G)
{
  DeleteP(G->Sphere);
}


/* private stuff */


void SphereRender(PyMOLGlobals * G, int level, const float *centroid, const float *color, float alpha, float radius){
  SphereRec *sp = G->Sphere->Sphere[level];
  int a, cc;
  int *q = sp->Sequence;
  float pt[3];
  if (color)
    glColor4f(color[0], color[1], color[2], alpha);
  for(a = 0; a < sp->NStrip; a++) {
    glBegin(GL_TRIANGLE_STRIP);
    cc = sp->StripLen[a];
    while(cc--) {
      glNormal3fv(sp->dot[*q]);
      mult3f(sp->dot[*q], radius, pt);
      add3f(centroid, pt, pt);
      glVertex3fv(pt);
      q++;
    }
    glEnd();
  }
}

SphereRec* GetSpheroidSphereRec(PyMOLGlobals* G)
{
  return G->Sphere->Sphere[2];
}
