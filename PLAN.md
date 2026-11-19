# pymolish-studio — reviewed roadmap

First reviewed 2026-11-08 against revision `3250e7a3`. Checked again 2026-11-16
at 4.12.6 (`f30d3525`) against the code, the detailed plans and the git log; the
user's decisions of that day are applied (4.12.8 to 4.13.0) and listed in
[PLAN-DONE.md](PLAN-DONE.md). Extended 2026-11-18 at 4.14.4 (`6125122a`) with
the request of that day: 15g, 15h and steps 16 to 19, all planned, none built.
Extended 2026-11-19 at 4.19.26 with step 21: the stubs of the commercial
build, removed or to rebuild. Checked again 2026-11-19 at 4.19.32: every
shipped milestone left the table below for [PLAN-DONE.md](PLAN-DONE.md); the
table lists only what is open. Same day, 4.19.33 to 4.19.37: 21a to 21e built.

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
| 5 | **1b** — [Performance and GPU](docs/plans/01-performance-gpu.md) | Large surfaces off the GUI thread (waits for the user). The triangulation, a third of a surface build since the profile of 2026-11-19 and one thread. Draw cost of sticks and lines as triangles on every driver: both need frame times on a quiet machine, the second also on Windows and macOS drivers. One measured bottleneck per change. | Each change has before and after numbers. |
| 5 | **3** — [Modern workspace and metadata](docs/plans/03-modern-ui.md) | Rows moved by dragging, a picked atom selects its row, sequence viewer text and scene buttons still drawn by the core, spacing of the remaining dialogs. | Each increment ships in a reviewable test build. |
| none | **8** — [Modern C++ in the core](docs/plans/08-cpp-modernization.md) | No rewrite. One idiom per PR behind sanitizers and tests; vendored C stays; files go in profile order so cleanup and step 1 meet. Open: 8c (started: seven buffers of `Executive.cpp` in 4.19.39; next `Selector.cpp`, `ObjectMolecule.cpp`, `Ray.cpp`, `RepSurface.cpp`), 8d to 8g, the about 80 string calls through a pointer of 8b. Many PRs, no date. | Each slice passes the suite, the sanitizer job, `compare.py` and a PSE round trip. |
| none | **5c** — [Release builds without GitHub Actions](docs/plans/05-builds-binaries.md) | A proposal of 2026-11-16 inside finished step 5: Linux in podman, Windows on the host, macOS not possible off Apple hardware. Nothing is built. | The user accepts or drops the proposal. |
| none | **15** — [Presets and looks](docs/plans/15-presets.md) | 15b: the outline of the looks in the viewport (today only in ray-traced images). 15c: ChimeraX object colors as a palette. 15e: five more effects, tried and described. | The user picks or drops 15b, 15c and each effect of 15e. |
| none | **17** — [Legacy menu rows and the old internal GUI](docs/plans/17-legacy-ui.md) | 17d: the panel list, after 19g. 17e: the menus the core draws in OpenGL (969 lines). | 17d and 17e each pass the suite, the sanitizer job and a PSE round trip. |
| none | **19** — [Movie timeline](docs/plans/19-movie-timeline.md) | The shot list in the session file, a shorter Movie menu, removal of the core's movie panel (19g), dragging on the strip. | The user answers the three questions; 19g passes the suite and the sanitizer job. |
| none | **21** — [Features of the commercial build](docs/plans/21-commercial-features.md) | 21f: three rendering details (smooth edges in the viewport, sphere modes 10 and 11, the background image in the session file). 21g: undo of more than the last move. Both wait for an answer. With the last of them the error "only in Incentive PyMOL", the test mark `incentive` and the option `-n` go. | Each slice makes its old test pass under `pymolish -ckqyn`, then the `incentive` mark comes off. |

Steps 8, 5c, 15, 17, 19 and 21 never got an order number. What can be built
without an answer: 8c to 8g, and the items of 1b that are not the surface
thread, each on a quiet machine. Everything else
in the table waits for an answer in "Waiting for the user": 1b's surface
thread (1), 5c (4), 15 (5 to 7), 19 (13), 17d behind 19g, 17e (14), 21f (16),
21g (17). GPU compute is not on the critical path.

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
| 1 | A large surface freezes the window while it builds (4v6x 30 s, 1aon 5 s). Build it on a worker thread (A, recommended), make large surfaces coarser (B), or only announce the build in the status line (C)? | [01-performance-gpu.md](docs/plans/01-performance-gpu.md), Status 2026-11-19 | The next item of 1b |
| 3 | Rights line for the icon and the logo: who made them, which license. | [09-icons-logo.md](docs/plans/09-icons-logo.md), `docs/licenses.md` | A complete license list; no code |
| 4 | 5c: build the Linux and Windows bundles on the development machine, or stay with GitHub Actions now that the failing test is fixed (4.12.7)? | [05-builds-binaries.md](docs/plans/05-builds-binaries.md), 5c | 5c |
| 5 | 15b: draw the black outline of the looks figure, soft, flat, comic and sketch in the viewport too? It needs a new edge pass in the shaders; today the outline appears only in ray-traced images. The preset illustration depends on it most: without the outline the viewport shows only flat blue shapes. | [15-presets.md](docs/plans/15-presets.md), Slices | 15b |
| 6 | 15c: add ChimeraX's object colors (tan, sky blue, plum, ...) as one more palette? | [15-presets.md](docs/plans/15-presets.md), Slices | 15c, one line |
| 7 | 15e: which of the five effects to build: color steps in the viewport, fog toward a white background, helices as cylinders, ambient occlusion in the soft look, a "balls in glass" preset? | [15-presets.md](docs/plans/15-presets.md), 15e | 15e |
| 13 | 19: keep the shot list after a restart, as a new entry in the session file (recommended: yes; it changes PSE output)? Remove the 58 Program rows of the Movie menu that Add and Tour replace (recommended: yes)? Remove the keyframe strip the core draws under the viewport (recommended: not yet)? | [19-movie-timeline.md](docs/plans/19-movie-timeline.md), Options and Questions | 19 |
| 14 | 17e: remove the menus the core draws in OpenGL (969 lines)? Since the window shows Qt menus, only a program that embeds the viewport through `pymol2` without the window still gets them. Recommended: yes, if no such program is in use. | [17-legacy-ui.md](docs/plans/17-legacy-ui.md), 17e and question 4 | 17e |
| 15 | 20: blue hover in every menu of the program, not only in the toolbar's (recommended: yes)? Should Orient act only on what is visible, like Zoom since 4.19.1 (recommended: yes)? | [20-toolbar-look.md](docs/plans/20-toolbar-look.md), Options and Questions | Two lines |
| 16 | 21f: which rendering details, and how? Smooth edges in the viewport: FXAA shader (recommended), multisampling, or leave. Sphere modes 10 and 11 (cubes, tetrahedra): build, or cap the setting at 9 (recommended). Background image stored inside the session file (recommended; it changes what a PSE contains), or leave. | [21-commercial-features.md](docs/plans/21-commercial-features.md), 21f | 21f |
| 17 | 21g: undo by snapshots for edits plus the coordinate ring for moves (C, recommended), or coordinates only, as today, for now? | [21-commercial-features.md](docs/plans/21-commercial-features.md), 21g | 21g |

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
