# 30 — Eight repairs after a first look at 4.35.0

[Roadmap](../../PLAN.md) · Request 2026-11-20 · **Planned 2026-11-20 at
4.35.0. Six slices, 30a to 30f, each one commit and one version. All six
done the same day, 4.36.0 to 4.40.0: see [Status](#status) at the end.**

**The user tried 4.35.0 and came back with eight points: the look of the 2D
ligand picture, the property table, two messages in the console, blurred
icons, the preset menu and what presets may color, a row that removes
crystallization additives, and whether Undo works after a preset. Each was
reproduced first; what was found is in the table.**

## What was found

| Point | Found at 4.35.0 |
| --- | --- |
| 2D picture | Residues are ellipses of 58 x 40 px with 11 px text, the same pastel fills on a light and on a dark window, a grey outline. The legend is one row of 11 px text; its first row is 519 px long in a picture 514 px wide (1OKY, staurosporine), so its end is cut. |
| `qt.svg: Invalid path data` | Comes from the 2D picture, not from an icon: all 56 icon files load without a message. rdkit writes a space in a text as a path without data, and Qt complains about each. The legend has three names with a space, so three lines per drawing, and the panel draws again at every resize. |
| `QHighDpiScaling::setFactor` | From the live UI scale (27b): Qt prints it whenever a window object exists, and they all do; only their native windows are gone. The change itself works. |
| Blurred icons | After a live change of the UI scale. An icon is a picture made for the scale of that moment; afterwards Qt stretches the old one. Menus that are filled when they open are sharp; the toolbar and the buttons of the States panel are not. |
| Table: alignment | Numbers are right-aligned, text left. |
| Table: icon | `table-2` of Lucide: a frame with one line across and one down. It reads as a window with panes. |
| `ExecutiveGetProperty: objname='3iis_types' not found` | The table asks every row for its properties, also a group (A > split > by type makes one). Only molecules have properties; the core prints an error for anything else, twice a second while the table is open. Typing into such a cell raises an error. |
| Presets menu | 33 rows in one list: 16 presets, two switches, 5 themes, 3 floor rows, 10 lights. |
| Presets and colors | Four rows give the surface a color of their own: glass and illustration (white), protein-protein interaction (orange, white where chains touch), antibody and antigen (sand, the epitope orange). "default" colors the carbons, and with them the cartoon. Glass colors every non-carbon atom by element under its surface; ligand sites does so for the pocket. |
| Clean | Rows for waters, ions, both, ligands. Nothing for what is in the crystal only because of how it was grown. |
| Undo after a preset | Does nothing. Tried on 3IIS: "pretty" changed lines, sticks, cartoon and spheres from 286, 359, 1249, 16 atoms to 0, 364, 1624, 0; `undo` returned nothing and changed nothing. Undo restores coordinates only; undo of everything else is 21g, now order 21 of the roadmap (2026-11-23). |

## Slices

Each slice: code, its test, a look in the real window, `ChangeLog`, version.

### 30a — the 2D picture (4.36.0)

`modules/pymol/ligand2d.py`, `modules/pmg_qt/ligand_panel.py`.

- A residue is a circle, 52 px across, with the name and the number in
  14 px text.
- The fill runs from a lighter to a deeper tone of the kind's color, top to
  bottom, and the outline is a darker tone of the same color in place of
  grey. Two sets of tones: on a light window light fills with dark text, on
  a dark window deep fills with white text and a bright outline. The ring
  of a selected residue is the blue of the window's links, which is lighter
  on dark.
- The legend has 14 px text and larger marks, and wraps into as many rows
  as the picture's width needs; nothing is cut.
- The paths without data are taken out of the SVG: no message from Qt.
- **How:** rdkit cannot draw a gradient. It draws the circles in one flat
  color each; in the SVG text those fills are then replaced by a reference
  to a gradient. A PNG written by `ligand_2d` comes from rdkit directly and
  keeps the flat fill.
- **Test:** `testing/tests/api/ligand2d.py`: circles, one gradient per
  kind, both sets of tones, no path without data, the legend inside the
  picture. `ligand_panel.py`: clicks still land.

### 30b — the property table (4.37.0)

`modules/pmg_qt/property_table.py`, `modules/pmg_qt/icons.py`, one icon file.

- Every value is left-aligned. The row number stays right-aligned.
- A new icon. Options (question 36): **`sheet`, a grid of three rows and
  three columns under a header, recommended**; `table`, two columns;
  `table-properties`, a narrow column on the right.
- Only molecules are asked for properties, and only their cells are
  written: no message for a group, a map or a measurement.
- **Test:** `property_table.py`: alignment; a group and a measurement in
  the table with the core's output captured.

### 30c — the live UI scale: no warning, sharp icons (4.37.1)

`modules/pmg_qt/theme.py`.

- Qt's warning is not printed: a message handler is set for the one call.
- After the change every widget gets the event it gets when the theme
  changes. What draws tinted icons already listens to it and draws them
  again, now for the new scale: the toolbar, the States panel, the 2D
  picture.
- **Test:** `theme.py`: the live change prints nothing and sends the event.
  In the real window: the toolbar before and after 150 % to 200 %.

### 30d — the preset menu, and what a preset may color (4.38.0)

`modules/pymol/menu.py`, `modules/pymol/preset.py`.

- **Menu:** the 16 presets stay as they are. Under them the two switches
  (cartoon transparency, solvent), then three submenus: **theme** (5),
  **light** (10), **floor** (3). 21 rows in place of 33. No preset is taken
  out: that is question 39.
- **Rule:** no row but a theme changes the color of a cartoon or of a
  surface.
  - "default" colors the non-carbon atoms by element and leaves the
    carbons.
  - glass and illustration: the surface has the colors of its atoms. Glass
    colors by element only the ligands it draws as sticks.
  - ligand sites: the pocket's surface has the color of the carbons under
    it; the sticks and lines keep their element colors.
  - protein-protein interaction: the surface has the colors of its atoms,
    and only the residues within 4.5 A of another chain get one color.
    Options (question 37): **orange, recommended**: it shows on every
    theme and on the default chain colors; white, as before, is lost on the
    pale themes.
  - antibody and antigen: the same, only the epitope is orange.
- **Test:** `preset.py`: every row of the menu and of its submenus but the
  themes is run on a structure colored yellow; cartoon atoms and surface
  colors are checked after each. `menu.py`, `stage.py`: the new list.

### 30e — clean: remove crystallization additives (4.39.0)

`modules/pymol/menu.py`, `modules/pymol/grouping.py`.

- A fifth "remove" row in A > clean: "remove crystallization additives". It
  removes residues by name from one list and says how many atoms went.
- **The list**, by group. Sources: the BioLiP list of ligands that are
  suspected artifacts, as PLIP ships it (2014-07-10), read on 2026-11-20
  and reduced to what a crystallographer adds; the PDB codes of PEG
  fragments.

  | Group | Residue names |
  | --- | --- |
  | PEG and glycol fragments | PEG PGE PG4 PG0 PG5 PG6 1PE 2PE P6G PE3 PE4 PE5 PE8 P33 P3G P4G 12P 15P 16P 7PE 7PG XPE PEU PGF ETE EDO PGO PGR PDO 1PG AE3 AE4 TOE ME2 |
  | Cryoprotectants and solvents | GOL MPD MRD BU1 BU3 HEZ IPA EOH MOH DMS DMF ACN DIO TBU |
  | Buffers and organic salts | TRS EPE MES MPO BTB B3P CAC NHE CXS TAM BCN IMD CIT FLC ACT ACY FMT MLI MLA TLA TAR SRT MLT LMR SIN BET URE GAI |
  | Precipitant ions | SO4 PO4 NO3 SCN NH4 |
  | Reducing agents | BME DTT DTV DTD DTU |
  | Detergents and lipids of the mother liquor | BOG BNG HTG SOG LDA LMT LMU DMU UMQ SDS C8E CE9 CXE CPS OLC OLB |
  | Sugars of glycosylation, as asked | NAG NDG BMA MAN FUC |
  | NAD and NADP, as asked | NAD NAI NAP NDP |

- **A warning that belongs here:** the last two groups are not additives.
  NAG, BMA, MAN and FUC are the sugars a cell puts on a glycoprotein, and
  NAD(P) is the cofactor of most enzymes it is found in. They are on the
  list because the request names them. Options (question 38): **one row
  with all of it, as asked, recommended for now**; a row of their own for
  sugars and one for cofactors, so that "additives" can be removed without
  them.
- **Test:** `cleanup.py`: a structure with an additive, a sugar and a drug:
  the row removes the first two and keeps the drug.

### 30f — Undo and Redo for a row of the preset menu (4.40.0)

New `modules/pymol/snapshots.py`; `editing.py` (undo, redo), `menu.py`,
`commanding.py` (reinitialize).

- **Checked:** it did not work (table above).
- **Built:** the first piece of 21g's decided design (option C: snapshots
  for what is not a move). Before a row of the preset menu runs, the
  session is kept in memory. Undo puts it back and keeps the state it
  leaves for Redo. Without a snapshot Undo and Redo restore coordinates as
  before.
- **Measured** (session without compression): 2RH1, 3,862 atoms: 0.01 s to
  keep, 1.2 MB. 1AON, 59,192 atoms: 0.15 s to keep, 0.06 s to put back,
  17.8 MB. Everything came back in both: colors, representations, cartoon
  types, object and global settings, the view, selections, scenes.
- **Limits, in the code as `ponytail:`:** five steps; 600,000 atoms over all
  kept steps (about 180 MB, an estimate from the one measurement of
  300 bytes per atom): above that a preset runs without an undo step and
  says so. A snapshot is the whole session, so Undo also takes back
  whatever was done after the preset; Redo brings all of it back. A
  snapshot comes before the coordinate ring: the two are not in one order
  until 21g builds one stack.
- **Test:** `testing/tests/api/snapshots.py`: preset, undo, redo, two steps,
  the depth, the size limit, a move without a preset still goes to the
  coordinate ring, `reinitialize` empties the stack.

## Questions

| | Question | Built for now |
| --- | --- | --- |
| 36 | The table's icon: `sheet`, `table` or `table-properties`? | `sheet` |
| 37 | The color of the contact area in "protein-protein interaction": orange or white? | orange |
| 38 | Sugars and NAD(P) in the additives row, or in rows of their own? | in the one row |
| 39 | "Clean the menu": should presets leave it? Candidates: classified (it is what loading does), ball and stick, b factor putty, five of the seven ligand sites rows. | none taken out |
| 40 | Undo of a preset takes back what was done after it, until 21g. Good enough until then? | yes |

## Skipped

- Gradients in the PNG of `ligand_2d`: rdkit draws it. The SVG and the
  panel have them.
- The 2D panel still lists glycerol and other additives as ligands, after
  the ligand in the pocket. The list of 30e could sort them out.
- A table icon that is drawn again for every scale by an icon engine of our
  own: the event of 30c does it with what exists.
- Undo for anything but the preset menu: 21g.
- A row that removes additives from a selection typed by the user: the row
  acts on the object or selection of its menu, like the other four.

## Status

Done 2026-11-20, one commit per slice. The suite passed before each commit
(968 tests at the end, 251 skipped); each slice was looked at in the real
window.

| Slice | Version | Measured | Differs from the plan |
| --- | --- | --- | --- |
| 30a | 4.36.0 | 1OKY, staurosporine: the picture is 429 x 553 px (was 514 x 560), the legend four rows. No message from Qt while the panel is resized. | The legend's text is 16 px, not 14; less empty margin (the 85 px the picture lost in width); a picture is at least 344 px wide. All three after a look at it in a panel 420 px wide, where the picture is drawn at 0.79 of its size. |
| 30b | 4.37.0 | A group and a measurement in the table: nothing printed. | None. |
| 30c | 4.37.1 | 150 to 200 % in the real window: the icon of a toolbar button was 30 x 30 px for a place of 40, and is 40 x 40. | The cause was not only that old icons stay: Qt keeps the application's pixel ratio from the start, so new icons were wrong too. Icons are made for the ratio of the screens. |
| 30d | 4.38.0 | 21 rows. One test runs the 40 rows of the menu and its submenus that are no theme on a yellow structure. | More: a surface drawn by a preset has the color of the carbons of each residue, in all five presets with a surface, because an earlier preset leaves element colors behind (one pass, 0.03 s on 1AON). A modified residue of the protein keeps the protein's color. Less: a residue of which the file has no carbon keeps the color of its atoms. |
| 30e | 4.39.0 | 111 names. 1OKY: 43 atoms go (three glycerols, five sulfates), staurosporine stays. | None. |
| 30f | 4.40.0 | 4HHB in the real window: after Undo the viewport is the same picture, pixel for pixel, as before the preset; after Redo the same as after it. The window keeps its size. | The steps are also dropped when a session file is opened. Undo and Redo print one line. |

Left out: the list under "Skipped". Questions 36 to 40 are in
[PLAN.md](../../PLAN.md); they were 33 to 37 here until 11b took 33 to 35
the same day.
