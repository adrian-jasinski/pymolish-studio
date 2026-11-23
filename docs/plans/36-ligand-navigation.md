# 36 — Next ligand with protein polar contacts

[Roadmap](../../PLAN.md) · Request 2026-11-23, draft 10 · **Planned at
4.43.0 and built the same day in 4.51.0: see the note below.** Question 58
chooses the shortcut; the command and menu are required either way.

**36a done 2026-11-23 in 4.51.0; the step is finished.**
`modules/pymol/ligand_nav.py`, 158 lines: `ligand_next [selection
[, step]]`, step 0 clears. Measured: 9 ms a step on 2RH1 (10 ligands),
100 ms on 1AON (59,192 atoms, 7 ligands): no cache was added. Tried in the
real window: the three rows of Display > Zoom, Ctrl+Shift+M and
Ctrl+Shift+H, the picture, the 2D panel following, Clear. Different from
the table below: there was no ligand or find menu, so the rows are in
Display > Zoom; the position of the walk is kept with the session (the key
of 28b), which also makes it the session's own; the site is every residue
within 4 A; the contacts object is `ligand_contacts`, or
`ligand_contacts_01` when the user has one of that name. Left out: Undo of
a step, the light theme, step 31's catalog (not built).

**Move to the next ligand, show it with its protein polar contacts and zoom
to its binding site. Previous moves back through the same list.**

## Reuse and boundary

`modules/pymol/util.py:ligand_zoom(step=1)` is bound to Ctrl+L in
`shortcut_dict.py`: it sorts `organic` residues by object/segment/chain/residue
and zooms, without changing their display or making contacts.
`modules/pymol/ligand2d.py:ligands` finds candidates for the 2D panel without
requiring rdkit for discovery. `preset.ligands` already builds polar contacts
with `distance(..., mode=2)`, but applying that whole preset would restyle
the protein. Share discovery/identity where appropriate; do not duplicate a
second residue walker or invoke the whole preset.

Proposed command: `ligand_next [selection [, step]]`, defaults `enabled, 1`;
`ligand_next enabled, -1` is Previous. Register in `api.py`, `keywords.py`,
completion/help and step 31's catalog. This adds behavior without changing
the existing `util.ligand_zoom` callable.

| Part | Behavior |
| --- | --- |
| Candidates | Visible/enabled molecular objects, organic non-polymer residues using the shared 2D-panel criteria. Deterministic order and wraparound; preserve current identity through list changes. An explicit selection can include a peptide/cofactor excluded by the default. Show residue name, object, chain and residue number. |
| Display | New ball-and-stick for the selected ligand (step 34), nearby protein residues as sticks if needed to make contacts legible, protein cartoon/colors otherwise preserved. Do not disable other loaded objects or recolor the protein. |
| Contacts | Protein–ligand polar contacts using the existing distance mode and thresholds, labelled as geometric polar contacts, not experimentally established bonds. Restrict the default host to the ligand's object; an explicitly supplied selection may include a separate protein object. Do not silently include contacts to unrelated overlaid structures. |
| Zoom | Whole ligand plus its immediate site, using the existing zoom buffer behavior. No ligand gives one status message and leaves view/selection/display unchanged. |
| Ownership | One uniquely named, reused temporary contact object; retain its identity, never delete a user's same-named object. Advancing replaces only the navigation contacts and cleans up only temporary display changes owned by this workflow. Preserve later user edits; if ownership cannot be established, leave them alone. |
| State | Current state determines contacts. Recompute on navigation; deletion, rename, hide/show and state changes invalidate cached candidates/results. Per-session navigation state, not a process-global cursor shared by independent instances. |
| 2D/table | An open 2D panel follows the selected ligand without reopening it. Navigation does not change object ratings or table filters. |
| UI | Next ligand / Previous ligand in the existing ligand/find menu, available from keyboard; no extra toolbar icon is needed. Clear contacts is available beside them. |

Question 58: **keep Ctrl+L for zoom-only and offer an assignable shortcut
for the new action (recommended)**, or replace Ctrl+L with the richer action
and keep zoom-only in the menu/command. Check the existing key map before
choosing a default; do not assume Ctrl+Shift+L is free.

## Slice and check

36a delivers the command, menus, shortcut choice, owned contacts and help in
one feature slice. Files: `util.py` or a focused command module,
`ligand2d.py` only for shared discovery, `menu.py`, `shortcut_dict.py`,
`api.py`, `keywords.py`, `completing.py`, `ligand_panel.py` integration.

Add `testing/tests/api/ligand_navigation.py`: no ligand; one and several
ligands; wrap and reverse; same residue numbers in different objects;
disabled/deleted/currently renamed ligand; changed state; no polar contacts;
protein in a separate selected object; pre-existing user contacts with the
same proposed name. Assert the chosen ligand, endpoints, zoom target and
preserved protein colors/settings. Check navigation and cleanup in a real
window, with and without the 2D panel; Undo restores the previous visit under
the existing snapshot limits. Measure a many-ligand case before adding caches.

An `X` version and `ChangeLog` entry; no new chemistry dependency. Skipped:
rescoring, docking, automatic protonation and a new interaction classifier.
