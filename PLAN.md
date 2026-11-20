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
Then the user answered questions 20 to 32 (answers in the table and in the
plans). Built on them: the version rule (step 29, done, in `AGENTS.md` §5)
and, as 4.20.0, the first under that rule, 26a with two more changes to the
bar: "Bg" with a paint roller, Builder and Scenes as icons, "Draw" for
"Draw/Ray".
Then all of order 1, 4.21.0 to 4.25.0: the Open button (26b), the palette
`chimerax` (15c), blue hover in every menu and Orient on what is visible
(step 20, finished), sleeping idle threads (1b), rename on the row of the
Objects panel (23a), and the scene buttons of the core deleted (17f). The
table below starts again at order 1.
Then 4.26.0 to 4.29.0: the packed session file `.psex` (28a), the property
table with editing, import and export (22a to 22c), and a fix in the core
(a property set again with another type ended the program). 4.30.0: the
quick-select chips and the final layout of the bar; step 26 is finished.
4.31.0: the UI scale from 50 to 300 %, live on Linux. 4.32.0 and 4.33.0:
the ligand in 2D, as a command and as a panel.

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
| 1 | **28b** — [One session key for new data](docs/plans/28-session-format.md) | 28a, the packed `.psex` file, shipped in 4.26.0. Left: one key `pymolish` in the session for everything new (table columns, shot list), with unknown entries kept. Built with its first user (22d or step 19), not ahead. | An entry of a "newer" version survives load and save; PyMOL 3 loads the `.pse` written with the key. |
| 2 | **22d, 22e** — [Property table, the rest](docs/plans/22-property-table.md) | 22a to 22c shipped in 4.27.0 to 4.29.0: the window, editing, columns, copy and paste, import from CSV and Excel, export. Left: 22d, column order and hidden columns kept in the session (with 28b), computed columns (atoms, residues, chains, states, weight, charge), a Columns menu, "follow" (the current row is the only object shown), the window's size between sessions; 22e, a picked atom selects its row. | Each slice has its test. |
| 3 | **27c** — [UI scale, Windows and macOS](docs/plans/27-ui-scale.md) | 27a and 27b shipped in 4.31.0: any percent from 50 to 300, live on Linux. Left: see in the first CI run whether the live change works on Windows and macOS (the test prints it); where it does not, restart in place or the "next start" message stays. | The CI log of both systems. |
| 4 | **24c** — [Ligand in 2D, the rest](docs/plans/24-ligand-2d.md) | 24a and 24b shipped in 4.32.0 and 4.33.0: the command `ligand_2d` and the panel with clicks both ways. Left: the contour around the pocket, grey halos on ligand atoms open to the solvent, metal contacts, the contacts as dashes in the viewport, the distance in a tooltip, Tab through the residues. | A picture next to the reference; the dashes go when the panel closes. |
| 5 | **15e, 25b-2** — [Five effects](docs/plans/15-presets.md), [color themes](docs/plans/25-studio-effects.md) | 15e as decided: color steps in the viewport; fog toward a white background; helices as cylinders; ambient occlusion in the soft look (timed on a large surface first); "balls in glass". With them five color themes (clay, blue, sage, mint, night): protein color, ligand color, background, as a group of their own. | Each has a check in the preset tests and a picture. |
| 6 | **1b** — [Grid surface, an experiment](docs/plans/01-performance-gpu.md) | A second `surface_type`: signed distance grid and marching cubes, with a smoothness value. Times and pictures of 1aon and 4v6x against today's surface, at two smoothness values; then the user decides whether it stays. Moved up: the surface looks wait for it. | The table and the pictures. |
| 7 | **25b** — [Surface looks and the blob](docs/plans/25-studio-effects.md) | Not planned in detail yet (answer to question 25): written again with the result of order 6. Until then no surface look and no new setting is added. The trial pictures (glossy, candy glass, clay, night) are in the plan. | A new plan section after order 6. |
| 8 | **25a** — [Floor, shadow, mirror, lights](docs/plans/25-studio-effects.md) | Command `stage`: a floor under the molecule with a shadow, a soft shadow, or a mirror image; three light setups. The shadow is ray traced only; the viewport shows the floor and the mirror. | The floor lies under every visible atom, `off` leaves nothing behind; ray times. |
| 9 | **19** — [Movie timeline](docs/plans/19-movie-timeline.md) | The shot list goes into the session file. The 58 Program rows of the Movie menu go. Dragging on the strip. The keyframe strip of the core (19g) stays for now. The list goes under the key of step 28. | A session with a shot list loads here with the list and loads in 4.19.x without it; the menu test. |
| 10 | **21f** — [Three rendering details](docs/plans/21-commercial-features.md) | `sphere_mode` is capped at 9, its test and two reference images go. The background image is stored inside the session file. Smooth edges in the viewport with an FXAA shader. The picture is stored in the setting, as decided. | Each old test passes or is deleted with its item. |
| 11 | **15b** — [Outline in the viewport](docs/plans/15-presets.md) | An edge pass over the drawn picture for the looks figure, soft, flat, comic and sketch. The line is black on a light background and light on a dark one. It is the same kind of pass as FXAA, so it comes right after it. | Frame time before and after; pictures on black and on white. |
| 12 | **1b** — [Surface on a worker thread](docs/plans/01-performance-gpu.md) | A large surface is built off the GUI thread: the window stays usable, the status line says it is being built, the surface appears when ready. Headless runs still wait. | 1aon and 4v6x in the real window; the suite and the sanitizer job. |
| 13 | **21g** — [Undo of more than the last move](docs/plans/21-commercial-features.md) | Snapshots for commands that add, remove or edit; the existing coordinate ring for moves. Three slices: the stack with create, delete, remove and the builder's edits; Undo and Redo in the toolbar say what they will undo; the rest of the test list. After it the error "only in Incentive PyMOL", the test mark `incentive` and the option `-n` go. | The 26 undo tests and the three jira tests pass, then the `incentive` mark comes off. |
| any time | **1b** — [Other measured items](docs/plans/01-performance-gpu.md) | The triangulation, a third of a surface build and one thread. Draw cost of sticks and lines as triangles on every driver: both need frame times on a quiet machine, the second also on Windows and macOS drivers. | Each change has before and after numbers. |
| any time | **23b** — [Rows moved by dragging](docs/plans/23-rename-in-panel.md) | Reorder and regroup in the Objects panel with the mouse. Carried over from step 3. | The drop goes through a function a test calls. |
| any time | **8** — [Modern C++ in the core](docs/plans/08-cpp-modernization.md) | No rewrite. One idiom per PR behind sanitizers and tests; vendored C stays; files go in profile order so cleanup and step 1 meet. Open: 8c (started: seven buffers of `Executive.cpp` in 4.19.39; next `Selector.cpp`, `ObjectMolecule.cpp`, `Ray.cpp`, `RepSurface.cpp`), 8d to 8g, the about 80 string calls through a pointer of 8b. Many PRs, no date. | Each slice passes the suite, the sanitizer job, `compare.py` and a PSE round trip. |

The session key and the rest of the table come first, then the scale and
the 2D ligand. For surfaces the grid surface of 1b comes first (order 6);
the surface looks are planned with its result. The old order is kept
behind: timeline, rendering details, outline, the surface on a worker
thread, and undo, the largest, last. Orders 10 and 11 share their shader
pass. 5c (release builds without GitHub Actions) is shelved: the builds stay
on GitHub for now. GPU compute is not on the critical path.

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
- [ponytail](https://github.com/dietrichgebert/ponytail) is already the rule
  (`AGENTS.md` §1): each plan has a "Skipped" list and, where code goes away,
  a "Deleted" list. Nothing on a "Skipped" list is built without a new request.
- [caveman](https://github.com/JuliusBrussee/caveman) shortens replies only;
  optional. The larger saving is the narrow slice and a fresh session per slice.

## Waiting for the user

Nothing waits for an answer. Questions 20 to 32 were answered on
2026-11-20; the answers are under "Decided by the user" in
[PLAN-DONE.md](PLAN-DONE.md).

One answer was cut off: question 27 reads "paint roller icon. rest". The
paint roller is built; say if the rest of the sentence asked for more.

The user's to do, not decisions:

- Merge pull request 9 (`feature11`, 4.19.12 to 4.33.0). `master` on GitHub
  has everything up to 4.19.11 (pull request 8, merged 2026-11-19).
- The checks marked "first CI run" can be looked at: the icon of the Windows
  program, the release notes, the `chem` and `fix` extras on three systems.
  The Windows bundle starts again only from 4.19.30 on.
- Remove the pymolish plugin from `~/.pymol/startup` (still there on
  2026-11-19): it wins over the native commands.
- `plan_images/` (the pictures of the request of 2026-11-20) is ignored by
  git and is deleted when steps 22 to 28 are built. The plans name its
  files by path.

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
