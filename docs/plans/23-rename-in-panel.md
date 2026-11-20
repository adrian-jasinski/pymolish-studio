# 23 — Rename in the Objects panel

[Roadmap](../../PLAN.md) · Request 2026-11-20 · Planned, not built.

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

**The old wizard** (it is a removal, so it is a choice):

| | Option | Note |
| --- | --- | --- |
| A | **Keep `renaming.py` as the fallback without a window. Recommended.** | 41 lines; `pymolish -x` and programs that embed the viewport keep a way to rename from a menu. |
| B | Delete it. | Without the window, renaming is `set_name` on the command line. The wizard test and the row "rename" of the viewport menus without a window go too. |

## Slices

| Slice | What | Files | Check |
| --- | --- | --- | --- |
| 23a | Rename in place, the hook, the guard in the poll. | `object_panel.py`, `scene_panel.py` (takes the hook for scenes), `menu.py` (eight rows), `pymol_qt_gui.py` | `testing/tests/api/object_panel.py`: F2 opens the editor; Enter renames; Esc and an existing name do not; a refresh during editing keeps the editor; "all" is not editable. Real window: right click > rename, type, paste. |
| 23b | Rows moved by dragging: reorder (`cmd.order`) and drop on a group (`cmd.group`). Carried over from step 3; any time. | `object_panel.py` | Drop through the same function a test calls |

## Skipped

- Renaming several rows at once (a pattern, a prefix): `set_name` in a loop
  on the command line does it.
- An undo entry for a rename before [21g](21-commercial-features.md).
