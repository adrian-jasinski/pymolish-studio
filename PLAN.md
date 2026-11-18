# pymolish-studio — reviewed roadmap

First reviewed 2026-11-08 against revision `3250e7a3`. Checked again 2026-11-16
at 4.12.6 (`f30d3525`) against the code, the detailed plans and the git log; the
user's decisions of that day are applied (4.12.8 to 4.13.0) and listed in
[PLAN-DONE.md](PLAN-DONE.md). Extended 2026-11-18 at 4.14.4 (`6125122a`) with
the request of that day: 15g, 15h and steps 16 to 19, all planned, none built.

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
| 5 | **1b** — [Performance and GPU](docs/plans/01-performance-gpu.md) | Renderer default on WSL, draw cost of sticks and surfaces, the two triangulation passes. One measured bottleneck per change. | Each change has before and after numbers. |
| 5 | **3** — [Modern workspace and metadata](docs/plans/03-modern-ui.md) | Rows moved by dragging, a picked atom selects its row, sequence viewer text and scene buttons still drawn by the core, spacing of the remaining dialogs. The removal of the old C++ panel moved to step 17 and the timeline to step 19; dialog sizes and the scroll bar of the sequence viewer shipped as step 18. | Each increment ships in a reviewable test build. |
| none | **8** — [Modern C++ in the core](docs/plans/08-cpp-modernization.md) | No rewrite. One idiom per PR behind sanitizers and tests; vendored C stays; files go in profile order so cleanup and step 1 meet. Next: 8c to 8g. Many PRs, no date. | Each slice passes the suite, the sanitizer job, `bench.py` and a PSE round trip. |
| none | **5c** — [Release builds without GitHub Actions](docs/plans/05-builds-binaries.md) | A proposal of 2026-11-16 inside finished step 5: Linux in podman, Windows on the host, macOS not possible off Apple hardware. Nothing is built yet. | The user accepts or drops the proposal. |
| none | **15** — [Presets and looks](docs/plans/15-presets.md) | 15b: the outline of the looks in the viewport (today only in ray-traced images). 15c: ChimeraX object colors as a palette. 15e: five more effects, tried and described. 15a (ordered menu, solvent row, glass, looks) shipped in 4.14.0, 15d (cartoon everywhere, ligand balls and sticks, cartoon transparency, comic and sketch) in 4.14.3, 15f (wire, illustration, shades of one color) in 4.14.4. 15g and 15h (one list, looks keep the background, working presets keep the protein colors) in 4.14.5. | The user picks or drops 15b, 15c and each effect of 15e. |
| none | **17** — [Legacy menu rows and the old internal GUI](docs/plans/17-legacy-ui.md) | 17a (the legacy menu rows) shipped in 4.16.0, 17b (the last Tk stand-ins and the Legacy Plugins menu) in 4.16.1. 17c (the C++ code of the panel, 2,694 lines) in 4.17.1. Open: 17d, the panel list, after step 19d; 17e, the menus the core draws in OpenGL. | 17d and 17e each pass the suite, the sanitizer job and a PSE round trip. |
| none | **19** — [Movie timeline](docs/plans/19-movie-timeline.md) | Built in 4.18.0: the Timeline panel with a shot list, a strip, record, tours, fades, easing and export with an estimate, on a new module `pymol.shots`. Open: keeping the shot list in the session file, a shorter Movie menu, removal of the core's movie panel (19g), dragging on the strip. | The user answers the three questions; 19g passes the suite and the sanitizer job. |

Steps 8, 5c, 15, 17 and 19 never got an order number. Steps 16 (4.15.0) and
18 (4.15.1, 4.17.0) shipped and moved to [PLAN-DONE.md](PLAN-DONE.md). Suggested order for the
request of 2026-11-18, smallest and most visible first: 15g with 15h, 16,
18a, 17a with 17b, 18b, 19a to 19c, then the removals 17c, 19d, 17d, 17e. GPU compute is not on the critical
path. What needs the user's answer first is in "Waiting for the user", not
repeated in this table.

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
| 1 | On WSL, should the app select the `d3d12` driver itself? Frames go from 50 to 120 ms down to 0.7 to 11 ms; lines are then 1 pixel wide, so `trilines` goes on with it and mesh lines stay thin. | [01-performance-gpu.md](docs/plans/01-performance-gpu.md), Status 2026-11-14 | The first open item of 1b |
| 3 | Rights line for the icon and the logo: who made them, which license. | [09-icons-logo.md](docs/plans/09-icons-logo.md), `docs/licenses.md` | A complete license list; no code |
| 4 | 5c: build the Linux and Windows bundles on the development machine, or stay with GitHub Actions now that the failing test is fixed (4.12.7)? | [05-builds-binaries.md](docs/plans/05-builds-binaries.md), 5c | 5c |
| 5 | 15b: draw the black outline of the looks figure, soft, flat, comic and sketch in the viewport too? It needs a new edge pass in the shaders; today the outline appears only in ray-traced images. The preset illustration depends on it most: without the outline the viewport shows only flat blue shapes. | [15-presets.md](docs/plans/15-presets.md), Slices | 15b |
| 6 | 15c: add ChimeraX's object colors (tan, sky blue, plum, ...) as one more palette? | [15-presets.md](docs/plans/15-presets.md), Slices | 15c, one line |
| 7 | 15e: which of the five effects to build: color steps in the viewport, fog toward a white background, helices as cylinders, ambient occlusion in the soft look, a "balls in glass" preset? | [15-presets.md](docs/plans/15-presets.md), 15e | 15e |
| 13 | 19: keep the shot list after a restart, as a new entry in the session file (recommended: yes; it changes PSE output)? Remove the 58 Program rows of the Movie menu that Add and Tour replace (recommended: yes)? Remove the keyframe strip the core draws under the viewport (recommended: not yet)? | [19-movie-timeline.md](docs/plans/19-movie-timeline.md), Options and Questions | 19 |
| 14 | 17e: remove the menus the core draws in OpenGL (969 lines)? Since the window shows Qt menus, only a program that embeds the viewport through `pymol2` without the window still gets them. Recommended: yes, if no such program is in use. | [17-legacy-ui.md](docs/plans/17-legacy-ui.md), 17e and question 4 | 17e |
| 15 | 20: blue hover in every menu of the program, not only in the toolbar's (recommended: yes)? Icons 20 px with line width 2 and regular text as built, or one of the other options? | [20-toolbar-look.md](docs/plans/20-toolbar-look.md), Options and Questions | Two lines |

The user's to do, not decisions:

- `master` on GitHub has everything up to 4.14.4 (pull requests 5 to 7,
  merged 2026-11-16). The checks marked "first CI run" can now be looked at:
  the icon of the Windows program, the release notes, the `chem` and `fix`
  extras on three systems.
- Take the line `set internal_gui_width, 400` out of `~/.pymolrc`: since
  4.17.1 it prints "unknown Setting" at every start.
- Remove the pymolish plugin from `~/.pymol/startup`: it still wins over the
  native commands.
- Look at the Windows artifact after the merge.

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
