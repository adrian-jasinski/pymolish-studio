# 21 — Features of the commercial build: removed, kept, to rebuild

[Roadmap](../../PLAN.md) · Request 2026-11-19 · **Removals done in 4.19.18
to 4.19.26. 21a to 21e built in 4.19.33 to 4.19.37. 21f was decided on
2026-11-20 and is to build; 21g was decided the same day (option C) and is
to build last.** Answers of the
user from 2026-11-19 are applied: all Maestro support removed, a command is
enough for stereochemistry, stubs that break nothing else removed.

**The code that only said "this needs the commercial PyMOL" is going away
in two directions: what this program will never do is deleted, with its
tests; what is worth having is rebuilt here, one feature per slice, and
its old test becomes the acceptance test.**

## What existed at 4.19.17

Schrödinger's open-source tree keeps the commands of the commercial
("Incentive") build as stubs that raise `IncentiveOnlyException`, and keeps
their tests, marked `incentive`. Here 63 such tests were skipped on every
run, and 26 more that wait for multi-step undo.

The flag `-n` makes the test runner believe it is the commercial build, so
those tests run and fail instead of being skipped:

    pymolish -ckqyn testing/testing.py --run testing/tests/api/morphing.py

That is the acceptance check of every slice below: its tests pass with
`-n` first, then the `incentive` mark comes off.

## Done: removed

| Version | Removed | Stays |
| --- | --- | --- |
| 4.19.18 | The commercial Maestro reader's leftovers: the `mae` stub, the Maestro load dialog, load types 65 and 66, `.maegz`, the unused parser `chempy.mae`, the `mimic` plumbing under `cmd.load`. 36 tests, 14 data files. | `cmd.load` still accepts `mimic`. The rest of Maestro went in 4.19.24. |
| 4.19.19 | Automatic atom typing through mmlibs: 206 lines behind `NO_MMLIBS` and `_PYMOL_IP_EXTRAS`, none compiled. Test PYMOL-317, test flag `mmlibs`. | The property and keyword `text_type`, MOL2 atom types (`assign_atom_types`), the keyword `stereo`. |
| 4.19.20 | Stubs for MOE (`.moe`, `.ph4`), Maestro surfaces (`.vis`), Phase pharmacophores (`.phypo`). 6 tests, 7 data files. | Nothing; loading one reports "unsupported file type". |
| 4.19.21 | The FreeMOL test and its flag. | `chempy/tinker` still reads `FREEMOL_ETC` when set. |
| 4.19.22 | `api/computing.py` (expected the commercial force field's energy). | `clean` itself: rebuilt in 4.12.1 with rdkit ([step 13](13-structure-cleanup.md)). `jira/PYMOL-2985.py` now runs against it. |
| 4.19.24 | All Maestro file support: saving `.mae` (exporter, `get_maestr`, the row in the save dialog), the VMD plugin `maeffplugin` that read `.mae` and Desmond `.cms`, and with it the Desmond `.idx` loader, which needs a `.cms`. 3,014 lines of code, 5 test cases. | Desmond `.dtr` trajectories through `load_traj`, on a structure loaded from another format. |
| 4.19.25 | `help_setting`, `callout`, `desaturate`. Tests for `help_setting` and for the PDB header as a property. | Nothing. |
| 4.19.26 | Maps from MTZ files: `load_mtz`, `map_generate`, the MTZ dialog, the header parser `pymol.headering`, the C++ function. 985 lines; no call ever produced a map. | Every other map format. |

**What the full Maestro removal touched besides Maestro** (4.19.24):

- Loading a Desmond `.idx` file is gone: it loads a `.cms` first.
- `api/pbc.py`, the periodic-boundary tests, used that `.idx` as their
  data. They now load an mmCIF copy of the same structure (same atoms and
  1,672 bonds) and the same trajectory; every expected value is unchanged.
- The APBS plugin can call Schrödinger's `prepwizard`. It asked for a
  Maestro file back; it now asks for a PDB file. Not tested: it needs a
  Schrödinger installation.
- Left alone: the mouse mode "Emulate Maestro" (a set of mouse buttons,
  no file format).

**FreeMOL, decided as asked:** only the dead test went. Nothing else in the
tree uses FreeMOL, so nothing else changed.

## To rebuild

Order: smallest and most independent first. Each slice is one session and
one commit, with `ChangeLog` and a version bump. A–C are options; the
recommended one is marked.

### 21a — STL export

**Done in 4.19.33, option A.** `RayRenderUSDA` got a second output: the
meshes it already builds (tessellated solids, the scene's triangles) are
written as binary STL facets, 60 lines in `layer1/USD.cpp`; `_cmd.get_stl`
shares its body with `get_glb`. Checked besides the test: spheres, sticks
and a surface of a fragment give closed meshes with unit normals that point
outward (positive signed volume). Not checked: a slicer or another program
reading the file.

- **Now:** `save file.stl` and `cmd.get_stlstr` raise. Reading STL
  (`read_stlstr`) raises too.
- **Options**

  | | Option | Note |
  | --- | --- | --- |
  | A | Write binary STL in C++ next to the USD and glTF exporters (`layer1/USD.cpp`, `GLTF.cpp`), from the triangles they already collect. **Recommended.** | Every representation those exporters handle comes for free. |
  | B | Convert the text of `save file.obj` in Python. | No C++, but parses text the program has just written. |
  | C | Also read STL, as a CGO object. | Not asked. Skip until someone needs it; then `read_stlstr` is about 30 lines of numpy. |

- **Tests:** keep `exporting_geom.py::testSTL` (spheres, sticks, surface:
  more than 84 bytes each). Add one line: the triangle count in the header
  equals (length − 84) / 50.
- **Size:** about 60 lines. No dependency.

### 21b — Stereochemistry (R/S)

**Done in 4.19.34, option A.** 25 lines in
`modules/pymol/stereochemistry/__init__.py`: each object of the selection
goes to rdkit as a MOL block, unsanitized (a PDB file has no bond orders or
charges, and the CIP rules need neither), `AssignStereochemistryFrom3D`,
labels back with `alter`. 1oky (2,475 atoms, 301 centers) takes 0.03 s.
Label > other properties > stereochemistry is back. Not looked at: atoms
with alternate coordinates (both copies go into the MOL block), and
rdkit's newer, slower CIP labeler, which differs from the classic rules in
rare cases.

- **Now:** `assign_stereo` raises. The atom property and selection keyword
  `stereo` exist and are always empty.
- **Options**

  | | Option | Note |
  | --- | --- | --- |
  | A | `assign_stereo` with rdkit: molecule out as MOL block, CIP labels from the 3D coordinates, written back with `alter`. `method=schrodinger` gives a clear error. **Decided 2026-11-19.** | rdkit is already the approved extra `chem`. About 40 lines of Python. |
  | B | A, plus automatic assignment whenever `stereo` is used in `iterate`, `label` or a selection. Not built. | What mmlibs did. Needs a hook from the C++ core into Python on every such call; the hooks were deleted in 4.19.19 as dead code. |

- **Menu:** label > stereochemistry was dropped in
  [step 14](14-menus.md) because it labelled nothing. It comes back, and
  calls `assign_stereo` first.
- **Tests**

  | Test | What happens to it |
  | --- | --- |
  | `stereochemistry.py::test_assign_stereo_rdkit` | Keep; the acceptance test (15 R, 5 S on `1ehz-5.pdb`). |
  | `stereochemistry.py::test_assign_stereo_schrodinger` | Delete: needs a Schrödinger installation. |
  | `mmpymolx.py::testStereo`, `testStereoPYMOL2782` | Rewrite with a call to `assign_stereo` before each check, move into `stereochemistry.py`; `mmpymolx.py` then has nothing left and goes. |

### 21c — Pi interactions

**Done in 4.19.35, option A, with 5 lines instead of 150.** The plan was
wrong about what was missing: the finder `FindPiInteractions` (rings, cations,
the distance and angle rules) was already in `layer3/Interactions.cpp`,
compiled and never called. Only `ObjectDistNewFromSele` refused modes 5 to 7.
It now calls the finder, and `pi_interactions` calls `distance` with mode 5.
Checked besides the test: the two menu rows on 1rx1 give four and one
dashes. Not looked at: structures without formal charges on lysine and
arginine (the finder asks the core to assign them), several states.

- **Now:** `cmd.pi_interactions` raises. The menu rows find > pi-pi and
  pi-cation are there and call `distance` with mode 6 and 7, which prints
  "modes 5-7 only available in Incentive PyMOL" and leaves an empty object.
  (Step 14 recorded these two rows as working; they are not.)
- **Options**

  | | Option | Note |
  | --- | --- | --- |
  | A | Modes 5, 6 and 7 in C++ next to the halogen-bond finder (`FindHalogenBondInteractions`, mode 9), which has the same shape: find partners, fill a `DistSet`. **Recommended.** | The menu rows, sessions and `pi_interactions` then work unchanged. Dashes run between ring centres. |
  | B | Python with rdkit: ring centres as pseudoatoms, ordinary distances between them. | Adds helper objects to the object list and needs rdkit for a measurement. |
  | C | Remove the two menu rows and the command. | If the feature is not wanted after all. |

- **The rules to implement** (the usual ones; the test fixes the numbers):
  aromatic ring centres closer than the cutoff with ring planes parallel or
  perpendicular (pi-pi); a positively charged atom above a ring centre,
  close to the ring normal (pi-cation).
- **Tests:** keep `querying.py::testPiInteractions`: `1rx1.pdb` has four
  pi-pi and one pi-cation contact, with reference coordinates. Delete its
  last line `pytest.skip("TODO")`.
- **Size:** about 150 lines of C++.

### 21d — Focal blur

**Done in 4.19.36.** 45 lines in `experimenting.py`, as planned: the camera
positions lie on a sunflower pattern inside the aperture, `png` hands each
image over in memory, `QImage` decodes and encodes, numpy averages. The
result goes on display with `load_png` and `movie=0`; with the default the
picture became a movie frame and the core's movie panel took 26 pixels from
the viewport. Checked in the real window on WSLg (1rx1, 8 samples, 0.7 s)
and ray traced (12 samples, 9 s). Not done: a blur that grows with the
distance in depth only; turning the camera also blurs what is far to the
side.

- **Now:** `focal_blur` raises.
- **Plan:** the published method of the command's own docstring (Underhaug,
  Vertrees, Holder): render `samples` images, each with the camera turned a
  little around the point in focus, and average them. One option only:
  Python in `experimenting.py`, `QImage` for reading and writing PNG, numpy
  for the average. No new dependency, about 40 lines.
- **Tests:** keep `experimenting.py::testFocalblur`, and make it check
  something: the result differs from a single sharp image.

### 21e — Morphing

**Done in 4.19.37, option A.** 110 lines in `modules/pymol/morphing.py`.
States of one object are interpolated as they are; two objects are paired
through the alignment object of `align` or `super`. The refinement uses the
sculpting of the core with the mask for bonds, angles, pyramids, planes and
lines only (`sculpt_field_mask` 0x1F), so that the restraints taken from
the first conformation do not pull the intermediates back to it; the two
ends are not touched. Measured on 1rx1 with one half turned by 60 degrees
(1,268 atoms, 30 states): 0.02 s without refinement, 0.11 s with 3; mean
bond length error half way 0.065 A, 0.012 A after 1, 0.007 A after 3,
0.004 A after 10. Not looked at: clashes between the two halves on the
way (the mask leaves van der Waals terms out), nucleic acids, the look
of the movie in the window.

- **Now:** `morph` raises for both methods.
- **Options**

  | | Option | Note |
  | --- | --- | --- |
  | A | `method=linear`: match the atoms, interpolate coordinates, then `refinement` cycles of the sculpting that is already in the core. Linear becomes the default; `method=rigimol` gives a clear error. **Recommended.** | No dependency. Intermediates of large motions are distorted; refinement repairs bond lengths, not the path. |
  | B | A, plus an energy minimisation of each frame with OpenMM. | OpenMM is the approved extra `fix`. Better frames, seconds per frame, proteins only. |
  | C | Interpolate torsion angles instead of coordinates. | Good paths for hinge motions, new code of some size. Only after A has been used. |

  RigiMOL itself is Schrödinger's and is not rebuilt.
- **Tests**

  | Test | What happens to it |
  | --- | --- |
  | `morphing.py::testMorphMulti` | Keep; it already uses `linear`. |
  | `morphing.py::testMorphRigimol` | Rewrite for `linear`; drop `import epymol.rigimol`. |
  | `jira/PYMOL-174.py` (fewer than four atoms) | Rewrite for `linear`. |

### 21f — Rendering details

Three unrelated items; each can be taken or dropped alone.

**Decided 2026-11-20, as recommended:** smooth edges with FXAA (item 1,
option A); sphere modes 10 and 11 dropped, the setting capped at 9, the
test and its two reference images deleted (item 2, option B); the
background image stored inside the session file (item 3, option A). The
answer covers the two things that needed a yes: deleting the two image
files, and the change of what a PSE contains.

Since 2026-11-20 there is a second place for the picture: the session key
of [step 28](28-session-format.md). With it PyMOL would still see the file
name in the setting instead of text it cannot use. Option A stands as
decided: the answer to question 29 (2026-11-20) did not move it. The FXAA pass is
also what a shadow pass for the floor of [step 25](25-studio-effects.md)
would follow.

**1. Smooth edges in the viewport.** Edges of sticks, spheres and cartoons
look like small stairs on screen, because each pixel is either object or
background. Ray-traced images do not have this; the live view does.
Anti-aliasing blurs exactly those stairs. The commercial build has two methods for it, FXAA and SMAA. Here the menu
rows (Setting > Rendering > Antialias (Real Time)) and the setting
`antialias_shader` exist and do nothing: the two
shader programs were never part of the open source.

| | Option | Note |
| --- | --- | --- |
| A | FXAA: one small shader that runs once over the finished picture. **Recommended.** | Public algorithm, about 100 lines of shader. Cheap. Slightly softens text and thin lines. |
| B | SMAA as well. | Sharper than FXAA, but three passes and two lookup pictures to ship. Only if A looks too soft. |
| C | No shader; ask the graphics card for 4 samples per pixel (multisampling), one line in `pymol_gl_widget.py`. | Sharpest edges, but every frame costs more on large scenes, and it does not smooth the round shapes the shaders draw inside a square (spheres, sticks). Measure first. |
| D | Leave it; remove the two dead menu rows and the test. | |

**2. Sphere modes 10 and 11.** `set sphere_mode, 10` draws every atom as a
cube, 11 as a tetrahedron, in the commercial build. A stylistic effect, not
something a structure is usually shown with. Here the setting accepts both
numbers and nothing draws them.

| | Option | Note |
| --- | --- | --- |
| A | Build both, next to the shader spheres of mode 9. | New shader code for an effect few will use. |
| B | Cap the setting at 9, delete the test and its two reference images. **Recommended.** | |

**3. Background image inside the session file.** A picture can be put
behind the molecule (`bg_image_filename`). A session file (.pse) stores
only the path of that picture. Send the session to someone, or move the
picture, and the background is gone. The commercial build writes the
picture itself into the session.

| | Option | Note |
| --- | --- | --- |
| A | On save, store the picture inside the session, as text in the same setting. **Recommended.** | The session gets larger by the size of the picture. It changes what a PSE contains: an older program opening it finds a setting it cannot use as a file name and shows no background image. That is why this needs a yes. |
| B | Leave as is, delete the test. | |

**Tests:** `settings.py::testAA` (needs a real window),
`cgos/reps.py::test_sphere_mode_10_11` with its two reference images,
`jira/PYMOL-1571.py` (needs a real window). Each is kept if its item is
built and deleted if it is dropped.

### 21g — Undo of more than the last move

The largest slice; last, and after a measurement.

- **Now:** each molecule keeps its last 16 coordinate sets
  (`ObjectMoleculeSaveUndo`). `undo` and `redo`, the two toolbar buttons and
  Ctrl-Z restore coordinates only. Deleting an object, removing atoms,
  changing a bond or a colour cannot be undone. `editor.undocontext`, which
  the builder already calls around every edit, does nothing.
- **Options**

  | | Option | Note |
  | --- | --- | --- |
  | A | Snapshots: before a command that changes something, keep the session data of the objects it names on one stack; undo puts them back. | One mechanism for every command. Measured: a snapshot of 1aon (58,870 atoms) takes 0.14 s and 17 MB. So: a limit on depth and on size, and above the size limit the command runs without undo and says so. |
  | B | One inverse operation per command, in C++. | What the commercial build does. Fast and small, but every command needs its own code: a long tail. |
  | C | A for everything that adds, removes or edits; the existing coordinate ring for moves (drag, rotate, sculpt, fit, clean). **Recommended.** | The frequent, large operations stay cheap; the rest is covered by one mechanism. |

- **Slices:** (1) the stack, `undo_enable` and `undo_disable`, the
  capability `multi_undo`, and undo for create, delete, remove and the
  builder's edits through `undocontext`; (2) Undo and Redo in the toolbar
  show whether there is something to undo and name it; (3) the rest of the
  test list.
- **Tests**

  | Test | What happens to it |
  | --- | --- |
  | `testing/tests/undo/api/` (26 cases: create, fragment, group, isosurface, select, protect, fit, clean, symexp, load_traj, ...) | Keep as the list of what must work. They start running by themselves when the capability `multi_undo` appears. |
  | `jira/PYMOL-1276.py` (undo a changed element), `jira/PYMOL-1697.py` (undo a removed atom, discrete object) | Keep. |
  | `jira/PYMOL-1567.py` (label offsets survive remove and undo) | Deleted in 4.19.18 because it loaded a Maestro file. Write it again on `cmd.fragment`. |

## Stubs outside the request: resolved

Rule given by the user on 2026-11-19: remove what breaks nothing else, keep
the rest. All five broke nothing, so all five are gone: `help_setting`,
`callout`, `desaturate` and the test for the PDB header property in 4.19.25,
`load_mtz` with `map_generate` in 4.19.26.

`copy_image` was never on the list: the Qt window has its own
implementation and it works. Only a source comment still calls it
proprietary.

State at 4.19.37: no command raises `IncentiveOnlyException` any more.
`read_stlstr` raises an ordinary error (reading STL stays skipped). What is
left of the machinery: the exception class, its one user
`incentive_format_not_available_func` in `importing.py`, the option `-n`
(`incentive_product`), the test flags `incentive` and `properties`. Five
test files still carry the mark, all for 21f and 21g: `settings.py`
(`testAA`), `cgos/reps.py` (sphere modes), `jira/PYMOL-1571.py`,
`jira/PYMOL-1276.py`, `jira/PYMOL-1697.py`. All of it goes with the last of
those two slices.

## Questions

1. 21f: which of the three rendering details are wanted, and with which
   option? Recommended: smooth edges with FXAA (A), sphere modes 10 and 11
   dropped (B), background image stored in the session (A). The last one
   changes what a PSE contains. **Answer 2026-11-20: as recommended.**
2. 21g: is option C the right size (snapshots for edits, the coordinate ring
   for moves), or is undo of coordinates, as today, enough for now?
   **Answer 2026-11-20: as recommended, option C.**

Answered 2026-11-19: Maestro, remove all of it (done, 4.19.24). 21b, the
command is enough (option A). The stubs outside the request: remove what
breaks nothing else (done, 4.19.25 and 4.19.26).

## Skipped

- Reading STL, torsion-space morphing, SMAA: listed as options, not planned.
- RigiMOL and the commercial readers for Maestro, MOE and Phase:
  proprietary; not rebuilt.
- The remaining `_PYMOL_IP_EXTRAS` blocks (twelve, in eight files) and the
  `INCENTIVE_ONLY` error code: dead guards for
  [step 8](08-cpp-modernization.md), 8i style, not part of this request.
