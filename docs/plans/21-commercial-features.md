# 21 — Features of the commercial build: removed, kept, to rebuild

[Roadmap](../../PLAN.md) · Request 2026-11-19 · **Removals done in 4.19.18
to 4.19.22. The seven rebuilds are planned, none is built.**

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
| 4.19.18 | The commercial Maestro reader's leftovers: the `mae` stub, the Maestro load dialog, load types 65 and 66, `.maegz`, the unused parser `chempy.mae`, the `mimic` plumbing under `cmd.load`. 36 tests, 14 data files. | Saving `.mae`. Loading `.cms`. `cmd.load` still accepts `mimic`. See question 1. |
| 4.19.19 | Automatic atom typing through mmlibs: 206 lines behind `NO_MMLIBS` and `_PYMOL_IP_EXTRAS`, none compiled. Test PYMOL-317, test flag `mmlibs`. | The property and keyword `text_type`, MOL2 atom types (`assign_atom_types`), the keyword `stereo`. |
| 4.19.20 | Stubs for MOE (`.moe`, `.ph4`), Maestro surfaces (`.vis`), Phase pharmacophores (`.phypo`). 6 tests, 7 data files. | Nothing; loading one reports "unsupported file type". |
| 4.19.21 | The FreeMOL test and its flag. | `chempy/tinker` still reads `FREEMOL_ETC` when set. |
| 4.19.22 | `api/computing.py` (expected the commercial force field's energy). | `clean` itself: rebuilt in 4.12.1 with rdkit ([step 13](13-structure-cleanup.md)). `jira/PYMOL-2985.py` now runs against it. |

**One side effect to know.** With the stub gone, `load file.mae` falls
through to the VMD plugin that reads Desmond `.cms` files (kept on purpose
with the other VMD plugins). So a `.mae` file now loads: atoms, bonds and
cell, without styles, labels or properties. Removing that too means removing
the plugin, `.cms` loading and `.mae` saving: question 1.

**FreeMOL, decided as asked:** only the dead test went. Nothing else in the
tree uses FreeMOL, so nothing else changed.

## To rebuild

Order: smallest and most independent first. Each slice is one session and
one commit, with `ChangeLog` and a version bump. A–C are options; the
recommended one is marked.

### 21a — STL export

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

- **Now:** `assign_stereo` raises. The atom property and selection keyword
  `stereo` exist and are always empty.
- **Options**

  | | Option | Note |
  | --- | --- | --- |
  | A | `assign_stereo` with rdkit: molecule out as MOL block, CIP labels from the 3D coordinates, written back with `alter`. `method=schrodinger` gives a clear error. **Recommended.** | rdkit is already the approved extra `chem`. About 40 lines of Python. |
  | B | A, plus automatic assignment whenever `stereo` is used in `iterate`, `label` or a selection. | What mmlibs did. Needs a hook from the C++ core into Python on every such call; the hooks were deleted in 4.19.19 as dead code. |

- **Menu:** label > stereochemistry was dropped in
  [step 14](14-menus.md) because it labelled nothing. It comes back, and
  calls `assign_stereo` first.
- **Tests**

  | Test | What happens to it |
  | --- | --- |
  | `stereochemistry.py::test_assign_stereo_rdkit` | Keep; the acceptance test (15 R, 5 S on `1ehz-5.pdb`). |
  | `stereochemistry.py::test_assign_stereo_schrodinger` | Delete: needs a Schrödinger installation. |
  | `mmpymolx.py::testStereo`, `testStereoPYMOL2782` | Rewrite with a call to `assign_stereo` before each check, move into `stereochemistry.py`. With option B they stay as they are. |

### 21c — Pi interactions

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

- **Now:** `focal_blur` raises.
- **Plan:** the published method of the command's own docstring (Underhaug,
  Vertrees, Holder): render `samples` images, each with the camera turned a
  little around the point in focus, and average them. One option only:
  Python in `experimenting.py`, `QImage` for reading and writing PNG, numpy
  for the average. No new dependency, about 40 lines.
- **Tests:** keep `experimenting.py::testFocalblur`, and make it check
  something: the result differs from a single sharp image.

### 21e — Morphing

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

| Item | Now | Options |
| --- | --- | --- |
| Smooth edges in the viewport (`antialias_shader`) | The setting, the menu rows and the render stage (`SceneRenderAA`) exist; the FXAA and SMAA shaders were never in the open tree. | A: FXAA only, one shader and one pass, a public algorithm (**recommended**). B: SMAA as well, three passes and two lookup textures. C: no shader, switch on 4x multisampling of the window (`pymol_gl_widget.py`, one line, costs frame time on large scenes: measure). |
| Sphere modes 10 (cubes) and 11 (tetrahedra) | The setting accepts 10 and 11; nothing in the tree draws cubes or tetrahedra, and the test's image comparison fails. | A: build both as shader impostors next to mode 9. B: cap the setting at 9 and delete the test (**recommended**: no use beyond novelty). |
| Background image inside the session file | `bg_image_filename` is saved as a path; the session breaks when the image moves. | A: on save, store the image in the setting as a `data:` text (**recommended**; changes PSE output, so it needs a yes: question 4). B: leave as is, delete the test. |

**Tests:** `settings.py::testAA` (needs a real window), `cgos/reps.py::test_sphere_mode_10_11`
with its two reference images, `jira/PYMOL-1571.py` (needs a real
window). Each is kept if its item is built and deleted if it is dropped.

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

## Not asked, still refusing

These still raise `IncentiveOnlyException`. Nothing was changed; question 5.

| Command | What it would do | Suggestion |
| --- | --- | --- |
| `load_mtz`, `map_generate` | X-ray reflections (MTZ) to a density map | Remove both with the MTZ load dialog, or rebuild on the vendored FFT; the largest item on this list. |
| `help_setting` | Describe a setting | Remove: this tree has no description texts for settings. |
| `callout` | A label with a pointer line that stays put on screen | Remove, or rebuild in step 19 if movies need it. |
| `desaturate` | Fade the colours of a selection | Rebuild: about 10 lines. |
| PDB header as object property (`testPdbHeader`) | Keep the header text of a PDB file | Rebuild if properties are used; small. |

`copy_image` is not on the list: the Qt window has its own implementation
and it works. Only a source comment still calls it proprietary.

When the last stub is gone, `IncentiveOnlyException`, the test flags
`incentive` and `properties` and the option `-n` go too.

## Questions

1. Maestro: keep what is left (`.mae` saving, `.cms` loading, and through
   the same plugin basic `.mae` loading), or remove all of it (the plugin
   `maeffplugin.cpp`, 2,130 lines, and the exporter: 276 lines of helpers
   and its class in `MoleculeExporter.cpp`)? Kept so far
   because it works, has passing tests, and removing a format that is
   written needs a yes.
2. 21b: is the explicit command enough (A), or must `stereo` fill itself in
   (B)?
3. 21f: which of the three items are wanted? Recommended: FXAA yes, sphere
   modes 10 and 11 no, background image in the session yes.
4. 21f: may the session file store the background image itself? It changes
   what is written to a PSE.
5. The five commands under "Not asked": remove or rebuild, each?
6. 21g: is option C the right size, or is undo of coordinates enough for
   now?

## Skipped

- Reading STL, torsion-space morphing, SMAA: listed as options, not planned.
- RigiMOL and the commercial readers for Maestro styles, MOE and Phase:
  proprietary; not rebuilt.
- The remaining `_PYMOL_IP_EXTRAS` blocks (twelve, in eight files) and the
  `INCENTIVE_ONLY` error code: dead guards for
  [step 8](08-cpp-modernization.md), 8i style, not part of this request.
