# 22 — Property table

[Roadmap](../../PLAN.md) · Request 2026-11-20 · Planned, not built. Questions
20 and 21 answered the same day: a window of its own over the viewport,
stuck to the Objects panel; Excel read with the standard library.
Replaces the metadata table of [step 3](03-modern-ui.md); step 3 is closed.

**22a done 2026-11-20 in 4.27.0.** Differences from the plan below:

- The widget is a `QTreeWidget` with rows that compare by value, not a
  `QTreeView` on a model with a proxy: it is what the Objects panel uses,
  about a third of the code, and one poll of 1,000 objects with 20
  properties takes 16 ms (the limit was 20). The model is the upgrade if
  editing or 10,000 rows need it.
- No Ctrl+T: it is "bond" in the viewport. The Table button and Display >
  Panels open the window. Esc is not bound yet.
- The window is placed by its visible area: under WSLg the frame has an
  invisible margin of 25 px, which put the first version 50 px over the
  panel. Measured in the real window: opens exactly over the viewport, its
  right edge on the panel's left edge, and stays there when the main window
  is moved or made wider.
- Not exercised: a resize by the real mouse. The size is remembered from
  the window system's resize event; a script cannot send one.
- The size is not saved between sessions yet (the first size is the
  viewport's each time).

**A table with one row per object: row number, a dot that shows or hides the
object, the name, then one column per property. Cells are edited in place,
columns are added by hand or come from a CSV or Excel file. It is a window
of its own that lies over the viewport with its right edge against the
Objects panel, opened and closed by a Table button in the toolbar.**

The pictures in `plan_images/` (Maestro's project table and entry list) are
the model for the arrangement only: Row, In, Title, then properties, dark.
No icon, text or drawing of Maestro is copied.

## What exists (checked 2026-11-20 at 4.19.43)

| Thing | State |
| --- | --- |
| Object properties | In the core: `cmd.set_property(name, value, object, state)`, `get_property`, `get_property_list` ([properties.py](../../modules/pymol/properties.py), `layer1/Property.h`). Typed: boolean, int, float, color, string. |
| In the session | A property survives save and load of a `.pse`. PyMOL 3.2 loads that file and reads the property too. Tried here. |
| From SDF | The data fields of an SDF file become properties at load (`load_object_props_default` is `*`); `save x.sdf` writes them back. Tried here. |
| Gap | `split_states` loses them: the new objects have no property. |
| A table widget | None. The read-only table of 4.5.0 (`object_table.py`) was replaced by the Objects panel in 4.5.11. |
| Row source | `object_panel.snapshot(cmd)` already lists objects, groups and visibility for the Objects panel, polled every 0.5 s. |

So the table needs no data model of its own: **it is a view of the object
properties the core already keeps and saves.** What is new is the widget,
import and export, and the list of columns.

## Design

```
+------------------------------------------------------------------------+
| [Import] [Export] [+ Column] [Columns v] [Filter ............]         |
+-----+----+--------------------+---------------+----------+-------------+
| Row | In | Name               | docking score | emodel   | note        |
+-----+----+--------------------+---------------+----------+-------------+
|   1 | o  | 4KNN               |               |          | apo         |
|   2 | o  | 4KNN_minimized     |               |          |             |
|     |    | v ligprep_out (3)  |               |          |             |
|   3 | .  |   MOL004004        |        -6.847 |  -83.554 |             |
|   4 | o  |   MOL004004_2      |        -6.405 |  -66.639 | best pose   |
+-----+----+--------------------+---------------+----------+-------------+
```

| Part | Decision |
| --- | --- |
| Widget | `QTreeView` on a `QAbstractItemModel` (a tree, so group members nest as in the pictures), with a `QSortFilterProxyModel` for sorting and the filter box. New file `modules/pmg_qt/property_table.py`. The window: see "Where the table lives". |
| Row | One per molecular object, map and group, in the order of the Objects panel. Selections ("(sele)") are not rows. Row identity is the object name, never the row number: the number is only what is displayed and follows the sort. |
| Row | The first column, 1 to n over the rows shown. Not stored. |
| In | A dot, filled when the object is enabled. Click or Space toggles `enable` / `disable`, the same call as the dot of the Objects panel, so both agree at the next poll. Ctrl+click: show only this one (`disable all`, `enable name`). |
| Name | The object name. F2 or a slow second click renames in place with `set_name` ([step 23](23-rename-in-panel.md) builds the same for the Objects panel; one helper serves both). |
| Property columns | One per property name found on any object, plus the columns the user added. Shown in the order they first appeared; the header can be dragged, hidden (Columns menu) and resized. |
| Cell | Shows the property of state 1 (`state=0` first, the object-level value, then state 1). Numbers are right-aligned, sorted as numbers; an empty cell is a missing property. |
| Edit | Double click, F2 or typing on a cell opens Qt's editor. The value goes to `cmd.set_property`; the type is taken from the text: integer, float, else string ("true"/"false" stay strings unless the column is boolean already). Emptying a cell deletes the property. Several rows selected: the edit goes to all of them. |
| Add a column | "+ Column" asks for a name; the column appears empty. A property name is a column name, no second naming. |
| Delete, rename a column | Right click on the header. Rename moves the values to the new property name on every object. |
| Look | The palette of the window, so it is dark with the dark theme and light with the light one; alternating row colors from the palette (`AlternateBase`), the blue of the menus for the selected rows. No hard-coded color. |
| Selection | Selecting rows selects nothing in the viewport. Double click on the row number zooms on the object. Right click on a row: the same menu as in the Objects panel (`object_panel.context_menu`). |
| Keyboard | Arrow keys, Tab and Shift+Tab between cells, F2 edit, Space toggles In, Delete empties cells, Ctrl+C and Ctrl+V copy and paste a block as tab-separated text (pasting from a spreadsheet fills cells). |
| Refresh | Reads names and properties in the window's 0.5 s poll, only while the window is shown, one call per poll that returns everything (a list of `(name, enabled, {property: value})`). Marked `ponytail:`; the upgrade is the change notification the Objects panel also waits for. |
| Where the column list lives | Order, hidden columns and empty added columns are saved in the session under the key of [step 28](28-session-format.md) and restored with it. Column widths are window layout: `QSettings`. |

### Import

`cmd.load_table(filename, key="", object_column="")`, new, in a new
`modules/pymol/tables.py`; the Import button and File > Import Table call it.

| Step | Rule |
| --- | --- |
| Read | CSV and TSV with the `csv` module (the delimiter by `csv.Sniffer`, UTF-8 with or without a mark). Excel: see the options below. |
| Which column holds the names | The first column whose header is `name`, `title`, `object`, `id` or `entry` (any case), else the first column. `object_column=` names it. |
| Match | A row goes to the object with that name. No such object: the row is skipped and counted. |
| New columns | A header that is no property yet becomes a new column. An existing property is overwritten by a non-empty cell and kept by an empty one. |
| Report | One line: rows matched, rows skipped (first five names), columns added. |
| Undo | With [21g](21-commercial-features.md): one import is one undo step. Before 21g: none; the report says what changed. |

### Export

`cmd.save_table(filename, selection="")`: the shown columns of the shown rows
as CSV (`csv` module). The Export button; Ctrl+C for a block. `.xlsx` is not
written: every spreadsheet opens CSV.

## Where the table lives (decided 2026-11-20)

The answer to question 20: "a separate window that can be closed and
resized; placed on the visualization, covering it, and it sticks to the
Objects panel on the right side". None of the three options below; this
replaces them.

| Part | Decision |
| --- | --- |
| Kind of window | A floating `QDockWidget` named `dock_table` that cannot be docked (`setAllowedAreas(NoDockWidgetArea)`): a window of its own that stays above the main window, with a title bar, a close button and edges to resize. Being a dock widget, it is listed in Display > Panels, its Table button in the toolbar is its `toggleViewAction`, and the layout save keeps whether it was open. |
| Where it opens | Over the viewport: the same top-left corner and the same height, its right edge on the left edge of the Objects panel. With the panel closed or floating, on the right edge of the viewport. It covers the picture; the picture is back when the table is closed or made smaller. |
| Stuck to the panel | While the main window is moved or resized, or the Objects panel is made wider or narrower, the table's right edge follows the panel's left edge and its top follows the viewport. Width and height stay what the user made them, cut to the viewport's size when that is smaller. |
| Coming unstuck | Dragging the table by its title bar to another place (another screen, for instance) frees it; it then keeps its place. Display > Panels > Reset Layout sticks it back. |
| Size | Remembered in `QSettings` with the layout. One constant sets the first size (the whole viewport). |
| Keyboard | Ctrl+T opens and closes it; Esc in the table gives the focus back to the command line without closing. |
| How | An event filter on the main window and on the Objects dock (move, resize, show, hide) calls one function that places the table; about 25 lines. |

To check in the real window under WSLg (X11): a floating dock stays above
the main window and follows it without a visible lag; under Wayland a
program cannot place its own windows, so there the table opens where the
compositor puts it and "stuck" does nothing. That limit goes into the help.

## Options

**Where the table lives** (question 20, answered: none of these, see above):

| | Option | Note |
| --- | --- | --- |
| A | A dock of its own at the bottom; the Objects panel stays as it is. | Two views of the same objects: a narrow one with the action menus on the right, a wide one with the properties at the bottom, as Maestro has entry list and project table. Nothing that works is rebuilt. |
| B | The table replaces the Objects panel; A, S, H, L, C become five columns. | One list instead of two, but the panel was rebuilt twice already, and a wide table on the right takes the viewport's room. |
| C | A tab inside the Objects dock. | Too narrow for more than one property column. |

**Excel** (question 21, answered 2026-11-20: A):

| | Option | Note |
| --- | --- | --- |
| A | **Read `.xlsx` with the standard library. Recommended.** | An `.xlsx` is a zip of XML: `zipfile` and `xml.etree` read the first sheet (shared strings, numbers, inline strings) in about 40 lines. Limits, written in the help: first sheet only, a formula gives its stored result, a date arrives as Excel's day number, `.xls` (the old binary format) is not read. |
| B | `openpyxl` as an optional dependency, extra `table`. | Reads dates and every sheet. One more package in the bundles (about 4 MB with `et-xmlfile`). |
| C | CSV only. | Smallest. The user saves as CSV in Excel first. |

## Other options worth having (the request: "think about other needed options")

In the order I would build them; each is small and separate.

| Option | What | In the first version |
| --- | --- | --- |
| Sort by a column | Click on the header; numbers as numbers. | Yes (the proxy model does it) |
| Filter box | Rows whose name or any cell contains the text. | Yes |
| Computed columns | Columns menu > Add: atoms, residues, chains, states, molecular weight, formal charge, sequence length. Filled once from the core when added, as ordinary properties (so they are saved and exported). "Refresh" recomputes. | Yes, the first four; weight and charge with them |
| SDF fields | Already properties, so already columns. Fix `split_states` so the new objects keep them, and offer "one object per molecule" when a multi-state SDF is loaded with the table open. | Yes (the fix is in the core, with a test) |
| Color rows by a column | A gradient in the cell background for a numeric column, from the palette in use. | Later |
| Select by value | Right click on a cell: "enable only rows with this value", "disable rows above/below". | Later |
| Step through rows | Up and Down with "follow" checked shows only the current row's object: the way docking poses are looked at one by one. | Yes: it is the main use of the In column |
| Stars | A 0 to 3 rating column, as in the picture. It is an integer property named `stars` drawn as stars. | Later |
| 2D structure column | The ligand drawn in the row, from [step 24](24-ligand-2d.md)'s rdkit drawing. | Later, after 24 |
| Plot two columns | A scatter plot. Needs a plotting library or own painting. | Skipped |

## Slices

| Slice | What | Files | Check |
| --- | --- | --- | --- |
| 22a | The window with Row, In, Name and the properties that exist, read-only, sorted and filtered; the Table button. `split_states` keeps properties. | `property_table.py` (new), `pymol_qt_gui.py`, `action_toolbar.py`, `icons.py` + `table-2.svg`, the core's `split_states` | `testing/tests/api/property_table.py`: rows and nesting, In toggles, identity after rename and delete under a sort, an SDF's fields as columns; a test for `split_states` |
| 22b | Editing cells, adding, renaming and deleting columns, copy and paste. | `property_table.py` | Type rules, multi-row edit, delete; paste of a 2 x 3 block |
| 22c | `load_table`, `save_table`, CSV; the Excel option that was chosen. | `tables.py` (new), `api.py`, `keywords.py`, `_gui.py` | Round trip CSV; match, skip and overwrite rules; a hand-made `.xlsx` in `testing/data` |
| 22d | Column list in the session; computed columns; follow mode. | `property_table.py`, the session task of step 28 | A session keeps order and hidden columns; counts against `count_atoms` |
| 22e | A picked atom selects its row (carried over from step 3). | `property_table.py`, `object_panel.py` | Simulated pick in the real window |

Real window at 150 % for each slice: 1,000 objects with 20 properties must
scroll and sort without a pause (measure the poll; the limit is 20 ms).

## Carried over from step 3

Step 3 closes with this plan. Its open rows go here:

| Row of step 3 | Where it goes |
| --- | --- |
| A picked atom selects its row | 22e |
| Rows moved by dragging | [Step 23](23-rename-in-panel.md), 23b |
| Sequence viewer text and scene buttons still drawn by the core | Answered 2026-11-20: the scene buttons of the core are deleted ([17f](17-legacy-ui.md)); the sequence viewer stays as it is. |
| Spacing of the remaining dialogs | Dropped as a roadmap row: fixed when a dialog is touched or reported. |

## Skipped

- A row per state, per chain or per atom. One row per object, as asked.
- Formulas in cells, a calculator, find and replace, charts.
- Writing `.xlsx`.
- A second store beside the object properties.
- Properties of maps and CGOs beyond what the core already accepts.
