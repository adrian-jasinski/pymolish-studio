# 3 — Modern workspace and metadata panel

[Roadmap](../../PLAN.md) · Draft; no UI prototype implemented

**Evolve the existing main window into a clear molecular workspace.** Deliver
movable, resizable panels and a useful metadata table before replacing every
internal control. Preserve command-line workflows and existing `.ui` dialogs.

## Status 2026-11-08

Slices 1 to 3 shipped in 4.5.0: `modules/pmg_qt/object_table.py` (model + dock, headless test in `testing/tests/api/object_table.py`), named docks (`dock_command`, `dock_objects`, `dock_builder`), `QSettings` layout save/restore with off-screen recovery, Display > Panels with Reset Layout. Viewport-to-table synchronization, object controls migration (slice 4), menu cleanup (6) is open. Slice 5 started in 4.5.2: `modules/pmg_qt/theme.py` (Fusion + dark palette, default on, Display > Dark Theme, persisted); spacing/labels not touched yet. Slice 5 continued in 4.5.7: Display > UI Scale and the dark-theme color audit, see [Display scale, typography and color](#display-scale-typography-and-color).

## Reference products and current constraints

Use commercial PyMOL for familiar molecular workflows and Maestro for its
relationship between a workspace and a project table. Maestro's published changes
include table configuration and selecting the corresponding table entry from a
picked workspace atom. These are useful interaction references, not a requirement
to reproduce its complete suite or proprietary assets. [PyMOL product](https://www.pymol.org/),
[Maestro table improvements](https://www.schrodinger.com/life-science/download/release-notes/release-2025-2/),
[workspace-to-table selection](https://www.schrodinger.com/life-science/download/release-notes/release-2025-4/)

The [current main window](../../modules/pmg_qt/pymol_qt_gui.py) already has docks,
menus and command entry. The internal object controls and sequence viewer also
involve [Executive](../../layer3/Executive.cpp) and
[Ortho](../../layer1/Ortho.cpp). They are not standalone Qt widgets that can be
reparented into docks. Keep the sequence display initially; replace it only as a
separately scoped, tested feature.

## Proposed workspace

| Region | Initial content | Behavior |
| --- | --- | --- |
| Center | Existing OpenGL viewport | Stable parent/context; largest useful area |
| Left, later increment | Objects, groups and selections | Visibility controls and existing actions through named menus |
| Bottom | New object metadata table | Sort/filter, row selection and object navigation |
| Bottom, tabbed or separate | Existing command entry and log | History/completion retained; easy keyboard focus |
| Right, when opened | Existing properties, builder or tool panels | Dock, float, resize, close and reopen |
| Within viewport initially | Existing sequence display | Preserve current selection behavior and settings |

Use `QDockWidget` and `QMainWindow` capabilities. “Unpinned” initially means
floating/detached; IDE-style edge auto-hide is a separate, deferred requirement.
Provide View → Panels, Reset Layout, and keyboard-accessible move/float actions.
Qt supports movable, floatable and closable docks directly.
[QDockWidget](https://doc.qt.io/qt-6/qdockwidget.html)

## Implementation slices

1. **Docks and persistence:** improve the existing window, name docks stably,
   save geometry/state in `QSettings`, and restore after widgets exist. Handle a
   missing monitor or invalid layout by returning tools to a visible location.
   Keep Reset Layout reachable with all tool panels closed. Store UI layout in
   settings, not by changing PSE output. [QMainWindow persistence](https://doc.qt.io/qt-6/qmainwindow.html)
2. **Object table MVP:** use `QTableView`, `QAbstractTableModel` and a
   `QSortFilterProxyModel`. Start read-only with one row per object, not per atom.
   Provide object name, type, enabled state, atom count where applicable, and
   state count. Add existing object properties only when the current API exposes
   them; show unavailable values explicitly instead of inventing metadata.
3. **Selection and navigation:** select the corresponding object from a row and
   provide Zoom/Orient actions. Distinguish a highlighted row, an atom selection,
   and object visibility; selecting a row must not silently hide other objects.
   Add viewport-to-table synchronization after the basic model is stable.
4. **Object controls:** migrate the most-used internal object actions into Qt
   only after parity for groups, names, visibility and command-driven updates.
   Keep legacy controls until their replacement passes those checks, then remove
   the replaced path deliberately. Avoid permanent duplicate object panels.
5. **Visual consistency:** standardize spacing, typography and action labels;
   follow the system palette with minimal QSS where needed. Reuse available icons
   and Qt standard icons first. Keep text labels/tooltips for ambiguous actions.
6. **Menus and discovery:** simplify actual common tasks while retaining access
   to advanced commands. Consider a small action search only after menu cleanup
   shows a discovery problem; reuse registered `QAction`s rather than treating
   every `cmd` keyword as an executable UI action with no arguments.

## Display scale, typography and color

Detail for slice 5. Problem reported 2026-11-12 on a 2560x1600 laptop panel
under WSLg: every letter in menus, panels and plugins is too small, and the
Lighting Settings plugin has blue and red text that disappears on the dark theme.

**Cause, measured.** Qt 6 follows the scale the OS reports. WSLg (and bare X11)
report none: the panel arrives as 96 dpi, device pixel ratio 1, default font
"Sans Serif 9pt" = 12 px. Windows, macOS and Wayland/GNOME/KDE desktops report
a real scale, so they were already correct. The physical size WSLg reports is
made up (650 mm for a laptop panel), so the size cannot be detected.

| Item | Decision | State |
| --- | --- | --- |
| Text, widgets, icons, spacing | One knob: Display > UI Scale (100 to 300 %), saved in `QSettings` `ui/scale`, handed to Qt as `QT_SCALE_FACTOR` before the application object exists. It multiplies the OS scale. An exported `QT_SCALE_FACTOR` wins. Applies on next start. | Done 4.5.7 |
| Viewport menus, object panel, labels | Drawn by the C++ core with the integer `display_scale_factor`. Now rounded from the window scale, not truncated: 150 % gives 2, was 1. | Done 4.5.7 |
| Text colors | No hard-coded foreground color in Qt code, forms or bundled plugins: bold or the palette instead. Text on a hard-coded light background sets its own dark color. Links use the palette link color. | Done 4.5.7: Lighting Settings, APBS, PNG dialog, Fetch, Plugin Manager, script editor syntax colors |
| First start on an unscaled high-resolution screen | Offer a scale once when the OS reports scale 1 and the screen is 2560 px wide or more. Offer, do not guess: a 27" monitor at that width is fine at 100 %. | Open |
| 125 % in the viewport | `display_scale_factor` is an integer, so 125 % still draws viewport text at 1x. Needs a fractional factor in `layer1` text and Ortho layout. | Open, only if reported |
| Live rescale without restart | Qt reads the factor once. Skip unless restarts prove painful. | Skipped |
| Separate font-size setting | A second knob next to UI Scale. Skip unless the scale alone is not enough. | Skipped |
| Fixed point sizes in rich text | `help_shortcut.ui` (13 pt) and `pluginmanager.ui` (9 pt) carry a designer font in their HTML; they scale with UI Scale but ignore the app font. Strip when those forms are next edited. | Open |
| Spacing and labels | Hand-built dialogs with zero margins (Lighting Settings fixed); remaining dialogs audited one at a time. | Open |

Rule for plugins (goes into the step 4 plugin contract): do not set text colors
or pixel font sizes; use the palette, `<b>`, and layouts with default spacing.

Checks: `testing/tests/api/theme.py` (saved scale reaches Qt, exported value
wins, syntax colors readable on dark). Real GUI checked on WSLg at 100 % and
150 %: window scale 1.5, `display_scale_factor` 2.

## Table behavior and performance

- Use the proxy model's row mapping when sorted/filtered. Do not use a displayed
  row number as object identity. Refresh identity mapping after rename, deletion,
  reinitialize or session replacement; discard stale references.
- Batch metadata queries and keep a snapshot for display. `data()` should not
  query the molecular engine or copy coordinates for every cell paint.
- Start with Refresh and refresh after known actions in this window. Command
  scripts/plugins can also mutate the scene: mark the initial limitation clearly
  and add an existing notification hook when a real need justifies it. Avoid
  polling every atom or rebuilding the table on each frame.
- Prevent selection feedback loops. If a rename or delete invalidates a row during
  synchronization, refresh or clear it rather than selecting an unrelated object.
- Keep Qt model updates on the GUI thread. A worker may prepare safe detached
  results and queue them back; model APIs are not thread-safe.
  [Qt model threading](https://doc.qt.io/qt-6/qabstractitemmodel.html#thread-safety)
- Add residue/atom rows later through bounded queries or lazy loading. A million
  Python row dictionaries and widgets are not an acceptable default.

An initial manual-refresh implementation should carry a `ponytail:` comment naming
its ceiling (external mutations need Refresh) and upgrade path (existing change
notifications). Do not introduce a general event bus just for this table.

## Additional ideas, ordered by usefulness

- **Copy selected rows:** tab-separated clipboard output for quick reporting;
  add CSV export via the stdlib only when a workflow needs a saved table.
- **Column chooser and remembered widths:** useful once real metadata creates
  more columns than fit, without a new preferences dialog.
- **Selection inspector:** summarize the active object/selection before adding
  editable atom properties or a new molecular data model.
- **Source provenance:** show file source and load time only when recorded by a
  defined load path. Existing sessions may lack them. Decide persistence
  separately; do not silently alter PSE or invent historical values.
- **Saved workspace presets:** defer until testing demonstrates a need beyond
  the last layout plus Reset Layout.

## Acceptance checks and scope

Use a real GUI test build to load multiple structures, float/resize/tab/close and
reopen panels, restart, restore the layout, and recover after monitor changes.
Repeat key tasks with keyboard only and at multiple display scales on supported
OSes. Keep the GL viewport and its context stable while moving tool panels.

Leave runnable tests for table sorting/filtering and identity after delete/rename,
plus layout recovery where practical. Verify load/save, PNG, selection, command
history/completion and plugin menus. Measure table refresh and rotation with the
panel visible/hidden using step 1's baseline.

No second complete main-window implementation, custom-painted docking system,
external icon pack, editable atom grid, or sequence-view rewrite is required for
the first release. Add them only for a demonstrated unmet requirement.
