# 33 — Multiple sequences and structures in a separate window

[Roadmap](../../PLAN.md) · Request 2026-11-23, draft 2 · **Planned at
4.43.0; not built.** Code inspected; no alignment benchmark or GUI trial in
this planning run. **Question 54 answered 2026-11-23: loaded chains plus
FASTA import/alignment in the first release**, with helix/sheet/coil for
loaded structures. Questions 55 (backend) and 60 (entry point) remain open.

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
| Input | Loaded structure chains, FASTA and aligned FASTA in the first release (33a), as confirmed in answer 54. A FASTA-only row can be aligned but cannot be moved in 3D. |
| Selection | Click/drag residues to select them in 3D; Ctrl adds. Picking in 3D highlights matching cells. Use stable residue identities, rebuilding mappings after object edits; never reuse stale atom indices. |
| Sequence alignment | Separate action from structure fitting. Align selected rows without changing coordinates. Show gaps, numbering, reference row, identity and a simple consensus/conservation row. State how gaps and unknown letters enter the identity denominator. |
| Structure alignment | Choose reference, mobile rows, state and `align`, `super` or `cealign`; run pairwise or “Align all to reference”. Display RMSD, aligned atom/residue count and failures per mobile. Apply transforms to whole mobile objects; reject conflicting transforms for chains of the same object. |
| Secondary structure | Helix, sheet and coil track with a legend, lined up with residues through gaps. Unknown/unassigned is distinct from coil. Optional `dss` reassignment changes the structure explicitly and is undoable. |
| Useful options | Search sequence/residue number, zoom selected residues, show only selected rows, change reference, copy selected sequence, export aligned FASTA and alignment statistics; delivery follows the slices below. |
| Keyboard | Arrows and Shift extend selection, Enter selects in 3D, search has a labelled field, all actions have keyboard access. Secondary structure has text/tooltips as well as shapes/colors. |
| Work | Alignment computation runs off the GUI thread or in the existing native path with responsiveness verified. Apply object changes through the existing command dispatch; Stop prevents unapplied results from changing the session. One fit batch is one undo action where snapshots support it. |
| Persistence | Loaded structures remain normal objects. Keep alignment rows, gaps, reference and residue mapping under the step 28 key when they cannot be reconstructed from an alignment object. Validate mappings on restore; missing objects stay visibly unmapped. |

## Decisions

| Question | Options and recommendation |
| --- | --- |
| 54 — inputs | **Answered 2026-11-23: loaded chains plus FASTA import/alignment in the first release.** Do not release a loaded-chains-only version first. This selects input scope, not an alignment dependency. |
| 55 — true multiple sequence alignment | **An optional local MAFFT executable (recommended)** supplies an established MSA method without writing a new scientific algorithm. It needs approval as a new native dependency, a license/packaging check on all supported systems and an installation story. Alternative: build a native progressive aligner around `Match.cpp`, with algorithm validation and performance measurements; larger maintenance cost. A reference-anchored alignment can serve as a prototype but does not complete this requirement. |
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
| 33a | First release: window, loaded chains plus FASTA/aligned FASTA input, pairwise sequence alignment and genuine MSA using the chosen backend, aligned export, residue mapping, linked selection, secondary-structure track, search and copy. | Gaps, insertion codes, alternate locations, repeated chain IDs, unknown residues, empty/deleted rows and multiple states; three or more sequences including a FASTA-only row; aligned export preserves every input sequence after gaps are removed; sequence alignment leaves coordinates unchanged; backend failure/cancel; keyboard and real-window resize/scale checks. Compare a documented alignment fixture against the chosen backend. |
| 33b | Pairwise and multi-object structure fitting to a reference, result table and Undo. | Known transformed fixtures superpose; reference stays fixed; FASTA-only rows cannot be fitted in 3D; partial failure is reported and cancelled work cannot apply later. |
| 33c | Consensus/conservation, identity statistics and session persistence. | Documented gap/unknown-letter counting; alignment and residue mapping survive reload, including FASTA-only rows and missing structure objects. |

Answer 54 moves FASTA and its sequence-alignment backend from the former
33c into 33a. Question 55 must therefore be settled before the first
release; no new dependency is approved by the input choice alone.

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
