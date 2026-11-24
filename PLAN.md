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

Built the same day, 4.43.1 to 4.51.0: the first ten rows of the open-work
table of that morning (27d, 24d, 35a, 28b with 22d and 22e, 22f, 35b, 34a
and 34b, 34c, 11c, 36a). Steps 22, 28, 34, 35 and 36 are finished and step
11 is closed again; of step 27 the check on Windows and macOS (27c) is left.
Questions 57 to 59 were built with their recommended answers; five new
questions, 61 to 65, came out of the work.

**Shipped state, checked 2026-11-24: 4.60.0.** Built since 4.19.43,
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
| 4.43.1 to 4.43.2 | Two repairs: the UI scale waits for the next start on WSLg, where the rebuilt window came back late or not at all; the 2D picture of a ligand is no longer cut at one side. |
| 4.44.0 | One click recalls a scene. |
| 4.45.0 to 4.46.0 | The property table: columns kept in the session (the new session key `pymolish`), counted columns, Follow, the row of a picked atom, stars. |
| 4.47.0 | Scenes keep the style of presets and colorings. |
| 4.48.0 to 4.49.0 | The representation `ball_and_stick`; ligands drawn with it by the presets and when a structure is loaded. |
| 4.50.0 to 4.51.0 | `color_cpk`; `ligand_next`, the next ligand with its polar contacts. |
| 4.52.0 to 4.55.0 | Ball and stick in the S and H menus of the panel and under C > by rep; S > ball and stick holds only ball size and bond thickness; balls 0.25 of the atom radius by default (was 0.31); wire, sticks and nb_spheres taken out of S and H (the commands stay). |
| 4.56.0 | The ligand in 2D (24c): the pocket's outline, halos on atoms open to the solvent, metal contacts, Show in 3D, distances in tooltips, Tab through the residues. |
| 4.57.0 | Sequence window (33a–c): loaded chains and FASTA, local MAFFT, secondary structure, linked selection, fitting with Undo, statistics/export and session persistence. |
| 4.58.0 | AI chat (31a, 31c): a Chat tab beside the command line, `ask`, live discovery of commands/settings/presets, reviewed execution with confirmation, Stop and Undo; optional `ai` extra. Stand-in tests only, no live provider yet. |
| 4.58.1 | Ligand 2D: a ligand in an object of its own (extracted, docked) selects and zooms on its residues again. |
| 4.59.0 | Action toolbar: a Sequence alignment button, Zoom and Rock as menus like the others (Rock: rock, spin about X/Y/Z, random axis, stop), Bg and Draw icon only. |
| 4.60.0 | Sequence window: a Jalview-like consensus secondary-structure track (cylinders, arrows, numbered) and residue colors (Zappo, hydrophobicity, percent identity). |

Of the ten features requested on 2026-11-20, nine have a working version.
The tenth, the surface looks, waits for the grid surface of 1b. Steps 20, 26,
29 and 32 are finished. Of the eleven drafts of 2026-11-23, all eleven have a working version;
the chat (31a, 31c) shipped in 4.58.0, its external connector 31b is open.

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
| 1 | **27c** — [UI scale on Windows and macOS](docs/plans/27-ui-scale.md) | 27d shipped in 4.43.1: on WSLg the scale waits for the next start. Left: read what `test_scale_change_keeps_the_window_alive` prints in the Windows and macOS CI jobs (live, with the time until the window is back, or "unsupported"), and try the change once by hand on each. Question 61. | Both systems either change the scale in the running window within two seconds, or are added to `theme.live_scale_blocker`. |
| 2 | **31 trial, then 31b** — [Chat and agent tools](docs/plans/31-ai-agents.md) | 31a and 31c shipped in 4.58.0 (stand-in tests only). Left: the consented live trial with each provider (a ligand figure, ball-and-stick color only, a scene, a native fork command, an unavailable optional feature; commands, errors, time and tokens recorded); then the external connector 31b (questions 45, 47). Subscription login 31d is only an investigation. | Live trial recorded for Anthropic and OpenAI; connector tests against the installed clients. No promise of login entitlement. |
| 3 | **15e** — [Five effects](docs/plans/15-presets.md) | Color steps, fog toward white, cylindrical helices, measured ambient occlusion in soft look, balls in glass. Color themes already shipped in 4.35.0. | Preset checks and images; scenes preserve the added visual settings (add them to the list in `MovieScene.cpp`; the inventory test fails until then). |
| 4 | **1b** — [Grid surface experiment](docs/plans/01-performance-gpu.md) | Signed distance grid/marching cubes as a second surface type and a smoothness value. Compare 1aon and 4v6x at two values; user judges the experiment. | Actual times and pictures against today's surface. |
| 5 | **25b** — [Surface looks and blob](docs/plans/25-studio-effects.md) | Replan using the grid-surface result from order 4; no new surface-look setting before that. | New detailed section grounded in the experiment. |
| 6 | **19** — [Movie timeline](docs/plans/19-movie-timeline.md) | Persist the shot list under the session key `pymolish` (shipped with 28b in 4.45.0: `pymol.session_extra`); remove 58 Program rows; dragging on the strip. Core keyframe strip stays. Playback already recalls the style of scenes (35b, tested in 4.47.0). | Shot-list session compatibility, menu and playback tests. |
| 7 | **21f** — [Rendering details](docs/plans/21-commercial-features.md) | Cap sphere mode at 9 with its obsolete test/images removed; store background image in its setting; FXAA. | Checks per slice and viewport images. |
| 8 | **15b** — [Viewport outline](docs/plans/15-presets.md) | Edge pass for figure/soft/flat/comic/sketch, contrasting with the background. Follows FXAA's pass. | Frame times and pictures on black/white. |
| 9 | **1b** — [Surface worker](docs/plans/01-performance-gpu.md) | Build large surfaces off the GUI thread with status; headless commands still wait. | Real-window responsiveness, suite and sanitizer checks. |
| 10 | **21g** — [General undo](docs/plans/21-commercial-features.md) | Extend the existing preset snapshots to add/remove/edit commands, retain coordinate ring; toolbar labels and remaining tests. Remove incentive error/mark and `-n` afterwards. | Existing undo/jira cases pass before their marks are removed. |
| any time | **1b** — [Other measured items](docs/plans/01-performance-gpu.md) | The triangulation, a third of a surface build and one thread. Draw cost of sticks and lines as triangles on every driver: both need frame times on a quiet machine, the second also on Windows and macOS drivers. | Each change has before and after numbers. |
| any time | **23b** — [Rows moved by dragging](docs/plans/23-rename-in-panel.md) | Reorder and regroup in the Objects panel with the mouse. Carried over from step 3. | The drop goes through a function a test calls. |
| any time | **8** — [Modern C++ in the core](docs/plans/08-cpp-modernization.md) | No rewrite. One idiom per PR behind sanitizers and tests; vendored C stays; files go in profile order so cleanup and step 1 meet. Open: 8c (started: seven buffers of `Executive.cpp` in 4.19.39; next `Selector.cpp`, `ObjectMolecule.cpp`, `Ray.cpp`, `RepSurface.cpp`), 8d to 8g, the about 80 string calls through a pointer of 8b. Many PRs, no date. | Each slice passes the suite, the sanitizer job, `compare.py` and a PSE round trip. |

The earlier surface dependencies are preserved: grid experiment before surface
looks; FXAA before outline. The user approved optional local MAFFT and official OpenAI/Anthropic SDKs
on 2026-11-24; MAFFT remains separately installed, SDKs will be a lazy extra. 5c stays shelved; builds
stay on GitHub Actions.

The toolbar baseline remains the measurement from 4.43.0 at 150 %: 1236 px
of content, a 1244 px window. The versions up to 4.51.0 added no button to
the bar and did not measure it again; steps 31 and 33 must check space
before adding or repurposing controls.

## Coverage of the 2026-11-23 drafts and superseded decisions

| Draft | Plan | Earlier decision reconciled |
| --- | --- | --- |
| 1 — ligand image/panel does not fit | 24d, built in 4.43.2 | The existing resize path needs a regression fix despite 24b/30a's earlier successful pictures. |
| 2 — sequence window, alignments, secondary structure | 33a–33c | Replaces “sequence viewer stays as it is” in steps 3/22; retains the current strip during delivery. Loaded chains plus FASTA in the first release confirmed in answer 54. Additional options: search, linked selection, consensus, identity, export and fit statistics. |
| 3 — independent ball-and-stick | 34a/b, built in 4.48.0 | The existing preset is not a separate representation; shared sphere/stick settings no longer satisfy this request. |
| 4 — default ligand representation in presets | 34c / 15, built in 4.49.0 | Supersedes the old 0.18/0.13 ligand recipe and exclusion of pretty/publication/glass. |
| 5 — CPK by residues | 11c, built in 4.50.0 | Answer 56 confirms standard CPK atom colors within selected residues. |
| 6 — scenes preserve preset style and colors | 35b, built in 4.47.0 | Extends existing scene color/visibility storage to the visual state it currently lacks; does not turn recall into full-session rollback. |
| 7 — one-click scene switching | 35a / 3, built in 4.44.0 | Replaces Enter/double-click-only recall; keyboard and rename/reorder remain. |
| 8 — freeze on 150 → 120 | 27d, built in 4.43.1; 27c open | Answer 53 confirms toolbar UI scale at 150 % → 120 %. Reliability must be established before claiming live scale support; the accepted next-start fallback remains. |
| 9 — three stars in the property table | 22f, built in 4.46.0 | Promotes the explicitly deferred `stars` idea into requested work. |
| 10 — next ligand with protein contacts and zoom | 36a, built in 4.51.0 | Adds a workflow beyond Ctrl+L's existing zoom-only helper; shortcut choice is open. |
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

Open choices are listed below, with recommendations. No unanswered
recommendation is recorded as the user's decision.
Questions 53, 54 and 56 were answered on 2026-11-23; 55 and 42 on
2026-11-24. They no longer wait:

| No. | Confirmed decision | Plan |
| --- | --- | --- |
| 53 | The freeze occurs when changing toolbar UI scale from 150 % to 120 %. | [27d](docs/plans/27-ui-scale.md), built in 4.43.1 |
| 54 | The first sequence-window release includes loaded structure chains and FASTA import/alignment, with helix/sheet/coil for loaded structures. | [33](docs/plans/33-sequence-window.md), built in 4.57.0 |
| 56 | Standard CPK atom colors within selected residues. | [11c](docs/plans/11-color-palettes.md), built in 4.50.0 |

| 55 | Optional local MAFFT executable. | [33](docs/plans/33-sequence-window.md), built in 4.57.0 |
| 42 | Optional official OpenAI and Anthropic SDKs. | [31](docs/plans/31-ai-agents.md), built in 4.58.0 as the extra `ai` |

These decisions are also recorded in `PLAN-DONE.md`.

Five questions came out of the building of 4.43.1 to 4.51.0. Each has a
built answer, so nothing waits for them; say so if another one is wanted.
The first two touch what a session file contains, which `AGENTS.md` asks
to be agreed: they were built because the plans of steps 34 and 35 named
this layout, and they are one line each to take back.

| No. | Question | Built |
| --- | --- | --- |
| 61 | On WSLg a change of the UI scale left a dead window for 0.1 to 4.6 s, sometimes longer. Wait for the next start there, or keep the change in the running window and accept the gap? | The next start, with a message that says why (4.43.1). Other displays still change at once. |
| 62 | What may a session file hold that PyMOL does not know? | Three things, each read by this program and passed over by PyMOL 3.2.0a (tried): the key `pymolish` (table columns, the ligand walk), a seventh item in the record of a scene (its style), and the key `pymolish_unique_settings` (settings of atoms that PyMOL does not have; in its own list PyMOL ends when it saves them). A session without these features has none of the three. |
| 63 | Should a loaded structure open with its ligands as `ball_and_stick`, as the presets now draw them, or as sticks as before? | `ball_and_stick` (4.49.0): the same picture from a load and from a preset. One line in `Selector.cpp` to take back. |
| 64 | The colors of `color_cpk` are the CPK table of the RasMol manual as known; the manual could not be read in that run. Compare, or name another CPK table? | The table as written, 28 elements; only the color for other elements, FF1493, was confirmed against a source (4.50.0). |
| 65 | Since one click recalls a scene, a scene is picked for Update, Rename and Delete with a right click or the arrow keys. Enough, or a menu on the row? | Right click and arrow keys (4.44.0). |

Built with the recommended answer, without an answer from the user; say so
if the other one is wanted:

| No. | Question | Built |
| --- | --- | --- |
| 57 | What does clicking star N do? | An empty star rates up to it, a filled one down to the one before (4.46.0). The other reading: any click adds or removes one. |
| 58 | Replace Ctrl+L or keep its zoom-only action? | Kept; `ligand_next` has Ctrl+Shift+M and Ctrl+Shift+H, changeable in the shortcut editor, and three rows in Display > Zoom (4.51.0). |
| 59 | Ball-and-stick bond colors? | Each half of a bond in the color of its atom's ball (4.48.0). The other: uniform dark bonds with a color of their own. |

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
Questions 41, 43, 44, 46 and 48 were built in 4.58.0 with the
recommendation below; say so if another one is wanted. 45 and 47 still
wait: no toolbar button was added, and the connector is not built.

| No. | Question | Recommendation |
| --- | --- | --- |
| 41 | Chat first or connector first? | Shared tools 31a, required chat 31c, then connector 31b. The new request settles that chat is required. |
| 43 | Reviewed operations or unrestricted Python/files by default? | Reviewed operations; concrete confirmation for destructive/file/network actions, separate trusted Python mode. |
| 44 | Chat tab in command area or a separate dock? | Chat tab, distinct from command input, with history and Stop. |
| 45 | Assistant icon/name? | `bot`, “AI assistant”; alternative `message-circle`, “Chat”. Measure toolbar space first. |
| 46 | Present but off until used, or a build option to remove it? | Present but inactive. |
| 47 | Which external clients get setup helpers? | Installed Codex and Claude Code after actual compatibility checks; other clients separately. |
| 48 | Session/environment keys only or persistent credentials? | Session/environment first; persistent storage needs an OS-appropriate security design. |

Remaining choices from the new drafts:

| No. | Question | Recommendation / alternatives |
| --- | --- | --- |
| 60 | How does SEQ open the new window? | Built with the recommendation in 4.57.0: SEQ keeps the strip toggle, with the alignment window in its context menu and Display > Panels. |

One answer was cut off: question 27 reads "paint roller icon. rest". The
paint roller is built; say if the rest of the sentence asked for more.

Small things that were left out on the way and are built only if asked for:
shortcuts for the UI scale (Ctrl+=, Ctrl+-, Ctrl+0) and the option
`--ui-scale`; the five themes as palettes and backgrounds of their own; from step 30,
the tones of the 2D picture in a PNG written by `ligand_2d` (rdkit draws
it), and glycerol and other additives sorted out of the 2D panel's list of
ligands. From 4.43.1 to 4.51.0: sequence length as a counted column of the
table, and a header "Stars" in place of the property's name "stars";
transparency and quality settings of its own for `ball_and_stick`, and a
bond color of its own; `ball_and_stick` for ligands in the presets "simple"
and "default"; settings of single states and the secondary structure in a
scene; Undo of a step of `ligand_next`.

The user's to do, not decisions:

- Push the remaining `feature12` commits and check/open its pull request.
  The sequence feature is commit `f25db6d3` on `feature12`, the chat 4.58.0
  follows it. No push or
  merge was performed in this run; PR status was not inspected.
- Review the available CI runs, then the run after the remaining commits
  are pushed: the Windows icon, release notes, `chem`/`fix` extras on three
  systems. For 27c read the line that
  `test_scale_change_keeps_the_window_alive` prints in the Windows and
  macOS jobs: "live ... shown after" with a time, or "unsupported on ...".
  Remote runs checked 2026-11-24: latest successful master run
  [44750297890](https://github.com/adrian-jasinski/pymolish-studio/actions/runs/44750297890)
  is at `d40f09f6`, before the scale repair. It cannot verify the current
  Windows/macOS behavior. Native MAFFT launch also needs those systems.
  The sequence feature has 21 passing focused tests and a Linux/WSLg
  window check; no native Windows/macOS result is claimed.
- Try the Chat tab with your own Anthropic and OpenAI keys and a model
  ID each (`pip install 'pymolish[ai]'`); no live request was sent in
  the 4.58.0 run.
- Compare `palettes.CPK` (`modules/pymol/palettes.py`) with the "CPK
  Colours" table of the RasMol manual (question 64).
- Look at one thing that went wrong in the run of 2026-11-23: a helper of
  the freeze test sent Ctrl+A, "120", Enter once, at about 10:06, to
  whatever window had the focus on the Windows desktop. The working tree
  was unchanged; an editor or a terminal that had the focus may show it.
- Remove the pymolish plugin from `~/.pymol/startup` (still there on
  2026-11-20): it wins over the native commands.
- `plan_images/` (the pictures of the request of 2026-11-20) is ignored by
  git. It is deleted when the last plan made from it is built: 25b
  (22d and 24c are built). The plans name its files by path.

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
