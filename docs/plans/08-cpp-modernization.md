# 8 — Modern C++ in the core

[Roadmap](../../PLAN.md) · Request 2026-11-13 · Draft; counts are `grep` counts,
nothing was built, timed or changed for this plan

> **2026-11-25, 4.76.1 to 4.76.14.** The `malloc` half of 8c is done as far
> as a buffer has one owner: 230 of 297 allocation sites and 274 of 353
> frees are gone (67 and 79 left, each with its reason below). The
> mechanical part of 8d is done: 215 macro calls on `pymol::vla` objects are
> member calls; 611 calls on raw pointers are left. Measured: the suite
> (1154 passed, 250 skipped), a sanitizer run without a report, the ray
> geometry of 385 combinations and a session round trip identical to
> 4.76.0. Eight defects that were in 4.76.0 came out and are fixed. Left
> out: `compare.py` (the machine was in use), any run on Windows, macOS or
> GCC 11, any look at a window. Not started: raw `new` / `delete`, 8e, 8f,
> 8g. Where the step should end is question 106 in
> [PLAN.md](../../PLAN.md).

**Modernize the C-style C++ of the core one idiom and one file at a time, behind
tests and sanitizers. No from-scratch rewrite. Vendored C stays C.**

## What exists

- **The core is already C++.** `layer0/` to `layer5/` and `layerGraphics/` hold
  165 `.cpp` files, 219,000 lines, and no `.c` file. MSVC builds with
  `/std:c++17`; GCC and Clang use their default. The work is "C written in
  C++", not a language port.
- **Real C is vendored only:** `contrib/champ` (10 files, 7,500 lines) and the
  VMD molfile plugins in `contrib/uiuc` (30 files, 23,500 lines).
- **Upstream started the same migration and left it half done:**

  | Old idiom | Sites | Modern form already in the tree | Sites |
  | --- | --- | --- | --- |
  | `VLAlloc`, `VLACheck`, ... macros | 902 | `pymol::vla<T>` | 222 |
  | `Alloc`, `Calloc`, `FreeP`, `malloc`, `free` | 714 | `std::vector` | 676 |
  | raw `new` / `delete` | 589 | `std::unique_ptr` | 102 |
  | `sprintf`, `strcpy`, `strcat`, `strncpy` | 517 | `std::string` | 465 |
  | fixed buffers (`OrthoLineType`, `WordType`, ...) | 221 | | |
  | `ok_assert` / `ok_raise` chains, `goto` | 246 | `pymol::Result` | 419 |
  | C pointer casts | 572 | | |
  | `#define` (includes header guards) | 1,917 | | |

  About 3,800 sites plus the macros.
- **Safety net today:** 167 Python test files, 23 Catch2 files,
  `testing/compare.py`. No sanitizer build. Test coverage of the core was never
  measured.

## Decisions

- **No rewrite from scratch.** 219,000 lines whose behavior is defined by the
  code itself, not by a specification; a rewrite loses function by
  construction. Small behavior-neutral steps do not.
- **Vendored C is not touched.** The molfile plugins track VMD; rewriting them
  gains nothing and makes every plugin update a manual port. Champ: same.
- **The CPython C API code stays as it is** (2,479 `PyObject` uses, mostly
  `layer4/Cmd.cpp`). The API is C. pybind11 would be a new dependency for no
  user-visible gain.
- **One idiom per PR, behavior-neutral,** commit type `simplify(<scope>)`. A
  modernization PR never changes an algorithm, and a speed PR never sweeps
  idioms. A regression then has one cause.
- **Speed stays step 1's job.** Modernization does not make code faster by
  itself and can make it slower (`std::vector` zero-fills where `malloc` did
  not; `std::string` allocates inside loops). The two steps share an order
  instead: files are modernized in profile order, so a hot function is cleaned
  just before or after it is optimized, and `compare.py` gates both.
- **Delete first.** A line removed under step 2 is a line not modernized.
- **Session layout is frozen.** Structs written by `pse_binary_dump`
  (`layer2/AtomInfoHistory.h`) keep their layout; PSE files must load and save
  as before.
- **No public change.** `cmd.*`, settings and file formats are untouched, so
  `ChangeLog` needs no entry.

## Order

| Slice | Work | Why here |
| --- | --- | --- |
| 8a | Safety net: one Linux CI job with `-fsanitize=address,undefined` running the Python suite and Catch2; one `gcov` run that lists core files the suite never enters | Without it "no lost function" cannot be shown. A file with no coverage gets a test before it is touched. |
| 8b | `sprintf` / `strcpy` / fixed buffers to `std::string` and `snprintf` | The only idiom that is a memory-safety bug class. Mechanical. |
| 8c | `Alloc` / `FreeP` / `malloc` and raw `new` / `delete` to `std::vector` and `std::unique_ptr` | Removes manual cleanup paths, which makes 8e possible. |
| 8d | VLA macros to `pymol::vla<T>` or `std::vector`; delete the macro layer when its last user is gone | Finishes upstream's migration; ends in a deletion. |
| 8e | `ok` chains and `goto` cleanup to `pymol::Result` and early return | Needs 8c: early return is only safe once ownership is automatic. |
| 8f | Function-like macros to `constexpr` / inline functions; C casts to named casts | Lowest value; do it only in files already open for another slice. |
| 8g | `ov/` (3,700 lines of hand-written hash maps and string interning) to `std::unordered_map`, if `compare.py` is not slower | The one slice that deletes a directory. Measure before deciding. |

Inside a slice, go file by file in profile order: `Executive.cpp`,
`Selector.cpp`, `ObjectMolecule.cpp`, `CGO.cpp`, `Ray.cpp`, `RepSurface.cpp`
first.

## Risk

- **Tests prove only what they cover.** Rendering and GUI paths do not run
  headless. Slices that touch `layer1/` need the real GUI check, and 8a's
  coverage list decides where a test comes first.
- **Upstream merges.** Every modernized file stops taking upstream patches
  cleanly. Decided 2026-11-16: upstream is no longer merged, so the work is
  not limited to files this fork already changed.
- **Size.** This is not one step finished in a week. Each slice is many PRs.
  No date or line-count target is promised.

## Skipped, and when to add

- **C++20 / 23** (`std::span`, `std::format`): add when a slice needs one and
  the three CI compilers support it. It is a one-line build flag.
- **Splitting the large files** (`Executive.cpp` is 17,700 lines) or
  redesigning the object class hierarchy: only when a change inside is blocked
  by it.
- **`clang-tidy` `modernize-*` automatic fixes:** decide in 8a. It is a new
  pinned dev tool, and whole-tree automatic fixes break the one-idiom,
  reviewable-diff rule; per-file use may pay off in 8f.

## Checks

Every PR: the full Python suite, Catch2, the sanitizer job, `compare.py` within
noise of the last run in [docs/benchmark.md](../benchmark.md), and a PSE load and
save round trip. `layer1/` changes: real GUI.

## Status

**8a done 2026-11-13 in 4.7.2.**

- CI job `sanitize-Linux` builds with
  `-fsanitize=address,undefined -fno-sanitize-recover=undefined` and runs the
  Python suite; any report fails the job. Run it locally with the same
  `CXXFLAGS` / `CFLAGS` / `LDFLAGS` and
  `LD_PRELOAD="$(gcc -print-file-name=libasan.so) $(gcc -print-file-name=libstdc++.so)" ASAN_OPTIONS=detect_leaks=0`
  (libstdc++ since 8h).
- The first run found three bugs, fixed in `c2de3087`: `free()` of an object
  made with `new` (`PyMOL_Free`), left shifts of negative ints in the sculpting
  hash, and four uninitialized `bool` in `ObjectCGOState`.
- Left open on purpose: the alignment check is off. CGO keeps structs that
  hold pointers inside its `float` buffer, so every access is misaligned.
  Harmless on x86-64 and arm64; fixing it is a CGO storage change, not a
  sweep. Leak detection is off because Python does not free everything at
  exit.
- Coverage of the headless suite (`--coverage` build, `gcov`): **about half of
  the core**, 96,000 of 191,600 executable lines (68,400 of them are the
  stroke-font table in `VFont.cpp`).

  | Never entered by the suite | Lines |
  | --- | --- |
  | `layer1/CGOGL.cpp`, `SceneRender.cpp`, `ScenePicking.cpp`, `Picking.cpp` (OpenGL drawing and picking) | 2,682 |
  | `layer1/SceneMouse.cpp`, `layer3/Interactions.cpp`, `layer1/ScrollBar.cpp` (mouse) | 2,130 |
  | `layer4/PopUp.cpp`, `Menu.cpp` (viewport menus; `PopUp.cpp` deleted in 4.19.42) | 696 |
  | `layer0/GenericBuffer.cpp`, `ShaderPrg.cpp`, `PostProcess.cpp`, `layerGraphics/gl/GLVertexBuffer.cpp` (GPU buffers, shaders) | 890 |
  | `layer2/ObjectCurve.cpp`, `RepSphereImmediate.cpp`, `RepSphereGenerate.cpp` | 520 |
  | `ov/src/OVOneToAny.cpp`, `OVRandom.cpp` | 300 |

  | Large and under 25 % | Covered |
  | --- | --- |
  | `layer1/CGO.cpp` (6,343 lines) | 17 % |
  | `layer5/PyMOL.cpp` (1,481) | 24 % |
  | `layer2/RepLabel.cpp` (1,296) | 15 % |
  | `layer3/Seeker.cpp` (1,181) | 7 % |
  | `layer0/ShaderMgr.cpp` (988) | 6 % |
  | `layer2/ObjectSlice.cpp` (752) | 10 % |
  | `layer1/Control.cpp`, `Seq.cpp`, `ButMode.cpp` (1,544) | 9 to 21 % |

  For scale: `Executive.cpp` 55 %, `ObjectMolecule.cpp` 70 %, `Selector.cpp`
  80 %, `Ray.cpp` 59 %, `Cmd.cpp` 76 %, `Scene.cpp` 29 %, `RepSurface.cpp` 32 %.

  Rule that follows: in the files above only compiler-checked mechanical
  changes are allowed without a new test or a real GUI check. Hand-written
  changes there wait for one.
- Not done: the Catch2 tests are compiled in CI but no step runs them
  (`pymolish --testing`); Catch2 is not installed on the development machine,
  so adding the step could not be tried. (Corrected in 8h below: the suite
  runs them.)

**8b in progress.**

- 4.7.3: 227 of 251 `sprintf` are `snprintf(buf, std::size(buf), ...)`.
  `std::size` does not compile on a pointer, so the compiler proved every
  destination is an array. Left for a hand pass: 17 calls whose destination is
  a pointer parameter (the callee does not know the size) and 7 that write at
  an offset into a larger buffer.
- 4.7.4: 159 of 197 `strcpy` are `UtilNCopy(dst, src, std::size(dst))`, the
  bounded copy the tree already had. Left for a hand pass: 28 with a pointer
  destination and 10 with a computed one.
- 4.7.5: 22 of 27 `strcat` are `UtilNConcat(dst, src, std::size(dst))`. Left:
  5 with a pointer destination.
- 4.7.6, hand pass over what the sweeps left. Three real defects, with a test
  (`testing/tests/api/long_strings.py`) that fails under the sanitizer job
  without the fixes: an unterminated `strncpy` in `SettingGetTextValue`
  (reachable with `set` of a long text value), an off-by-one in the C label
  parser (`cmd.label2`), and unbounded `sprintf` of the file name in the PDB
  reader's load message (C API only).
- Open in 8b: about 60 `sprintf` / `strcpy` / `strcat` calls still write
  through a pointer. Read one by one, each is bounded by its own logic today
  (constant text, a name of known maximum length, or a size check just
  before), so they are not defects; they go away when the function gets a
  modern signature (`std::string` return or a size argument), which is 8c/8e
  work in the same files. The other 20 `strncpy` were read: each ends up
  terminated or needs no terminator, though several rely on the destination
  struct having been zero-filled. Then the fixed buffer types themselves
  (`OrthoLineType`, `WordType`, ...).

**8h done 2026-11-16.**

- The premise was wrong: the Catch2 tests have run in CI all along.
  `testing/tests/api/ctest.py` calls them from the Python suite, and the three
  build jobs compile with `testing=True`. The logs of run 43864077834 show
  "All tests passed (735 assertions in 135 test cases)" on Linux, Windows and
  macOS.
- What was missing: the sanitizer job built without `testing=True`, so there
  they were skipped. It now builds them and installs `catch2`.
- That needed one more change. With only `libasan.so` preloaded into a
  `python` that does not link libstdc++, ASan cannot find `__cxa_throw` and
  aborts on the first C++ exception (`Test_Image.cpp` expects one). Preloading
  `libstdc++.so` next to it fixes that.
- Tried on the development machine in a copy of the tree (`git archive`, its
  own venv, the job's flags): 136 Catch2 cases and the 1069 tests of the
  suite pass. The first run found one defect, fixed in 4.14.1: a signed left
  shift in `ColorGetName`, reached by the new `testLook`.
- Not tried: the job itself on GitHub (GCC 11 on Ubuntu 22.04; here GCC 13).

**8i done 2026-11-16 in 4.14.2.** Two more macros of the same kind went in
4.19.19 with [step 21](21-commercial-features.md): `NO_MMLIBS` (always
defined) and the atom-typing blocks behind `_PYMOL_IP_EXTRAS` (never
defined). The remaining guards went in 4.19.38: `_PYMOL_IP_EXTRAS` and
`_PYMOL_IP_SPLASH`, and the three product macros that alone defined them
(`PYMOL_COMM`, `PYMOL_COLL`, `PYMOL_EDU`): 100 lines in 10 files, same tool
and same proof (195 translation units, two configurations, identical
hashes), then the suite, Catch2 (137 cases) and a PSE round trip. The
sanitizer job was not run for it: the compiler sees the same text. What the
removal lays bare, not removed because it is not neutral:
`_cmd.get_m2io_first_block_properties` always raises and has no caller
(Maestro went in 4.19.24); two empty `auto_copy_images` branches in
`Scene.cpp` and `SceneRay.cpp`; the macros `AXPYMOL_EVAL`, `JYMOL_EVAL` and
`PYMOL_EVAL` next to them in `Ortho.cpp` were not surveyed.

- 12 macros, one commit each (`59cc08ee` to `374acdcc`) and a last pass for
  conditions that name two of them: 2,207 lines gone from 97 files.

  | Macro | Lines removed |
  | --- | --- |
  | `PURE_OPENGL_ES_2` | 568 |
  | `_PYMOL_LIB` | 498 |
  | `_PYMOL_NOPY` | 475 |
  | `WITH_UNUSED_FUNCTIONS` | 354 |
  | `_WEBGL` | 190 |
  | `PYMOL_EVAL` | 40 |
  | `_PYMOL_NO_RAY` | 31 |
  | `_PYMOL_EMBEDDED`, `PICKLETOOLS`, `_PYMOL_INCENTIVE`, `_PYMOL_ACTIVEX`, `_MACPYMOL_XCODE` | 51 |

- Tool: `unifdef` 2.12, the Ubuntu package unpacked in a scratch directory
  (`apt-get download unifdef`, `dpkg -x`); nothing was installed.
- Proof, per commit: `g++ -E -P -D__LINE__=0` of all 197 translation units of
  `layer0` to `layer5`, `layerGraphics`, `layerCTest` and `ov`, in two
  configurations (the defines of this machine's build; no optional feature
  and asserts on): the SHA-256 of every output is the same before and after.
  The limit of the proof: it is Linux text. Branches under `_WIN32` or
  `__APPLE__` are covered by `unifdef` being mechanical and by the first CI
  run on those systems.
- Then, once for the whole slice: build, the suite (1069 tests), Catch2 (136
  cases), a PSE save and load.
- Kept: `os_gl_glut.h` and `os_gl_glut_pretend.h`. Their 22 key and button
  constants are used at about 100 places; only the file names are history.
- Seen, not done: the shaders in `data/shaders/` have their own
  `PURE_OPENGL_ES_2` blocks. The C++ line that set that shader variable was
  inside a removed branch, so those blocks are dead as well, but shader text
  has no such proof: it needs a real GUI check on each renderer path. Other
  macros were not surveyed again (the 2026-11-14 list was taken as given).

**8c started 2026-11-19 in 4.19.39: `Executive.cpp`.**

- Seven function-local buffers went from `pymol::malloc` / `calloc` plus
  `FreeP` to `std::vector`: `ExecutiveReorder` (four arrays; the old code
  freed one of them half way and used the null pointer as the mark "already
  put back", now a `bool`), `ExecutiveSetVisFromPyDict` (the stack of
  visible records; the pointer still walks up and down, over a vector),
  `ExecutiveMapSet` (three buffers), the selection indicator texture, and
  in `ExecutiveRMS` the two index arrays, the vertex array and the outlier
  flags. 13 allocations and 16 frees gone; the null checks after `malloc`
  went with them (a failed allocation now throws).
- Left in the file: the `free` calls of `ExecutiveCEAlign` (the arrays come
  from `ccealignmodule.cpp` and change with that file), and raw `new` /
  `delete` (32 / 9), which are objects handed to the object list.
- Not neutral in one point, on purpose: a vector zero-fills where `malloc`
  did not. The buffers are per call, not per atom pair.
- Checks: the suite (929 passed) and Catch2; a sanitizer build of the
  working tree in a scratch copy (address and undefined behavior, the flags
  of the CI job): 908 passed, 269 skipped (no rdkit, PDBFixer or OpenMM
  there), no report, exit code 0. `set_vis` had no test: added
  `viewing.py::testGetSetVis`, run in both builds. The selection indicator
  texture is drawn only in a window: checked on WSLg, the markers of a
  selection appear and grow with `selection_width`. A PSE round trip.
  Not run: `compare.py` (the machine was busy with the sanitizer build;
  none of the seven functions is on a profile of the benchmark rows).

**8c, the `malloc` half, 2026-11-25 in 4.76.1 to 4.76.14.**

- Done in four groups of files, three of them in parallel branches, one
  commit per group: Selector, ObjectMolecule, ObjectMolecule2, PlugIOManager
  (4.76.1); Sculpt and ten small files (4.76.3); Ray, Basis, RepSurface,
  Triangle, Sphere, Isosurf, Tetsurf, RepMesh, ObjectMap, ObjectVolume
  (4.76.8); Extrude, RepCartoon, RepRibbon, RepSphere and the bond reps
  (4.76.10); the two AMBER readers (4.76.12).
- Counts over `layer0` to `layer5` and `layerGraphics`, without the files
  that define the macros: allocation sites 297 before, 67 now; frees 353
  before, 79 now. 60 source files changed, 1,181 lines added and 2,605
  removed.
- The rule that was kept: a vector zero-fills where `malloc` did not. Where
  that costs (a buffer sized for the worst case and filled in part, a buffer
  made every frame) the owner is `std::unique_ptr<T[]>` without
  initialization: the arrays of `CExtrude`, `tempVertex` and `tempRef` of
  `BasisMakeMap`, the dots of `RepMesh`, the two sort buffers of a
  transparent surface.
- Dead code that went with it, each in a commit of its own: the sphere
  generator of `Sphere.cpp` under a macro the same file always defines (554
  lines, same preprocessed text before and after, 4.76.11),
  `createPreintegrationTexture` (62 lines, 4.76.9),
  `ObjectMoleculeConvertIDsToIndices` (69 lines, 4.76.7),
  `OrthoSetBackgroundImage` (30 lines, 4.76.4), the `#if 0` blocks of
  `Extrude.cpp` (179 lines, in 4.76.10).
- Defects that were in 4.76.0, found by the new tests or by reading, and
  fixed:

  | Defect | Found by | Version |
  | --- | --- | --- |
  | `load_png` and `bg_image_filename` crash on a `data:image/png;base64,` text that is not base64 | a new test | 4.76.5 |
  | `valence` with a source object writes one byte before a vector (bond index -1) and ends in "double free or corruption" | a new test | 4.76.6 |
  | a surface with `ambient_occlusion_mode` 3 reads a neighbor map that was freed | the sanitizer run on a new test | 4.76.13 |
  | spheres of a part of an object with `sphere_mode` 6 to 8 take their normals from the wrong atoms and read past the coordinate buffer | reading, then reproduced under the sanitizer | 4.76.14 |
  | with `cartoon_all_alt` the cartoon leaks four arrays per alternate location | reading | 4.76.10 |
  | every surface leaks two arrays (`LastVisib`, `LastColor`) | reading | 4.76.8 |
  | a mesh without solvent dots writes into a zero-size buffer | reading | 4.76.8 |
  | `MatchAlign` leaks one table when the other allocation fails | reading | 4.76.3 |

- Left, and why (67 allocation sites):

  | Where | Sites | Why it stays |
  | --- | --- | --- |
  | `ccealignmodule.cpp` and the frees of `ExecutiveCEAlign` | 14 | contributed code in its own style, `double**` matrices handed across two files, one path allocated per cell of the search |
  | `RepDot.cpp` | 12 | allocated for the worst case and cut down with `realloc`; a vector would zero-fill ten floats per dot and atom |
  | `PyMOL.cpp`, `Editor.cpp`, `Cmd.cpp`, `P.cpp`, `Util.cpp`, `Word.cpp`, `TypeFace.cpp`, `Character.cpp`, `VFont.cpp` | 13 | singletons that hang off the calloc'd `PyMOLGlobals`; they belong to the `new` / `delete` half |
  | `PConv.cpp`, `File.cpp`, `Util.cpp` (`UtilArrayCalloc`), `ObjectMolecule.cpp` (`AtomInfoGetSortedIndex`), `ObjectMolecule2.cpp` (the other-index list) | 9 | the block is returned to callers in other files |
  | `ObjectMolecule.cpp` `UndoCoord` | 2 | the null pointer is the mark of an empty undo slot; 21g reworks the ring |
  | `Ray.cpp` | 4 | the depth buffer goes to the global `rayDepthPixels`; `VectorHash` sits inside VLA records (8d) |
  | `MyPNG.cpp` | 2 | assigned after `setjmp` |
  | `RepLabel.cpp`, `RepDistLabel.cpp`, `RepCylBond.cpp`, `Pixmap.cpp`, `CGOGL.cpp`, `Field.cpp`, `TestPyMOL.cpp`, `ListMacros.h` | 11 | `Rep::P` is freed in `Rep.cpp`; `CPixmap` is memset; a three-float block per bond; the rest was not looked at |

- Checks: the suite on the final tree, 1154 passed and 250 skipped (1122
  and 251 before; the new tests are in `core_buffers.py`,
  `buffers_ray_surface.py` and five existing files). A sanitizer build of the committed tree in a
  copy (address and undefined behavior, the flags of the CI job, GCC 13):
  no report; 1123 passed, 275 skipped (no rdkit, PDBFixer or OpenMM there).
  Ray geometry: the SHA-256 of `cmd.get_povray()` is the same on the 4.76.0
  build and on the new one for 385 combinations of five structures
  (protein, DNA, RNA), nine cartoon types, 31 cartoon settings, ribbon,
  sticks, lines, spheres and nonbonded; and for 95 more rows of the ray and
  surface group (surface types 0 to 7 and their settings, ambient
  occlusion, mesh, dots, maps with isomesh and isosurface, ray pictures),
  run on 4.76.13 with one thread. With four threads ray pictures differ
  between two runs of the same build, 4.76.0 included. A session written by
  either build is read by either build with the same atoms, bonds, view and
  geometry; two old sessions of `testing/data` read the same.
- Coverage, measured with `gcov` on the final tree (suite plus the geometry
  script): of 727 changed places, 132 are never executed. 59 of them are
  member calls of the mechanical 8d pass, which the compiler proves. The 73
  written by hand: `RepSurface.cpp` 10 (transparency sorting and other
  paths of a window), `ObjectMolecule.cpp` 10 (the AMBER restart reader,
  branches of valence guessing and of the SDF names), `ObjectVolume.cpp` 9
  (color ramps), `ObjectMap.cpp` 9 (the readers without a sample file: PHI,
  ACNT, FLD, GRD, XPLOR), `RepCartoon.cpp` 7 (cyclic peptides, one helix
  branch), `Ray.cpp` 5, `FontType.cpp` 5 (text drawn with OpenGL),
  `Selector.cpp` 4, `RepMesh.cpp` 4, `Extrude.cpp` 4, `Sculpt.cpp` 2,
  `ShaderPrg.cpp` 2, `Util.cpp` 1, `Triangle.cpp` 1. These compile and
  were read; no test or picture proves them.
- Seen and not fixed: in `RepCartoonNew` the VLA `ring_anchor` is
  allocated on every pass of the loop over alternate locations and freed
  once after it (a leak with `cartoon_all_alt`; it goes with 8d).
- Not run: `compare.py` (the user's own pymolish ran on the machine; none
  of the changed functions got a new zero-fill inside a loop per atom or
  pixel). Nothing was compiled with MSVC, Apple Clang or GCC 11: the first
  CI run of the pushed branch is that check. No window was opened.

**8d, the mechanical part, 2026-11-25 in 4.76.2 and 4.76.12.**

- `VLACheck`, `VLASize`, `VLAFreeP` and `VLAGetSize` forward to `check`,
  `resize`, `freeP` and `size` when the array is a `pymol::vla` (overloads
  in `vla.h`). A script rewrote every such call to the member and compiled
  the file; a rewrite that did not compile (a raw pointer) was taken back.
  215 calls in 25 files.
- 829 macro calls before, 611 now, all on raw pointers: 174 allocations (`VLAlloc`,
  `VLACalloc`, `VLAMalloc`), 378 `VLACheck` / `VLASize` / `VLAFreeP` /
  `VLAGetSize`, 48 `VLAprintf` (all in `MoleculeExporter.cpp`), 11 others.
  The largest families: the members of `ObjectMoleculeOpRec` (used by
  `Executive.cpp`, `ObjectMolecule.cpp`, `Selector.cpp`, `Cmd.cpp`), the
  lists of `Selector.cpp`, the readers of `ObjectMolecule.cpp`.

**Counts on 2026-11-25 at 4.76.13, unchanged by 4.76.14** (`grep`, same patterns as above):

| Idiom | Left | Slice |
| --- | --- | --- |
| `malloc` family / frees | 67 / 79 | 8c, each with a reason above |
| raw `new` (outside smart pointers) / `delete` / `DeleteP` | 181 / 109 / 64 | 8c, not started; 27 of them are local `MapType` |
| VLA macros on raw pointers | 611 | 8d |
| `ok_assert` / `ok_raise` / `ok_except`, `goto`, `CHECKOK` | 197, 24, 198 | 8e |
| `sprintf` / `strcpy` / `strcat` through a pointer | 60 | 8b, closes with 8d and 8e |
| `ov/` users | 72 | 8g, not measured |

## Review 2026-11-14: is it finished, and what is next

`grep` counts and CI configuration only; nothing was built or changed.

**Not finished.** 8a is done, 8b is mostly done, 8c to 8g are not started.

| Idiom | Left today | Slice |
| --- | --- | --- |
| `sprintf` / `strcpy` / `strcat` through a pointer | 31 / 44 / 5 | 8b, closes with 8c and 8e |
| `Alloc` / `FreeP` / `malloc` / `free` | about 420 | 8c |
| raw `new` / `delete` | about 500 / 110 | 8c |
| VLA macros | about 700 | 8d |
| `ok_assert` / `ok_raise` / `goto`, `CHECKOK` | about 190, 260 | 8e |
| `ov/` users | about 110 | 8g |

`NULL` is already gone (27 left against 4,000 `nullptr`).

### Order from here: the safest work first

The working version is the constraint, so the next slices are the ones the
compiler or a byte comparison can prove neutral. Hand-written changes come
after them.

| Slice | Work | Proof that nothing changed |
| --- | --- | --- |
| 8h | Run the Catch2 tests in CI: add `pymolish --testing` to the Linux job. They are compiled today and never run. | It is a new check, not a change. |
| 8i | Delete `#ifdef` branches for macros nothing defines. Neither `setup.py` nor any source defines `PURE_OPENGL_ES_2` (211 guards), `_PYMOL_NOPY` (145), `_WEBGL` (66), `_PYMOL_NO_RAY`, `_PYMOL_LIB`, `PYMOL_EVAL`, `WITH_UNUSED_FUNCTIONS`, `_PYMOL_EMBEDDED`, `PICKLETOOLS`, `_PYMOL_ACTIVEX`, `_PYMOL_INCENTIVE`, `_MACPYMOL_XCODE`. About 460 simple guards and at least 1,100 dead lines; compound conditions were not counted. One macro per PR, with `unifdef` (a tool on the development machine, not a dependency; not installed yet). | The compiler sees the same text: `g++ -E -P` output of every touched file is identical before and after, apart from `__LINE__` values. Then the suite. |
| 8c to 8g | As planned above, file by file in profile order. | Suite, sanitizer job, `compare.py`, PSE round trip. |

8i comes before 8c because it removes lines that 8c to 8e would otherwise
modernize, and because it is the only slice with a mechanical proof.
`os_gl_glut.h` and `os_gl_glut_pretend.h` (GLUT is gone since 4.3.1) go in the
same slice if their constants have no other user.

### New mechanisms and libraries, judged

CI compilers: GCC 11 (Ubuntu 22.04), Apple Clang, MSVC. Cold build is 54 s
([baseline](../baseline.md)).

| Idea | Verdict |
| --- | --- |
| C++20 flag | **Later.** All three compilers have it. Today it would replace only `include/pymol/span.h` (58 lines, 21 uses). Turn it on when a slice needs `std::span` or designated initializers; it is one line in `CMakeLists.txt` and `setup.py`. |
| `std::format` or the fmt library | **Skip.** GCC 11 has no `<format>`; fmt is a new dependency. `snprintf` is bounded since 8b. |
| `std::expected` (C++23) | **Skip.** `pymol::Result` does the job at 419 sites; GCC 11 lacks it. |
| pybind11 | **Skip**, decided above. |
| Eigen | **Skip.** GLM is linked and used at 600 sites. `layer0/Vector.cpp` and `Matrix.cpp` (3,500 lines of hand-written math on `float*`) move to GLM only inside functions step 1 is optimizing anyway. |
| Drop `include/tnt` (10,800 vendored lines) | **Candidate, not neutral.** Two files use it for a 3x3 eigen solve, SVD and LU (`Matrix.cpp`, `ccealignmodule.cpp`). A replacement changes results in the last digits, so it needs an RMSD tolerance test for `cealign` and `fit` first. After 8g. |
| `std::from_chars` or fast_float for number parsing | **Only on a profile.** 315 `atof` / `sscanf` sites; float `from_chars` is recent in Apple's libc++. Belongs to step 1 if a loader profile shows parsing. |
| TBB or a thread pool | **Skip.** OpenMP is there (14 pragmas), `Ray.cpp` has its own workers. |
| `-Wall -Wextra` | **Cheap, once.** Add to the sanitizer job without `-Werror`, read the list once, fix what is a real defect (uninitialized values), ignore the rest. |
| `clang-tidy` | **Still open**, as above: per file in 8f, never whole-tree. Not installed on the development machine. |
| ccache, Ninja, unity build, precompiled headers | **Skip.** 54 s cold build is not a problem. |
| Fonts as `.ttf` data files instead of `FontTTF.h` (16.8 MB of source) | **Skip.** Smaller repository, but the file must then be found at run time on three platforms: a packaging risk for no user-visible gain. |

### Code structure

- **The layers are not layers.** In about 120 cases a file includes a header from a higher
  layer (`layer0` from `layer1`: 20 files; `layer2` from `layer5`: 26;
  `layer1` from `layer5`: 16). The directory names describe history, not
  dependencies.
- **Do not move or rename directories anyway.** A move changes no behavior and
  helps no user, makes every `git blame` and upstream comparison harder, and
  the roadmap already rejected collapsing directories without evidence. The
  repo map in `AGENTS.md` is the cheap fix for "where is what".
- **What does improve structure without risk is deletion:** 8i (dead
  branches), 8d (the VLA macro layer and `MemoryDebug`), 8g (`ov/`), then
  `include/tnt`. Each ends with files gone.
- **Splitting large files** (`Executive.cpp`, 17,700 lines) stays skipped
  until a change inside is blocked by the size. A split is a pure move, so
  when it is needed it gets its own PR with no other edit in it.
