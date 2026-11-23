# 24 — Ligand in 2D with its contacts

[Roadmap](../../PLAN.md) · Request 2026-11-20 · **24a done 2026-11-20 in
4.32.0:** the command `ligand_2d` with finder, layout and picture. The panel
(24b) shipped in 4.33.0; contour and halos (24c) remain open.

**2026-11-23, draft 1: 24d below repairs panel resizing and picture fitting
before 24c. Planned at 4.43.0 and built the same day in 4.43.2: see the note below.**
The earlier statement that the picture scales describes the intended path,
not proof that all dock/window sizes work. Step 30's picture styling stays.

**24d done 2026-11-23 in 4.43.2.** Measured first in the real window on
2RH1: the picture always fitted its label, at every size of the panel. The
picture itself was cut: `layout` puts the ring of residues around the mean
of the ligand's atoms, rdkit centers the box around the ligand, and for
carazolol the two are far enough apart that three circles ran over the
right edge. `draw` now draws the molecule once to see where the mean lands
and again with it in the middle of the square above the legend; the saved
SVG and PNG are fixed with it. The panel's ceiling of 125 % is gone. Tried
on 2RH1 docked from 259 to 600 px wide and floating from 300 x 300 to
800 x 1000: every circle whole. Left out: dragging the floating panel's
edge with the mouse, scales other than 150 %. The picture above is from
before the fix.

![2RH1, carazolol](../img/ligand-2d.png)

As built: `modules/pymol/ligand2d.py`, 330 lines, no Qt. The picture is
drawn by rdkit itself (shapes, text and lines in pixel coordinates), so the
command writes SVG and PNG without a window. Found in 2RH1: Asp113 salt
bridge, hydrogen bonds to Ser203, Asn312 and Tyr316, ring stacking with
Phe193 and Phe290, 17 residues, 0.2 s. In 1OKY (the test): the two hinge
hydrogen bonds of staurosporine, Ser160 and Ala162, and Glu166 at its amine.
Differences from the plan: lines have no arrow heads and do not tell
backbone from side chain; the ring grows instead of a second ring; charged
groups of the ligand are found by pattern (amines, amidines, acids), since
deposited ligands carry no charges; ring stacking is by distance of ring
centers only, without the angle; the largest ligand is the default, so
glycerol and buffer come last. The prototype's picture is replaced.

**24b done 2026-11-20 in 4.33.0:** the panel and the toolbar button.

![the panel](../img/ligand-panel.png)

`modules/pmg_qt/ligand_panel.py`, 190 lines. Tried in the real window on
2RH1: the button is off before a structure is loaded and on after; the
panel opens with carazolol; a real mouse click on Asp113 selects its 8
atoms and shows sticks; a selection made in the viewport rings Asn312 and
Asp113 at the next poll. Differences from the plan: the panel is docked on
the left, 420 px wide, not floating (2D and 3D side by side; it can be
floated like any panel); the picture is scaled to the panel; the default
ligand is the one with the most protein atoms within 4 A, not the largest
(in 2RH1 the largest is a cholesterol on the surface). Not built: the
distance in a tooltip, "Show in 3D" dashes, Tab through the residues: they
move to 24c with the contour, the halos and the metal contacts.

**A flat drawing of the ligand with the residues around it and the contacts
between them, in the style of Maestro's ligand interaction diagram. A button
in the action toolbar, enabled when a visible object has a ligand. Clicking a
residue in the drawing selects it in 3D.**

`plan_images/ligand_2D_effects.png` is the look to aim at: residue drops
colored by kind, arrows for hydrogen bonds, a line for ring stacking, a
contour around the pocket, grey halos on atoms open to the solvent.

## What exists

| Thing | State |
| --- | --- |
| rdkit | Approved optional dependency, extra `chem`, shipped in the bundles ([step 12](12-native-commands.md)). It gives 2D coordinates (`Compute2DCoords`), keeps wedges for stereo centers, and draws to SVG (`MolDraw2DSVG`) with the pixel position of every atom (`GetDrawCoords`). |
| Qt | `QtSvg` is part of PySide6: it renders that SVG. `QPainter` draws the rest. |
| Contacts in the core | `cmd.find_pairs(mode=1)` for hydrogen bonds by distance and angle; `distance` modes 5 to 7 and `pi_interactions` for ring stacking and cation-ring since 4.19.35 ([21c](21-commercial-features.md)); selections `organic`, `polymer`, `solvent`, `inorganic`, `donor`, `acceptor`. |
| Solvent exposure | `get_sasa_relative`, fast since 4.19.8. |

## The prototype (2026-11-20)

2RH1 with its ligand carazolol: the ligand's mol block from `cmd.get_str`,
flat coordinates from rdkit, residues within 4 Å, hydrogen bonds from
`find_pairs`, residues on a ring around the ligand at the angle of the atom
they touch, SVG rendered by Qt. 0.06 s. Three hydrogen bonds found (Ser203,
Asn312, Tyr316), 17 residues.

(The prototype's picture is replaced by the one at the top.)

What it shows: the approach works with what is installed, and the hard part
is not finding contacts but the layout (residues overlap; Asp113's salt
bridge is not drawn because the prototype only looks for hydrogen bonds).

## PandaMap and the others (read 2026-11-20)

| Project | License | What it needs | Verdict |
| --- | --- | --- | --- |
| [PandaMap](https://github.com/pritampanda15/PandaMap) | MIT | numpy, matplotlib, biopython, requests; rdkit used if present. About 313 KB of Python, `core.py` 2,567 lines. Draws with matplotlib only. | Not a dependency: matplotlib and biopython are two new packages and it reads the PDB file again with its own parser. **Its layout idea is taken** (allowed by MIT, credited in the source): residue boxes on a ring, each at the angle of the ligand atoms it touches, then pushed apart to a minimum gap; and its cutoffs were compared. |
| [ProLIF](https://github.com/chemosim-lab/ProLIF) LigNetwork | Apache-2.0 | pandas, scipy, MDAnalysis, networkx; output is HTML with a JavaScript library from a CDN | No: needs a web view (`AGENTS.md` §2.4). |
| rdkit alone | BSD | nothing new | A [recipe](https://greglandrum.github.io/rdkit-blog/posts/2025-09-26-drawing-interactions-1.html) of about 30 lines: dummy atoms with labels and zero-order bonds. Plain look, no residue shapes; rdkit decides the layout. A fallback, not the goal. |
| [PLIP](https://github.com/pharmai/plip) | GPL-2.0 | openbabel | No (license and dependency). Its published cutoffs are the reference below. |
| LigPlot+, PoseView | closed | | Not usable. |

## Design

New command `ligand_2d [ligand [, cutoff [, filename ]]]` in a new
`modules/pymol/ligand2d.py` (finding and layout, no Qt), and a panel in
`modules/pmg_qt/ligand_panel.py` (painting, clicks). Without rdkit the
command says how to install the extra, as `load_smiles` does.

### Which ligand

`organic` and not `polymer`, at least 6 heavy atoms, in the enabled objects.
One: it is taken. Several: a list in the panel's header (residue name, chain,
number), the first one chosen; an atom selection named `sele` that lies in a
ligand chooses that one. None: the toolbar button is disabled, with the
tooltip "No ligand in the visible objects". Peptide ligands are polymer and
are not found: the `ligand` argument takes any selection.

### Contacts

Heavy atoms only where no hydrogens are present. Cutoffs as PLIP publishes
them, each one constant at the top of the file:

| Contact | Rule | Drawn as |
| --- | --- | --- |
| Hydrogen bond | donor to acceptor 3.5 Å (PLIP uses 4.1 to the hydrogen's donor), angle from `find_pairs` mode 1 | violet arrow from donor to acceptor; dashed when the residue's side is a side chain, solid for backbone, as in the picture |
| Salt bridge | charged groups (Asp, Glu against Lys, Arg, His; ligand charges from rdkit's formal charges) within 5.5 Å | line in red to blue |
| Ring stacking | `pi_interactions` of the core (ring centers 5.5 Å) | green line between ring centers, a dot at each end |
| Cation to ring | same finder, 6.0 Å | red line |
| Metal | ligand atom to a metal within 3.0 Å | grey line; the metal is a small circle |
| Hydrophobic and other near residues | any heavy atom within 4.0 Å | no line: the residue is only placed |
| Water bridge | Skipped in the first version | |

### Layout

1. Ligand: rdkit flat coordinates, drawn by rdkit into the SVG (bond orders,
   wedges, atom colors). Explicit hydrogens off except on hetero atoms.
2. Residue anchors: each residue goes to the mean position of the ligand
   atoms it touches, pushed outward from the ligand's center to a ring at
   1.6 bond lengths outside the ligand's outline.
3. Push apart: residues that overlap move along the ring until none do;
   more residues than fit make a second ring. Neighbors in sequence stay
   next to each other and are joined by a black line, as in the picture.
4. Pocket contour: a closed smooth line (a `QPainterPath` through points
   halfway between ligand and residue ring), colored piecewise by the
   nearest residue's kind; open where the ligand is exposed.
5. Solvent halo: a grey blurred circle behind a ligand atom whose relative
   accessible area in the complex is over 30 %.

### Residue shapes and colors

A drop pointing at the ligand, the residue name over its number. One table:

| Kind | Residues | Color |
| --- | --- | --- |
| Hydrophobic | Ala, Val, Leu, Ile, Met, Phe, Trp, Tyr, Pro, Cys | green |
| Polar | Ser, Thr, Asn, Gln, His | cyan |
| Negative | Asp, Glu | orange-red |
| Positive | Lys, Arg | violet-blue |
| Glycine | Gly | cream |
| Other (water, metal, nucleotide) | | grey |

The colors come from the object palette in use where it has them, else from
this table; a legend is drawn under the picture. The background follows the
theme: the drawing is black on white in the light theme and light on dark in
the dark one (the SVG's colors are set, not inverted), and an export is
always on white unless "transparent" is chosen.

### The panel

| Part | Decision |
| --- | --- |
| Where | A dock `dock_ligand`, floating at first, that can be docked; opened by the toolbar button "2D" (icon `hexagon` of the Lucide set, already shipped; [step 26](26-toolbar-buttons.md) has the place). Display > Panels lists it. |
| Click on a residue | `select sele, <that residue>` and the residue is shown as sticks; Ctrl+click adds. Double click zooms on it. |
| Click on a ligand atom | Selects the atom. |
| Hover | The contact's distance in a tooltip. |
| Selection, both ways | A residue or ligand atom selected in the drawing is selected in 3D (the two rows above). The other way too: residues that are in `sele` are drawn with a blue ring, so a click in the viewport or on a quick-select chip shows in the drawing. Read from `sele` in the window's 0.5 s poll while the panel is shown. |
| Contacts in 3D | "Show in 3D" check box: the drawn contacts appear as dashes in the viewport (`distance` objects in a group `ligand_2d`), removed when the panel closes. |
| Update | A Refresh button, and by itself when the ligand choice changes. Not on every frame or state change. |
| Export | Save as SVG or PNG (the command's `filename`), Copy to the clipboard. |
| Keyboard | Tab walks the residues, Enter selects the current one; the buttons are ordinary buttons. |

## Options

**How it is drawn** (question 23, answered 2026-11-20: A, "our own code, it could use rdkit; try to make it interactive, e.g. selecting a residue in 2D selects it in 3D as well"). The interactive part is the panel of 24b; the answer makes the selection go both ways, see below.

| | Option | Note |
| --- | --- | --- |
| A | **Own layout and painting: rdkit for the ligand, `QPainter` for the rest. Recommended.** | About 300 lines in two files. No new dependency. The Maestro-like look is reachable (drops, arrows, contour). |
| B | PandaMap as an optional dependency. | Its look, done today; matplotlib, biopython and requests come with it (tens of MB in the bundles), and it works on a file, not on the loaded object. |
| C | The rdkit recipe only. | About 40 lines; a plain picture: labels around the ligand, lines for contacts, no shapes, no contour, no clicks on residues. Could ship first as 24a and stay if it is enough. |

## Slices

| Slice | What | Check |
| --- | --- | --- |
| 24a | `ligand_2d`: finder and layout, SVG and PNG from the command line (no panel). Hydrogen bonds, salt bridges, stacking, near residues. | `testing/tests/api/ligand2d.py` (needs rdkit): on 2RH1 the contact list has Ser203, Asn312, Tyr316 as hydrogen bonds and Asp113 as a salt bridge; no two residue shapes overlap; the SVG parses. Pictures of 2RH1, 1OKY, 3IIS in the plan. |
| 24b | The panel and the toolbar button: clicks, hover, ligand list, export, theme. | Simulated click selects the residue; the button is disabled without a ligand; real window at 150 %, dark and light. |
| 24c | Pocket contour, solvent halos, metal contacts, "Show in 3D". | Picture next to the reference; the dashes go when the panel closes. |
| 24d (before 24c) | Resizable dock/floating window; fit the complete picture and legend to its content area. | Repeated shrink/grow and scale changes, correct hit testing, no cropping or layout growth loop. |

## 24d — resize and fit the picture (request 2026-11-23)

`modules/pmg_qt/ligand_panel.py` already has a `QDockWidget`, a resizable
`_Picture` label with `Ignored` size policy and a 240 × 240 minimum, and
`_render` scales the SVG using the label dimensions with a 1.25 ceiling.
These are code facts, not measurements of the reported failure. Inspect the
header's minimum size, dock constraints and SVG bounds as well as the label.

1. Reproduce with the user's crowded ligand/pocket and a small fixture,
   docked and floating. Record widget/content/SVG bounds and device-pixel
   ratio while shrinking and growing; check the legend is inside SVG bounds.
2. Fix the constraint or transform at its source. Fit the entire drawing
   into the available content rectangle, preserving aspect ratio and
   centering. The minimum size must come from usable controls, not a stale
   pixmap. Handle zero-size/hidden widgets without division by zero or an
   allocation loop. Resize rerenders the cached SVG; it must not rerun
   contact analysis on every mouse movement.
3. Draw sharp at the current pixel ratio. Painting and residue/atom hit
   testing must share the actual scaled size and offset, including rounding.
   The growth cap may remain only if the image still uses the space as
   intended; remove it if it prevents fitting the requested panel behavior.
4. Keep mouse resize handles and dock splitters usable and all header
   controls reachable. Use the existing dock geometry persistence. Fit is
   automatic; explicit zoom/pan is an optional later choice if fitting a very
   crowded pocket makes its labels unreadable.

Checks in `testing/tests/api/ligand_panel.py`: shrink/grow several times,
non-square and crowded SVGs, whole legend visible, hit coordinates after
resize, hidden/empty panel, dark/light and fractional scaling. Real window:
drag both dock splitter and floating edges at 100/120/150/200 %, with the
main window also resized. Those are proposed test inputs, not completed
measurements. SVG/PNG export stays at its requested output size. A fix
gets a `Y` version; no new dependency or separate image viewer.

## Skipped

- Water bridges, halogen bonds, covalent links: add when asked, each is one
  rule in the finder.
- Editing the layout by dragging residues.
- Several ligands in one picture; protein-protein interfaces.
- Recomputing during a trajectory.

## Sources

- PandaMap, MIT, version 4.4.1: `core.py` (contact rules), `ligand2d.py`,
  `diagram.py` (ring layout).
- PLIP defaults: <https://github.com/pharmai/plip/blob/master/plip/basic/config.py>.
- rdkit drawing recipe: Greg Landrum's blog, 2025-09-26.
