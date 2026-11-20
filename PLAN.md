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
Extended the same day at 4.19.43 with a second request of ten features:
steps 22 to 29, all planned, none built. Step 3 is closed: the property table
of step 22 replaces its metadata table. Where a new plan contradicts an old
decision the new one wins; the old decisions that fall are listed in
[PLAN-DONE.md](PLAN-DONE.md). Experiments were run for six of the plans and
their numbers and pictures are in the plan files.

**Keep Qt Widgets with PySide6, simplify the supported product, measure performance,
modernize the existing window, and deliver downloadable builds early.** Changing
bindings does not move molecular computation to the GPU. Follow
[AGENTS.md](AGENTS.md): smaller, faster, simpler, prettier.

Finished steps are in [PLAN-DONE.md](PLAN-DONE.md), and so are the shipped
milestones of the steps that are still open. A step moves there when its last
milestone ships; its detailed plan stays in `docs/plans/`.

## Open work, in execution order

One table: what is open, in the order to do it. The step numbers are the
user's original numbers; the letters are milestones of the detailed plans.

| Order | Step | What is left | Exit condition |
| --- | --- | --- | --- |
| 1 | **29** — [Version numbers](docs/plans/29-versioning.md) | A rule for the second and third number that does not hang on roadmap steps; the first stays 4. Waits for question 30. Then `AGENTS.md` §5 is rewritten; no number changes at that moment. | The rule is in `AGENTS.md`; the next feature takes the first number under it. |
| 1 | **26a** — [Bg](docs/plans/26-toolbar-buttons.md) | "Background" reads "Bg" and gets a better icon (question 27). | The toolbar test; a look in the real window. |
| 1 | **26b** — [Open button](docs/plans/26-toolbar-buttons.md) | A button before Residues: open file, open folder, recent, get by PDB code, by UniProt, predicted structure. All rows exist in File. | The toolbar test; reachable by keyboard. |
| 1 | **23a** — [Rename in the Objects panel](docs/plans/23-rename-in-panel.md) | F2 or "rename" edits the name on the row; the green line in the viewport is only the fallback without a window. | The panel test: Enter renames, Esc and a taken name do not. |
| 1 | **15c** — [ChimeraX colors](docs/plans/15-presets.md) | One more palette: tan, sky blue, plum, light green, salmon, ... | The palette is in the toolbar menu and in the palette test. |
| 1 | **20** — [Toolbar look, two follow-ups](docs/plans/20-toolbar-look.md) | Blue hover in every menu of the program (one rule in `pymol.sty`). Orient acts only on what is visible, like Zoom. | Both looked at in the real window. |
| 1 | **1b** — [Idle threads sleep](docs/plans/01-performance-gpu.md) | `OMP_WAIT_POLICY=passive` is set at start unless the user set one. | CPU time of a 1aon surface before and after; wall time not worse. |
| 2 | **28** — [Session file `.psex`](docs/plans/28-session-format.md) | The same content as a `.pse`, packed: 14 to 18 times smaller, saved faster. One key `pymolish` in the session for everything new (table columns, shot list). `.pse` stays for PyMOL. Waits for question 29. | Round trip test; PyMOL 3 loads the `.pse` written with the key. |
| 3 | **22** — [Property table](docs/plans/22-property-table.md) | A dock at the bottom: row number, a dot that shows or hides the object, name, one column per property. Cells edited in place, columns added by hand or from CSV and Excel, export to CSV. Five slices, 22a to 22e. Waits for questions 20 and 21. | Each slice has its test; 1,000 objects with 20 properties scroll and sort without a pause. |
| 4 | **26c, 26d** — [Quick select and the layout of the bar](docs/plans/26-toolbar-buttons.md) | Chips P, L, S, a menu with chains and more, All, none. With them the bar is too wide: one row with icons only, or two rows (question 26). | Each chip selects the atoms of its expression; no button starts in the overflow menu at 150 %. |
| 5 | **27** — [UI scale 50 to 300 %, live](docs/plans/27-ui-scale.md) | A field for any percent; the window changes at once (worked in a trial on Linux), "Keep this size?" with a revert, the old message where the live change cannot work. Windows and macOS to try in CI. Question 28. | The GUI test: 150, 100, 225, 150, the viewport still draws. |
| 6 | **24** — [Ligand in 2D with its contacts](docs/plans/24-ligand-2d.md) | Command `ligand_2d` and a panel: the ligand flat (rdkit), residues around it colored by kind, hydrogen bonds, salt bridges, ring stacking; a click selects in 3D. A toolbar button, off without a ligand. Three slices. Question 23. | On 2RH1 the known contacts are found and no two residues overlap. |
| 7 | **15e, 25b** — [Five effects](docs/plans/15-presets.md), [surface looks and themes](docs/plans/25-studio-effects.md) | 15e as decided: color steps in the viewport; fog toward a white background; helices as cylinders; ambient occlusion in the soft look (timed on a large surface first); "balls in glass". With them the looks glossy, candy glass and frosted, and five color themes (clay, blue, sage, mint, night). Question 25. | Each has a check in the preset tests and a picture. |
| 8 | **25a** — [Floor, shadow, mirror, lights](docs/plans/25-studio-effects.md) | Command `stage`: a floor under the molecule with a shadow (ray traced), a soft shadow, or a mirror image; three light setups. The clay blob (25b-3). Question 24. | The floor lies under every visible atom, `off` leaves nothing behind; ray times. |
| 9 | **19** — [Movie timeline](docs/plans/19-movie-timeline.md) | The shot list goes into the session file. The 58 Program rows of the Movie menu go. Dragging on the strip. The keyframe strip of the core (19g) stays for now. The list goes under the key of step 28. | A session with a shot list loads here with the list and loads in 4.19.x without it; the menu test. |
| 10 | **21f** — [Three rendering details](docs/plans/21-commercial-features.md) | `sphere_mode` is capped at 9, its test and two reference images go. The background image is stored inside the session file. Smooth edges in the viewport with an FXAA shader. As decided the picture is stored in the setting; the key of step 28 is a second place for it (question 29). | Each old test passes or is deleted with its item. |
| 11 | **15b** — [Outline in the viewport](docs/plans/15-presets.md) | An edge pass over the drawn picture for the looks figure, soft, flat, comic and sketch. The line is black on a light background and light on a dark one. It is the same kind of pass as FXAA, so it comes right after it. After it, if chosen, the shadow pass of 25a for the viewport. | Frame time before and after; pictures on black and on white. |
| 12 | **1b** — [Surface on a worker thread](docs/plans/01-performance-gpu.md) | A large surface is built off the GUI thread: the window stays usable, the status line says it is being built, the surface appears when ready. Headless runs still wait. | 1aon and 4v6x in the real window; the suite and the sanitizer job. |
| 13 | **1b** — [Grid surface, an experiment](docs/plans/01-performance-gpu.md) | A second `surface_type`: signed distance grid and marching cubes. Times and pictures of 1aon and 4v6x against today's surface; then the user decides whether it stays. With a smoothness value, it is also the blob surface of 25b. | The table and the pictures. |
| 14 | **21g** — [Undo of more than the last move](docs/plans/21-commercial-features.md) | Snapshots for commands that add, remove or edit; the existing coordinate ring for moves. Three slices: the stack with create, delete, remove and the builder's edits; Undo and Redo in the toolbar say what they will undo; the rest of the test list. After it the error "only in Incentive PyMOL", the test mark `incentive` and the option `-n` go. | The 26 undo tests and the three jira tests pass, then the `incentive` mark comes off. |
| any time | **1b** — [Other measured items](docs/plans/01-performance-gpu.md) | The triangulation, a third of a surface build and one thread. Draw cost of sticks and lines as triangles on every driver: both need frame times on a quiet machine, the second also on Windows and macOS drivers. | Each change has before and after numbers. |
| any time | **23b** — [Rows moved by dragging](docs/plans/23-rename-in-panel.md) | Reorder and regroup in the Objects panel with the mouse. Carried over from step 3. | The drop goes through a function a test calls. |
| any time | **8** — [Modern C++ in the core](docs/plans/08-cpp-modernization.md) | No rewrite. One idiom per PR behind sanitizers and tests; vendored C stays; files go in profile order so cleanup and step 1 meet. Open: 8c (started: seven buffers of `Executive.cpp` in 4.19.39; next `Selector.cpp`, `ObjectMolecule.cpp`, `Ray.cpp`, `RepSurface.cpp`), 8d to 8g, the about 80 string calls through a pointer of 8b. Many PRs, no date. | Each slice passes the suite, the sanitizer job, `compare.py` and a PSE round trip. |

The new requests go first where they are small or where others wait for
them: the version rule (every later change uses it), three small changes to
the bar and the panel, then the session file, because the table and the shot
list store into it. The table follows, then
the rest of the bar, the scale, the 2D ligand, and the looks. The old order
is kept behind them: timeline, rendering details, outline, the two large
pieces of 1b, and undo, the largest, last. Orders 10 and 11 share their
shader pass. 5c (release builds without GitHub Actions) is shelved: the
builds stay on GitHub for now. GPU compute is not on the critical path.

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
- [ponytail](https://github.com/dietrichgebert/ponytail) is already the rule
  (`AGENTS.md` §1): each plan has a "Skipped" list and, where code goes away,
  a "Deleted" list. Nothing on a "Skipped" list is built without a new request.
- [caveman](https://github.com/JuliusBrussee/caveman) shortens replies only;
  optional. The larger saving is the narrow slice and a fresh session per slice.

## Waiting for the user

Thirteen questions from the request of 2026-11-20 (second). Each has the
options in its plan; the recommendation is the first thing named here. Work
that does not depend on an answer goes on meanwhile.

| # | Question | Recommended | Plan |
| --- | --- | --- | --- |
| 20 | Where does the property table live? | A dock of its own at the bottom; the Objects panel stays. Not: the table replaces the panel. | [22](docs/plans/22-property-table.md) |
| 21 | Excel import: how? | Read `.xlsx` with the standard library (first sheet, values). Not: `openpyxl` as a new optional dependency; not: CSV only. | [22](docs/plans/22-property-table.md) |
| 22 | Rename: keep the old wizard for a viewport without a window? | Keep it as the fallback (41 lines). Not: delete it. | [23](docs/plans/23-rename-in-panel.md) |
| 23 | Ligand 2D: drawn by our own code, by PandaMap, or the plain rdkit recipe? | Own layout and painting on rdkit and Qt, about 300 lines, no new dependency. PandaMap would bring matplotlib and biopython. | [24](docs/plans/24-ligand-2d.md) |
| 24 | A shadow in the viewport, or only in ray-traced pictures? | Ray traced only at first; the viewport shows floor and mirror. A flat projected shadow as a second slice if that reads unfinished; a real shadow pass only after FXAA and the outline. | [25](docs/plans/25-studio-effects.md) |
| 25 | Surface looks: settings only, or new shader terms? And the blob: by a map now, or wait for the grid surface? | Settings only; the blob by a gaussian map now, as a surface type once the grid surface of 1b is judged. | [25](docs/plans/25-studio-effects.md) |
| 26 | The bar with all new buttons: one row or two? | One row, icons only except Residues and Presets (about 1140 to 1210 px at 150 %, today 1096). | [26](docs/plans/26-toolbar-buttons.md) |
| 27 | Which icon for Bg? | `paint-roller`. Others in the picture: `contrast`, `wallpaper`, `square-dashed`, `layers-2`. | [26](docs/plans/26-toolbar-buttons.md) |
| 28 | Live scale through a private function of Qt? | Yes, with today's "next start" message where it cannot work. Others: restart in place (loses log and undo); font-only zoom; restart as today. | [27](docs/plans/27-ui-scale.md) |
| 29 | A new session file type? And does a `.pse` from pymolish carry the new data? | `.psex` (same content, packed) as what Save Session writes; the `.pse` carries the new data too, PyMOL ignores it (measured). The request suggested leaving it out of the `.pse`: that is option B2. Also: should the background picture of 21f go under the new key instead of into its setting? | [28](docs/plans/28-session-format.md) |
| 30 | The version rule. | Second number: something a user can see shipped; third: everything else; no number for commits that change only plans, docs, CI or tests. Other: second number per release to `master`. | [29](docs/plans/29-versioning.md) |
| 31 | Two rows left over from step 3: the scene buttons the core draws in the viewport, and the sequence viewer's text. | Delete the scene buttons (the Scenes dock replaced them; a removal, so it needs a yes); leave the sequence viewer as it is. | [22](docs/plans/22-property-table.md) |
| 32 | Color themes set the protein color and the background, against 15g and 15h. | Yes, for the themes only, as a group of their own that says so. | [25](docs/plans/25-studio-effects.md) |

Questions up to 19 are answered; the answers are under "Decided by the
user" in [PLAN-DONE.md](PLAN-DONE.md).

The user's to do, not decisions:

- Merge pull request 9 (`feature11`, 4.19.12 and later). `master` on GitHub
  has everything up to 4.19.11 (pull request 8, merged 2026-11-19).
- The checks marked "first CI run" can be looked at: the icon of the Windows
  program, the release notes, the `chem` and `fix` extras on three systems.
  The Windows bundle starts again only from 4.19.30 on.
- Take the line `set internal_gui_width, 400` out of `~/.pymolrc` (line 12,
  still there on 2026-11-19): since 4.17.1 it prints "unknown Setting" at
  every start.
- Remove the pymolish plugin from `~/.pymol/startup` (still there on
  2026-11-19): it wins over the native commands.
- `plan_images/` (the pictures of the request, 7 MB) is not committed:
  screenshots of another product do not belong in the repository, and the
  `:Zone.Identifier` files in it break a checkout on Windows. The plans name
  the pictures by path; say if they should be committed or ignored
  (`.gitignore`).

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
