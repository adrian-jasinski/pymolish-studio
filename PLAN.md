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
allow it. Not tried with a real account: that is part of order 2.

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
the requested Objects, palette, Sequence and font controls: step 37,
plus the existing drag-and-drop slice 23b promoted into execution order.
Planning only; nothing shipped or measured in the GUI in this update.
The palette sizes below are requested targets. Choices 91 to 97 were
answered on 2026-11-25 and are recorded in [PLAN-DONE.md](PLAN-DONE.md).

Built 2026-11-25, 4.68.1 to 4.75.0, from the request "run the planned
tasks that can be run now, except 27c and the trial of 31": all of step
37 (37a to 37g) and 23b, one version each. Steps 23 and 37 are finished
and left this file; the specification of step 37 is now
[docs/plans/37-gui-followups.md](docs/plans/37-gui-followups.md). 37b and
37f follow the user's answers of that day where they differ from what was
recommended (the Delete key without a button; a row of lists). Seven
choices were made while building (98 to 104).

Built in the same run, 4.76.0: the grid surface experiment of 1b,
`surface_type 7`, with its times, triangle counts, memory and pictures for
1aon and 4v6x. It is an experiment to be judged (question 105), not a
default. Not started in that run: the outline (15b), the surface worker
and general undo (21g), each a slice of its own in the core; 25b waits for
that judgment. Two of them need long benchmark runs and many test windows
on the machine the user was working at: the runs of 4v6x took 10 of its
17 GB, and a test window once caught what the user was typing. What was
read for 15b is noted in its plan.

Built 2026-11-25, 4.76.1 to 4.76.14, from the request "can we finish 8,
modern C++ in the core": not finished, and not finishable in one run. The
`malloc` half of 8c is done where a buffer has one owner (230 of 297
allocation sites gone), the mechanical part of 8d is done (215 of 829 macro
calls), five functions or blocks of dead code are deleted, and eight
defects that were in 4.76.0 are fixed, four of them crashes or memory
errors of commands (`load_png` with a bad data URL, `valence` with a
source, a surface with `ambient_occlusion_mode` 3, spheres of a part of
an object with `sphere_mode` 6 to 8). Nothing a user sees
changed otherwise, so there is no new `X`. What is left of the step, with
counts, is in its plan. Where the step should end was question 106; the
user answered it the same day: finish here. Step 8 is closed and left this
file for [PLAN-DONE.md](PLAN-DONE.md).

Built 2026-11-25, 4.77.0 to 4.78.0, from a conversation in the Chat tab
that failed ("download EGFR structures by UniProt id": every UniProt
command was refused) and the request that followed, "check other commands
if they are in the allowed list, if not add them". The model now runs 286
of the 504 commands it finds (84 before the run); 218 stay out, with the reason
per kind in the `ChangeLog`. A switch "Download without asking" was new in
the Chat tab (choices 107 and 108, answered in the run; replaced in
4.79.0). Found by the
check and fixed in 4.77.1: `safe_eval` ran any Python, and `set_color`
gave it text of the model without a question. Step 31 stays open for its
trial with real accounts (order 2).

Built 2026-11-25, 4.79.0, from the request "add option to chat windows
to run agents / commands without asking (like checkbox to mark)": the
check box "Run without asking" in the Chat tab, off at every start. While
it is on, no reviewed command asks "Allow this action?", for the model of
the tab and for the agents on the connector, and with "Trusted Python"
ticked Python runs without the question too. "Download without asking"
(4.77.0) is gone, the new switch covers it. Choices 109 to 111 were asked
and answered in the run.

Built 2026-11-25, 4.80.0, from the request "add OAuth option to other
chats like OpenAI like current claude code option": the provider "OpenAI"
of the Chat tab has the button "Continue with ChatGPT" next to its field
for an API key, and the entry "ChatGPT" left the list. It is the sign-in
of 4.66.0, moved; no new sign-in was built. Three options were offered
(question 112); the user chose this one, recommended was a provider
"Codex" that works like "Claude Code". Two choices were made while
building (113 and 114). Still no real sign-in to ChatGPT was made: order 2.

See [Shipped state](PLAN-STATE.md) for the shipped versions and their summary.

**Keep Qt Widgets with PySide6, simplify the supported product, measure performance,
modernize the existing window, and deliver downloadable builds early.** Changing
bindings does not move molecular computation to the GPU. Follow
[AGENTS.md](AGENTS.md): smaller, faster, simpler, prettier.

Finished steps are in [PLAN-DONE.md](PLAN-DONE.md), and so are the shipped
milestones of the steps that are still open. A step moves there when its last
milestone ships; its detailed plan stays in `docs/plans/`.

## Open work, in execution order

The first two orders need what this machine does not have: other systems,
keys and accounts. Step numbers identify detailed plans; slice letters
remain stable. No release dates are promised. Each slice is a separate
implementation task/PR, with an `X` feature or `Y` fix version under
`AGENTS.md`.

| Order | Step | What is left | Exit condition |
| --- | --- | --- | --- |
| 1 | **27c** — [UI scale on Windows and macOS](docs/plans/27-ui-scale.md) | 27d shipped in 4.43.1: on WSLg the scale waits for the next start. Left: read what `test_scale_change_keeps_the_window_alive` prints in the Windows and macOS CI jobs (live, with the time until the window is back, or "unsupported"), and try the change once by hand on each. Needs the pushed branch: the last CI run is older than the repair. | Both systems either change the scale in the running window within two seconds, or are added to `theme.live_scale_blocker`. |
| 2 | **31 trial** — [Chat and agent tools](docs/plans/31-ai-agents.md) | 31a and 31c shipped in 4.58.0, the connector 31b in 4.61.0 (tried with Claude Code 2.1.322 in the real window). Left: the consented live trial of the Chat tab with each provider (a ligand figure, ball-and-stick color only, a scene, a native fork command, an unavailable optional feature; commands, errors, time and tokens recorded), which needs the user's API keys; one real sign-in and one conversation each with ChatGPT (since 4.80.0 the button of the provider "OpenAI") and with OpenRouter (31d, shipped in 4.66.0 on stand-ins), which needs the user's accounts; for the provider "Claude Code" (4.68.0, two turns tried on WSLg with a Team plan) the same five tasks, the button "Continue with Claude Code" with a signed-out Claude Code, and one turn on Windows or macOS; and one call through the connector from Codex, whose account had no credits on 2026-11-24. | Live trial recorded for Anthropic, OpenAI and Claude Code; a sign-in and a conversation recorded for ChatGPT, OpenRouter and Claude Code, on WSL and on one other system; one Codex call through the connector. |
| 3 | **25b** — [Surface looks and blob](docs/plans/25-studio-effects.md) | Replan with the result of the grid surface experiment (4.76.0: times and pictures are there). Waits for the user's judgment of it, question 105; no new surface-look setting before that. | New detailed section grounded in the experiment. |
| 4 | **15b** — [Viewport outline](docs/plans/15-presets.md) | Edge pass for figure/soft/flat/comic/sketch, contrasting with the background. A second pass over the texture that FXAA reads since 4.65.0 (`SceneRenderAA`, `fxaa.fs`). | Frame times and pictures on black/white. |
| 5 | **1b** — [Surface worker](docs/plans/01-performance-gpu.md) | Build large surfaces off the GUI thread with status; headless commands still wait. | Real-window responsiveness, suite and sanitizer checks. |
| 6 | **21g** — [General undo](docs/plans/21-commercial-features.md) | Extend the existing preset snapshots to add/remove/edit commands, retain coordinate ring; toolbar labels and remaining tests. Remove incentive error/mark and `-n` afterwards (two test files still carry the mark: `jira/PYMOL-1276.py`, `jira/PYMOL-1697.py`). | Existing undo/jira cases pass before their marks are removed. |
| any time | **1b** — [Other measured items](docs/plans/01-performance-gpu.md) | The triangulation, a third of a surface build and one thread. Draw cost of sticks and lines as triangles on every driver: both need frame times on a quiet machine, the second also on Windows and macOS drivers. | Each change has before and after numbers. |

The earlier surface dependency is preserved: the grid experiment (tried in
4.76.0) and its judgment come before the surface looks. FXAA shipped in 4.65.0, so the outline can follow it. MAFFT stays
separately installed and the provider SDKs are the lazy extra `ai`. 5c stays
shelved; builds stay on GitHub Actions.

The toolbar, measured in the real window at 4.61.0 at 150 %, with the AI
assistant button: 1297 px of content, a 1305 px window, nothing in the
overflow menu. (4.43.0: 1236 px in 1244 px; the Sequence alignment button of
4.59.0 was not measured on its own.) The user's screen is 1707 px wide at
150 %: a further button still has to be measured before it is added.

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
| 11 — chat control, aware of the fork | 31, built in 4.58.0 (chat) and 4.61.0 (connector) | In-app chat plus a live capability catalog, and the external connector on the same operations. The live trial is open (order 2). |

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

One question waits, the judgment of the grid surface (4.76.0). Its
numbers are in the `ChangeLog` and in
[docs/plans/01-performance-gpu.md](docs/plans/01-performance-gpu.md), its
pictures are `docs/img/grid-surface-1aon.jpg` and
`docs/img/grid-surface-4v6x.jpg`; try it with `set surface_type, 7`.

| Question | A — recommended | B | C | Dependent work |
| --- | --- | --- | --- | --- |
| 105 — Does the grid surface stay, and for what? | It stays as a choice beside today's surface, which remains the default: a row "Solid (grid)" in Setting > Surface, and the settings it lacks (carving, cavities) are added. Decide about a default once the surface worker (order 5) is built, since a build then no longer blocks the window. | It becomes the default above a size, for example 100,000 atoms, where today's surface takes longest (4v6x: 34 s against 9 s). Colors meet in more jagged borders there. | It is taken out again: the three-fold shorter build is not worth a second kind of surface. | 25b (order 3): with A or B the rounded "clay" surface is this surface with a probe of about 3 A, which keeps fine triangles where today's surface gets coarse; with C it stays the Gaussian map. |

Choices 91–97 were answered on 2026-11-25 and built the same day (4.69.0
to 4.75.0); they are in [PLAN-DONE.md](PLAN-DONE.md). So are 107 and 108
(big downloads of the chat in the background; a switch that turns the
question for downloads off), asked and answered in the run of 4.77.0,
and 109 to 111 ("Run without asking": commands and Python, in place of
the download switch, off at every start), asked and answered in the run
of 4.79.0, and 112 (the ChatGPT sign-in inside the provider "OpenAI"),
asked and answered in the run of 4.80.0.

Seven choices were made while building 4.68.1 to 4.75.0 (98 to 104),
each the smaller option; they are listed in PLAN-DONE.md with what it
takes to change them. Three are worth a look:

- 98: the old pymolish plugin is not loaded at all when it is found as a
  startup plugin, so the commands of it that this program does not have
  are gone too. The other way: load it and refuse only the names that are
  built in.
- 99: Delete acts on the current row, the one with the frame, which is
  the row clicked last. A click on a row hides or shows the object first,
  as always; the arrow keys reach a row without that.
- 101: the colors added to the palettes are computed in each palette's own
  tone, not taken from Material, Nord, Dracula, Catppuccin, ChimeraX or
  the color-blind sets. Say which palettes should rather stay short.

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
scrolling on while a drag passes the edge.
From 4.68.0: a Sign out for Claude Code
(it would sign it out everywhere), the marks of the providers as icons
(their rules for use were not read), one long-lived Claude Code per
conversation in place of one start per turn (the start was not timed
alone; a resumed turn with a one-word answer took 2.66 s in all), a conversation without Claude Code's transcript on disk, and a
check of the sign-in after a failed turn (the row shows the state of the
last check). From 4.68.1 to 4.75.0: deleting several selected rows of the
Objects list at once; Esc to give up a drag of a row (release it where no
mark is shown), and scrolling the list while a row is dragged past its
edge; keys for A−, A+ and Reset (Tab reaches them); less padding inside
the mouse mode button than its neighbors have; a check of the thirty
colors for color-vision deficiencies. From 4.76.0, the grid surface:
carving, cavity culling and cavity mode, `surface_solvent` and trimming;
strips longer than one triangle; a grid in blocks instead of one over the
whole box (above 67 million cells the cells grow); frame times in the
viewport; ray times on a cool machine. From 4.80.0: a provider "Codex"
that runs the conversation through the installed Codex and its own
sign-in, as "Claude Code" does (option A of question 112; Codex 0.163.0
is installed and signed in on this machine, and its shell tool can only
be put into the read-only sandbox, not switched off), the same for the
Gemini CLI (option B; not installed here), and a way to use the API key
while signed in to ChatGPT (today: Sign out).

The user's to do:

- Look at the changes of 2026-11-25 in your own window. They were built
  and tried in a copy; at the end of the run, with pymolish closed, your
  `.venv` was rebuilt to 4.76.0 with the extras `dev`, `chem`, `fix` and
  `ai` (it had 4.67.0; the extra `ai` added `keyring` 25.7.0, which "Stay
  signed in" needs), and the suite passed there: 1121 passed, 252 skipped.
- Judge the grid surface (question 105): the two pictures in `docs/img`,
  and `set surface_type, 7` on a structure of your own.
- Say where File > Get by UniProt failed (37a). On this machine the old
  plugin is not loaded (`~/.pymolpluginsrc.py` sets an empty startup
  path) and the action worked before the change; the error was
  reproduced only by putting `~/.pymol/startup` into the startup path. If
  it happened elsewhere, with another cause, it is not fixed.
- Try the drag with the right button (4.70.0) once on Windows and on
  macOS: there the system asks for the menu when the button is released,
  on Linux when it is pressed. Both are handled; only Linux was tried.
- Push `feature13` again. Checked 2026-11-25 after 4.80.0:
  `origin/feature13` is at the plan commit of 4.76.14 (`5101e943`), so
  what was listed here before is pushed, and pull request #11 ("Feature13")
  is open. Including this plan commit the branch is 10 commits ahead:
  4.77.0, 4.77.1, 4.78.0, 4.79.0, 4.79.1, 4.80.0 and four plan commits.
  No push or merge was performed in this run.
- After the push, read the CI run first for step 8: 4.76.1 to 4.76.14
  changed 60 files of the core and were compiled with GCC 13 on Linux
  only. The Windows (MSVC), macOS (Apple Clang) and `sanitize-Linux` (GCC
  11) jobs are the check that was not possible here.
- With "Run without asking" and "Trusted Python" both ticked, Python of
  the model or of an agent runs unseen, with your rights on this
  computer. That was your choice (109); recommended was commands only.
  Untick one of the two before you let it read files or pages you do not
  trust.
- Try in the Chat tab what failed: "download EGFR structures, human, by
  UniProt id". All 388 entries of P00533 (counted 2026-11-25) load in the
  background; they pass 600,000 atoms (an estimate from the first five
  entries, 28,061 atoms), and above that the chat refuses further changes
  of the session, its Undo limit. A limit ("the first 20") avoids that.
- Then the rest of the CI run: the Windows icon, release notes,
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
- Sign in once with each sign-in of the Chat tab (4.66.0): choose
  OpenAI, then "Continue with ChatGPT" (since 4.80.0 the button is in that
  entry; "ChatGPT" is no entry any more); choose OpenRouter, then "Continue
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
  2026-11-25). Since 4.68.1 it is no longer loaded, and the log says so
  at every start where the startup path names that folder.
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
