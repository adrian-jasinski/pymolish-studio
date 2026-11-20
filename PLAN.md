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
| 1 | **15c** — [ChimeraX colors](docs/plans/15-presets.md) | One more palette: tan, sky blue, plum, light green, salmon, ... | The palette is in the toolbar menu and in the palette test. |
| 1 | **20** — [Toolbar look, two follow-ups](docs/plans/20-toolbar-look.md) | Blue hover in every menu of the program (one rule in `pymol.sty`). Orient acts only on what is visible, like Zoom. | Both looked at in the real window. |
| 1 | **1b** — [Idle threads sleep](docs/plans/01-performance-gpu.md) | `OMP_WAIT_POLICY=passive` is set at start unless the user set one. | CPU time of a 1aon surface before and after; wall time not worse. |
| 2 | **15e** — [Five effects](docs/plans/15-presets.md) | Color steps in the viewport; fog toward a white background; helices as cylinders; ambient occlusion in the soft look (timed on a large surface first); a "balls in glass" preset. | Each has a check in the preset tests and a picture. |
| 3 | **19** — [Movie timeline](docs/plans/19-movie-timeline.md) | The shot list goes into the session file. The 58 Program rows of the Movie menu go. Dragging on the strip. The keyframe strip of the core (19g) stays for now. | A session with a shot list loads here with the list and loads in 4.19.x without it; the menu test. |
| 4 | **21f** — [Three rendering details](docs/plans/21-commercial-features.md) | `sphere_mode` is capped at 9, its test and two reference images go. The background image is stored inside the session file. Smooth edges in the viewport with an FXAA shader. | Each old test passes or is deleted with its item. |
| 5 | **15b** — [Outline in the viewport](docs/plans/15-presets.md) | An edge pass over the drawn picture for the looks figure, soft, flat, comic and sketch. The line is black on a light background and light on a dark one. It is the same kind of pass as FXAA, so it comes right after it. | Frame time before and after; pictures on black and on white. |
| 6 | **1b** — [Surface on a worker thread](docs/plans/01-performance-gpu.md) | A large surface is built off the GUI thread: the window stays usable, the status line says it is being built, the surface appears when ready. Headless runs still wait. | 1aon and 4v6x in the real window; the suite and the sanitizer job. |
| 7 | **1b** — [Grid surface, an experiment](docs/plans/01-performance-gpu.md) | A second `surface_type`: signed distance grid and marching cubes. Times and pictures of 1aon and 4v6x against today's surface; then the user decides whether it stays. | The table and the pictures. |
| any time | **1b** — [Other measured items](docs/plans/01-performance-gpu.md) | The triangulation, a third of a surface build and one thread. Draw cost of sticks and lines as triangles on every driver: both need frame times on a quiet machine, the second also on Windows and macOS drivers. | Each change has before and after numbers. |
| any time | **3** — [Modern workspace and metadata](docs/plans/03-modern-ui.md) | Rows moved by dragging, a picked atom selects its row, sequence viewer text and scene buttons still drawn by the core, spacing of the remaining dialogs. | Each increment ships in a reviewable test build. |
| any time | **8** — [Modern C++ in the core](docs/plans/08-cpp-modernization.md) | No rewrite. One idiom per PR behind sanitizers and tests; vendored C stays; files go in profile order so cleanup and step 1 meet. Open: 8c (started: seven buffers of `Executive.cpp` in 4.19.39; next `Selector.cpp`, `ObjectMolecule.cpp`, `Ray.cpp`, `RepSurface.cpp`), 8d to 8g, the about 80 string calls through a pointer of 8b. Many PRs, no date. | Each slice passes the suite, the sanitizer job, `compare.py` and a PSE round trip. |
| waits | **21g** — [Undo of more than the last move](docs/plans/21-commercial-features.md) | Question 17 has no answer yet. With the last slice of step 21 the error "only in Incentive PyMOL", the test mark `incentive` and the option `-n` go. | The old undo tests pass, then the `incentive` mark comes off. |

The order is by size and by what is seen first: three one-line changes, then
presets, the timeline, the rendering details, and the two large pieces of 1b
last. Order 4 and 5 share their shader pass. 5c (release builds without
GitHub Actions) left the table: the builds stay on GitHub for now. GPU
compute is not on the critical path.

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

| # | Decision | Where it is described | What it holds up |
| --- | --- | --- | --- |
| 3 | The icon and the logo: under which license do they ship? MIT like the new code (recommended: one rule for everything this project added), or no license, all rights with you? Who made them is answered. | [09-icons-logo.md](docs/plans/09-icons-logo.md), `docs/licenses.md` | One cell of the license list; no code |
| 17 | 21g: undo by snapshots for edits plus the coordinate ring for moves (C, recommended), or coordinates only, as today, for now? | [21-commercial-features.md](docs/plans/21-commercial-features.md), 21g | 21g, and the end of step 21 |

Answered on 2026-11-20, see "Decided by the user" in
[PLAN-DONE.md](PLAN-DONE.md): 1, 4, 5, 6, 7, 13, 15, 16, 18, 19.

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
