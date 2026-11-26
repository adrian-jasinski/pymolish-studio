# 34 — An independent ball-and-stick representation

**34d done 2026-11-26 in 4.84.0; the step is finished again.** As built:
setting 801, `ball_and_stick_transparency`, at the level of an object and
its states (answer 124 A), read in `RepCylBond.cpp` where the
representation forced opacity, also for a ball without bonds; in the scene
list of `MovieScene.cpp`; the rows are Presets > transparency
([15n](15-presets.md)). Measured in the real window, 957 x 468 logical
pixels, 1aon with all 59,192 atoms: 20.9 and 21.9 ms a frame opaque,
19.1 ms at 50 %; a ligand of 53 atoms 0.6 to 0.7 ms either way. PyMOL
3.2.0a loads, ray traces and saves a session with the setting and drops
it. ASan and UBSan clean on `ball_and_stick.py`. Left out: pictures of
clipping and of multiple bonds of their own (the stick code draws both),
ray times, memory.

**Planning update 2026-11-26 at 4.82.0: reopened for 34d.** The requested
Transparency submenu in [15n](15-presets.md) needs core support: this
representation currently forces opacity. The original 34a–34c remain
shipped. No renderer or benchmark was run for this update.

## 34d — independent transparency

Do not simulate this by changing `sphere_transparency` and
`stick_transparency`, which would affect other representations and do not
currently affect `ball_and_stick` at all. Reuse the existing CGO alpha path
in `layer2/RepCylBond.cpp`; no new representation or shader framework.

**Question 124, shared with 15n:** A, recommended: a single
`ball_and_stick_transparency`, default 0, global/object scope, affecting
both balls and bonds. Selection menu actions resolve containing objects,
as today's Cartoon transparency does. B: atom/residue scope with half-bond
transitions and per-atom alpha. B is a separate scope choice, not implied
by the existing size/color controls. No independent opacity for balls
versus bonds is requested.

Under A:

- Append the setting in `layer1/SettingInfo.h`; never reuse a positional
  hole. Use the existing transparency range convention. Add invalidation
  of `cRepBallAndStick` in `Setting.cpp`, without invalidating spheres or
  sticks unnecessarily.
- In `RepCylBond.cpp`, replace the forced `transp = 0.0F` for `balls`
  with this setting. Trace bonded balls, both bond halves, multiple bonds,
  zero-order bonds, caps and the isolated-atom path, which currently resets
  CGO alpha to 1. Mark transparency on all affected paths and check cached
  shader geometry, ray tracing, picking and clipping. A change must not
  leave opaque cached geometry behind.
- Preserve the representation's own visibility, colors, sizes and bond
  orders. With ordinary spheres and sticks visible at the same time,
  changing any of the three transparency settings affects only its own
  representation. Opaque remains the default for existing sessions.
- Include the new setting in `layer3/MovieScene.cpp`'s visual-state list;
  verify existing PSE/PSEX serialization and snapshot Undo. Reuse the
  established setting storage; do not introduce a new file-format layout.
  Any required output-format change needs a separate decision under
  `AGENTS.md`, not an assumption made by this plan.
- Wire the menu/reset behavior through 15n. Keep S > ball and stick's
  existing size controls and its C/H actions; do not spread duplicate
  transparency controls across the UI for this task.

Extend `testing/tests/api/ball_and_stick.py` with opaque and partial-alpha
viewport/ray images, isolated atoms, multiple bonds, simultaneous spheres
and sticks, setting inheritance/unset, multiple objects, clipping and
state changes. Extend `scene_style.py`, `snapshots.py`, `preset.py` and
`menu.py` for round trips, Undo/Redo and every requested percentage. Build
with C++ tests, run the full suite and sanitizer checks; compare opaque
frame time before/after and report the cost of transparency on the same
small ligand and larger object. Timings and native-driver checks are still
to be done. Ship with 15n as one feature slice if practical.

## Earlier releases and design

[Roadmap](../../PLAN.md) · Request 2026-11-23, drafts 3 and 4 · **Planned
at 4.43.0 and built the same day, 4.48.0 and 4.49.0: see the note below.**
The plan itself made no benchmark; its values are requested defaults or
proposals, and what was measured is in the note.

**34a and 34b done 2026-11-23 in 4.48.0, 34c in 4.49.0; the step is
finished.** As built: representation 21 (`cRepBallAndStick`), made by the
stick code with its own visibility bit; settings 798 to 800,
`ball_and_stick_scale` (0.31), `ball_and_stick_bond_radius` (0.12) and
`ball_and_stick_color`, all at atom level, so `set name, value, selection`
does what the examples below say; "atomic" as color is by element. Bonds
always show their order; each half has the color of its atom's ball
(question 59); an atom without bonds is a ball. Measured in the window on
1AON with all 59,192 atoms: 23.6 ms a frame, against 24.2 ms for sticks
plus spheres of the same sizes and 23.0 ms for sticks alone. A real click
on a ball picks its atom. Sanitizer runs clean. Different from the
contract below: the quality settings of sticks are shared and it is never
transparent (a `ponytail:` note in `RepCylBond.cpp`); no bond color of its
own; memory and ray time were not measured. Found with PyMOL 3.2.0a: it
loads, ray traces, recalls scenes and saves such a session, but ended when
it saved one with a setting it does not know on an atom, so those are
written under `pymolish_unique_settings` (question 62); it does not draw
the representation. 34c: twenty presets and the view at load (question
63); "simple" and "default" still draw ligands as lines.

**Changed 2026-11-23 in 4.53.0, at the user's request:** `ball_and_stick_scale`
defaults to 0.25, not 0.31; S > ball and stick in the panel holds only ball
size and bond thickness (4.52.0 added the menus).

**Ball-and-stick gets its own visibility, sizes, colors and bond orders.
Showing, hiding or styling it must not change lines, sticks or spheres.**
Ligands drawn by molecular presets use it by default once it is complete.

## Why the existing preset is insufficient

`preset.ball_and_stick` and `_ball_and_stick_ligand` in
`modules/pymol/preset.py` show sticks plus spheres and set their settings.
The ligand helper uses sphere scales 0.18/0.13 and changes atom colors;
the general preset uses 0.25 in mode 1, or `stick_ball` in mode 2. Neither
has independent visibility or colors. Those are historical implementations,
not the new design. This supersedes the corresponding rules and exclusions
in [step 15](15-presets.md).

## Representation and commands

Canonical name proposed: `ball_and_stick`, displayed as “Ball-and-stick” in
S and H for objects and selections, including the viewport menus. Use the
ordinary command family rather than new synonyms:

```pml
show ball_and_stick, organic
hide ball_and_stick, organic
as ball_and_stick, sele
set ball_and_stick_scale, 0.31, organic
set ball_and_stick_color, marine, organic
set ball_and_stick_bond_radius, 0.12, organic
unset ball_and_stick_color, organic
```

Names and the proposed bond radius are reviewed against existing settings
before coding. `0.31 × atom.vdw` is the requested ball-radius default, using
the same radius basis as `sphere_scale=0.31`, without reading or writing
`sphere_scale`. Scaling does not change either representation's color.

| Requirement | Contract |
| --- | --- |
| Independent visibility | A new appended representation ID/bit, not an alias for two existing bits. `show`, `hide`, `as`, `toggle`, `rep` selections and `hide everything` include it normally. Simultaneous spheres/ball-and-stick are allowed. |
| Independent color | A dedicated atom/object/global color override, defaulting to the existing atom color. C > Ball-and-stick offers a color and “By element” / “Use atom colors”; 11c adds the explicit CPK scheme afterwards. These operations touch only its color overrides, including per-element overrides; ordinary atom coloring continues to affect representations inheriting atom colors. |
| Independent size | Ball scale and bond radius are separate settings with appropriate atom/bond scope and validation. Changing line width, stick radius, valence or sphere scale cannot change this model. |
| Bonds | Single, double and triple bonds use stored bond order. Aromatic bonds use the core's existing convention with a documented appearance. Missing order is shown as unknown/single fallback, never guessed from distance as a chemical claim. No molecule data is changed by drawing it. |
| Bond colors (question 59) | **Half-bonds follow the endpoint ball colors (recommended)**; alternative: uniform dark bonds, with a separate bond-color override. The latter is useful but adds a control; decide before building. |
| Other essentials | Existing atom picking, state/coordinate updates, clipping, transparency, lighting, ray tracing and PNG export work. Hydrogen visibility follows the atom selection; drawing does not add/remove hydrogens. |
| Reset and inheritance | `unset` removes the override and returns to this representation's own defaults/inheritance. No save-and-restore of sphere or stick settings around a draw. |

Implement in the existing representation/CGO/shader path, reusing sphere and
cylinder generation where practical. A wrapper that temporarily changes global
settings is invalid, as are duplicate molecular objects or a detached CGO
that loses selection and session behavior. Reuse must not copy entire renderers
or create a general rendering framework for this one feature.

## Reach of the change

- `layer1/Rep.h`, `Rep.cpp`: append ID and masks; audit all `cRepCnt` loops
  and fixed-size tables. Preserve all existing numeric IDs.
- `layer2/CoordSet.cpp`, `RepSphere*`, `RepCylBond*`, new representation
  implementation as needed: factory, caches, invalidation, picking, ray/GL.
- `layer1/SettingInfo.h`, `Setting.cpp`: append settings, levels, updates and
  defaults; never reuse positional holes. Trace atom/bond setting serialization.
- `modules/pymol/constants.py`, `viewing.py`, `menu.py`, completion and help:
  names, representation lists, S/H/C, `color_deep`/reset semantics.
- `preset.py`, affected preset tests and docs; step 35 scene capture of its
  per-atom/per-bond overrides; session save/load and backward readers.
- Session compatibility is an implementation gate: step 28's success with
  extra dictionary keys does **not** prove a new core representation bit is
  safe in an older reader. Preserve ordinary PSE/PSEX data, test old files
  here and new files in the supported older reader, and document unsupported
  display state. Agree any new output layout before implementing it.

## Presets (34c)

Audit every molecular preset that draws ligands: classified/default view,
simple/technical, pretty, publication/publication green, glass, illustration,
ligands and every ligand-sites variant, plus complex presets where applicable.
Replace the ligand's legacy sticks/spheres composite with the new
representation. Explicitly retain solvent, ion and protein representations;
only ligands visible under that preset are affected. Old sphere/stick color
and size overrides are preserved, including hidden ones.

The “ball and stick” preset remains reachable and uses the new representation.
Existing callable mode arguments must not be silently ignored: document the
mapping or deliberate deprecation in help and `ChangeLog`, with regression
coverage. Presets keep the current rule against recoloring cartoons/surfaces.
Ligand-specific preset colors go to the new overrides, not atom colors.
34c follows scene-style storage (35b); a stored pre-preset scene must recall
its old ligand style after the new preset has run.

## Slices and acceptance

| Slice | What | Check |
| --- | --- | --- |
| 34a | Core representation, independent settings, bond orders, commands and serialization. | New `testing/tests/api/ball_and_stick.py` plus Catch2 where needed: single/double/triple/aromatic fixtures, 0.31 radius basis, state updates, picking, ray/viewport images; legacy settings/atom colors/visibility unchanged after show/color/scale/hide. |
| 34b | S/H/C menus, size controls using existing settings UI, completion/help and scene integration. | Every menu route works on object and selection; set conflicting sphere/line/stick styles and alternate views; its element coloring affects only ball-and-stick; old/new PSE and PSEX, scene and Undo round trips. |
| 34c | Ligand defaults in presets and migration of the existing preset. | Parameterized preset test on a protein, ligand, water and ion; expected ligand bit is present, legacy settings preserved, polymer colors unchanged, scene A/preset B/recall A restores A. |

Measure viewport frame time, ray time and memory on a small ligand and a
large ligand collection against today's composite; record actual results,
not a promised speedup. Each completed feature slice gets an `X` version.
No default switch in presets until all render/export paths pass.

Skipped: a new chemistry toolkit, automatic bond-order repair, another shader
framework and independent appearance controls beyond those needed here.
