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

Built 2026-11-24, 4.60.1 to 4.65.0, from the request "continue with the
open tasks, take the recommended option where a question has no answer":
the repair of Rock > Random, 31b (the agent connector and its toolbar
button), 15e, the three parts that were left of step 19, and the three
items of 21f. Steps 19 and 31b are finished; of step 21 only 21g is left.
Every question that had no answer is decided as recommended and left this
file for [PLAN-DONE.md](PLAN-DONE.md). Not built in that run, and why:
27c and the live trial of step 31 need things this machine does not have
(Windows and macOS runs of the pushed code; API keys; Codex credits); the
grid surface, the outline, the surface worker and general undo are each a
slice of their own.

Built 2026-11-24, 4.66.0, from the request "authorize via web browser, not
by providing model ID and API key (as an alternative)": 31d, the sign-in
of the Chat tab with a ChatGPT plan or with OpenRouter. The user chose both
of these and "Stay signed in" as a box (questions 74 and 75). A Claude
subscription cannot be signed in to from pymolish: Anthropic's terms do not
allow it. Not tried with a real account: that is part of order 10.

Built 2026-11-24, 4.67.0, from the request "move the robot icon into the
row under the object list, after SEQ; give SEQ a tab between Command and
Chat that works like the sequence in the viewport; the viewport stays as
the second place": the Sequence tab, and the AI assistant button in that
row. It is not a step of this plan; it is recorded with steps 32 and 33,
which stay finished. Five choices were made while building (81 to 85).

Built 2026-11-24, 4.68.0, from the request "connect to Claude and ChatGPT
through the session in my browser; add OAuth verification": the provider
"Claude Code" of the Chat tab. ChatGPT had its sign-in since 4.66.0. For
Claude the rule of Anthropic was read again that day and still holds: no
Claude.ai sign-in inside another program. What it leaves open was built:
the Claude Code installed on the computer runs the conversation and holds
the sign-in, which its own "auth login" makes in the browser. It belongs
to step 31 (31d). Five choices were made while building (86 to 90).

Extended 2026-11-24 at 4.68.0 with the File > Get by UniProt error and
the requested Objects, palette, Sequence and font controls: step 37 below,
plus the existing drag-and-drop slice 23b promoted into execution order.
Planning only; nothing shipped or measured in the GUI in this update.
The palette sizes below are requested targets. Choices 91 to 97 are open.

**Shipped state, checked 2026-11-24: 4.68.0.** Built since 4.19.43,
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
| 4.60.1 | Rock > Random keeps turning: by a random 15 to 180 degrees about one axis, then about another one, until Stop (it stopped after the second turn). |
| 4.61.0 | Agent connector (31b): `agent_server on` serves the reviewed operations of the Chat tab to Claude Code or Codex on this computer, over MCP on 127.0.0.1 with a token. An AI assistant button in the toolbar: Chat, the connector on and off, a setup line to copy. |
| 4.62.0 | 15e: the presets "balls in glass" and "cartoon cylinders", a fog row in the light menu, shade in the pockets of a surface in the look "soft". |
| 4.63.0 | Step 19: the shot list of the Timeline is kept in the session; shots are dragged and stretched on the strip, under a ruler of seconds; Movie > Program lost Camera Loop, Scene Loop and State Loop. |
| 4.63.1 | `sphere_mode` stops at 9 (21f). |
| 4.64.0 | A session carries its background picture (21f). |
| 4.65.0 | Smooth edges in the viewport: Setting > Rendering > Antialias (Real Time), an FXAA pass, off by default (21f). |
| 4.66.0 | Chat sign-in in the browser (31d): "Continue with ChatGPT" (the user's ChatGPT plan) and "Continue with OpenRouter" (credits there), the models of the account as a list, "Stay signed in" in the keychain of the operating system. Stand-in tests only, no real sign-in yet. |
| 4.67.0 | The sequence in a tab: Sequence, between Command and Chat, with the clicks, drags and menus of the rows in the viewport; SEQ opens it, and its arrow has "Show in viewport". The AI assistant button moved from the toolbar to the row under the object list. |
| 4.68.0 | Chat with a Claude account (31d): the provider "Claude Code" runs the conversation through the Claude Code installed on the computer and its own sign-in in the browser; no API key, no extra `ai`. Tried in the real window with a Team plan. |

Of the ten features requested on 2026-11-20, nine have a working version.
The tenth, the surface looks, waits for the grid surface of 1b. Steps 19, 20,
26, 29 and 32 are finished. Of the eleven drafts of 2026-11-23, all eleven have a working version;
the chat (31a, 31c) shipped in 4.58.0, its external connector 31b in 4.61.0,
the sign-in in the browser 31d in 4.66.0, the provider "Claude Code" in
4.68.0. Only that last one was tried with a real account (two turns on
the user's Team plan); the other providers saw no paid request and no
real sign-in by this program itself: the live trial is order 10.

**Keep Qt Widgets with PySide6, simplify the supported product, measure performance,
modernize the existing window, and deliver downloadable builds early.** Changing
bindings does not move molecular computation to the GPU. Follow
[AGENTS.md](AGENTS.md): smaller, faster, simpler, prettier.

Finished steps are in [PLAN-DONE.md](PLAN-DONE.md), and so are the shipped
milestones of the steps that are still open. A step moves there when its last
milestone ships; its detailed plan stays in `docs/plans/`.

## Open work, in execution order

The order below puts the new reported breakage and requested workflows first;
the platform/provider trials still need access to other systems or accounts.
Step numbers identify detailed plans, or the step 37 specification below;
slice letters remain stable. No release dates are promised. Each slice is a
separate implementation task/PR, with an `X` feature or `Y` fix version under
`AGENTS.md`.
Questions gate the dependent slice, not unrelated repairs.

| Order | Step | What is left | Exit condition |
| --- | --- | --- | --- |
| 1 | **37a** — [UniProt fetch from File](#step-37--gui-follow-ups-requested-2026-11-24) | Diagnose `fetch_by_uniprot P01542, async_=1` raising an unexpected-keyword `TypeError`; repair the active GUI dispatch path. | File action reaches the native asynchronous fetch; no keyword error or blocked GUI; regression check covers command registration. |
| 2 | **37b** — [Delete objects and groups](#step-37--gui-follow-ups-requested-2026-11-24) | Delete directly from the Objects list: no confirmation for an object, confirmation for a group. Choices 91–92. | Object deletion is immediate; group Cancel changes nothing; confirmed deletion has exactly the scope shown in the dialog. |
| 3 | **23b** — [Rows moved by dragging](docs/plans/23-rename-in-panel.md) | Promote the existing reorder/regroup work; the request specifies a right button, move and drop. Gesture choice 93 and acceptance checks are below. | Real mouse drop and keyboard equivalent update core order/group membership, survive refresh and session reload, and share a tested operation. |
| 4 | **37c** — [Thirty-color palettes](#step-37--gui-follow-ups-requested-2026-11-24) | Extend existing palettes to 30 colors; show only the first 10 in GUI palette previews. Scope choice 94. | Full cycle uses all 30 before repeating; previews show 10; existing colors and names are preserved under the recommended scope. |
| 5 | **37d** — [Drag palette colors](#step-37--gui-follow-ups-requested-2026-11-24) | Reorder colors by drag and drop in both New palette and Edit palette. | Saved order drives coloring and survives reopening/restart; Cancel preserves the old palette; keyboard Up/Down still works. |
| 6 | **37e** — [Narrower mouse-mode button](#step-37--gui-follow-ups-requested-2026-11-24) | Shorten the width of “3-Button Viewing” at the bottom of Objects. Choice 95. | Button no longer expands to fill spare width; all footer controls remain usable in a narrow panel and at supported UI scales. |
| 7 | **37f** — [Sequence tab controls](#step-37--gui-follow-ups-requested-2026-11-24) | Add Sequence Mode, labels, gaps and a multiple sequence alignment viewer action inside the tab between Command and Chat. Placement choice 97. | All existing sequence options work from the tab and stay synchronized with Display/commands; alignment opens the existing viewer. |
| 8 | **37g** — [Command, Sequence and Chat font size](#step-37--gui-follow-ups-requested-2026-11-24) | Add font controls beside the tabs, with immediate resizing and a reset. Scope choice 96. | Each requested tab can be resized; text input, drawing, scrolling and sequence picking stay correct; chosen sizes survive restart. |
| 9 | **27c** — [UI scale on Windows and macOS](docs/plans/27-ui-scale.md) | 27d shipped in 4.43.1: on WSLg the scale waits for the next start. Left: read what `test_scale_change_keeps_the_window_alive` prints in the Windows and macOS CI jobs (live, with the time until the window is back, or "unsupported"), and try the change once by hand on each. Needs the pushed branch: the last CI run is older than the repair. | Both systems either change the scale in the running window within two seconds, or are added to `theme.live_scale_blocker`. |
| 10 | **31 trial** — [Chat and agent tools](docs/plans/31-ai-agents.md) | 31a and 31c shipped in 4.58.0, the connector 31b in 4.61.0 (tried with Claude Code 2.1.322 in the real window). Left: the consented live trial of the Chat tab with each provider (a ligand figure, ball-and-stick color only, a scene, a native fork command, an unavailable optional feature; commands, errors, time and tokens recorded), which needs the user's API keys; one real sign-in and one conversation each with ChatGPT and with OpenRouter (31d, shipped in 4.66.0 on stand-ins), which needs the user's accounts; for the provider "Claude Code" (4.68.0, two turns tried on WSLg with a Team plan) the same five tasks, the button "Continue with Claude Code" with a signed-out Claude Code, and one turn on Windows or macOS; and one call through the connector from Codex, whose account had no credits on 2026-11-24. | Live trial recorded for Anthropic, OpenAI and Claude Code; a sign-in and a conversation recorded for ChatGPT, OpenRouter and Claude Code, on WSL and on one other system; one Codex call through the connector. |
| 11 | **1b** — [Grid surface experiment](docs/plans/01-performance-gpu.md) | Signed distance grid/marching cubes as a second surface type and a smoothness value. Compare 1aon and 4v6x at two values; user judges the experiment. | Actual times and pictures against today's surface. |
| 12 | **25b** — [Surface looks and blob](docs/plans/25-studio-effects.md) | Replan using the grid-surface result from order 11; no new surface-look setting before that. | New detailed section grounded in the experiment. |
| 13 | **15b** — [Viewport outline](docs/plans/15-presets.md) | Edge pass for figure/soft/flat/comic/sketch, contrasting with the background. A second pass over the texture that FXAA reads since 4.65.0 (`SceneRenderAA`, `fxaa.fs`). | Frame times and pictures on black/white. |
| 14 | **1b** — [Surface worker](docs/plans/01-performance-gpu.md) | Build large surfaces off the GUI thread with status; headless commands still wait. | Real-window responsiveness, suite and sanitizer checks. |
| 15 | **21g** — [General undo](docs/plans/21-commercial-features.md) | Extend the existing preset snapshots to add/remove/edit commands, retain coordinate ring; toolbar labels and remaining tests. Remove incentive error/mark and `-n` afterwards (two test files still carry the mark: `jira/PYMOL-1276.py`, `jira/PYMOL-1697.py`). | Existing undo/jira cases pass before their marks are removed. |
| any time | **1b** — [Other measured items](docs/plans/01-performance-gpu.md) | The triangulation, a third of a surface build and one thread. Draw cost of sticks and lines as triangles on every driver: both need frame times on a quiet machine, the second also on Windows and macOS drivers. | Each change has before and after numbers. |
| any time | **8** — [Modern C++ in the core](docs/plans/08-cpp-modernization.md) | No rewrite. One idiom per PR behind sanitizers and tests; vendored C stays; files go in profile order so cleanup and step 1 meet. Open: 8c (started: seven buffers of `Executive.cpp` in 4.19.39; next `Selector.cpp`, `ObjectMolecule.cpp`, `Ray.cpp`, `RepSurface.cpp`), 8d to 8g, the about 80 string calls through a pointer of 8b. Many PRs, no date. | Each slice passes the suite, the sanitizer job, `compare.py` and a PSE round trip. |

The earlier surface dependency is preserved: grid experiment before surface
looks. FXAA shipped in 4.65.0, so the outline can follow it. MAFFT stays
separately installed and the provider SDKs are the lazy extra `ai`. 5c stays
shelved; builds stay on GitHub Actions.

The toolbar, measured in the real window at 4.61.0 at 150 %, with the AI
assistant button: 1297 px of content, a 1305 px window, nothing in the
overflow menu. (4.43.0: 1236 px in 1244 px; the Sequence alignment button of
4.59.0 was not measured on its own.) The user's screen is 1707 px wide at
150 %: a further button still has to be measured before it is added.

## Step 37 — GUI follow-ups requested 2026-11-24

Open at 4.68.0. This section specifies the new work; earlier deliveries in
steps [11](docs/plans/11-color-palettes.md),
[20](docs/plans/20-toolbar-look.md),
[32](docs/plans/32-footer-icons-movie-button.md) and
[33](docs/plans/33-sequence-window.md) remain shipped. The Objects drag
work is still **23b**, not a second implementation under a new number.
Recommendations below await the choices in “Waiting for the user”.

**37a — UniProt fetch.** Reported from File > Get by UniProt:

```text
fetch_by_uniprot P01542, async_=1
TypeError: fetch_by_uniprot() got an unexpected keyword argument 'async_'
```

Source inspection: `file_fetch_uniprot` in `modules/pmg_qt/file_dialogs.py`
passes that argument, and the native function in `modules/pymol/fetching.py`
already accepts it and uses `_self.async_`. First inspect the function
registered in `cmd.keyword`, its module/signature and the installed version;
compare normal startup with plugins disabled. A legacy startup override or
an older installed build is a hypothesis, not a confirmed cause. Fix the
dispatch/registration mismatch at its source; do not remove background
execution to hide the error. Check the adjacent predicted-structure action
for the same cause. Leave a GUI-to-command regression in
`testing/tests/api/test_file_dialogs.py` and the relevant dispatch check in
`testing/tests/api/fetching.py`, with mocked network results. Try P01542 in
the real window: loading or a useful no-results/network error is acceptable;
the keyword error and a frozen GUI are not.

**37b — Delete from Objects.** An object is deleted immediately; a group
always asks first. Resolve the visible button versus Delete-key wording
(91), and whether group deletion includes its members (92). Recommendation:
a small trash button on each object/group row plus Delete for the focused
row; group confirmation names the group and summarizes affected members,
including nested groups. No delete action on “all”; a row action must not
also toggle visibility or zoom. Use the native deletion/group operations
in `modules/pmg_qt/object_panel.py`, matching the confirmed scope. Tests in
`testing/tests/api/object_panel.py`: object, empty/nested group, Cancel,
and unrelated objects retained. General undo stays in 21g.

**23b — Object order by dragging.** Resolve right mouse button versus a
handle on the right of the row (93). Keep an ordinary right click as the
context menu, left click as visibility, and F2 as rename. Show the drop
position; between rows calls `cmd.order`, onto a group uses `cmd.group`
as already planned, and a root drop can move a member out of its group.
Reject moving “all”, dropping a group into itself/its descendants, and
invalid targets. Keep refresh from interrupting a drag. Use Qt's existing
tree and provide keyboard move actions through the same operation. Check
order and membership in `testing/tests/api/object_panel.py`, including
filtered lists, nested groups, refresh and a PSE round trip; then exercise
the chosen gesture in the real window.

**37c — Palette length and preview.** Requested sizes: 30 usable colors
per palette, only the first 10 shown in the GUI preview. Recommended scope
(94): all named built-ins in `modules/pymol/palettes.py`; keep existing hex
values and their order, append distinct colors in each palette's style.
The menu already slices `colors[:10]` in
`modules/pmg_qt/action_toolbar.py`; retain and test it. Full object and chain
color cycles must use all 30, not just the preview. Review contrast and
neighbor separation with the existing palette checks, including the wrap
from last to first; do not claim 30 colors are all distinguishable with
color-vision deficiencies. The editor must still expose every color.
Extend `testing/tests/api/palettes.py` to check lengths, retained prefixes,
cycle and session behavior; check previews in
`testing/tests/api/action_toolbar.py`.

**37d — Drag colors in New/Edit palette.** Enable Qt internal list moves
in `modules/pmg_qt/palette_dialog.py`. Moving a swatch changes its position,
not its value; retain Add, Change, Remove and keyboard Up/Down. Saving uses
the visible order; Cancel leaves the stored palette untouched. Check first,
middle and last moves, reopening and QSettings persistence in the existing
palette/toolbar tests. No external drag source or new palette format needed.

**37e — Compact mouse mode.** The current button in
`modules/pmg_qt/pymol_qt_gui.py` expands into spare footer width and only
shortens its label when squeezed. Replace that behavior with the chosen
compact label (95); recommend the mouse icon plus “Viewing”/“Editing”, full
mode name in the tooltip and the existing menu. Measure the before/after
width in the real window, including a narrow Objects panel and UI scaling;
do not choose an unmeasured fixed pixel width. This supersedes choice 84's
expanding button, not the menu's available mouse modes.

**37f — Sequence tab options and alignment.** Reuse the settings already
listed by Display > Sequence Mode in `modules/pymol/_gui.py`:

- Mode (`seq_view_format`): Residue Codes, Residue Names, Chain Identifiers,
  Atom Names, States.
- Labels (`seq_view_label_mode`): All Residue Numbers, Top Sequence Only,
  Object Names Only, No Labels.
- Gaps (`seq_view_gap_mode`): No Gaps, All Gaps, Single Gap.
- “Multiple sequence alignment…” opens the existing `sequence_panel.open`
  viewer, with loaded chains/FASTA and its existing local MAFFT action.

Recommend one Options menu in the Sequence tab with Mode/Labels/Gaps
submenus and the alignment action (97). Keep Command → Sequence → Chat
order. Wire existing settings/actions in `pymol_qt_gui.py` and
`sequence_tab.py`: Display, commands, the tab and viewport stay synchronized.
Test every option, command-driven updates, picking after format changes and
opening the same alignment viewer in `testing/tests/api/sequence_tab.py` /
`sequence_window.py`. MAFFT remains separately installed; reuse its current
missing-executable message. No second viewer or alignment engine.

**37g — Font size beside the tabs.** Recommend compact A− / A+ and Reset
controls on the right of `command_tabs`, acting on the active tab's content
and remembering a separate size per tab in QSettings (96). Command covers
log and entry; Chat covers conversation and prompt; Sequence keeps its
monospace font and recalculates scroll ranges and mouse hit positions.
Use `pymol_qt_gui.py`, `sequence_tab.py` and `chat_panel.py`; preserve each
tab's font family. Changes are live and independent of overall UI scale.
Keyboard access and tooltips are required. Check changing tabs, reset,
restart, long text and sequence selection at changed sizes; no provider
request is needed to test Chat fonts.

Each shipped slice follows the normal version/ChangeLog and runnable-check
rules; this documentation update has neither a version nor a ChangeLog entry.
Skipped here: implementation, live fetch/GUI trials, new dependencies,
bulk deletion UI, palette import/export and a new alignment backend.

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
| 11 — chat control, aware of the fork | 31, built in 4.58.0 (chat) and 4.61.0 (connector) | In-app chat plus a live capability catalog, and the external connector on the same operations. The live trial is open (order 10). |

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

**New choices 91–97 from the GUI request of 2026-11-24.** These are design
choices for later implementation, not permission to update this plan.
No answer is needed to diagnose 37a or plan the independent slices.
Object deletion without confirmation, group deletion with confirmation,
30-color palettes and 10-color previews are already requested requirements.

| Question | A — recommended | B — alternative | Dependent work |
| --- | --- | --- | --- |
| 91 — “Delete button” in Objects | A visible trash button per object/group row, plus the Delete key on the focused row. | Delete key only, keeping the existing menu action and adding no row button. | 37b: settle whether “button” means a GUI button or a keyboard key. |
| 92 — What happens to a group's members? | Confirm deletion of the group and all its members, including nested groups; show the scope before applying. | Confirm removal of the group container only; retain its objects. | 37b: confirmation is required in either case; do not infer permission to remove members. |
| 93 — “Right button, moving and dropping” | Hold the right mouse button on a row, drag and release to drop; a click without dragging still opens the context menu. | A handle on the right side of each row, dragged with the left mouse button. | 23b: both retain the ordinary left-click visibility action. |
| 94 — Which existing palettes grow to 30? | All named built-ins; append colors, preserve existing entries/order. Leave legacy “PyMOL default” and saved user palettes as they are. | Include “PyMOL default” too; still leave user-created palettes at their chosen length. | 37c: the GUI preview is limited to the first 10 either way. |
| 95 — Shorter “3-Button Viewing” | Mouse icon plus compact mode name, such as “Viewing” or “Editing”; full name in the tooltip. | Mouse icon only; full mode name in the tooltip/menu. | 37e: both use content width instead of stretching across the footer. |
| 96 — Font controls for Command / Sequence / Chat | A− / A+ and Reset at the right of the tab strip; adjust content in the active tab, remember each tab separately. | The same controls set one shared content size for all three tabs. | 37g: tab-title font follows the application theme; clarify if title text was intended instead. |
| 97 — Sequence controls placement | One Options menu inside the Sequence tab: Mode, Labels, Gaps and Multiple sequence alignment. | A row of Mode/Labels/Gaps dropdowns and an alignment button inside the tab. | 37f: the menu uses less width; the dropdowns expose current settings without opening a menu. |

Earlier on 2026-11-24 the user chose the recommended option for every
question that then had no answer; those, the earlier answers, the two
answers about the sign-in (74 and 75) and the choices made while building
4.60.1 to 4.68.0 are in
[PLAN-DONE.md](PLAN-DONE.md) under "Decided by the user" and "Chosen while
building". The choices say there what it takes to change them.

One of the choices of that run is worth a look, because only the user's
other computers can settle it: smooth edges (FXAA, 4.65.0) are **off** when
the program starts, since only WSLg was tried. Recommended: on by default
once the picture was seen on Windows and macOS (Setting > Rendering >
Antialias (Real Time), or `set antialias_shader, 1`).

The five choices of 4.67.0 (81 to 85) are about what is seen, and were
made without asking, each as the request read: the Sequence tab always
lists the sequence and `seq_view` only puts it into the viewport as well;
a click on SEQ opens the tab and "Show in viewport" is in the menu of its
arrow; the tab has the background color of the viewport; the name of the
mouse mode is shortened in a narrow panel; the robot keeps its drawing.

The five choices of 4.68.0 (86 to 90) were made without asking, after two
options were offered and the answer was "add OAuth verification; a button
or an icon": Claude signs in through the installed Claude Code and not
through a sign-in of pymolish, which Anthropic does not allow; the button
starts Claude Code's own sign-in and there is no Sign out; Claude Code's
own tools, MCP servers and settings are off in the Chat tab; Claude Code
keeps its transcript; the button keeps the plain sign-in icon, without the
marks of the providers. One point is the user's to weigh: Anthropic's page
for the Agent SDK says that, unless approved, a product may not "offer
claude.ai login or rate limits". Starting the user's own, unchanged Claude
Code is how its legal page reads to me ("does not prevent an end user from
signing in to the unmodified Claude Code binary"); nobody at Anthropic was
asked. Before pymolish is given to others with this provider, ask them, or
take the provider out (`"Claude Code"` in `assistant.ROUTES`).
Say so if another one is wanted.

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
scene; Undo of a step of `ligand_next`. From 4.60.1 to 4.65.0: a token of
the agent connector that is kept between runs (today: the environment
variable `PYMOLISH_AGENT_TOKEN`, or a new one each run, so the setup line
of a client is run again; a kept one is the storage question 48), the
stateless MCP revision 2026-07-28, and a setup helper for other clients
than Claude Code and Codex; a shot "state sweep" for the Timeline (its 24
rows stay under Movie > Program); undo of a drag on the Timeline strip;
SMAA; smooth edges in stereo and in images drawn at another size than the
window; ambient occlusion in other looks than "soft"; the answer about the
paint roller of question 27 ended "rest", cut off, and nothing more was
built from it. From 4.66.0: the list of models for the two providers with
an API key; a sign-in to an API account at Anthropic through its `ant`
tool (offered in question 74, not chosen); more than one ChatGPT account;
the check of the signature of ChatGPT's ID token; the ChatGPT access token
kept between runs (today the next run renews it); deleting the OpenRouter
key at OpenRouter on Sign out (today a link to its page). From 4.67.0, in
the Sequence tab: the dimming of the unaligned residues of an alignment,
the frame around a drag, the marks of the selection along the scroll bar,
scrolling on while a drag passes the edge; and the full name of the mouse
mode in the tooltip of its button. From 4.68.0: a Sign out for Claude Code
(it would sign it out everywhere), the marks of the providers as icons
(their rules for use were not read), one long-lived Claude Code per
conversation in place of one start per turn (the start was not timed
alone; a resumed turn with a one-word answer took 2.66 s in all), a conversation without Claude Code's transcript on disk, and a
check of the sign-in after a failed turn (the row shows the state of the
last check).

The user's to do:

- Choose options 91–97 above before the corresponding GUI slices are built.
- Push `feature13` and open its pull request. Local tracking refs checked
  2026-11-24: `origin/feature13` is at the plan commit of 4.66.0; including
  this documentation commit, the branch is 5 commits ahead (4.67.0,
  4.68.0, their plan commits and this update) and contains `feature12`
  (itself 9 commits ahead of its tracking ref). At the previous remote check,
  `feature13` had no pull request; the last one was #10 (`feature11`, merged
  2026-11-20). Remote PR/CI state was not rechecked in this documentation
  run; no push or merge was performed.
- After the push, read the CI run: the Windows icon, release notes,
  `chem`/`fix` extras on three systems, and for 27c the line that
  `test_scale_change_keeps_the_window_alive` prints in the Windows and
  macOS jobs: "live ... shown after" with a time, or "unsupported on ...".
  The latest successful master run,
  [44750297890](https://github.com/adrian-jasinski/pymolish-studio/actions/runs/44750297890),
  is at `d40f09f6`, before the scale repair. Native MAFFT launch, the agent
  connector and the FXAA shader have also been tried on Linux/WSLg only.
- Try the Chat tab with your own Anthropic and OpenAI keys and a model
  ID each (`pip install 'pymolish[ai]'`): no request was ever sent by the
  Chat tab itself.
- Sign in once with each new provider of the Chat tab (4.66.0): choose
  ChatGPT, then "Continue with ChatGPT"; choose OpenRouter, then "Continue
  with OpenRouter"; send one request each. No real sign-in was made: the
  code follows the two published flows, and OpenAI's server took the first
  request up to its log-in page. Three things only a real try shows:
  whether OpenAI lets pymolish register without being asked first (its
  page says the plan route is for "all open-source partners"); whether
  OpenRouter takes the requests in the form the OpenAI package sends them;
  and, on WSL, whether the browser of Windows reaches the listener inside
  WSL (`127.0.0.1:1455` for ChatGPT, `localhost` with a free port for
  OpenRouter). "Stay signed in" needs a keychain service: Windows and
  macOS have one, a Linux desktop usually, WSL usually not; without one
  the box says so and the sign-in lasts for the run.
- Try the provider "Claude Code" of the Chat tab (4.68.0) yourself: choose
  it, check the account in the row, send a request. On another computer,
  or after `claude auth logout`, try "Continue with Claude Code": that
  button was run against a stand-in only, since a real try would have
  signed your Claude Code out. The trial of 2026-11-24 made eleven small
  requests on your Team plan (model haiku): seven to find the right
  switches of Claude Code, four turns in the window. Each conversation leaves a transcript
  under `~/.claude/projects` (the folder named after the temporary
  directory).
- Try the connector from Codex once its account has credits: AI assistant
  > Agent connector, then "Copy setup line for Codex". On 2026-11-24
  `codex mcp list` showed the server as enabled, and `codex exec` stopped
  with "Your workspace is out of credits" before it called anything. The
  trial with Claude Code made two small requests on your Claude account
  (model haiku; the client reported 0.005 USD for the second one).
- Turn "Antialias (Real Time)" on once on Windows and on macOS and say
  whether it should be on by default.
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
