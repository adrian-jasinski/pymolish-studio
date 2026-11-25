# 37 — GUI follow-ups requested 2026-11-24

[Roadmap](../../PLAN.md) · Request 2026-11-24 · choices 91 to 97 answered
2026-11-25 · **built 2026-11-25 in 4.68.1 to 4.75.0, finished.**

**Built 2026-11-25.** One commit and one version per slice:

| Slice | Version | What shipped | Measured or tried | Left out |
| --- | --- | --- | --- | --- |
| 37a | 4.68.1 | A startup plugin named "pymolish" is not loaded; a line in the log says so. | Reproduced in the real window with `~/.pymol/startup` in the startup path: the reported `TypeError` before, `fetch_by_uniprot P01542, 3, async_=1` loaded 3 entries after. On this machine `~/.pymolpluginsrc.py` sets an empty startup path, so the plugin was not loaded here and the command worked without the change (27 of 27 entries). | The test of `fetching.py` with mocked network that the plan named: the fault was not in the fetch. Where the user met the error is not known. |
| 37b | 4.69.0 | Delete on the current row of the Objects list; a group asks and goes with all its members. No button (choice 91). | Real window: a click on a row and Delete, a second press (nothing), the question of a group (default Cancel) answered with Yes, Delete inside the rename editor (edits the text). | Deleting several selected rows at once; undo (21g). A first build with a trash icon on every row was made before the decision was read, and taken out. |
| 23b | 4.70.0 | Rows moved by a drag with the right button, or Alt+arrows; a line or a frame shows the place. | Real window, real right-button input through the X server: a drag above another row, a drag onto a group, a click (the menu opened on release, not on press). A session round trip in the test. | Esc to cancel a drag (release where no mark is shown), scrolling while dragging past the edge, Windows and macOS (there the system asks for the menu on release: handled in code, not tried). |
| 37c | 4.71.0 | 30 colors in each of the ten named palettes; a tooltip with the number. | Smallest RGB distance between neighbors in a cycle: 0.23 (pastel), the test asks for more than 0.2. A picture of the menu (ten swatches a row) and of 30 objects in "dracula". | No check for color-vision deficiencies; the added colors are computed, not from the palettes' sources. |
| 37d | 4.72.0 | Colors dragged to their place in the palette dialog. | A real left-button drag on the dialog alone: the first of five colors dropped below the fourth. | Nothing. |
| 37e | 4.73.0 | The mouse mode button: icon and short name, as wide as that; the buttons stand at the left. | Real window on WSLg: 83 px for "Viewing", 78 px for "Editing" (139 px for "3-Button Viewing" before, more in a wider panel), the same at a UI scale of 100, 150 and 200 %; narrowest panel 234 px before and after. | A stylesheet with less padding inside the button: it would draw this button unlike its neighbors. |
| 37f | 4.74.0 | Mode, Labels and Gaps lists and the alignment button over the sequence. | Real window: "Residue Names" picked in the list changed the rows and the mark in Display > Sequence Mode; the button opened the alignment window. | Mnemonics for the lists (Tab reaches them). |
| 37g | 4.75.0 | A−, A+ and Reset at the right of the tabs; a size per tab, kept. | Real window with a settings folder of its own: 12, 11 and 8 points after the clicks, the same at the second start, where a tab starts with 9. | Keys for the three buttons (Tab reaches them); the label "PyMOL>" and the lists of the Sequence tab keep their size. |

The suite after the last slice: 1120 passed, 251 skipped. One test,
`test_mouse_mode_button_is_as_wide_as_its_content`, runs in a real window
only and passed there. The specification below is the plan as it was.

---

Open at 4.68.0. This section specifies the new work; earlier deliveries in
steps [11](11-color-palettes.md),
[20](20-toolbar-look.md),
[32](32-footer-icons-movie-button.md) and
[33](33-sequence-window.md) remain shipped. The Objects drag
work is still **23b**, not a second implementation under a new number.
Choices 91–97 were decided by the user on 2026-11-25; the specifications
below include those answers. No feature shipped in this decision update.

**37a — UniProt fetch.** Reported from File > Get by UniProt:

```text
fetch_by_uniprot P01542, async_=1
TypeError: fetch_by_uniprot() got an unexpected keyword argument 'async_'
```

Source inspection: `file_fetch_uniprot` in `modules/pmg_qt/file_dialogs.py`
passes that argument, and the native function in `modules/pymol/fetching.py`
already accepts it and uses `_self.async_`. First inspect the function
registered in `cmd.keyword`, its module/signature and the installed version;
compare normal startup with plugins disabled. A legacy startup override or
an older installed build is a hypothesis, not a confirmed cause. Fix the
dispatch/registration mismatch at its source; do not remove background
execution to hide the error. Check the adjacent predicted-structure action
for the same cause. Leave a GUI-to-command regression in
`testing/tests/api/test_file_dialogs.py` and the relevant dispatch check in
`testing/tests/api/fetching.py`, with mocked network results. Try P01542 in
the real window: loading or a useful no-results/network error is acceptable;
the keyword error and a frozen GUI are not.

**37b — Delete from Objects.** Bind the keyboard Delete (Del) key to the
selected object/group while the Objects list has focus; add no new button
and keep the existing menu action (91). An object is deleted immediately;
a group always asks first. Confirm deletion of the group and all its
members, including nested groups; name the group and show the full scope
before applying (92). No delete action on “all”; deletion must not also
toggle visibility or zoom. Use the native deletion/group operations in
`modules/pmg_qt/object_panel.py`, matching the confirmed scope. Tests in
`testing/tests/api/object_panel.py`: Del on the selected object, empty/nested
group, Cancel, unrelated objects retained, and Delete in a text editor
does not delete an object. General undo stays in 21g.

**23b — Object order by dragging.** Hold the right mouse button on a row,
drag and release to drop (93, recommended option accepted). A right click
without dragging still opens the context menu; keep left click as
visibility and F2 as rename. Show the drop position; between rows calls
`cmd.order`, onto a group uses `cmd.group`
as already planned, and a root drop can move a member out of its group.
Reject moving “all”, dropping a group into itself/its descendants, and
invalid targets. Keep refresh from interrupting a drag. Use Qt's existing
tree and provide keyboard move actions through the same operation. Check
order and membership in `testing/tests/api/object_panel.py`, including
filtered lists, nested groups, refresh and a PSE round trip; then exercise
the chosen gesture in the real window.

**37c — Palette length and preview.** Requested sizes: 30 usable colors
per named built-in palette, only the first 10 shown in the GUI preview.
Chosen scope (94): all named built-ins in `modules/pymol/palettes.py`; keep
existing hex values and their order, append distinct colors in each palette's style.
Leave legacy “PyMOL default” and saved user palettes as they are.
The menu already slices `colors[:10]` in
`modules/pmg_qt/action_toolbar.py`; retain and test it. Full object and chain
color cycles must use all 30, not just the preview. Review contrast and
neighbor separation with the existing palette checks, including the wrap
from last to first; do not claim 30 colors are all distinguishable with
color-vision deficiencies. The editor must still expose every color.
Extend `testing/tests/api/palettes.py` to check lengths, retained prefixes,
cycle and session behavior; check previews in
`testing/tests/api/action_toolbar.py`.

**37d — Drag colors in New/Edit palette.** Enable Qt internal list moves
in `modules/pmg_qt/palette_dialog.py`. Moving a swatch changes its position,
not its value; retain Add, Change, Remove and keyboard Up/Down. Saving uses
the visible order; Cancel leaves the stored palette untouched. Check first,
middle and last moves, reopening and QSettings persistence in the existing
palette/toolbar tests. No external drag source or new palette format needed.

**37e — Compact mouse mode.** The current button in
`modules/pmg_qt/pymol_qt_gui.py` expands into spare footer width and only
shortens its label when squeezed. Use the mouse icon plus a compact mode
name such as “Viewing”/“Editing”, with the full name in the tooltip and the
existing menu (95). Size the button to its content and reduce excess
horizontal padding as requested; shortening the text alone does not remove
the current spare space. Measure the before/after width in the real window,
including a narrow Objects panel and UI scaling;
do not choose an unmeasured fixed pixel width. This supersedes choice 84's
expanding button, not the menu's available mouse modes.

**37f — Sequence tab options and alignment.** Reuse the settings already
listed by Display > Sequence Mode in `modules/pymol/_gui.py`:

- Mode (`seq_view_format`): Residue Codes, Residue Names, Chain Identifiers,
  Atom Names, States.
- Labels (`seq_view_label_mode`): All Residue Numbers, Top Sequence Only,
  Object Names Only, No Labels.
- Gaps (`seq_view_gap_mode`): No Gaps, All Gaps, Single Gap.
- “Multiple sequence alignment…” opens the existing `sequence_panel.open`
  viewer, with loaded chains/FASTA and its existing local MAFFT action.

Use a row of Mode/Labels/Gaps dropdowns and an alignment button inside the
Sequence tab (97, option B). Keep Command → Sequence → Chat
order. Wire existing settings/actions in `pymol_qt_gui.py` and
`sequence_tab.py`: Display, commands, the tab and viewport stay synchronized.
Test every option, command-driven updates, picking after format changes and
opening the same alignment viewer in `testing/tests/api/sequence_tab.py` /
`sequence_window.py`. MAFFT remains separately installed; reuse its current
missing-executable message. No second viewer or alignment engine.

**37g — Font size beside the tabs.** Use compact A− / A+ and Reset
controls on the right of `command_tabs`, acting on the active tab's content
and remembering a separate size per tab in QSettings (96, recommended
option accepted). Tab-title fonts follow the application theme. Command
covers log and entry; Chat covers conversation and prompt; Sequence keeps its
monospace font and recalculates scroll ranges and mouse hit positions.
Use `pymol_qt_gui.py`, `sequence_tab.py` and `chat_panel.py`; preserve each
tab's font family. Changes are live and independent of overall UI scale.
Keyboard access and tooltips are required. Check changing tabs, reset,
restart, long text and sequence selection at changed sizes; no provider
request is needed to test Chat fonts.

Each shipped slice follows the normal version/ChangeLog and runnable-check
rules; this documentation update has neither a version nor a ChangeLog entry.
Skipped here: implementation, live fetch/GUI trials, new dependencies,
bulk deletion UI, palette import/export and a new alignment backend.
