# 33 — Multiple sequences and structures in a separate window

[Roadmap](../../PLAN.md) · Request 2026-11-23, draft 2 · **Planned at
4.43.0; not built.** Code inspected; no alignment benchmark or GUI trial in
this planning run. Questions 54, 55 and 60 are open.

**A resizable sequence window for comparing chains, aligning sequences and
superposing structures, with secondary structure above the aligned letters.**
This supersedes the decision in steps 3 and 22 to leave sequence work at the
existing strip. Keep that strip working while the separate window is built;
its eventual removal is a separate choice, not part of this request.

## Starting points and limits

- `layer1/Seq.cpp` draws the current strip; its Qt scrollbar is in step 18.
- `modules/pymol/fitting.py`: `align`, `super`, `cealign`, `extra_fit` and
  `alignto`. `align(..., transform=0, object=...)` can derive correspondence
  for loaded structures without moving them. `alignto` fits several objects
  independently to one reference; it is not a joint multiple alignment.
- `get_raw_alignment` / `set_raw_alignment` and
  `layer2/ObjectAlignment.cpp` connect aligned columns to atoms.
- `modules/pymol/seqalign.py` imports Biopython lazily. That package is not an
  approved runtime dependency: reusing this file does not make it free.
  `layer0/Match.cpp` is the existing native pairwise alignment machinery.
- Read secondary structure from atom `ss`; offer an explicit reassignment
  through `dss`. A sequence without coordinates has no observed secondary
  structure; do not invent it or add a prediction service.

## Interaction

Use Qt Widgets, a `.ui` form for the controls and a model/view for aligned
cells; no widget per residue. The window opens from Display > Panels >
Sequence alignment. Remember its geometry in `QSettings`, with screen bounds
checked. It can close and reopen without losing the alignment.

| Part | Planned behavior |
| --- | --- |
| Rows | One chosen chain and state per row, identified by object, segment, chain and state. Preserve residue numbers, insertion codes and nonstandard residues; gaps have no atom target. |
| Input | Loaded structure chains; FASTA and aligned FASTA in 33c if question 54's recommendation is accepted. A FASTA-only row can be aligned but cannot be moved in 3D. |
| Selection | Click/drag residues to select them in 3D; Ctrl adds. Picking in 3D highlights matching cells. Use stable residue identities, rebuilding mappings after object edits; never reuse stale atom indices. |
| Sequence alignment | Separate action from structure fitting. Align selected rows without changing coordinates. Show gaps, numbering, reference row, identity and a simple consensus/conservation row. State how gaps and unknown letters enter the identity denominator. |
| Structure alignment | Choose reference, mobile rows, state and `align`, `super` or `cealign`; run pairwise or “Align all to reference”. Display RMSD, aligned atom/residue count and failures per mobile. Apply transforms to whole mobile objects; reject conflicting transforms for chains of the same object. |
| Secondary structure | Helix, sheet and coil track with a legend, lined up with residues through gaps. Unknown/unassigned is distinct from coil. Optional `dss` reassignment changes the structure explicitly and is undoable. |
| Useful first options | Search sequence/residue number, zoom selected residues, show only selected rows, change reference, copy selected sequence, export aligned FASTA and alignment statistics. |
| Keyboard | Arrows and Shift extend selection, Enter selects in 3D, search has a labelled field, all actions have keyboard access. Secondary structure has text/tooltips as well as shapes/colors. |
| Work | Alignment computation runs off the GUI thread or in the existing native path with responsiveness verified. Apply object changes through the existing command dispatch; Stop prevents unapplied results from changing the session. One fit batch is one undo action where snapshots support it. |
| Persistence | Loaded structures remain normal objects. Keep alignment rows, gaps, reference and residue mapping under the step 28 key when they cannot be reconstructed from an alignment object. Validate mappings on restore; missing objects stay visibly unmapped. |

## Decisions before implementation

| Question | Options and recommendation |
| --- | --- |
| 54 — inputs | **Loaded chains plus FASTA (recommended)** covers sequences without structures; loaded chains first is a smaller first release, with FASTA still a planned slice. |
| 55 — true multiple sequence alignment | **An optional local MAFFT executable (recommended)** supplies an established MSA method without writing a new scientific algorithm. It needs approval as a new native dependency, a license/packaging check on all supported systems and an installation story. Alternative: build a native progressive aligner around `Match.cpp`, with algorithm validation and performance measurements; larger maintenance cost. A reference-anchored alignment can ship earlier but does not complete this requirement. |
| 60 — opening the window | **Keep SEQ as the existing strip toggle and add the window to its context menu plus Display > Panels (recommended)**; alternatively make SEQ open the new window and move the strip toggle to Display. Step 32's icon/label stays in either case. |

MAFFT accepts amino-acid or nucleotide sequences in FASTA and provides
automatic method selection; confirm current options and supported builds
before implementing. [MAFFT manual](https://mafft.cbrc.jp/alignment/software/manual/manual.html),
[project downloads and documentation](https://mafft.ddbj.nig.ac.jp/alignment/software/).
Run a chosen executable with an argument list, local temporary files, checked
exit status and cancellation. No shell interpolation, silent download or
upload of sequences. Do not introduce Biopython just for parsing FASTA.

## Slices and checks

| Slice | Scope | Acceptance |
| --- | --- | --- |
| 33a | Window, loaded chains, residue mapping, linked selection, secondary-structure track, search and copy. | Gaps, insertion codes, alternate locations, repeated chain IDs in different objects, unknown residues, empty/deleted rows and multiple states; keyboard and real-window resize/scale checks. |
| 33b | Sequence correspondence for structures; pairwise and multi-object fitting to a reference, result table and Undo. | Sequence-only operation leaves coordinates byte-for-byte unchanged; known transformed fixtures superpose; reference stays fixed; partial failure is reported and cancelled work cannot apply later. |
| 33c | FASTA input, genuine MSA using the chosen backend, aligned export, conservation and session persistence. | Three or more sequences with internal insertions, a row without coordinates and an ambiguous residue; aligned round trip preserves every input sequence after gaps are removed; backend failure/cancel and mapping after reload. Compare a documented fixture against the chosen backend. |

Files: new `modules/pmg_qt/sequence_panel.py` and form; the window's panel
registration in `pymol_qt_gui.py`; `fitting.py`, `seqalign.py`, `querying.py`,
`editing.py` only where shared operations are needed; step 28 persistence.
Any new headless sequence command must be registered in `api.py`,
`keywords.py`, completion and help, and appear in step 31's live catalog.
Prefer existing fitting commands over a redundant `multialign` wrapper.
Tests extend `testing/tests/api/fitting.py` and `seqalign.py`, with a new
`sequence_panel.py` for mapping and interaction. Each feature slice gets an
`X` version; public API changes and output changes are documented explicitly.

Skipped: phylogenetic trees, a sequence editor, secondary-structure
prediction, remote alignment services and a new docking framework. Joint
multiple-structure optimization is an option beyond fitting all structures
to a reference; do not call the latter a joint optimizer.
