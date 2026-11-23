# 34 — An independent ball-and-stick representation

[Roadmap](../../PLAN.md) · Request 2026-11-23, drafts 3 and 4 · **Planned
at 4.43.0; not built.** No renderer benchmark or reference image made in this
run. Values below are requested defaults or proposals, not measurements.

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
