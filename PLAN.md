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

**State 2026-11-20 at 4.43.0.** Built since 4.19.43, each with its test and
a look in the real window, all listed in [PLAN-DONE.md](PLAN-DONE.md):

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

Of the ten requested features, nine have a working version. The tenth, the
surface looks, waits for the grid surface of 1b, as decided. Steps 20, 26,
29 and 32 are finished.

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
| 5 | **15e** — [Five effects](docs/plans/15-presets.md) | As decided: color steps in the viewport; fog toward a white background; helices as cylinders; ambient occlusion in the soft look (timed on a large surface first); "balls in glass". The color themes that were to come with them shipped in 4.35.0. | Each has a check in the preset tests and a picture. |
| 6 | **1b** — [Grid surface, an experiment](docs/plans/01-performance-gpu.md) | A second `surface_type`: signed distance grid and marching cubes, with a smoothness value. Times and pictures of 1aon and 4v6x against today's surface, at two smoothness values; then the user decides whether it stays. Moved up: the surface looks wait for it. | The table and the pictures. |
| 7 | **25b** — [Surface looks and the blob](docs/plans/25-studio-effects.md) | Not planned in detail yet (answer to question 25): written again with the result of order 6. Until then no surface look and no new setting is added. The trial pictures (glossy, candy glass, clay, night) are in the plan. | A new plan section after order 6. |
| 8 | **19** — [Movie timeline](docs/plans/19-movie-timeline.md) | The shot list goes into the session file. The 58 Program rows of the Movie menu go. Dragging on the strip. The keyframe strip of the core (19g) stays for now. The list goes under the key of step 28. | A session with a shot list loads here with the list and loads in 4.19.x without it; the menu test. |
| 9 | **21f** — [Three rendering details](docs/plans/21-commercial-features.md) | `sphere_mode` is capped at 9, its test and two reference images go. The background image is stored inside the session file. Smooth edges in the viewport with an FXAA shader. The picture is stored in the setting, as decided. | Each old test passes or is deleted with its item. |
| 10 | **15b** — [Outline in the viewport](docs/plans/15-presets.md) | An edge pass over the drawn picture for the looks figure, soft, flat, comic and sketch. The line is black on a light background and light on a dark one. It is the same kind of pass as FXAA, so it comes right after it. | Frame time before and after; pictures on black and on white. |
| 11 | **1b** — [Surface on a worker thread](docs/plans/01-performance-gpu.md) | A large surface is built off the GUI thread: the window stays usable, the status line says it is being built, the surface appears when ready. Headless runs still wait. | 1aon and 4v6x in the real window; the suite and the sanitizer job. |
| 12 | **21g** — [Undo of more than the last move](docs/plans/21-commercial-features.md) | A first piece shipped in 4.40.0 (30f): a row of the preset menu is undone and redone through a snapshot of the whole session, five steps. Left, all of the plan: snapshots for commands that add, remove or edit; the existing coordinate ring for moves. Three slices: the stack with create, delete, remove and the builder's edits; Undo and Redo in the toolbar say what they will undo; the rest of the test list. After it the error "only in Incentive PyMOL", the test mark `incentive` and the option `-n` go. | The 26 undo tests and the three jira tests pass, then the `incentive` mark comes off. |
| any time | **1b** — [Other measured items](docs/plans/01-performance-gpu.md) | The triangulation, a third of a surface build and one thread. Draw cost of sticks and lines as triangles on every driver: both need frame times on a quiet machine, the second also on Windows and macOS drivers. | Each change has before and after numbers. |
| any time | **23b** — [Rows moved by dragging](docs/plans/23-rename-in-panel.md) | Reorder and regroup in the Objects panel with the mouse. Carried over from step 3. | The drop goes through a function a test calls. |
| any time | **8** — [Modern C++ in the core](docs/plans/08-cpp-modernization.md) | No rewrite. One idiom per PR behind sanitizers and tests; vendored C stays; files go in profile order so cleanup and step 1 meet. Open: 8c (started: seven buffers of `Executive.cpp` in 4.19.39; next `Selector.cpp`, `ObjectMolecule.cpp`, `Ray.cpp`, `RepSurface.cpp`), 8d to 8g, the about 80 string calls through a pointer of 8b. Many PRs, no date. | Each slice passes the suite, the sanitizer job, `compare.py` and a PSE round trip. |
| after the answers | **31** — [AI agents: Claude and ChatGPT drive the program](docs/plans/31-ai-agents.md) | Request of 2026-11-20, planned the same day, nothing built. Four slices. 31a: the tools (run commands, the scene, a picture of the viewport, a table of atoms, help), a connector that listens on this machine only, behind a token, off until it is turned on, and an icon in the action toolbar. 31b: "Connect Claude Code" and "Connect ChatGPT and Codex" in one click. 31c: a built-in assistant in the command area, with an API key. 31d: Sign in with ChatGPT. There is no login for a Claude subscription inside the program: Anthropic does not allow it, so that route is the connector. Waits for questions 41 to 48; 31a needs 41, 43, 45 and 46. | Each slice has its test and a look in the real window. In 31a Claude Code and Codex each make one figure of 1OKY through the connector. |

The session key and the rest of the table come first, then the scale and
the 2D ligand. For surfaces the grid surface of 1b comes first (order 6);
the surface looks are planned with its result. The old order is kept
behind: timeline, rendering details, outline, the surface on a worker
thread, and undo, the largest, last. Orders 9 and 10 share their shader
pass. 5c (release builds without GitHub Actions) is shelved: the builds stay
on GitHub for now. GPU compute is not on the critical path.

Step 31, the AI agents, has no number in the order yet: it is built when
its questions are answered, its first slice before the rest.

The icon of 31a has no room in the bar as it is. Measured at 4.43.0 and
150 %: the bar needs 1236 px and the window opens 1244 px wide; a 1920 px
screen has 1280. The Movie button took 41 px, so one more icon needs about
1285 px (estimate). 31a decides what gives way.

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

Eight questions are open, all for step 31, further down.

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

Eight questions are for step 31, the AI agents
([plan](docs/plans/31-ai-agents.md), with the reasons). Nothing of it is
built. The last column is the recommended answer.

| No. | Question | Recommended |
| --- | --- | --- |
| 41 | Which routes: the connector only (the agent runs in the user's Claude or ChatGPT program); the connector, then an assistant built into the window; also an assistant through `claude -p` and `codex exec`? | The connector, then the built-in assistant. The third is a grey area of Anthropic's rules. |
| 42 | A new dependency: the official `anthropic` and `openai` packages as an optional extra `ai` for the built-in assistant, or the standard library only? | The official packages, once their size in a bundle is measured. |
| 43 | What an agent may run by default: commands only, with a switch for Python and files; or everything? | Commands only. |
| 44 | Where the built-in assistant lives: in the command area (a command `ask`, answers in the log), or in a panel of its own? | The command area. |
| 45 | The icon (`bot`, `sparkle`, `message-circle`) and the name ("Assistant", "AI", "Agent"). | `bot`, "AI assistant" on mouse-over, the commands `agent` and `ask`. |
| 46 | "Native build option": always built in and off until used, or also a build flag that leaves it out? | Always built in. |
| 47 | "Connect" rows for Claude Code and for Codex with the ChatGPT desktop app; also for the chat tab of Claude Desktop, which needs a helper program? | The first two; the chat tab as a slice 31e if wanted. |
| 48 | A key or a token is kept in a file only the user can read, or in the keychain of the system (`keyring`, a new dependency)? | The file. |

One answer was cut off: question 27 reads "paint roller icon. rest". The
paint roller is built; say if the rest of the sentence asked for more.

Small things that were left out on the way and are built only if asked for:
shortcuts for the UI scale (Ctrl+=, Ctrl+-, Ctrl+0) and the option
`--ui-scale`; the five themes as palettes and backgrounds of their own; the
table window's size between sessions (it is part of 22d); from step 30,
the tones of the 2D picture in a PNG written by `ligand_2d` (rdkit draws
it), and glycerol and other additives sorted out of the 2D panel's list of
ligands.

The user's to do, not decisions:

- Push `feature12` and open a pull request. The branch is local only: 40
  commits after `master` on GitHub, 4.20.0 to 4.43.0 (counted 2026-11-20).
  Pull request 10 was merged on 2026-11-20; `master` on GitHub is at
  4.19.43.
- The checks marked "first CI run" can be looked at once the branch is
  pushed: the icon of the Windows program, the release notes, the `chem` and
  `fix` extras on three systems, and new with 4.31.0: whether the live UI
  scale works on Windows and macOS (the test `test_scale_range_and_live`
  prints it; step 27c).
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
