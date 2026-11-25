# 23 — Rename in the Objects panel

[Roadmap](../../PLAN.md) · Request 2026-11-20 · **23a done 2026-11-20 in
4.24.0.** 23b (rows moved by dragging) is open, order 3 in the roadmap.

**Decision update 2026-11-25:** choice 93 accepts the recommended gesture:
hold the right mouse button on a row, drag and release to drop; a right
click without dragging still opens the context menu. Left click still
toggles visibility; F2 still renames. The drop-position indicator, keyboard
move actions and checks for order/group membership, invalid targets,
refresh and session reload are specified in [the roadmap's 23b section](../../PLAN.md#step-37--gui-follow-ups-requested-2026-11-24).
Planning only; no feature shipped or GUI measurement made in this update.

Built as planned, with two differences. A taken name gives a line in the log
and no rename, but the editor does not stay open: Qt has closed it by then,
and opening it again would lose what was typed. The hook is for objects and
selections only: the one row that renames a scene belongs to the scene
buttons of the core, which [17f](17-legacy-ui.md) deletes. Tried in the
real window: F2, typing, Enter, and the "rename" row of the menu.

**A name is changed where it is written: F2 or "rename" on a row of the
Objects panel opens a text field on that row. The green line in the viewport
is no longer the way to rename.**

## What exists

| Thing | State |
| --- | --- |
| Rename today | The row "rename" of the A menu and of the right-click menu runs `cmd.wizard("renaming", name)`: seven rows in [menu.py](../../modules/pymol/menu.py) for objects and selections, one for scenes. |
| The wizard | [wizard/renaming.py](../../modules/pymol/wizard/renaming.py), 41 lines. It takes the keys of the viewport and draws "Renaming 3iis to: 3iis_" there, with a Cancel button in the wizard box of the panel (`plan_images/renaming.png`). The keyboard focus must be in the viewport; no cursor, no selection, no paste. |
| The same done right | The Scenes panel since 4.13.4: the item is editable, F2 calls `editItem`, `itemChanged` runs the rename ([scene_panel.py](../../modules/pmg_qt/scene_panel.py) lines 82 to 107). |
| The panel | `ObjectPanel` in [object_panel.py](../../modules/pmg_qt/object_panel.py), a `QTreeWidget`; a click toggles the object, a double click zooms. |

## Design

| Part | Decision |
| --- | --- |
| Start | F2 on the current row; "rename" in the right-click menu and in the A menu. Not a double click (it zooms) and not a slow second click (a click toggles visibility). |
| Editor | Qt's own line editor on the row (`ItemIsEditable`, `tree.editItem(item, 0)`), with the old name selected. Enter applies, Esc cancels, clicking elsewhere applies as Qt does. |
| Apply | `cmd.set_name(old, new)`. Spaces become `_` as the wizard did. An empty name, the same name, or a name that exists: no rename; for a name that exists the status line says so and the editor stays open. |
| The row "all" | Not editable. Selections are: "(sele)" is renamed as `sele`. Groups too. |
| Poll | The 0.5 s refresh must not rebuild the tree while an editor is open (the Scenes panel has the same guard, line 62). |
| The menu rows | They call one new function instead of the wizard: `menu.rename(name, mode)`. With the window it puts the row of the Objects panel (or of the Scenes panel for `mode="scene"`) into edit; the window sets the hook, as it sets `pymol.menu.popup`. Without a window (`pymolish -x`, an embedded viewport) it starts the wizard as today. |
| The table of step 22 | Its Name column uses the same validation function. |

## Options

**The old wizard** (question 22, answered 2026-11-20: A, it is kept):

| | Option | Note |
| --- | --- | --- |
| A | **Keep `renaming.py` as the fallback without a window. Recommended.** | 41 lines; `pymolish -x` and programs that embed the viewport keep a way to rename from a menu. |
| B | Delete it. | Without the window, renaming is `set_name` on the command line. The wizard test and the row "rename" of the viewport menus without a window go too. |

## Slices

| Slice | What | Files | Check |
| --- | --- | --- | --- |
| 23a | Rename in place, the hook, the guard in the poll. | `object_panel.py`, `scene_panel.py` (takes the hook for scenes), `menu.py` (eight rows), `pymol_qt_gui.py` | `testing/tests/api/object_panel.py`: F2 opens the editor; Enter renames; Esc and an existing name do not; a refresh during editing keeps the editor; "all" is not editable. Real window: right click > rename, type, paste. |
| 23b | Rows moved by holding the right mouse button, dragging and releasing: reorder (`cmd.order`), drop on a group (`cmd.group`), or drop at the root to ungroup. Right click without dragging keeps the context menu. Carried over from step 3; open, order 3 (choice 93). | `object_panel.py` | Real mouse drop and keyboard move actions share the operation tested in `testing/tests/api/object_panel.py`; order and membership survive refresh and a PSE round trip. |

## Skipped

- Renaming several rows at once (a pattern, a prefix): `set_name` in a loop
  on the command line does it.
- An undo entry for a rename before [21g](21-commercial-features.md).
