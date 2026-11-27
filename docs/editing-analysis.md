# Build, clean up, measure and compare

[Docs home](README.md) · Checked with version 4.90.0.

Build a small molecule, tidy a structure from the Protein Data Bank, measure
it and compare it with another one. Most of this needs nothing extra. A few
actions need the optional packages rdkit, pdbfixer and openmm, which the
downloadable builds include. Examples with `fetch` need an internet
connection.

**On this page:** [Before you start](#before-you-start) ·
[From SMILES](#build-a-molecule-from-smiles) ·
[Builder](#build-a-molecule-piece-by-piece) ·
[Hydrogens](#add-or-remove-hydrogens) · [Bonds](#change-bonds) ·
[Remove waters and additives](#remove-waters-ions-ligands-and-additives) ·
[Optimize, fix or relax](#optimize-fix-or-relax-which-one-do-i-need) ·
[Measure](#measure-distances-angles-and-dihedrals) ·
[Contacts](#find-contacts) · [Compare](#compare-two-structures) ·
[Morph](#morph-between-two-conformations) ·
[Maps](#show-a-density-map) · [Trajectories](#trajectories-and-states) ·
[Symmetry](#symmetry-mates-and-the-unit-cell) ·
[Stereo](#label-r-and-s-centers) · [Wizards](#wizards) ·
[Selections](#selections-a-short-primer) ·
[Limits](#limits-and-common-problems)

## Before you start

Every row of the Objects panel has the buttons **A** (action), **S** (show),
**H** (hide), **L** (label) and **C** (color). "**A** > clean" below means:
click A on the row of the object, then the row clean. Selections, groups and
the row `all` have an A menu too.

The examples use two entries of the Protein Data Bank:

```
fetch 1oky
fetch 1rx1
```

1OKY is a kinase with the inhibitor staurosporine (residue name `STU`).
1RX1 is an enzyme with its cofactor NADPH (residue name `NAP`). In a script
write `fetch 1oky, async=0`, so that the next line waits for the download.

Several actions here delete atoms or move them. Keep a copy first:
**A** > duplicate object, or `create backup, 1oky`.

## Build a molecule from SMILES

SMILES is a way to write a molecule as one line of text.

1. Choose **Build** > From SMILES...
2. Type or paste the SMILES and confirm. The field starts with the text of
   the clipboard when that is one word.

A new object appears, with hydrogens and 3D coordinates.

```
load_smiles "CC(=O)Oc1ccccc1C(=O)O", aspirin
load_smiles "CCCCCc1ccccc1", pentylbenzene, 10
```

The third argument asks for up to that many conformers (shapes of the same
molecule). They become states of one object; similar ones are dropped, so
fewer may remain. Given a text or CSV file, `load_smiles` builds one molecule
per line: the SMILES first, then an optional name. A line that is not a
SMILES is reported and skipped.

Needs rdkit; see [packages](#the-packages-and-what-you-see-without-them).

## Build a molecule piece by piece

1. Click **Builder** in the toolbar, or choose **Display** > Panels >
   Builder. The panel has the tabs Chemical, Protein and Nucleic Acid and,
   under them, rows of buttons for atoms, bonds and the model.
2. Click a fragment button. With no atom picked, a wizard starts and its box
   appears in the Objects panel: click **Create As New Object** there, or
   click an atom in the viewport to attach the fragment to it.
3. Click the next fragment. While an atom is picked, a fragment goes onto
   that atom at once.

The same pieces are in the menu: **Build** > Fragment (elements, rings,
amide, carbonyl ...) and **Build** > Residue (the amino acids and the caps
Acetyl, Amine and N-Methyl). Each row shows its shortcut: Ctrl-Shift and a
letter for the elements, Alt and a digit or a letter for rings, groups and
residues. They act on the picked atom, called `pk1`: in the mouse mode
3 Button Editing (**Mouse** menu) a click on an atom picks it.

`fab ACDEF, pep` builds a peptide from one-letter codes without any clicks.

## Add or remove hydrogens

| **A** > hydrogens > | Does | Command |
| --- | --- | --- |
| add | adds all hydrogens | `h_add 1oky` |
| add polar | adds them on donors and acceptors only | `h_add 1oky & (don.\|acc.)` |
| remove | deletes all hydrogens | `remove 1oky and hydro` |
| remove nonpolar | deletes those that are not on a donor or acceptor | `remove 1oky & hydro & not nbr. (don.\|acc.)` |

`h_add` places hydrogens from the bond orders it finds. It knows nothing
about pH; for that use [fix structure](#fix-a-structure). **Build** > Fill
Hydrogens on (pk1) (Ctrl-Shift-R) fills the picked atom only.

## Change bonds

Pick two atoms one after the other (they become `pk1` and `pk2`), then
use the **Build** menu:

| Row | Shortcut | Does |
| --- | --- | --- |
| Create Bond (pk1)-(pk2) | Ctrl-Shift-T | adds a bond |
| Cycle Bond Valence | Ctrl-Shift-W | changes the order of the picked bond, step by step |
| Remove (pk1) | Ctrl-Shift-D | deletes the picked atom |
| Invert (pk2)-(pk1)-(pk3) | Ctrl-Shift-E | inverts the center pk1 |
| Make (pk1) Positive / Negative / Neutral | Ctrl-Shift-K / J / U | sets the formal charge |

Typed, with atoms named in full:

```
valence 2, 1oky and resn STU and name C8, 1oky and resn STU and name O5
unbond 1oky and resn STU and name C8, 1oky and resn STU and name O5
bond 1oky and resn STU and name C8, 1oky and resn STU and name O5, 2
```

`valence` sets the order of a bond that exists, `unbond` removes it, `bond`
adds one with the given order. A bond joins atoms of one object only.
**S** > more > valence draws double and triple bonds as such.

## Remove waters, ions, ligands and additives

**A** > clean has five rows that delete atoms. On 1OKY they remove:

| **A** > clean > | Removes | In 1OKY |
| --- | --- | --- |
| remove waters | what `solvent` matches | the waters |
| remove ions | what `inorganic` matches | five sulfate ions |
| remove waters and ions | both | both |
| remove ligands | what `organic` matches | staurosporine and three glycerols |
| remove crystallization additives | a fixed list of residue names | the glycerols and the sulfates; staurosporine stays |

The list of additives holds what a crystal is grown and frozen in: PEG
fragments, glycerol and other cryoprotectants, buffers, sulfate, phosphate
and nitrate, reducing agents, detergents. It also holds the sugars of
glycosylation (NAG, NDG, BMA, MAN, FUC) and NAD(P): in 1RX1 this row deletes
the cofactor. The log says how many atoms went.

```
remove 1oky and solvent
remove 1oky and (resn GOL+SO4)
```

The atoms are gone from the object, not hidden. To hide water instead use
**H** > waters.

## Optimize, fix or relax: which one do I need

| | optimize ligand geometry | fix structure... | optimize protein geometry |
| --- | --- | --- | --- |
| Command | `clean` | `fix_structure` | `minimize` |
| For | one small molecule | a protein or nucleic acid from a file | a protein with complete residues |
| Does | corrects bond lengths, angles and clashes inside the molecule | builds missing atoms, adds hydrogens for a pH, replaces nonstandard residues | removes clashes and strain; heavy atoms are held near their place |
| With | rdkit, MMFF94 | PDBFixer | OpenMM, Amber14, implicit solvent |
| Result | the coordinates of the object change | a new object `<object>_fixed` | a new object `<object>_min` |
| Cannot | take a protein, or more than 1000 atoms | build gaps in the chain | take ligands, modified residues or a chain with a gap |

All three are rows of **A** > clean. From the menu they work in the
background; the window stays usable.

### Optimize the geometry of a ligand

1. Click the ligand in the viewport; it becomes the selection `sele`.
2. On the row `sele`: **A** > clean > optimize ligand geometry.

```
clean aspirin
clean 1oky and resn STU
```

Give one whole molecule of one object. On a whole protein the command
answers `clean is for small molecules ... For a protein use "minimize"`.

- The atoms around the molecule are not seen: a ligand can move into the
  protein.
- Bond orders are used as they are. Where a file gave a ligand only single
  bonds, set the double bonds first, or flat rings pucker.
- Missing hydrogens are added for the calculation only.

### Fix a structure

1. **A** > clean > fix structure... opens the dialog Fix Structure.
2. Leave or clear the boxes: Build missing atoms of residues that are
   present, Replace nonstandard residues (MSE becomes MET), Add hydrogens
   for pH (with the pH), Keep water, Keep ligands and ions.
3. Click OK. The dialog shows the command it will run.

```
fix_structure 1rx1
fix_structure 1oky, ph=5.5, keep_water=0
```

The result is the new object `1rx1_fixed`; the original is not changed.

- Residues that are missing as a whole (gaps) are not built.
- All hydrogens are built new; the ones that were there are replaced.
- For the hydrogens of a ligand, PDBFixer downloads the ligand's definition
  from files.rcsb.org. Without a connection the ligand gets none.
- The new object has default colors and representations, and its ligands
  have single bonds only.

### Optimize the geometry of a protein

```
fix_structure 1rx1 and polymer, name=prot
minimize prot
```

The result is the new object `prot_min`. The log gives the energy before
and after and how far the heavy atoms moved. **A** > clean > optimize
protein geometry does the same for the object or selection of the row.

- Missing heavy atoms stop the command: run fix structure first.
- Ligands and modified residues have no parameters. Leave them out with
  `polymer`; `minimize 1rx1_fixed` stops at the cofactor.
- A chain with a gap is refused. 1OKY has one: after fix structure,
  `minimize` answers `chain A has a gap between residues 232 and 239; give
  one piece at a time`.
- The calculation runs on the CPU.

### The packages and what you see without them

| Package | Needed by | With pip |
| --- | --- | --- |
| rdkit | `load_smiles`, `clean`, `assign_stereo` | `pip install 'pymolish[chem]'` |
| pdbfixer and openmm | `fix_structure`, `minimize` | `pip install 'pymolish[fix]'` |

The downloadable builds include all three. Without a package the command
changes nothing and prints, for example,
`Error: this command needs rdkit: pip install 'pymolish[chem]'`.

## Measure distances, angles and dihedrals

1. Choose **Wizard** > Measurement. Its box appears in the Objects panel.
2. Click two atoms. A dashed line with the distance appears, in a new
   object named `measure01`.
3. For another kind, open the first menu of the box: Distances, Distances
   to Rings, Angles, Dihedrals, Polar Neighbors, Heavy Neighbors, Neighbors,
   Polar Contacts.
4. Click **Done** to leave the wizard. The measurements stay.

Typed, with one selection per atom:

```
distance hinge, 1oky and resn STU and name N1, 1oky and resi 160 and name O
angle ang, 1oky and resi 160 and name N, 1oky and resi 160 and name CA, 1oky and resi 160 and name C
dihedral psi160, 1oky and resi 160 and name N, 1oky and resi 160 and name CA, 1oky and resi 160 and name C, 1oky and resi 161 and name N
```

Each command makes a measurement object with a row in the Objects panel;
delete the row to remove the dashes. `get_distance`, `get_angle` and
`get_dihedral` return the number to a script; each of their selections
must match exactly one atom.

Labels on atoms come from the **L** menu: residues, chains, atom name,
b-factor and more; **L** > clear removes them.

```
label 1oky and resi 160 and name CA, "%s%s" % (resn, resi)
label 1oky
```

The second line clears the labels of the object.

## Find contacts

**A** > find draws contacts as dashes in a new object:

| **A** > find > | Finds | Typed |
| --- | --- | --- |
| polar contacts | likely hydrogen bonds | `distance` with `mode=2` |
| any contacts | atoms of different chains within 3.0, 3.5 or 4.0 Å | `distance` with a cutoff |
| halogen-bond interactions | halogen bonds | `distance` with `mode=9` |
| salt-bridge interactions | salt bridges | `distance` with `mode=10` |
| pi interactions | pi-pi (ring to ring), pi-cation (ring to positive charge) | `pi_interactions`, `mode=6`, `mode=7` |

The rows under polar contacts choose which atoms count: within the
selection, with or without solvent, main chain or side chains only, to
other atoms of the object or to any atoms, or between chains.

```
distance stu_polar, 1oky and resn STU, 1oky and polymer, mode=2
pi_interactions pi, 1rx1
distance salt, 1oky, same, mode=10
```

A contact is a guess from distances and angles; most files have no
hydrogens. The [ligand guide](ligands.md) shows the contacts of one ligand
at a time.

## Compare two structures

`fetch 1ake 4ake` loads the closed and the open form of adenylate kinase.

| Command | Pairs the atoms by | Use it for |
| --- | --- | --- |
| `align mobile, target` | a sequence alignment | similar sequences |
| `super mobile, target` | the structure, not the sequence | low sequence similarity |
| `cealign target, mobile` | the CE algorithm on C-alpha atoms | different sequences, same fold |
| `fit mobile, target` | equal chain, residue number and atom name | two copies of one molecule |
| `pair_fit atoms1, atoms2` | the pairs you give, in order | a few chosen atoms |

```
align 4ake and chain A, 1ake and chain A
super 4ake and chain A, 1ake and chain A
cealign 1ake and chain A, 4ake and chain A
fit 4ake and chain A and name CA, 1ake and chain A and name CA
pair_fit 4ake and chain A and resi 1-10 and name CA, 1ake and chain A and resi 1-10 and name CA
```

The first selection moves (for `cealign` the second). The moved object
keeps its new coordinates. The log gives the result, for example
`Executive: RMSD = 2.069 (1135 to 1135 atoms)`: the RMSD is the root mean
square distance of the paired atoms in Å.

- `align` and `super` throw out pairs that fit badly, in up to five rounds.
  Their RMSD is for the pairs that remain, so it flatters a large motion.
- `fit` keeps every pair: the same two chains give 7.131 Å over 214 C-alpha
  atoms. `rms` gives that number without moving anything; `rms_cur` gives
  the RMSD of the atoms where they are now.
- `align ..., object=aln` also makes an alignment object that shows which
  residues were paired.

In the menu: **A** > align > to molecule (*/CA) lists the other objects and
fits the row's object onto the one you choose, with `align` on the C-alpha
atoms. **A** > align > all to this (*/CA) fits every other object onto this
one, enabled to this (*/CA) only the ones that are switched on.

The [sequence guide](sequences.md) describes the alignment window, which
fits several structures to a reference and lists the results.

## Morph between two conformations

```
align 4ake and chain A, 1ake and chain A
morph mout, 4ake and chain A, 1ake and chain A
```

`mout` is a new object with 30 states that lead from the first conformation
to the second. Play it with the States strip of the Objects panel.

- What it does: moves every atom on a straight line, then repairs bond
  lengths, angles and flat groups in every state in between.
- Two objects are paired by `align` (or `match=super`); atoms without a
  partner are left out.
- It does not superpose: run `align` first, as above.
- States in between can look distorted when the motion is large. The
  RigiMOL method of the commercial PyMOL is not part of this program;
  `method=rigimol` is an error.

## Show a density map

A map is a grid of numbers in space, such as electron density. Open the
file with **File** > Open... or `load`; CCP4, MRC, DX and cube files were
checked. A map gets its own row in the Objects panel.

```
fetch 1ubq
fetch 1ubq, type=2fofc
isomesh ubq_mesh, 1ubq_2fofc, 1.0, 1ubq, carve=2.0
isosurface ubq_surf, 1ubq_2fofc, 1.5
volume ubq_vol, 1ubq_2fofc
```

The second line downloads the electron density of the entry from
www.ebi.ac.uk as the map `1ubq_2fofc`. `isomesh` draws a mesh where the map
has the level 1.0, here only within 2 Å of the atoms of `1ubq`;
`isosurface` draws a closed surface; `volume` draws the map as a colored
fog. A CCP4 map is normalized when it loads, so a level counts standard
deviations.

In the menu, on the row of the map:

| **A** > | Makes |
| --- | --- |
| mesh > @ level 1.0 ... | the object `<map>_mesh` |
| surface > @ level 1.0 ... | the object `<map>_surf` |
| volume > default, or a named color ramp | the object `<map>_volume` |
| slice > default | a colored plane through the map that follows the camera |
| gradient > default | a gradient object of the map, colored by a ramp |

On the row of a mesh or a surface, **A** > level changes the level
(`isolevel ubq_mesh, 1.5`). On the row of a volume, **C** > panel opens the
Volume Color Map Editor (`volume_panel ubq_vol`): a histogram of the map
with points that set color and opacity. A click adds a point, a drag moves
it; **Help** in the panel lists every mouse action.

For 1UBQ the log warns `not all symmetry expanded points covered by map`:
part of the molecule lies outside the box of the map file, and the mesh is
missing there.

## Trajectories and states

A state is one set of coordinates of an object. A trajectory is loaded in
two steps: a file with the atoms, then the file with the coordinates of
every frame. The source tree has a small example; from its root:

```
load testing/data/sampletrajectory.pdb, traj
load_traj testing/data/sampletrajectory.dcd, traj
```

`traj` now has 10 states. `.dcd` and `.xtc` files were checked.

When an object has more than one state, the States strip appears in the
Objects panel: First, Previous, Play, Next, Last, a number field to jump to
a state, and a button for the speed. The Left and Right arrow keys step
back and forward while the viewport has the keyboard.

| To | Command | Menu |
| --- | --- | --- |
| Fit every state onto the first | `intra_fit traj and name CA` | **A** > align > states (*/CA) |
| Average out fast vibrations | `smooth traj, 1, 3` | |
| Make one object per state | `split_states traj` | **A** > split > by state |

`intra_fit` prints the RMSD of every state. `smooth` and `intra_fit` change
the coordinates of the states.

## Symmetry mates and the unit cell

A crystal structure file describes one copy; its neighbors in the crystal
are symmetry mates.

1. **A** > more > generate > symmetry mates > within 4 A (or 5 to 1000 A).
2. **S** > more > cell draws the unit cell as a box; **H** > more > cell
   hides it.

```
symexp sym, 1oky, 1oky, 4
show cell, 1oky
```

Every mate with an atom within 4 Å becomes an object of its own, named
`sym` and its symmetry operation. The object needs a real unit cell: an
entry without one, as many from electron microscopy, gives an error.

## Label R and S centers

```
assign_stereo 1oky and resn STU
label 1oky and resn STU, stereo
```

`assign_stereo` finds the chiral centers from coordinates and bonds and
sets the atom property `stereo` to R or S; `select stereo R` then works
too. In the menu: **L** > other properties > stereochemistry. The property
does not follow an edit: run the command again. Needs rdkit.

## Wizards

A wizard asks for clicks in the viewport and shows its buttons in a box in
the Objects panel; **Done** ends it. They are in the **Wizard** menu and
under the **Wizard** button below the object list.

| **Wizard** > | For |
| --- | --- |
| Appearance | color, show, hide or select what you click |
| Measurement | distances, angles, dihedrals, neighbors, polar contacts |
| Mutagenesis > Protein | replace a residue: pick it, choose the amino acid and a rotamer, **Apply** |
| Mutagenesis > Nucleic Acids | replace a base: pick the nucleotide, choose the new one |
| Pair Fitting | click pairs of atoms (mobile, then target) and fit on them |
| Density | map meshes around the picked residue; Next Res. and Previous Res. walk the chain |
| Filter | go through the states of an object and mark each Accept, Defer or Reject |
| Sculpting | sculpting around a picked center atom, with menus for radius and cushion |
| Label | label the atoms you click |
| Charge | copy or move partial charges from atom to atom |
| Demo | built-in demonstrations; End Demonstration leaves them |

## Selections: a short primer

A selection says which atoms a command acts on. These were counted on a
freshly fetched `1oky` with `count_atoms`:

| Selection | Atoms | Means |
| --- | --- | --- |
| `1oky and chain A` | 2502 | chain A; this entry has no other |
| `1oky and resn STU` | 35 | residues by name: the ligand |
| `1oky and resi 100-110` | 91 | residues by number |
| `1oky and name CA and resn LYS` | 27 | atoms by name: the C-alphas of the lysines |
| `1oky and polymer` | 2327 | the protein |
| `1oky and organic` | 53 | ligands: staurosporine and the glycerols |
| `1oky and solvent` | 97 | water |
| `1oky and not (polymer or solvent)` | 78 | everything else |
| `1oky and polymer within 4 of resn STU` | 35 | protein atoms within 4 Å of the ligand |
| `byres (1oky and polymer within 4 of resn STU)` | 117 | the same, as whole residues |
| `1oky and resn STU around 4` | 39 | all atoms within 4 Å of the ligand, without the ligand |

`and`, `or` and `not` combine selections; parentheses group them. `select
pocket, byres (1oky and polymer within 4 of resn STU)` gives a selection a
name and a row in the Objects panel. `help selections` prints more words;
the [Reference](reference.md) has a longer table.

## Limits and common problems

- **A removed atom is gone.** The clean rows, `remove`, the Builder and the
  mutagenesis wizard change the object itself. Undo brings the atoms
  back (up to 20 steps, 600,000 atoms); for more, duplicate the object or
  save a session before.
- **`fix_structure` and `minimize` never change the original.** They make
  a new object, with default colors. Delete it if you do not like it.
- **"More than one atom found"** from `get_angle` or `get_dihedral`: a
  selection matched several atoms. Name the object, the residue number and
  the atom.
- **"this command needs ..."**: an optional package is missing; see
  [packages](#the-packages-and-what-you-see-without-them).
- **Ctrl-Shift-M** is printed beside **Build** > Fragment > Methane, but
  the key goes to the next ligand. Use the menu row for methane.
- **A fit moves the object.** **A** > align > matrix reset
  (`matrix_reset 4ake`) puts an object back where it was before `align` or
  `super` moved it.

## Next

- [Inspect a ligand and its pocket](ligands.md)
- [Work with sequences and alignments](sequences.md)
- [Save sessions, structures, pictures and exports](saving.md)
- [Commands](commands.md) and [Reference](reference.md)
