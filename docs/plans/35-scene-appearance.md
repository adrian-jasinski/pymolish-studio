# 35 — Scenes recall appearance, and open with one click

[Roadmap](../../PLAN.md) · Request 2026-11-23, drafts 6 and 7 · **Planned
at 4.43.0 and built the same day, 4.44.0 and 4.47.0: see the note below.**
The plan was written from the source, without a running window.

**35a done 2026-11-23 in 4.44.0, 35b in 4.47.0; the step is finished.**
35a: a left click or Enter recalls once; a right click and the arrow keys
pick a row without recalling it (question 65). Tried with clicks sent
through the X server, dark theme. 35b as built: `MovieScene` got a style
(cartoon type per atom, the settings of atoms and bonds whichever they are,
89 listed settings at the object and the global level, the RGB of the named
colors referred to), written as a seventh item of the scene's session
record (question 62); a six-item record loads as before and changes no
style. `scene` got the keyword `settings`. Measured: ray-traced geometry
and the viewport picture of A identical after B and back; 4V6X (239,306
atoms) store 40 ms against 14 without style, recall 28 ms against 13;
1.7 MB more in the session when every atom carries two settings and a
cartoon type; a movie that visits two scenes brings each style; PyMOL
3.2.0a loads and recalls such a session without the style; the sanitizer
run is clean. Left out: settings of single states, secondary structure,
Undo, the test with a redefined color that the scene does not use (only
colors a scene refers to are kept, as planned).

**Store scene A, apply a different preset or coloring, then recall A: its
cartoon, ligand style and colors must return. One click on a scene recalls it.**
This changes the double-click interaction of step 3. It also strengthens the
scene contract used by presets, the movie timeline and the assistant.

## What the code stores

`modules/pmg_qt/scene_panel.py` connects `itemActivated` to `cmd.scene`.
`modules/pymol/viewing.py:scene` routes to `layer3/MovieScene.cpp`.
`MovieScene.h` stores camera, frame, enabled objects, atom/object colors,
representation visibility, text and thumbnail. It has no general setting
snapshot. In particular, changing a preset can change representation
settings and per-atom cartoon type without changing the stored visibility.
Atom colors are already stored; “save colors” is an audit of overrides and
custom color definitions, not a claim that scenes currently save no colors.

## 35a — single-click recall

- A completed primary click on a row or thumbnail recalls that scene once;
  Enter still recalls. F2 and Rename still edit the name.
- Drag/reorder, right click, inline rename and polling/programmatic row
  selection must not recall a scene. Do not connect `currentItemChanged`
  indiscriminately. Double click must not recall twice or open the editor.
- Keep Add, Update, Delete, ordering, thumbnails and keyboard shortcuts.
  Update the tooltip/help to say “Click or Enter”.
- Extend `testing/tests/api/scene_panel.py`: one click, Enter, double click,
  F2, reorder and list refresh; count recalls, not only selected rows.
  Check with a real mouse in both themes. This is a new `X` behavior slice.

## 35b — save the appearance that presets and colors change

Use the existing scene store/recall path so the command line, panel, function
keys and movie scene recalls agree. Do not restore the whole session when
recalling a scene: coordinates, newly loaded objects, table ratings and the
user's work after the scene was stored must survive.

| Capture | Details |
| --- | --- |
| Cartoon style | Per-atom cartoon type (`cartoon` command), secondary structure if explicitly changed as part of the visual setup, cartoon color and relevant shape/transparency settings. |
| Ligand and other representations | Sphere scale/color; stick radius/color and valence, including bond overrides; line width/color; surface color/transparency; the independent settings of step 34 as soon as it ships. |
| Preset/look state | The finite list of visual global/object/state/atom/bond settings actually changed by `preset.py`, including lighting, fog and outline. Capture displayed background and `stage` settings when they affect the stored look. Inventory this list in code/tests before implementing. |
| Colors | Existing atom/object colors plus representation overrides. A custom color redefined after storing must recall its stored RGB; restore only referenced definitions and document that those definitions are global. The selected palette need not become a persistent application preference merely because a scene is recalled. |
| Inheritance | Store both a value and whether its override existed. Recalling a scene with no override must remove one introduced later, not leave B's value under A. Preserve global/object/state/atom/bond scope. |
| Scope | Preserve the current `view`, `color`, `rep`, `active`, `frame` and `sele` controls. `color=0` does not restore color overrides; `rep=0` does not restore representation style. Specify a keyword-only `settings` opt-out for the additional visual settings without shifting positional arguments. |
| Lifecycle | Store/update/rename/delete/copy/order and session load keep style data attached to the right scene. Reuse existing atom unique IDs; deleted atoms/objects are skipped with no resurrection and no misapplication to reused indices. |

Prefer an additive extension of `MovieScene`'s own payload, since native
movie playback recalls scenes there. If compatibility requires a side entry
under `session['pymolish']` (step 28), restore it into the native scene data
on load; a panel-only Python hook misses movie playback. Unknown fields are
preserved where the session contract supports them; missing data in old
scenes retains old behavior. Older files cannot recover settings never stored.
Schema/output changes need the explicit review required by `AGENTS.md` before
implementation. Do not claim older readers support the new fields without a
round-trip check.

## Tests and files

Inventory every preset setting write and scene caller first. Main files:
`MovieScene.h/.cpp`, `viewing.py`, bindings in `layer4/Cmd.cpp` as needed,
session tasks, `preset.py` only where shared visual state needs exposing,
`testing/tests/api/viewing.py`, `scene_panel.py`, `preset.py`, `shots.py`.

The regression stores A with a nondefault cartoon, ligand dimensions and
colors, applies preset B and new color overrides, stores B, recalls A, B,
A, and compares settings plus viewport/ray images. Include initially unset
overrides, per-bond settings, a renamed/deleted object, a redefined custom
color, restricted `sele`, `color=0` and `rep=0`; PSE/PSEX reload, scene update
and rename, Undo and a movie that visits both scenes. Measure scene payload
size and recall time on a large structure before choosing storage detail.

35b changes public `cmd.scene` behavior: an `X` version, help and `ChangeLog`.
Only actual implementation measurements belong in the shipped-status note.

Skipped: storing every application setting, coordinates/topology, rebuilding
deleted contact objects, user preferences and an entire session per scene.
New/deleted objects are not restored by appearance recall; existing contact
objects still use the scene's normal enable/visibility behavior.
