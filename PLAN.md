# pymolish-studio — reviewed roadmap

First reviewed 2026-11-08 against revision `3250e7a3`. Checked again 2026-11-16
at 4.12.6 (`f30d3525`) against the code, the detailed plans and the git log; the
user's decisions of that day are applied (4.12.8 to 4.13.0) and listed in
[PLAN-DONE.md](PLAN-DONE.md). Extended 2026-11-18 at 4.14.4 (`6125122a`) with
the request of that day: 15g, 15h and steps 16 to 19, all planned, none built.
Extended 2026-11-19 at 4.19.26 with step 21: the stubs of the commercial
build, removed or to rebuild. Checked again 2026-11-19 at 4.19.32: every
shipped milestone left the table below for [PLAN-DONE.md](PLAN-DONE.md); the
table lists only what is open. Same day, 4.19.33 to 4.19.40: 21a to 21e built,
two slices of step 8 (the last dead product macros, 8c in `Executive.cpp`), one
change of 1b after a new profile of the surface build.
2026-11-20, 4.19.42: step 17 finished (17d, 17e); a web search for 1b added
questions 18 and 19.
Same day: the user answered questions 1, 3 to 7, 13, 15, 16, 18 and 19. The
answers are in the table below and in the detailed plans; none of that work is
built yet.
Then 3 (the icon and logo got a notice of their own, 4.19.43) and 17 (undo).
Extended the same day at 4.19.43 with a second request of ten features,
steps 22 to 29. Step 3 was closed: the property table of step 22 replaces
its metadata table. Where a new plan contradicted an old decision the new
one won; the old decisions that fell are listed in
[PLAN-DONE.md](PLAN-DONE.md). The user answered questions 20 to 32 the same
day.
Extended once more that day at 4.35.0 with a third request, eight repairs
after a first look at the program: step 30, built the same day in 4.36.0 to
4.40.0 and finished.
And a fourth request that day, at 4.40.0: step 31, the program works with
the AI agents of Anthropic and OpenAI. Planned, not built; questions 41
to 48.
A fifth, small one: 11b, a palette from the user's brand colors, planned
at 4.39.0 and built in 4.41.0 as `halo`.
A sixth, at 4.41.0: step 32, icons in the row under the object list and a
Movie button in the action toolbar. Planned, answered and built the same
day in 4.42.0 and 4.43.0, and finished.

Extended 2026-11-23 at 4.43.0 from eleven new drafts: repairs 24d and
27d; Stars 22f; CPK 11c; new steps 33–36; a rewrite of the unbuilt AI plan
31. **This is planning only: no feature shipped, no new version, no GUI or
performance result is claimed.** Recommendations awaiting a choice are
listed under “Waiting for the user”.

**Shipped state, checked 2026-11-23: still 4.43.0.** Built since 4.19.43,
with the tests and GUI checks recorded in [PLAN-DONE.md](PLAN-DONE.md):

| Version | What |
| --- | --- |
| 4.20.0 to 4.21.0 | The version rule (step 29). The bar: "Bg", icons, "Draw", the Open button. |
| 4.22.0 to 4.25.0 | Palette `chimerax`, blue hover in every menu, Orient on what is visible, sleeping idle threads, rename on the row, the scene buttons of the core deleted. |
| 4.26.0 | The packed session file `.psex`. |
| 4.27.0 to 4.29.0 | The property table: window, editing, import and export. A fix in the core. |
| 4.30.0 to 4.31.0 | Quick-select chips; UI scale from 50 to 300 %, live. |
| 4.32.0 to 4.35.0 | The ligand in 2D (command and panel), `stage` with floor, shadow and mirror, five color themes. |
| 4.36.0 to 4.40.0 | Step 30: the 2D picture with circles, tones and a larger legend; the table's alignment and icon; the live UI scale with sharp icons; the preset menu with three submenus, and no preset colors a cartoon or a surface; a clean row for crystallization additives; Undo and Redo for a row of the preset menu. |
| 4.41.0 | Palette `halo` (11b): five colors of a brand book and seven added ones. |
| 4.42.0 to 4.43.0 | Step 32: an icon on each of the four buttons under the object list; a Movie button in the action toolbar that opens and closes the Timeline panel. |

Of the ten features requested on 2026-11-20, nine have a working version.
The tenth, the surface looks, waits for the grid surface of 1b. Steps 20, 26,
29 and 32 are finished.

**Keep Qt Widgets with PySide6, simplify the supported product, measure performance,
modernize the existing window, and deliver downloadable builds early.** Changing
bindings does not move molecular computation to the GPU. Follow
[AGENTS.md](AGENTS.md): smaller, faster, simpler, prettier.

Finished steps are in [PLAN-DONE.md](PLAN-DONE.md), and so are the shipped
milestones of the steps that are still open. A step moves there when its last
milestone ships; its detailed plan stays in `docs/plans/`.

## Open work, in execution order

The order below prioritizes reported breakage, then the requested workflows,
then the earlier rendering work. Step numbers identify detailed plans; slice
letters remain stable. No release dates are promised. Each slice is a separate
implementation task/PR, with an `X` feature or `Y` fix version under `AGENTS.md`.
Questions gate the dependent slice, not unrelated repairs.

| Order | Step | What is left | Exit condition |
| --- | --- | --- | --- |
| 1 | **27d, then 27c** — [Scale freeze](docs/plans/27-ui-scale.md) | Reproduce the reported 150 → 120 freeze; inspect live scaling and ordinary resize paths. Repair the demonstrated cause, or use the accepted next-start fallback before an unsafe live path. Verify Windows/macOS as well as the reported platform. | A subprocess timeout/heartbeat regression and real GUI repaint/input checks; unsupported live scaling is reported distinctly. |
| 2 | **24d** — [Resizable ligand 2D](docs/plans/24-ligand-2d.md) | Fix dock/floating-window resizing and fit the complete SVG/legend to the available area; keep picking aligned after scale changes. | Shrink/grow repeatedly, docked/floating, crowded ligand, fractional DPI; no crop, freeze or stale click coordinates. |
| 3 | **35a** — [One-click scenes](docs/plans/35-scene-appearance.md) | Click or Enter recalls once; rename, drag, right click and list refresh do not trigger recall. | Interaction tests and a real mouse check. |
| 4 | **28b + 22d, 22e** — [Session key](docs/plans/28-session-format.md) and [remaining table work](docs/plans/22-property-table.md) | Build the shared `pymolish` key with its first consumer: column order/hidden/empty columns. Computed columns, Columns menu, follow mode, remembered window size and picked-atom row selection remain. | Unknown session entries survive; table layout reloads; computed values and selection checked. No unused persistence framework built ahead. |
| 5 | **22f** — [Stars](docs/plans/22-property-table.md) | Three outline/filled stars for a 0–3 integer object property, mouse and keyboard editing, sorting and numeric import/export. Independent of 28b. | All ratings/clicks, invalid values, sorted row identity and session/CSV round trips. |
| 6 | **35b** — [Scene appearance](docs/plans/35-scene-appearance.md) | Store cartoon type, relevant visual settings at their actual scopes, representation color overrides and referenced custom colors; recall through panel, command and movies. | Store A, apply preset/color B, recall A and B; settings and images match, including reload, without restoring/deleting molecular data. |
| 7 | **34a, 34b** — [Independent ball-and-stick](docs/plans/34-ball-and-stick.md) | A new representation with its own visibility, colors, ball scale (default 0.31), bond radius and single/double/triple/aromatic display; S/H/C, commands, ray, picking, sessions and scene integration. | Changing it preserves line/stick/sphere settings and colors; renderer, old/new session and scene checks pass. |
| 8 | **34c** — [Ligand preset defaults](docs/plans/34-ball-and-stick.md) | Use the new model for visible ligands in all applicable molecular presets, including pretty/publication/glass; preserve protein colors and existing hidden sphere/stick overrides. | Preset matrix on protein/ligand/water/ion; A/B scene recall and Undo. Depends on 34a/b and 35b. |
| 9 | **11c** — [CPK / residue-color choice](docs/plans/11-color-palettes.md) | Resolve “CPK by residues”; recommended CPK element colors within selected residues, including a ball-and-stick-only target. | Documented scheme, menu/command equivalence, target isolation and scene round trip. |
| 10 | **36a** — [Next ligand with contacts](docs/plans/36-ligand-navigation.md) | Next/Previous ligand, protein polar contacts and site zoom; shared discovery, owned temporary contacts and an assignable shortcut. | Wrap/reverse, absent/deleted ligands, host selection, cleanup and unchanged protein colors. |
| 11 | **33a–33c** — [Sequence alignment window](docs/plans/33-sequence-window.md) | Separate resizable window, linked 2D/3D selection and secondary structure, sequence alignment, pairwise/multiple-structure fitting, FASTA and genuine MSA with the chosen backend. | Residue/gap mapping, unchanged coordinates for sequence-only work, fit statistics/Undo, MSA and session/export checks. |
| 12 | **31a, 31c, then 31b** — [Chat and agent tools](docs/plans/31-ai-agents.md) | Built-in chat is required; live discovery of this fork's public commands/settings/presets, actual results/errors, cancellation and reviewed execution. External connector reuses it. Questions 41–48 resolve route/UI/dependencies; optional subscription login 31d is only an investigation. | Catalog coverage and provider stand-ins; live fork-specific workflows with each chosen provider. No promise of login entitlement. Can start independently of steps 33–36. |
| 13 | **24c** — [Remaining 2D contacts](docs/plans/24-ligand-2d.md) | Pocket contour, solvent halos, metal contacts, viewport dashes, distance tooltips and Tab through residues. | Reference picture, keyboard check, owned dashes removed on close. |
| 14 | **15e** — [Five effects](docs/plans/15-presets.md) | Color steps, fog toward white, cylindrical helices, measured ambient occlusion in soft look, balls in glass. Color themes already shipped in 4.35.0. | Preset checks and images; scenes preserve the added visual settings. |
| 15 | **1b** — [Grid surface experiment](docs/plans/01-performance-gpu.md) | Signed distance grid/marching cubes as a second surface type and a smoothness value. Compare 1aon and 4v6x at two values; user judges the experiment. | Actual times and pictures against today's surface. |
| 16 | **25b** — [Surface looks and blob](docs/plans/25-studio-effects.md) | Replan using the grid-surface result from order 15; no new surface-look setting before that. | New detailed section grounded in the experiment. |
| 17 | **19** — [Movie timeline](docs/plans/19-movie-timeline.md) | Persist the shot list under step 28's key; remove 58 Program rows; dragging on the strip. Core keyframe strip stays. Exercise step 35's style recall in playback. | Shot-list session compatibility, menu and playback tests. |
| 18 | **21f** — [Rendering details](docs/plans/21-commercial-features.md) | Cap sphere mode at 9 with its obsolete test/images removed; store background image in its setting; FXAA. | Checks per slice and viewport images. |
| 19 | **15b** — [Viewport outline](docs/plans/15-presets.md) | Edge pass for figure/soft/flat/comic/sketch, contrasting with the background. Follows FXAA's pass. | Frame times and pictures on black/white. |
| 20 | **1b** — [Surface worker](docs/plans/01-performance-gpu.md) | Build large surfaces off the GUI thread with status; headless commands still wait. | Real-window responsiveness, suite and sanitizer checks. |
| 21 | **21g** — [General undo](docs/plans/21-commercial-features.md) | Extend the existing preset snapshots to add/remove/edit commands, retain coordinate ring; toolbar labels and remaining tests. Remove incentive error/mark and `-n` afterwards. | Existing undo/jira cases pass before their marks are removed. |
| any time | **1b** — [Other measured items](docs/plans/01-performance-gpu.md) | The triangulation, a third of a surface build and one thread. Draw cost of sticks and lines as triangles on every driver: both need frame times on a quiet machine, the second also on Windows and macOS drivers. | Each change has before and after numbers. |
| any time | **23b** — [Rows moved by dragging](docs/plans/23-rename-in-panel.md) | Reorder and regroup in the Objects panel with the mouse. Carried over from step 3. | The drop goes through a function a test calls. |
| any time | **8** — [Modern C++ in the core](docs/plans/08-cpp-modernization.md) | No rewrite. One idiom per PR behind sanitizers and tests; vendored C stays; files go in profile order so cleanup and step 1 meet. Open: 8c (started: seven buffers of `Executive.cpp` in 4.19.39; next `Selector.cpp`, `ObjectMolecule.cpp`, `Ray.cpp`, `RepSurface.cpp`), 8d to 8g, the about 80 string calls through a pointer of 8b. Many PRs, no date. | Each slice passes the suite, the sanitizer job, `compare.py` and a PSE round trip. |

The earlier surface dependencies are preserved: grid experiment before surface
looks; FXAA before outline. New scene storage precedes the ligand preset
switch; the new representation and color isolation precede ligand navigation.
The alignment-engine and AI dependencies are explicit decisions, not already
approved additions. 5c stays shelved; builds stay on GitHub Actions.

The toolbar baseline remains the measurement from 4.43.0 at 150 %: 1236 px
of content, a 1244 px window. No new button width was measured in this run;
steps 31 and 33 must check space before adding or repurposing controls.

## Coverage of the 2026-11-23 drafts and superseded decisions

| Draft | Plan | Earlier decision reconciled |
| --- | --- | --- |
| 1 — ligand image/panel does not fit | 24d | The existing resize path needs a regression fix despite 24b/30a's earlier successful pictures. |
| 2 — sequence window, alignments, secondary structure | 33a–33c | Replaces “sequence viewer stays as it is” in steps 3/22; retains the current strip during delivery. Additional first options: search, linked selection, consensus, identity, export and fit statistics. |
| 3 — independent ball-and-stick | 34a/b | The existing preset is not a separate representation; shared sphere/stick settings no longer satisfy this request. |
| 4 — default ligand representation in presets | 34c / 15 | Supersedes the old 0.18/0.13 ligand recipe and exclusion of pretty/publication/glass. |
| 5 — CPK by residues | 11c | Distinguishes element CPK from amino-acid-type colors; question 56 stays open. |
| 6 — scenes preserve preset style and colors | 35b | Extends existing scene color/visibility storage to the visual state it currently lacks; does not turn recall into full-session rollback. |
| 7 — one-click scene switching | 35a / 3 | Replaces Enter/double-click-only recall; keyboard and rename/reorder remain. |
| 8 — freeze on 150 → 120 | 27d, then 27c | Reliability must be established before claiming live scale support; the accepted next-start fallback remains. |
| 9 — three stars in the property table | 22f | Promotes the explicitly deferred `stars` idea into requested work. |
| 10 — next ligand with protein contacts and zoom | 36a | Adds a workflow beyond Ctrl+L's existing zoom-only helper; shortcut choice is open. |
| 11 — chat control, aware of the fork | 31 | Already planned, unbuilt; now in-app chat plus a live capability catalog is required, not just an external connector. |

## Validation of the original draft

Rows that still steer an open step. The rows about finished steps are in
[PLAN-DONE.md](PLAN-DONE.md).

| Original idea or claim | Verdict and correction |
| --- | --- |
| Require a Core profile during binding cleanup | **Reject as an early change.** `Scene.cpp` and `Ortho.cpp` still use fixed-function calls. Audit and migrate required rendering paths separately. |
| Enable OpenMP by default | **Already largely true.** `setup.py` defaults it on outside macOS. Marching cubes uses it; `Ray.cpp` has its own workers. Check races and oversubscription before adding parallelism. |
| Move PDB/mmCIF parsing from Python to C++ | **Correct the premise.** Native readers already exist in `ObjectMolecule.cpp`, `ObjectMolecule2.cpp`, and `CifMoleculeReader.cpp`. Profile the actual load path. |
| GPU ray tracing and marching cubes are next | **Defer.** OpenGL 4.3 compute cannot be the common requirement for native macOS OpenGL. Step 1 gives the platform constraint and experiment gate. |
| Replace the whole window beside the old one | **Prefer incremental changes.** Two windows duplicate command, dialog, plugin, and lifecycle integration. Extract only the panel being implemented. |
| Object and sequence panels can simply become docks | **Underestimated.** Existing internal controls involve C++ drawing; a Qt replacement needs separate behavior and performance checks. The Objects panel was rebuilt in Qt in 4.5.11; the sequence viewer is still drawn by the core. |
| Test PRs only on Linux/Python 3.12 | **Reject for this migration.** Preserve three-OS coverage; optimize caching and artifact jobs first. Python is 3.13 and 3.14 only, in CI and in `pyproject.toml` (decided 2026-11-16, 4.12.8; the draft said 3.11–3.14). |
| Replace GLEW, collapse directories, cap setup.py at 300 lines | **Skip without evidence.** These can add coupling and churn without improving a measured workflow. |

Evidence and implementation boundaries are linked in each step. “Keep” means a
recommended direction, not a claim that an implementation has passed tests.

## Working rules

- One slice per session and per PR. Each plan names the files and lines to
  open, so a session starts there instead of exploring again.
- Version numbers: `AGENTS.md` §5 (rule of 2026-11-20). A commit that only
  changes plans, docs, CI or tests takes no version.
- This file and `PLAN-DONE.md` are brought up to date at the end of every
  run that ships a feature: `AGENTS.md` §5.
- [ponytail](https://github.com/dietrichgebert/ponytail) is already the rule
  (`AGENTS.md` §1): each plan has a "Skipped" list and, where code goes away,
  a "Deleted" list. Nothing on a "Skipped" list is built without a new request.
- [caveman](https://github.com/JuliusBrussee/caveman) shortens replies only;
  optional. The larger saving is the narrow slice and a fresh session per slice.

## Waiting for the user

Open choices are listed below, with recommendations. The new drafts request
all eleven outcomes; these questions refine behavior, not whether to plan
them. No unanswered recommendation is recorded as the user's decision.
Questions 53, 54 and 56 clarify the resize control, sequence inputs and CPK;
their interpretations remain provisional.

Questions 49 to 52 (step 32) were answered on 2026-11-20 and built the
same day in 4.42.0 and 4.43.0; the answers are under "Decided by the
user" in [PLAN-DONE.md](PLAN-DONE.md). One thing came with the answer to
51 without being asked: the "movie" rows of the menus show the video
camera too, so that a movie has one icon, and the clapperboard file is
deleted. Say so if the menus should get the clapperboard back.

Questions 33 to 35 (11b, the palette from the brand colors) got one
answer on 2026-11-20, "add this to code", without a choice. So the
recommended options were built in 4.41.0: the name `halo`, the twelve
colors with the five of the brand book as published, and the brand not
named. Say so if another name or the dark version is wanted: it is one
entry of data.

Questions 20 to 32 were answered on 2026-11-20; the
answers, with the version each one shipped in, are under "Decided by the
user" in [PLAN-DONE.md](PLAN-DONE.md).

Five more questions come from [step 30](docs/plans/30-polish.md). Each has
a built answer, so nothing waits for them; say so if another one is wanted.

| No. | Question | Built in 4.36.0 to 4.40.0 |
| --- | --- | --- |
| 36 | The icon of the Table button: `sheet`, `table` or `table-properties` of Lucide? | `sheet` |
| 37 | The color of the contact area in "protein-protein interaction": orange or white? | orange |
| 38 | "remove crystallization additives" also removes the sugars of glycosylation and NAD(P), as asked. One row, or rows of their own for sugars and cofactors? | one row |
| 39 | "Clean the preset menu": should presets leave it? Candidates: classified, ball and stick, b factor putty, five of the seven ligand sites rows. | none taken out |
| 40 | Undo of a preset takes back everything done after it (Redo brings it back) until 21g builds one stack. Good enough until then? | yes |

Step 31 is replanned in [the AI detail](docs/plans/31-ai-agents.md).
The previous questions retain their IDs, with updated choices:

| No. | Question | Recommendation |
| --- | --- | --- |
| 41 | Chat first or connector first? | Shared tools 31a, required chat 31c, then connector 31b. The new request settles that chat is required. |
| 42 | Optional official API SDKs or standard-library HTTP? | SDKs if measured bundle cost is acceptable; explicit dependency approval is still required. |
| 43 | Reviewed operations or unrestricted Python/files by default? | Reviewed operations; concrete confirmation for destructive/file/network actions, separate trusted Python mode. |
| 44 | Chat tab in command area or a separate dock? | Chat tab, distinct from command input, with history and Stop. |
| 45 | Assistant icon/name? | `bot`, “AI assistant”; alternative `message-circle`, “Chat”. Measure toolbar space first. |
| 46 | Present but off until used, or a build option to remove it? | Present but inactive. |
| 47 | Which external clients get setup helpers? | Installed Codex and Claude Code after actual compatibility checks; other clients separately. |
| 48 | Session/environment keys only or persistent credentials? | Session/environment first; persistent storage needs an OS-appropriate security design. |

Choices from the new drafts:

| No. | Question | Recommendation / alternatives |
| --- | --- | --- |
| 53 | Does 150 → 120 mean the toolbar UI-scale percentage or ordinary window resizing? | Provisionally UI scale; reproduce both paths until clarified. [27d](docs/plans/27-ui-scale.md). |
| 54 | Loaded structure chains only, or FASTA sequences too? | Loaded chains plus FASTA; loaded-only can be the first slice. Secondary structure means helix/sheet/coil from loaded coordinates, not predicted structure. [33](docs/plans/33-sequence-window.md). |
| 55 | Which true MSA engine? | Optional local MAFFT executable (dependency approval/packaging needed), or a larger native progressive aligner. Reference-based fits alone do not complete MSA. [33](docs/plans/33-sequence-window.md). |
| 56 | CPK element colors within residues, or one color per amino-acid type? | CPK by element within selected residues; otherwise name the action “By residue type”. [11c](docs/plans/11-color-palettes.md). |
| 57 | What does clicking star N do? | Empty sets rating N, filled sets N−1; alternative any empty/filled click adds/removes one. Both keep three outlines and a value 0–3. [22f](docs/plans/22-property-table.md). |
| 58 | Replace Ctrl+L or keep its zoom-only action? | Keep it; make Next ligand with contacts assignable and menu-accessible. Alternative: Ctrl+L becomes the richer workflow. [36](docs/plans/36-ligand-navigation.md). |
| 59 | Ball-and-stick bond colors? | Half-bonds follow endpoint ball colors; alternative uniform dark bonds with an independent override. [34](docs/plans/34-ball-and-stick.md). |
| 60 | How does SEQ open the new window? | Keep the strip toggle, add alignment window in its context menu and Display > Panels; alternative SEQ opens the new window and Display keeps the strip toggle. [33](docs/plans/33-sequence-window.md). |

One answer was cut off: question 27 reads "paint roller icon. rest". The
paint roller is built; say if the rest of the sentence asked for more.

Small things that were left out on the way and are built only if asked for:
shortcuts for the UI scale (Ctrl+=, Ctrl+-, Ctrl+0) and the option
`--ui-scale`; the five themes as palettes and backgrounds of their own; from step 30,
the tones of the 2D picture in a PNG written by `ligand_2d` (rdkit draws
it), and glycerol and other additives sorted out of the 2D panel's list of
ligands.

The user's to do, not decisions:

- Push the remaining `feature12` commits and check/open its pull request.
  Local git inspection on 2026-11-23 finds an `origin/feature12` tracking
  branch, so the previous “local only” statement is obsolete. Remote/PR
  status was not refreshed in this planning run; no push or merge is done.
- Review the available CI runs, then the run after the remaining commits
  are pushed: the Windows icon, release notes, `chem`/`fix` extras on three
  systems and live UI scaling. Current CI status was not checked here;
  the old scale test prints fallback status, and 27d/27c must distinguish
  that from working live scaling.
- Remove the pymolish plugin from `~/.pymol/startup` (still there on
  2026-11-20): it wins over the native commands.
- `plan_images/` (the pictures of the request of 2026-11-20) is ignored by
  git. It is deleted when the last plans made from it are built: 22d, 24c
  and 25b. The plans name its files by path.

Not the user's, and not a roadmap step: the screenshot in the README
(`docs/img/window.png`) shows the window of 4.19; it is retaken when the
bar has stopped changing.

## Shared completion criteria

- Preserve read/write PDB, mmCIF, SDF/MOL, PSE; PNG export; basic selection,
  representations, command entry, and supported plugin loading.
- Each non-trivial implementation change leaves a runnable check in
  `testing/tests/` or `layerCTest/`; removals run the full Python suite.
- Rendering/UI changes need real GUI and platform checks. Report skipped tests.
- Keep CI coverage, document public API changes in `ChangeLog`, and preserve
  `LICENSE`, `AUTHORS`, and copyright headers.
- New dependencies, data-file deletions, and file-format output changes follow
  the decisions required by `AGENTS.md` during implementation. These plans do not
  install, delete, or change them.
- Measure runtime, memory, artifact size, and build time before fixing hard
  targets. No speedup, binary size, or delivery date is promised by this draft.
