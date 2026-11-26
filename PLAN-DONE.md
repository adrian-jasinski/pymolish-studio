# pymolish-studio — finished plans

Steps of the [roadmap](PLAN.md) whose last milestone has shipped. Open work
stays in `PLAN.md`; the detailed plans stay in `docs/plans/`. Step numbers and
order numbers in the finished-work table are historical. “Open, order N”
references below follow the current roadmap (updated 2026-11-26).

## Decisions 128 and 129

Answered by the user on **2026-11-26**, both with **A, recommended**.
This is a planning update at 4.90.0; no feature shipped and no new
measurement was made. [Review history and background](docs/plans/roadmap-background.md)
and [detailed user checks](docs/plans/roadmap-checks.md) now live outside
the main roadmap.

| No. | Decision | State |
| --- | --- | --- |
| 128 | Keep the existing glow setting and add "glow" / "no glow" to the light menu, as for fog, for the viewport only. Leaving it setting-only, extending it to ray/sized images, and removing it were not selected. | The setting shipped in 4.88.0. The [15p menu follow-up](docs/plans/15-presets.md#question-128-a-glow-menu-follow-up) is open, order 3; it has not shipped. |
| 129 | "Solid" stays the default after the surface worker; "Solid (grid)" stays optional. Neither a size-dependent default nor grid everywhere was selected. | Decision complete; existing behavior retained, no code change or version. [Plan 1](docs/plans/01-performance-gpu.md). |

## Earlier decisions and implementation record

**Built 2026-11-26, 4.83.0 to 4.89.0:** orders 3 to 9 of the planning
update below, in that order: 15m, 34d with 15n, 15o, 32c, 15b, 15p and the
surface worker of 1b. Steps 32 and 34 are finished again; step 15 has every
original slice built; answer 128 A leaves the glow menu follow-up open.
Step 1 keeps its two measured items. The current open orders are:
27c 1, the trial of 31 2, the glow menu 3, general undo 4, the rest of the
documentation (step 38) 5. The rows are under "Finished
milestones of open steps"; the decisions and choices follow here.

Decided by the user on 2026-11-26, in the request that started the run
("for questions 123, 124 and 125 use recommended options"):

| No. | Decision | State |
| --- | --- | --- |
| 123 | A: four new entries, space filling, illustrated atoms, licorice and bond shell; the row "illustration" is called "contour cartoon". B was the first two only. | 4.83.0. `space_filling`, `illustrated_atoms`, `licorice`, `bond_shell` in `preset.py`; `preset.illustration` keeps its name. |
| 124 | A: transparency for whole objects, one value for the balls and bonds of ball and stick. B was atoms and residues with half bonds. | 4.84.0. `ball_and_stick_transparency` (setting 801, object and state level); `preset.transparency`; `menu.transparency`. |
| 125 | A: the groups cartoon, atoms and bonds, surface, binding, then transparency; light, theme and floor under a caption. B was two groups only. | 4.85.0. `menu.presets`. |
| 126 | A: the documentation is Markdown in this repository, with a docs home and task and command indexes. B was a separate website with full-text search. Answered in the run that built step 38. | Built 2026-11-26 at 4.90.0, no version. `docs/README.md` and the pages it links. |
| 127 | A: short videos opened from static posters. B was inline GIF loops. Answered in the same run. | Built 2026-11-26. Four MP4 files in `docs/media/`, posters `docs/img/demo-*.jpg`; how GitHub plays them is open, order 5. |

Reported by the user in the same message, not checked here: the drag with
the right button of 4.70.0 works; the Chat tab works with Claude Code and
with ChatGPT, signed in and with "Run without asking"; the old pymolish
plugin is removed from `~/.pymol/startup`. The system on which the drag was
tried, and what was asked in the Chat tab, were not said.

Chosen while building 4.83.0 to 4.89.0, without asking. Say so if another
one is wanted:

| No. | Choice | Built | To change it |
| --- | --- | --- | --- |
| 130 | "Illustrated atoms" is spheres in the light "flat": of the three lights with an outline that were tried on 1oky, comic has outlines that are too heavy and figure is too dark. "Bond shell" has its surface at transparency 0.5: at 0.25 the lines inside do not show, at 0.75 the surface hardly does. The labels are in small letters, like every other row of the menu. | 4.83.0. | `illustrated_atoms` and `bond_shell` in `preset.py`; the labels in `menu.presets`. |
| 131 | A row of the Transparency menu clears the value that a preset had set on the atoms of the object (glass, the surface looks) and sets it on the object, so that it shows everywhere. A preset takes the rows back by unsetting the four settings on its objects: new for `sphere_transparency`, `transparency` and `ball_and_stick_transparency`, where a user's own value on an object now ends with the next preset, as it did for the cartoon. `ball_and_stick_transparency` has no atom level. | 4.84.0. | `transparency` and `_prepare` in `preset.py`; the level `ostate` in `SettingInfo.h`. |
| 132 | Inside their group "wire", "spring" and "cylinders" lost the word "cartoon"; "theme" became "theme (colors and background)"; "surface look" is the first four rows of "surface", above glass, balls in glass and bond shell. | 4.85.0. | `menu.presets`. |
| 133 | The footer buttons are 32 px high with icons of 20 px, the sizes the plan named as a trial. Two rows are two plain rows, not a grid: a column of a grid would have made "Chat" as wide as the mouse mode above it. The name of the mouse mode is no longer shortened in a narrow panel. | 4.86.0. | `Footer` in `object_panel.py` (`ICON`, `HEIGHT`). |
| 134 | The outline follows `ray_trace_mode` and is on by default (`viewport_outline`): no look had to change, scenes and sessions carry it, and the viewport shows what the ray tracer will draw. A session or script that set `ray_trace_mode` for ray tracing now has the outline in the viewport too. The line falls on the far side of a step in depth, is as wide as the viewport is high divided by 500 (1 to 3 pixels), and has the ray tracer's color. Labels are not written into the depth while it is drawn. | 4.87.0. | `outlineMode` in `ShaderMgr.cpp`; the numbers in `fxaa.fs` (`line`, `level`). |
| 135 | The halo of "glow" is laid on background pixels only, mixed toward the color of what is drawn (so it shows on white too), from a blur at a quarter of the size that reaches about a twelfth of the viewport's height. One setting, the strength. | 4.88.0. | `glow.fs`, the last block of `fxaa.fs`, `Enable_GlowShader`. |
| 136 | A surface goes to the background from 5000 atoms; the status is two lines in the log, not a progress bar; a build that is no longer wanted runs to its end; the coloring of the vertices and the first upload stay on the GUI thread (the 1.2 s that are left on 1aon). On by default. | 4.89.0. | `cSurfaceBuildMinAtoms` in `RepSurface.h`; `async_surface`. |

One number is wrong in the git log: the commit message of 4.88.0
(`ba51b668`) calls the question about the glow "126". The documentation
plan had taken 126 and 127 an hour before; the question is 128.

**Planning update 2026-11-26 at 4.82.0:** no milestone shipped. Steps 32
and 34 reopen for 32c (larger labeled footer buttons) and 34d (independent
ball-and-stick transparency); their earlier completed scopes remain
recorded below. Step 15 adds 15m–15p for the reference-image recipes,
transparency menu, grouping and glow experiment. Current open orders:
15m 3, 34d/15n 4, 15o 5, 32c 6, 15b 7, 15p 8, surface worker 9,
general undo 10. Dated descriptions of past runs retain historical orders.

Decided by the user during this planning update, and built later that day:

| No. | Decision | State |
| --- | --- | --- |
| 121 | Larger icons with Viewing, SEQ, Chat, Wizard and Cmd labels beside them; two rows when narrow. Larger icons without the extra labels, and a wider single-row panel, were not selected. | [32c](docs/plans/32-footer-icons-movie-button.md), built in 4.86.0. |
| 122 | Existing rendering recipes first, then a measured experiment for true neon/glow. A settings-only endpoint was not selected. | [15m and 15p](docs/plans/15-presets.md), built in 4.83.0 and 4.88.0; answer 128 A adds the viewport-only menu entry, open, order 3. |

**Planning update 2026-11-23 at 4.43.0:** no milestone shipped. Step 11 is
reopened for CPK (11c); its existing palette releases remain recorded below.
New steps 33–36 and follow-ups 22f/24d/27d are open in `PLAN.md`. The unbuilt
step 31 was rewritten for in-app chat and live discovery of fork commands.
Earlier choices superseded by the new request are identified there; the
historical release record is preserved.

**Built 2026-11-23, 4.43.1 to 4.51.0:** the ten milestones 27d, 24d, 35a,
28b with 22d and 22e, 22f, 35b, 34a with 34b, 34c, 11c and 36a; their rows
are the first ten of "Finished milestones of open steps". Steps 22, 28, 34,
35 and 36 moved to "Finished steps", and step 11 is closed again.

**Built 2026-11-24, 4.60.1 to 4.65.0:** the repair of Rock > Random, 31b,
15e, the rest of step 19 and the three items of 21f; their rows are the
first seven of "Finished milestones of open steps". Step 19 moved to
"Finished steps". Open orders below were renumbered: 27c 1, the trial of 31
2, the grid surface 3, 25b 4, 15b 5, the surface worker 6, 21g 7.

**Built 2026-11-24, 4.66.0:** 31d, the sign-in of the Chat tab in the
browser; its row is the second of "Finished milestones of open steps". The
open orders keep their numbers; the trial of 31 (order 2) now also covers a
real sign-in.

**Built 2026-11-24, 4.67.0:** the Sequence tab and the AI assistant button
in the row under the object list, from a request of that day and not from
a plan; its row is the first of "Finished milestones of open steps", under
step 33. Steps 32 and 33 stay finished; the open orders keep their numbers.

**Built 2026-11-24, 4.68.0:** the provider "Claude Code" of the Chat tab,
a Claude account through the installed Claude Code; its row is the first of
"Finished milestones of open steps", under step 31. The open orders keep
their numbers; the trial of 31 (order 2) now also covers this provider.

**Built 2026-11-25 and 2026-11-26, 4.81.0 and 4.82.0:** 25b, the grid
surface as a menu row with its cavity settings and the four surface
looks; their two rows are the first of "Finished milestones of open
steps". Step 25 moved to "Finished steps". The open orders moved up by
one: 15b 3, the surface worker 4, 21g 5.

**Built 2026-11-25, 4.76.0:** the grid surface experiment of 1b; its row
is the first of "Finished milestones of open steps". Question 105 was
answered the same day: keep it as an option (A, recorded below).
The open orders moved up by one: 25b 3,
15b 4, the surface worker 5, 21g 6.

**Built 2026-11-25, 4.68.1 to 4.75.0:** all of step 37 (37a to 37g) and
23b; their eight rows are the first of "Finished milestones of open
steps". Steps 23 and 37 moved to "Finished steps". The open orders were
renumbered: 27c 1, the trial of 31 2, the grid surface 3, 25b 4, 15b 5,
the surface worker 6, 21g 7.

Chosen while building 4.68.1 to 4.75.0, without asking, each the smaller
option. Say so if another one is wanted:

| No. | Choice | Built | To change it |
| --- | --- | --- | --- |
| 98 | A startup plugin named "pymolish" is not loaded at all. The other way, loading it and refusing only the command names that are built in, keeps its other commands, and needs a list of the built-in names in the plugin loader. | 4.68.1. | `PluginInfo.load` in `modules/pymol/plugins/__init__.py`. |
| 99 | Delete acts on the current row of the list (the framed one: clicked last, or reached with the arrow keys), not on the rows marked with Ctrl+click for copying. After a delete no row is current, so a second press does nothing. | 4.69.0. | `ObjectPanel.delete` in `object_panel.py`. |
| 100 | Moving rows: on a group the middle half of the row means "into" (all of the row below its top quarter while the group is open, since its members follow); under the last row means the end of the top level; the moved row becomes the current one. With the keys: Alt and the arrows. | 4.70.0. | `_drop` and `move_current` in `object_panel.py`. |
| 101 | The colors added to the ten palettes are computed: an OKLCH grid inside each palette's own range of lightness and chroma, a contrast of 3 to its background, the farthest from all colors already there first, then ordered so that neighbors differ. The other way was to take more colors from each source; most sources have no more. | 4.71.0. | The lines after "added" in `PALETTES` of `modules/pymol/palettes.py`. |
| 102 | The five buttons under the object list stand at the left and the spare width is at the right. The other way: the three icon buttons at the right edge. | 4.73.0. | `footer.addStretch` in `pymol_qt_gui.py`. |
| 103 | The three lists of the Sequence tab have a word before each (Mode, Labels, Gaps) and no key of their own: Tab reaches them. | 4.74.0. | `Options` in `sequence_tab.py`. |
| 104 | A−, A+ and Reset change the text by one point per click, between 6 and 40 points, and keep the difference to the start size of each tab, so every widget keeps its font and its distance to the others. | 4.75.0. | `TabFontButtons` in `pymol_qt_gui.py`; the keys `fonts/<tab>` in the settings. |

Decided by the user on 2026-11-25, in the run of 4.81.0 and 4.82.0 (25b,
the surface looks):

| Question | Decision | State |
| --- | --- | --- |
| 115 | Option A, recommended: a row of "surface look" shows the surface of the protein itself, with the ligands as balls and sticks, in a submenu of its own in the Presets menu. B was the plan as written: four more rows in the light menu that change the material of whatever is shown. | 4.82.0. `surface` and `SURFACES` in `modules/pymol/preset.py`; the submenu in `menu.presets`. |

Chosen while building 4.81.0 and 4.82.0, without asking. Say so if
another one is wanted:

| No. | Choice | Built | To change it |
| --- | --- | --- | --- |
| 116 | Candy glass and frosted use the grid surface with a probe of 3 A, as clay does; answer 105 named clay only. At that probe the surface of dots has triangles one can see under a highlight (1aon: 195,556 triangles, measured in 4.76.0, against 668,588 now). Glossy stays on today's surface. | 4.82.0. | `_round` in `SURFACES`, `preset.py`. |
| 117 | A surface look sets its light for the whole scene, through `look`, and the round shape on the objects of the preset; transparency on the atoms, as "glass" does. The next preset takes all of it back, a row of the light menu only the light. The rows hide the cartoon and set no colors. | 4.82.0. | `preset.surface`; the three parts of an entry of `SURFACES`. |
| 118 | `cavity_cull` on the grid goes by volume: a closed cavity under 2.5 A3 per count is not drawn, 25 A3 at the default of 10. One water makes a cavity of 12 to 16 A3. Of the values tried this came closest to the dots: 2rh1 keeps 5 closed cavities (the dots 7), 4hhb 9 (the dots 8). It is on by default, as for the dots, so a grid surface shows fewer small cavities than in 4.76.0 to 4.80.0. | 4.81.0. | `CULL_VOLUME` in `SurfaceJobRunGrid`, `layer2/RepSurface.cpp`. |
| 119 | The cavity modes on the grid decide on a second, coarse grid (cells of 2 A at the default radius of 7 A) where the large probe fits, and keep the rims of a pocket as the dots do. They draw 71 % (2rh1) and 74 % (4hhb) of the area the dots draw, in the same places. | 4.81.0. | `GridPockets` in `layer2/RepSurface.cpp`; the cell is `radius / 3.5`. |
| 120 | "Solvent Accessible" works on the grid too, though answer 105 named carving and cavities only: the row sits next to "Solid (grid)" in the same menu. Trimming is not followed: a grid makes no folds. Carving worked already and only got a test. | 4.81.0. | The branch `I->surfaceSolvent` in `SurfaceJobRunGrid`. |

Decided by the user on 2026-11-25, in the run of 4.80.0, on the request
"add OAuth option to other chats like OpenAI like current claude code
option". The Chat tab had the sign-in to ChatGPT since 4.66.0, as an
entry of its own.

| Question | Decision | State |
| --- | --- | --- |
| 112 | Option C: no new provider; the entry "OpenAI" gets the button "Continue with ChatGPT" next to its key field and the entry "ChatGPT" goes away. Recommended was A, a provider "Codex" that runs the conversation through the installed Codex and its own sign-in, as "Claude Code" does; B was A and the same for the Gemini CLI. | 4.80.0. `_plan` and `_route` in `modules/pmg_qt/chat_panel.py`. A and B are not built; they are listed under the small things in [PLAN.md](PLAN.md). |

Chosen while building 4.80.0, without asking, each the smaller option.
Say so if another one is wanted. Choice 76 (the sign-in row "for ChatGPT
and OpenRouter only") now reads: for OpenAI and OpenRouter.

| No. | Choice | Built | To change it |
| --- | --- | --- | --- |
| 113 | While signed in to ChatGPT the plan is used and the key field is hidden, also when `OPENAI_API_KEY` is set; "Sign out" brings the key back. The other way: a switch between plan and key. | 4.80.0. | `_route` and the line `self.key.setVisible` in `chat_panel.py`. |
| 114 | "ChatGPT" stays the name of the route in `assistant.ROUTES`, of the keychain entry and of the setting `chat/model/ChatGPT`, so a sign-in kept before 4.80.0 and its model carry over, and the models of the plan and of the key are remembered apart. A saved choice of "ChatGPT" opens "OpenAI". | 4.80.0. | The list of the box `provider` in `chat_panel.py` leaves that one name out. |

Decided by the user on 2026-11-25, in the run of 4.79.0 (the switch
"Run without asking"). They change decision 43 (a question before file,
network and destructive actions, and before Python) and replace the
switch of 108: the question is the default at every start, and the user
can turn it off for the run.

| Question | Decision | State |
| --- | --- | --- |
| 109 | Option B: the switch covers the reviewed commands and Python (with "Trusted Python" ticked). Recommended was A, commands only, since text the model reads can then run code unseen. | 4.79.0. `Executor.unasked` in `modules/pymol/agent.py`; to go back to A, take `not self.unasked and` out of the `python` branch of `Executor.call`. |
| 110 | Option A, recommended: "Run without asking" replaces "Download without asking". B kept both boxes. | 4.79.0. `Executor.downloads` and `DOWNLOADS` are deleted. |
| 111 | Option A, recommended: off at every start. B kept the tick in the settings. | 4.79.0. The check box `unasked` in `chat_panel.py` is not read from `QSettings`. |

Decided by the user on 2026-11-25, in the run of 4.77.0 (the UniProt
commands in the Chat tab). Decision 43 (a question before file, network
and destructive actions) holds for everything else.

| Question | Decision | State |
| --- | --- | --- |
| 107 | Option A, recommended: a UniProt download of up to ten entries is waited for by the chat; more, or all, load in the background and the model is told so. B was at most ten per action, C no limit with a blocked window. | 4.77.0. `_policy` in `modules/pymol/agent.py` sets `async_`. |
| 108 | Option B: the list of entries asks nothing, a download asks once per call, and a switch "Download without asking" in the Chat tab, off at every start, turns that question off for `fetch` and the three UniProt and fold downloads. Recommended was A, the same without the switch; C asked for the list too. | 4.77.0. `Executor.downloads`, `DOWNLOADS` in `agent.py`; the check box in `chat_panel.py`. |

Decided by the user on 2026-11-25, after the run of step 8 (4.76.1 to
4.76.14).

| Question | Decision | State |
| --- | --- | --- |
| 106 | Option C, "finish here": step 8 ends with what is built. The VLA macros, raw `new` / `delete`, the `ok_assert` chains and `ov/` stay as they are. Recommended was A (go on with what ends in a deletion). | Step 8 closed at 4.76.14; nothing to build. To reopen: the counts and the reasons per file are in [docs/plans/08-cpp-modernization.md](docs/plans/08-cpp-modernization.md). |

Decided by the user on 2026-11-25, after the grid surface experiment
(4.76.0). This records the choice; no new feature shipped.

| Question | Decision | State |
| --- | --- | --- |
| 105 — Does the grid surface stay, and for what? | Option A, recommended: keep it beside today's surface, which remains the default; add "Solid (grid)" in Setting > Surface and support carving and cavities. Use the grid with a probe of about 3 A for the rounded clay surface. Reconsider the default after the surface worker. | Grid surface available as `surface_type 7` since 4.76.0. Menu row, cavities and the solvent surface in 4.81.0 (carving worked already); clay and two more looks on it in 4.82.0. The worker is built (4.89.0); answer 129 A keeps Solid as the default. B (default above a size) and C (remove it) were not selected. |

Decided by the user on 2026-11-25, choices 91–97 from the GUI request of
2026-11-24, and built the same day.

| Question | Decision | State |
| --- | --- | --- |
| 91 | Delete key only (option B): bind keyboard Del to the selected object/group in the focused Objects list, keep the existing menu action, and add no new button. Objects are deleted without confirmation. | 37b. 4.69.0. |
| 92 | Confirm deletion of the group and all its members, including nested groups; show the scope before applying. | 37b. 4.69.0. |
| 93 | Recommended option A: hold the right mouse button on a row, drag and release to drop; a click without dragging still opens the context menu. Ordinary left-click visibility stays. | 23b. 4.70.0. |
| 94 | Recommended option A: extend all named built-ins to 30 colors by appending colors, preserving existing entries/order. Leave legacy “PyMOL default” and saved user palettes as they are; preview only the first 10 colors. | 37c. 4.71.0; 37d (dragging in the dialog) 4.72.0. |
| 95 | Mouse icon plus compact mode name, such as “Viewing” or “Editing”; full name in the tooltip. Also reduce the button's spare width and excess horizontal padding, sizing it to its content. Supersedes the expanding/shortened-label behavior of choice 84. | 37e. 4.73.0. |
| 96 | Recommended option A: A− / A+ and Reset at the right of the tab strip adjust the active tab's content; remember each tab's size separately. Tab-title fonts follow the application theme. | 37g. 4.75.0. |
| 97 | Option B: a row of Mode/Labels/Gaps dropdowns and an alignment button inside the Sequence tab. | 37f. 4.74.0. |

Chosen while building 4.68.0. Two options were offered first (this
provider, or nothing new), and brand marks or the plain icon; the answer
was "the solution for login can be icon or button; add OAuth
verification". Say so if another one is wanted:

| No. | Choice | Built | To change it |
| --- | --- | --- | --- |
| 86 | A Claude account is used through the Claude Code installed on the computer, as a provider of its own. A sign-in of pymolish to Claude.ai is not allowed by Anthropic (read again on 2026-11-24), and its Claude Platform OAuth (beta) links the API billing of an organization to a server product, which needs an identity provider. | 4.68.0. | `"Claude Code"` in `assistant.ROUTES`; `_claude_code` in `assistant.py`. |
| 87 | "Continue with Claude Code" starts Claude Code's own `auth login`; the row shows what its `auth status` reports. No Sign out: it would sign Claude Code out in every terminal. No "Stay signed in": nothing of the account is kept by pymolish. | 4.68.0. | `claude_login`, `claude_status` in `signin.py`; `_show_access` in `chat_panel.py`. |
| 88 | In the Chat tab Claude Code has the tool of pymolish only: its shell, file and web tools, its other MCP servers and the user's settings files are off, so the reviews, confirmations, Stop and Undo of the tab hold. Who wants Claude Code with all its tools uses the agent connector (31b) from a terminal. | 4.68.0. | The arguments `--restricted`, `--tools ""`, `--strict-mcp-config` in `_claude_code`. |
| 89 | A later turn resumes Claude Code's session, so Claude Code keeps a transcript in its own folder. The other way, no transcript, needs one Claude Code that stays running for the whole conversation. | 4.68.0. | `--resume` in `_claude_code`; `--no-session-persistence` with `--input-format stream-json`. |
| 90 | The button keeps the plain sign-in icon of the other two sign-ins. The marks of Claude, OpenAI and OpenRouter were not added: their rules for use were not read. | 4.68.0. | `"sign in"` in `icons.py`. |

Chosen while building 4.67.0, without asking, each as the request read. Say
so if another one is wanted:

| No. | Choice | Built | To change it |
| --- | --- | --- | --- |
| 81 | The Sequence tab always lists the sequence; `seq_view` only puts it into the viewport as well, so both places can be on. The other way was one switch and a preference for the place. An object with `seq_view` off for itself is in neither place. | 4.67.0. | `SeqInViewport` in `layer1/Seq.cpp` and `listed` in `SeekerUpdate`. |
| 82 | A click on SEQ opens the tab (the preferred place); "Show in viewport" and "Sequence alignment" are in the menu of its arrow, and Display > Sequence became "Sequence in Viewport". SEQ no longer shows a state. | 4.67.0. | The `seq` button in `pymol_qt_gui.py`. |
| 83 | The tab is drawn on the background color of the viewport with its label color, not in the colors of the theme: the colors of the residues are chosen for that background. | 4.67.0. | `CmdSeqRows` in `layer4/Cmd.cpp` sends the colors, `paintEvent` in `sequence_tab.py` uses them. |
| 84 | The mouse mode button gives up width down to that of SEQ, and Qt shortens its name in the middle ("3-…ng"); the names were not abbreviated. | 4.67.0. | Superseded by choice 95 on 2026-11-25: 37e, built in 4.73.0. `mouse.setMinimumWidth` in `pymol_qt_gui.py`. |
| 85 | The robot keeps Lucide's `bot`, drawn like the other four icons of the row (16 px, lines of 1.5, blue while the agent connector is on); no new drawing. | 4.67.0. | `"ai assistant"` in `icons.py`. |

Decided by the user on 2026-11-24, asked before 4.66.0 was built:

| Question | Decision | State |
| --- | --- | --- |
| 74 | Which sign-in in the browser the Chat tab gets, of the three that the providers allow: OpenRouter (recommended) and the ChatGPT plan. Not chosen: a sign-in to an API account at Anthropic through its `ant` tool. | 4.66.0, both. A real sign-in is open, order 2. |
| 75 | How long a sign-in lasts: both, this run only or kept in the keychain of the operating system. The new optional package `keyring` was named in the question. Replaces answer 48 for sign-ins; a typed API key is still kept for the run only. | 4.66.0: the box "Stay signed in", off at first. |

Chosen while building 4.66.0, each the smaller option. Say so if another
one is wanted:

| No. | Choice | Built | To change it |
| --- | --- | --- | --- |
| 76 | The sign-in has a row of its own under the provider row, shown for ChatGPT and OpenRouter only: with it in the first row the window would have to grow. The button reads "Continue with ChatGPT", as OpenAI's guideline asks, and so for OpenRouter. Its icon is Lucide's `log-in`; OpenAI's logo is not used. | 4.66.0. | `_show_access` in `chat_panel.py`. |
| 77 | The keychain holds one entry per provider: the OpenRouter key, or the ChatGPT refresh token (Windows keeps 1280 characters per entry). The registration of pymolish at ChatGPT, the e-mail and a random name of this installation are in the ordinary settings: they are not secrets. | 4.66.0. | The comment marked `ponytail:` above `kept` in `signin.py`. |
| 78 | Without "Stay signed in" an OpenRouter key is asked to expire after one day (the user can change that on OpenRouter's page): a key that nobody keeps should not live on. | 4.66.0. | `expiring` in `signin.openrouter`. |
| 79 | The provider and the model of each provider are remembered between runs, for the two providers with an API key too. The keychain and the network are not touched before the Chat tab is shown. | 4.66.0. | `chat/provider` and `chat/model/...` in `chat_panel.py`. |
| 80 | The signature of ChatGPT's ID token is not checked: the token comes straight from OpenAI's server over TLS and only its e-mail is shown. | 4.66.0. | The comment marked `ponytail:` in `signin.chatgpt`. |

Decided by the user on 2026-11-24: "select the recommended option for those
unanswered questions". That settles every question that was built with its
recommendation and still waited for a word:

| Question | Decision (the recommended option) | State |
| --- | --- | --- |
| 33 to 35 | The palette from the brand colors is named `halo`, has the twelve colors with the five of the brand book as published, and does not name the brand. | 4.41.0. |
| 36 | The icon of the Table button is `sheet`. | Step 30, 4.36.0 to 4.40.0. |
| 37 | The contact area of "protein-protein interaction" is orange. | Step 30, 4.36.0 to 4.40.0. |
| 38 | "remove crystallization additives" is one row, sugars and NAD(P) included. | Step 30, 4.36.0 to 4.40.0. |
| 39 | No preset leaves the preset menu. | Step 30, 4.36.0 to 4.40.0. |
| 40 | Undo of a preset takes back everything done after it, until 21g builds one stack. | 4.40.0; 21g open, order 4. |
| 41 | Shared tools, then the chat, then the connector. | 4.58.0 and 4.61.0. |
| 43 | Reviewed operations; a concrete confirmation for destructive, file and network actions; a separate trusted Python mode. | 4.58.0; the connector uses the same executor (4.61.0). |
| 44 | A Chat tab in the command area. | 4.58.0. |
| 45 | The toolbar button is `bot`, "AI assistant"; measured first: 1297 px of content in a 1305 px window at 150 %, nothing in the overflow menu. | 4.61.0. |
| 46 | The assistant is present but off until used; nothing listens and no request leaves before the user turns it on. | 4.58.0, 4.61.0. |
| 47 | Setup helpers for the installed Codex and Claude Code, after a check against each. | 4.61.0: a setup line to copy for each. Checked with Claude Code 2.1.322 (it listed the tool and called it in the real window); Codex 0.163.0 listed the server but had no credits for a call. The Codex call is open, order 2. |
| 48 | Keys from the session or the environment only; nothing is stored. | 4.58.0. The connector's token follows the same rule (4.61.0). For a sign-in in the browser the user chose otherwise on 2026-11-24 (answer 75, 4.66.0). |
| 57 | A click on an empty star rates up to it, on a filled one down to the one before. | 4.46.0. |
| 58 | Ctrl+L stays zoom only; `ligand_next` has Ctrl+Shift+M and Ctrl+Shift+H. | 4.51.0. |
| 59 | Each half of a bond has the color of its atom's ball. | 4.48.0. |
| 60 | SEQ keeps the strip toggle; the alignment window is in its context menu and in Display > Panels. | 4.57.0. |
| 61 | On WSLg a change of the UI scale waits for the next start, with a message that says why. | 4.43.1. Other displays change at once; 27c open, order 1. |
| 62 | A session may hold three things PyMOL does not know: the key `pymolish`, a seventh item in the record of a scene, and the key `pymolish_unique_settings`. | Built 2026-11-23, in 4.43.1 to 4.51.0. Since 4.63.0 the key `pymolish` also holds the shot list; since 4.64.0 the setting `bg_image_filename` may hold the picture as text, which PyMOL 3.2.0a reads. |
| 63 | A loaded structure opens with its ligands as `ball_and_stick`. | 4.49.0. |
| 64 | The CPK table stays as written, 28 elements. | 4.50.0. Comparing it with the RasMol manual is still on the user's list. |
| 65 | A scene is picked for Update, Rename and Delete with a right click or the arrow keys. | 4.44.0. |

Chosen while building 4.60.1 to 4.65.0, each the smaller or the recommended
option, under the same word of the user. Say so if another one is wanted:

| No. | Choice | Built | To change it |
| --- | --- | --- | --- |
| 66 | Rock > Random: "change directions by random amount of rotation from 15-180 degrees" was read as: spin a random 15 to 180 degrees about one axis, then about another one, either way round. | 4.60.1. | `RANDOM_DEG` and `_random_turn` in `action_toolbar.py`. |
| 67 | The connector: command `agent_server`, port 9257, MCP over Streamable HTTP with the standard library (no SDK), token from `PYMOLISH_AGENT_TOKEN` or new each run. | 4.61.0. | The other names considered: `mcp`, `connector`. A kept token needs the storage design of question 48. |
| 68 | The setup helper copies a line for the user to run; it does not run it and does not edit a client's file. | 4.61.0. | A button that runs `claude mcp add` after a confirmation. |
| 69 | 15e, fog: a "fog" / "no fog" row in the light menu, on top of any look (the plan offered this or a look with fog). Names: "balls in glass", "cartoon cylinders". Balls in glass draws `ball_and_stick` in the atoms' colors, not grey spheres: presets do not recolor. | 4.62.0. | One row in `menu.presets`; `preset.balls_in_glass`. |
| 70 | 15e, shade of the look "soft": `ambient_occlusion_scale` 16, chosen by eye on 1oky against 12, 20 and the default 25 (black blotches). | 4.62.0. | One number in `preset.LOOKS`. |
| 71 | 15e, color steps in the viewport: nothing built. The look "comic" already draws them there (`ray_trace_mode_3` in `anaglyph_header.fs`); a new setting was written, measured to change nothing, and taken out. | 4.62.0. | - |
| 72 | Step 19: the strip got a ruler of seconds for the playhead, so that a drag on a block can move it. State Sweep stays under Movie > Program: the Timeline has no shot of its kind. | 4.63.0. | A shot "state sweep" in `shots.py`. |
| 73 | 21f: FXAA is off when the program starts, because only WSLg was tried; the menu is one check row; the setting stops at 1 (no SMAA). | 4.65.0. | Default 1 in `SettingInfo.h`, once seen on Windows and macOS. |

Decided by the user on 2026-11-23:

| Question | Decision | State |
| --- | --- | --- |
| 53 | The reported freeze is the toolbar UI-scale change from 150 % to 120 %. | 27d, built in 4.43.1: reproduced on WSLg, where the scale now waits for the next start. 27c open, order 1. |
| 54 | The first sequence-window release includes loaded structure chains plus FASTA import/alignment, with secondary structure from loaded coordinates. | 33a–c, built together in 4.57.0 with optional local MAFFT (answer 55). |
| 56 | Standard CPK atom colors within selected residues. | 11c, built in 4.50.0 (`color_cpk`). |
| 55 (2026-11-24) | Optional local MAFFT executable. | 4.57.0; separately installed, Linux 7.505 tested. |
| 42 (2026-11-24) | Optional official OpenAI/Anthropic SDKs. | 4.58.0, the extra `ai`; installed footprint of SDKs and dependencies measured at about 27 MB. The live trial of step 31 is open, order 2. |

Built with the recommended answer on 2026-11-23, and decided so by the user
on 2026-11-24 (table above):

| Question | Built | Version |
| --- | --- | --- |
| 57 | A click on an empty star rates up to it, on a filled one down to the one before. | 4.46.0 |
| 58 | Ctrl+L stays zoom only; the new action has Ctrl+Shift+M and Ctrl+Shift+H, which can be changed in the shortcut editor. | 4.51.0 |
| 59 | Each half of a bond has the color of its atom's ball. | 4.48.0 |

## Finished steps

| Step | Detailed plan | Recommendation |
| --- | --- | --- |
| 25 | [Studio effects: floor, lights, surface looks](docs/plans/25-studio-effects.md) | Requested 2026-11-20. 25a-1, 4.34.0: the command `stage` (a floor that takes the ray-traced shadow, a mirror image) and the lights studio, top light and soft shadow. 25b-2, 4.35.0: five color themes. 25b-3, 4.81.0: the grid surface of 1b (4.76.0) as "Solid (grid)" in Setting > Surface, with cavity culling, the cavity modes and the solvent surface. 25b-1, 4.82.0: Presets > surface look with glossy, candy glass, frosted and clay, the last three on the grid surface with a probe of 3 A. Not built, and only if asked for: a shadow in the viewport (25a-2), the "wrap" light of clay in the shaders, the Gaussian blob of the trial. |
| 8 | [Modern C++ in the core](docs/plans/08-cpp-modernization.md) | Closed 2026-11-25 at 4.76.14 by the user's answer to question 106, "finish here"; not finished as planned. Done: the sanitizer job (8a), bounded strings (8b, 408 of 475 calls), Catch2 under the sanitizers (8h), the dead `#ifdef` branches (8i), the `malloc` half of 8c (230 of 297 allocation sites), the mechanical part of 8d (215 of 829 macro calls). Not done and no longer planned: raw `new` / `delete` (181 / 109, with 64 `DeleteP`), 611 VLA macro calls on raw pointers, the error chains of 8e (`ok_assert` 197, `goto` 24, `CHECKOK` 198), 8f, `ov/` (8g, 72 users, never measured), 60 string calls through a pointer. The macro layer of `MemoryDebug.h` and the directory `ov/` stay. Never checked for 4.76.1 to 4.76.14: MSVC, Apple Clang, GCC 11, `compare.py`, a window. |
| 37 | [GUI follow-ups of 2026-11-24](docs/plans/37-gui-followups.md) | Requested 2026-11-24, answered and built 2026-11-25, 4.68.1 to 4.75.0, seven slices: the old plugin no longer takes the names of the fetch commands (37a); Delete in the Objects list (37b); thirty colors a palette, ten in the preview (37c); colors dragged in the palette dialog (37d); a compact mouse mode button (37e); Mode, Labels and Gaps lists and the alignment button in the Sequence tab (37f); A−, A+ and Reset beside the tabs (37g). |
| 23 | [Rename and move rows in the Objects panel](docs/plans/23-rename-in-panel.md) | Requested 2026-11-20. 23a, 4.24.0: F2 or "rename" edits the name on the row. 23b, 4.70.0: a row is moved by a drag with the right button or with Alt and the arrow keys, between rows, into a group and out of it; the order and the groups are the core's and are kept in a session. |
| 19 | [Movie timeline](docs/plans/19-movie-timeline.md) | The Timeline panel in 4.18.0 (shot list, strip, record, tours, effects, easing, export with an estimate); in 4.63.0 the shot list in the session, dragging on the strip under a ruler of seconds, and Movie > Program without Camera Loop, Scene Loop and State Loop (116 rows). The keyframe strip of the core stays (question 7). Not built: undo of timeline edits, lanes for object motions, a shot "state sweep", rendering through the Export presets was never run (needs ffmpeg or ImageMagick). |
| 33 | [Sequence alignment window](docs/plans/33-sequence-window.md) | 4.57.0, slices 33a–c delivered together: loaded chains plus FASTA, optional local MAFFT, mapped secondary structure and selections, structure fitting/Undo, consensus/identity/export and session rows. Platform launch checks remain alongside 27c. Added 4.67.0, not from the plan: the sequence of the loaded objects in a tab between Command and Chat. |
| 0 | [UI engine research](docs/plans/00-ui-engine.md) | PySide6 + Qt Widgets; preserve the renderer while simplifying bindings. |
| 3 | [Modern workspace and metadata](docs/plans/03-modern-ui.md) | Named docks with a saved layout, the Objects panel in Qt, the action toolbar on top and the command area at the bottom, the dark theme, the UI scale, scenes as a dock, Qt menus. Closed on 2026-11-20 without its metadata table: the property table of [step 22](docs/plans/22-property-table.md) replaces it. Its open rows went to 22e (a picked atom selects its row), 23b (rows moved by dragging) and question 31 (scene buttons and sequence text drawn by the core); the spacing of dialogs is fixed when a dialog is touched. |
| 24 | [Ligand in 2D with its contacts](docs/plans/24-ligand-2d.md) | Requested 2026-11-20; 4.32.0 and 4.33.0 (the command `ligand_2d` and the panel), 4.43.2 (the picture fits, 24d) and 4.56.0 (24c: the pocket's outline, solvent halos, metal contacts, Show in 3D, distances in tooltips, Tab through the residues). Water bridges, halogen bonds and dragging residues were left out on purpose. |
| 36 | [Next ligand with polar contacts](docs/plans/36-ligand-navigation.md) | Requested, planned and built on 2026-11-23, 4.51.0, one slice: `ligand_next` walks the ligands of the 2D panel, shows each as `ball_and_stick` with the site as sticks and the polar contacts as dashes, zooms, and takes back at the next step only what it turned on. Ctrl+Shift+M and Ctrl+Shift+H; Ctrl+L stays zoom only (question 58). |
| 35 | [Scenes recall appearance, one click](docs/plans/35-scene-appearance.md) | Requested, planned and built on 2026-11-23, 4.44.0 and 4.47.0, two slices. A click or Enter recalls a scene. A scene keeps the cartoon type, the settings of atoms, bonds and objects, the light and background settings and the definitions of the colors it uses, and takes away overrides that were not there. Its session record has a seventh item (question 62). |
| 28 | [Session format](docs/plans/28-session-format.md) | `.psex` in 4.26.0 (28a); the one session key `pymolish` for what the fork adds in 4.45.0 (28b), with the table columns as its first user and the walk of `ligand_next` as its second. The shot list of step 19 goes under it when that slice is built. |
| 22 | [Property table](docs/plans/22-property-table.md) | 4.27.0 to 4.29.0 (the window, editing, import and export), 4.45.0 (columns in the session, counted columns, Follow, the row of a picked atom, the size between starts) and 4.46.0 (stars). Not built: sequence length as a counted column, coloring rows by a column, a 2D structure column. |
| 11 | [Color palettes](docs/plans/11-color-palettes.md) | Five palettes and the toolbar button in 4.10.0, `halo` in 4.41.0, `color_cpk` in 4.50.0 (11c). The CPK table was written from what is known of the RasMol manual and not compared with it in that run (question 64). |
| 30 | [Eight repairs after a first look at 4.35.0](docs/plans/30-polish.md) | Requested, planned and built on 2026-11-20, 4.36.0 to 4.40.0, six slices: the 2D picture, the property table, the live UI scale, the preset menu and what a preset may color, a clean row for crystallization additives, Undo and Redo for a row of the preset menu. Questions 36 to 40 have built answers. |
| 29 | [Version numbers](docs/plans/29-versioning.md) | The first number stays 4. The second goes up when something a user can see ships, the third for every other change to the program; plans, docs, CI and tests take no number. In `AGENTS.md` §5 since 2026-11-20; 4.20.0 is the first version under it. |
| 26 | [Action toolbar: Bg, Open, quick select, layout](docs/plans/26-toolbar-buttons.md) | "Bg" with a paint roller; an Open button with the rows of File that bring something in; chips P, L, S, a menu with chains and more, All and "nothing", with Shift to add and Ctrl to take away; one row, 1154 px at 150 %, with a text only on Residues, Presets, Bg, Draw and the scale. 4.20.0, 4.21.0, 4.30.0. |
| 2 | [Code and dependencies](docs/plans/02-cleanup-dependencies.md) | One feature removal per PR; trace dependencies before deleting. |
| 4 | [Features and external libraries](docs/plans/04-extensibility.md) | Preserve `cmd` and the existing loader; document small integration patterns. |
| 5 | [Builds and test binaries](docs/plans/05-builds-binaries.md) | Improve incremental builds and deliver test artifacts before large changes. |
| 6 | [States panel](docs/plans/06-states-panel.md) | First, previous, play/stop, next, last, jump and speed in the Objects dock; replaces the state label and the toolbar's movie buttons. |
| 7 | [Toolbar icons and UI scale](docs/plans/07-toolbar-icons-scale.md) | Line icons on every action toolbar button, Undo and Redo icon-only, 150 % default scale, scale button in the toolbar; replaces Display > UI Scale. |
| 9 | [Own icon and logo](docs/plans/09-icons-logo.md) | Allowed and asked for by the license. One master PNG; window title and About box stop saying PyMOL. New art (blue, green and violet ribbon) in 4.19.27. |
| 10 | [README and license files](docs/plans/10-readme-license.md) | New README naming the fork; PyMOL notice kept word for word, new code MIT, third parties listed; two allowed slogans with the trademark footnote. |
| 12 | [pymolish plugin commands, native](docs/plans/12-native-commands.md) | Command bodies ported, not the framework: 58 plugin commands became 18 (19 since 4.12.9, `fetch_uniprot_ligands`), in five files; two dialogs, five menu entries, no new top menu. rdkit is the optional extra `chem`. |
| 13 | [Clean, fix and optimize structures](docs/plans/13-structure-cleanup.md) | Four layers, each shipped alone: remove water, ions and ligands; `clean` for ligands (rdkit); `fix_structure` (PDBFixer); `minimize` (OpenMM). PDBFixer and OpenMM are the optional extra `fix`. |
| 20 | [Look of the action toolbar, own palettes](docs/plans/20-toolbar-look.md) | Names on Palette and Background, icon-only view actions, larger and heavier icons, blue for what is chosen, a camera for Scenes, ray tracing with or without the background, palettes of the user. The two follow-ups shipped in 4.23.0: blue hover in every menu of the program, Orient on what is visible. "Background" became "Bg" in 4.20.0 (step 26). |
| 18 | [Dialog sizes and the scroll bar of the sequence viewer](docs/plans/18-dialogs-scrollbar.md) | The form loader sets a form up on the dialog itself; the sequence viewer scrolls with a Qt scroll bar. |
| 17 | [Legacy menu rows and the old internal GUI](docs/plans/17-legacy-ui.md) | Menu rows that led nowhere, the Tk stand-ins, then the C++ code of the old panel and of the GL menus: 316 lines of Tk stand-ins and 4,160 lines of panel and menu code deleted in five slices, each a working program. A sixth slice, 17f (4.25.0): the scene buttons of the viewport, 498 lines. |
| 16 | [Background menu and palette caption](docs/plans/16-background.md) | A toolbar button with 13 backgrounds, plain and gradient, remembered only when asked; the palette menu says what it colors. |
| 14 | [Action and right-click menus](docs/plans/14-menus.md) | One builder for objects and groups, one for selections; the A menu of an object has 10 rows, the rest under "more"; right click on a row gives rename, duplicate and delete at once. `menu.py` 1,869 to 1,745 lines. 14d (4.19.2): "select" and "split" rows by chain and by kind of molecule, new command `split_types`; presets left the A menus; "split by state" moved there in 4.19.3. 14e (4.19.31, 4.19.32): one list in Show, cartoon styles and hydrogens as hover menus, Show 21 to 15 rows, Hide 22 to 17. |

## Earlier completed scopes, reopened by the 2026-11-26 request

| Step | Completed scope | New work |
| --- | --- | --- |
| 34 | [Independent ball-and-stick](docs/plans/34-ball-and-stick.md), 34a–34c in 4.48.0/4.49.0: representation 21, its own visibility and three settings, native bond orders, ligand defaults without changing sphere/stick settings, and compatible storage of fork-specific atom settings. | 34d, transparency: done 2026-11-26 in 4.84.0. The step is finished again. |
| 32 | [Footer icons and Movie button](docs/plans/32-footer-icons-movie-button.md), 32a/32b in 4.42.0/4.43.0: mouse mode/SEQ with text, Wizard/Command as icons, Movie opens/closes Timeline. In 4.67.0 AI moved after SEQ and SEQ opens its tab; 4.73.0 shortened the mouse-mode label. | 32c, larger icons and short labels with a second row when narrow: done 2026-11-26 in 4.86.0. The step is finished again. |

## Finished work, in execution order

The letters identify milestones in the detailed plans. Of order 5 (measured
optimization and workspace increments) the optimization is still open and
stays in the roadmap; the workspace half closed with step 3 on 2026-11-20.

| Order | Work | Exit condition | Result |
| --- | --- | --- | --- |
| 1 | **0 — UI decision** | PySide6/Widgets recommendation, supported platforms and GL smoke checks are explicit. | Small research task; implemented in working tree 2026-11-08, see step 0 Status |
| 2 | **5a + 1a — feedback and baseline** | Repeatable build/test commands and recorded build/performance timings before removals. | Done 2026-11-08: [docs/baseline.md](docs/baseline.md), `testing/bench.py` |
| 3 | **2a — binding and legacy GUI cleanup**, with **4a — plugin contract** | Explicit runtime binding; alternative bindings removed in one PR; plugin migration precedes separate Tk and GLUT removals. | Done 2026-11-08: 4.1.0 bindings, 4.3.0 Tk + plugin contract, 4.3.1 GLUT |
| 4 | **5b — downloadable application**, alongside **2b — independent removals** | Tester launches without installing Python; each removal passes its own checks. | 5b done 2026-11-08 (4.4.0, Linux verified locally, CI artifacts for 3 OS; 4.5.1 publishes archives on a GitHub pre-release per push to master); 2b done 2026-11-08 (4.4.1 to 4.4.8): chempy.fast, VTK-m, mpeg_encode, RPC/HTTP/web, OpenVR, COLLADA+libxml2, MMTF, dev utilities. Kept: VMD plugins/netcdf, xwin paste, POV-Ray renderer |
| 6 | **4b — extension examples and proven helpers** | Command/menu integration documented; any dock helper has real consumers. | Done 2026-11-12: [docs/plugins.md](docs/plugins.md); no dock helper, no two consumers yet |
| 7 | **6 — states panel** | States of a trajectory and frames of a movie are stepped, played and timed from one panel. | Done 2026-11-13 (4.6.0): [docs/plans/06-states-panel.md](docs/plans/06-states-panel.md) |
| 8 | **7 — toolbar icons and UI scale** | Every toolbar button has an icon; the interface starts at 150 % and the scale is picked in the toolbar. | Done 2026-11-13 (4.7.0): [docs/plans/07-toolbar-icons-scale.md](docs/plans/07-toolbar-icons-scale.md) |
| 9 | **10a — README and license text** | The repository presents itself as a fork with both license files. | Done 2026-11-14 (4.9.0): [docs/plans/10-readme-license.md](docs/plans/10-readme-license.md). 14a, the other half of order 9, shipped in 4.10.1. |
| 10 | **9 — icon and logo** | Window and bundle show the new art; nothing shows the PyMOL logo. | Done 2026-11-14 (4.8.0): [docs/plans/09-icons-logo.md](docs/plans/09-icons-logo.md). The rights line for the two images came on 2026-11-20 (4.19.43). Open: a look at the Windows artifact. |
| 10 | **10b — images in the README** | README shows the logo and one screenshot. | Done 2026-11-14 (4.9.0): the icon and [docs/img/window.png](docs/img/window.png). The icon is used, not `logo.png`: its dark text does not show on a dark page. |
| 11 | **11 — color palettes** | A palette picked in the toolbar colors new objects and is back after a restart. | Done 2026-11-14 (4.10.0): [docs/plans/11-color-palettes.md](docs/plans/11-color-palettes.md). `util.cbc` still uses the PyMOL order. |
| 12 | **12a to 12e — native commands** | Kept plugin commands work without the plugin, from the command line and from File, Build and the group menu. | Done 2026-11-14 (4.11.0 to 4.11.4): [docs/commands.md](docs/commands.md). 12a groups, 12b folder load and export, 12c UniProt and predicted structures, 12d SMILES with rdkit, 12e sequence search and ligand clusters. The plugin in `~/.pymol/startup` still wins over the native names: remove it. |
| 13 | **13a to 13d — cleanup** | Water and ions go in one click; `clean` works on ligands; a protein is repaired and relaxed into a new object. | Done 2026-11-14 (4.12.0 to 4.12.3): the A > clean submenu, `clean`, `fix_structure`, `minimize`. Not built: gaps in a chain (PDBFixer needs SEQRES records). `minimize` has no ligand parameters. |
| 14 | **14a to 14c — menus** | Approved keep, merge, drop list applied; fewer rows and fewer lines in `menu.py`. | Done 2026-11-16 (4.13.0): [docs/plans/14-menus.md](docs/plans/14-menus.md). 14a in 4.10.1 (red trash icon on destructive rows), 14b on 2026-11-14 (audit, table of nine rows), 4.12.5 (zoom, orient, center, origin left the menus), 14c in 4.13.0 (all rows of the table). This was also slice 6 of step 3. |
| none | **16a to 16c — background** | The menu ships with the rows that passed 16b. | Done 2026-11-18 (4.15.0): [docs/plans/16-background.md](docs/plans/16-background.md). All 13 candidates passed the ray-traced trial. Rock became icon-only to keep the toolbar inside the default window at 150 %. |
| none | **20 — toolbar look** | The bar fits the default window; each option that was chosen is listed with its alternatives. | Done 2026-11-18 (4.19.0): [docs/plans/20-toolbar-look.md](docs/plans/20-toolbar-look.md). |

Sequencing used for orders 1 to 6: cleanup preceded speculative optimization;
recording a baseline was preparation. UI work needed the binding decision and a
usable test build, not completion of every unrelated removal. Plugin
compatibility work started before Tk removal; artifact work started after the
binding change while the remaining legacy cleanup proceeded.

Decided on 2026-11-14 and applied: rdkit, PDBFixer and OpenMM are approved
optional dependencies (`AGENTS.md` §2.2); the palette is remembered in
`QSettings`; `LICENSE` got a header above the unchanged notice.

Decided by the user on 2026-11-16 and applied:

| Decision | Applied in |
| --- | --- |
| The product name stays, with the mark "PyMOL" in it; the risk is accepted. | No change; noted in plans 9 and 10. |
| No more merges from upstream PyMOL. | `AGENTS.md` intro and §2.4; step 8 is not limited to files the fork already changed. |
| Python 3.13 and 3.14 only. | 4.12.8: `requires-python = ">=3.13"`. |
| `fetch_uniprot_ligands` comes back; the other dropped plugin commands stay dropped. | 4.12.9. |
| Menu table of 14b: the choice was left open; all rows were applied. | 4.13.0, step 14 finished. |
| Version rule: `X` bumps once per roadmap step, with its main user-visible change; everything else bumps `Y`. | `AGENTS.md` §5. |
| Merges to `master` are done by the user. | Listed in the roadmap under "Waiting for the user". |

Decided by the user on 2026-11-20, first round. The last column was brought
up to date through 4.43.0, with open orders revised 2026-11-23: a version
where the decision shipped, "open" with its order where it has not.

| # | Decision | Where it goes |
| --- | --- | --- |
| 1 | A large surface is built on a worker thread (option A). | 1b. Done 2026-11-26 in 4.89.0: `async_surface`; the window on 1aon is blocked 1.2 s at most instead of 5 s. |
| 3 | The icon and the logo were generated with ChatGPT; the user owns them. They get "a license that is good for trade marks". | Done in 4.19.43: `data/pymol/icons/LICENSE`, a notice outside the two code licenses (unchanged copies travel with the program and may refer to it; a changed version needs its own). `docs/licenses.md`, plan 9. |
| 4 | The release builds stay on GitHub Actions for now. | 5c is shelved; nothing was built for it. Plan 5. |
| 5 | The outline of the looks is drawn in the viewport too: black, or a color that shows on the chosen background. | 15b. Done 2026-11-26 in 4.87.0, as one more step of the FXAA pass of 4.65.0: `viewport_outline`. |
| 6 | The ChimeraX object colors become a palette. | 15c. Done in 4.22.0. |
| 7 | All five effects of 15e. | Done in 4.62.0: two presets, the fog row, shade in the soft look; the fifth, color steps in the viewport, was already there (choice 71). |
| 13 | "Decide by yourself." Decided as recommended: the shot list goes into the session file; the 58 Program rows of the Movie menu go; the keyframe strip of the core stays for now. | Step 19. Done in 4.63.0. The rows counted in the menu were 116 (49, 43 and 24), not 58. |
| 15 | As recommended: blue hover in every menu; Orient acts only on what is visible. | Step 20. Done in 4.23.0. |
| 16 | As recommended: FXAA for smooth edges; `sphere_mode` capped at 9, its test and two reference images deleted; the background image stored in the session file. | 21f. Done in 4.63.1 (sphere modes), 4.64.0 (background picture) and 4.65.0 (FXAA, off by default: choice 73). |
| 18 | As recommended: idle OpenMP threads sleep at once. | 1b. Done in 4.23.1. |
| 17 | As recommended: undo by snapshots for edits, the coordinate ring for moves (option C). | 21g. A first piece in 4.40.0: a row of the preset menu (30f). The rest open, order 4. |
| 19 | Yes: the grid surface is tried as an experiment, then judged on numbers and pictures. | 1b. Built as an experiment in 4.76.0 (`surface_type 7`); kept as an option by answer 105 A. Moved up by the answer to question 25. |

14 was answered by "release 17" (4.19.42).

Decided by the user on 2026-11-20, second round (questions 20 to 32 of the
ten-feature request). The last column gives the shipped result and, where
applicable, the 2026-11-23 follow-up.

| # | Decision | Where it goes |
| --- | --- | --- |
| 20 | The property table is a window of its own that can be closed and resized; it lies over the viewport and sticks to the Objects panel on the right. None of the three options offered. | [Plan 22](docs/plans/22-property-table.md), "Where the table lives". Done in 4.27.0. |
| 21 | As recommended: `.xlsx` is read with the standard library, no new dependency. | Plan 22, 22c. Done in 4.29.0. |
| 22 | As recommended: the rename wizard stays as the fallback without a window. | [Plan 23](docs/plans/23-rename-in-panel.md). Done in 4.24.0. |
| 23 | The 2D ligand drawing is our own code, rdkit allowed; interactive: selecting a residue in 2D selects it in 3D. | [Plan 24](docs/plans/24-ligand-2d.md); the selection goes both ways. Done in 4.32.0 (command) and 4.33.0 (panel). |
| 24 | Shadows ray traced only at first. | [Plan 25](docs/plans/25-studio-effects.md), 25a. Done in 4.34.0. |
| 25 | "Start with 1b then plan further. Do not add to settings yet." | The grid surface of 1b moved up and was built in 4.76.0, then kept by answer 105 A. The surface looks were built on it: 4.81.0 (the grid as a menu row with its cavity settings) and 4.82.0 (glossy, candy glass, frosted, clay). |
| 26 | As recommended: one row, icons. The same day: Builder and Scenes show only the icon, the name on mouse-over; "Draw/Ray" becomes "Draw". | Builder, Scenes and Draw done in 4.20.0; the rest in 4.30.0. |
| 27 | The paint roller. (The answer ends "rest", cut off.) | Done in 4.20.0 with "Bg". |
| 28 | As recommended: live scale through Qt's private function, the "next start" message as fallback. | [Plan 27](docs/plans/27-ui-scale.md). Done in 4.31.0 on Linux; 27d investigates the new freeze report before platform verification in 27c, open at order 1. |
| 29 | As recommended: `.psex` is what Save Session writes; a `.pse` carries the new data too. | [Plan 28](docs/plans/28-session-format.md). The file type done in 4.26.0; the key for new data (28b) comes with its first user. The background picture of 21f stays in its setting. |
| 30 | As recommended: the version rule by what changed for the user. | Done: `AGENTS.md` §5, step 29. |
| 31 | As recommended: the scene buttons the core draws are deleted; the sequence viewer stays. | Scene-button removal done in 4.25.0. The sequence decision is superseded by the separate alignment window of step 33 (2026-11-23), built in 4.57.0; the strip stays as a separate toggle. |
| 32 | As recommended: color themes set protein color and background, as a group of their own. | Plan 25, 25b-2. Done in 4.35.0, ahead of 15e. |

Questions 33 to 35 (11b, the palette from the user's brand colors: its name,
its colors, whether the brand is named) were answered on 2026-11-20 with
"add this to code", without a choice. The recommended options were built
in 4.41.0: `halo`, twelve colors with the five of the brand book as
published, the brand not named.

Decided by the user on 2026-11-20, questions 49 to 52 (step 32), built the
same day:

| # | Decision | Where it went |
| --- | --- | --- |
| 49 | B: icons for Wizard and the command line, the mouse mode keeps its name beside its icon. | 4.42.0. |
| 50 | "SEQ with letters but before the wizard. Wizard next." The four drawings as proposed. | 4.42.0: mouse mode, SEQ, Wizard, command line. |
| 51 | The video icon. | 4.43.0: `video`, also on the "movie" rows of the menus. |
| 52 | The button opens and closes the panel. | 4.43.0. |

Also on 2026-11-20: `plan_images/` is not committed and is ignored by git;
it is deleted when the last plans made from it (22d, 24c, 25b) are built; 22d and 24c are. Its `:Zone.Identifier`
files are deleted. The line `set internal_gui_width, 400` is out of the
user's `~/.pymolrc`.

Old decisions replaced by the second request of 2026-11-20 (ten features,
steps 22 to 29). The request said: where the new plans contradict the old
ones, the new ones win.

| Old decision | Where it was | Replaced by |
| --- | --- | --- |
| A read-only metadata table, one of the slices of step 3; "no editable grid". | Plan 3, slices 2 and 3, "Acceptance checks and scope" | [Step 22](docs/plans/22-property-table.md): an editable table on the object properties of the core, with import and export. Done in 4.27.0 to 4.29.0. Step 3 is closed. |
| Rename through the wizard that types into the viewport. | Plan 14 (the row "rename" of the A menu) | [Step 23](docs/plans/23-rename-in-panel.md): the name is edited on the row. Done in 4.24.0. |
| "Palette and Background carry their names." | Plan 20 | [26a](docs/plans/26-toolbar-buttons.md): "Bg" and a new icon. Done in 4.20.0. |
| The bar must fit 940 px; names on Builder, Scenes and Draw/Ray. | Plans 7 and 20 | [26d](docs/plans/26-toolbar-buttons.md): the bar is one row of icons, 1195 px at 150 % with every planned button (4.33.0); the default window opens that wide. |
| UI scale in five steps from 100 to 200 %, applied at the next start; "live rescale without restart: skipped". | Plans 3 and 7 | [Step 27](docs/plans/27-ui-scale.md): any value from 50 to 300 %, live where Qt allows it. Done in 4.31.0. |
| The shot list goes "into the session file". | Plan 19 | Unchanged in substance: it goes under the one key of [step 28](docs/plans/28-session-format.md), which is built with it. The background picture of 21f stays as decided: the answer to question 29 did not move it. |
| A look leaves the background alone; a preset keeps the protein colors. | Plan 15, 15g and 15h | Still true for looks and presets. The color themes of [25b](docs/plans/25-studio-effects.md) set both, as a group of their own (question 32). Done in 4.35.0. |
| The version: the second number once per roadmap step. | `AGENTS.md` §5 | [Step 29](docs/plans/29-versioning.md): done, the new rule is in `AGENTS.md`. |

## Finished milestones of open steps

Steps 1, 15, 21, 27, 31 and 38 stay in the roadmap (15 for the glow menu follow-up).
These parts of them have shipped. The rows of steps 3, 11, 17, 18, 19, 20, 22, 26,
23, 24, 25, 28, 30, 32, 34, 35, 36 and 37, which are finished, are kept here as the record of
their milestones. The rows are not in order of time: the newest, the
alignment window without the line of characters (4.90.0), the
seven rows of 2026-11-26 (4.83.0 to 4.89.0, the last built first), the
surface looks (4.82.0) and the grid surface as a menu row (4.81.0), the
ChatGPT sign-in inside "OpenAI" (4.80.0), the
switch "Run without asking" (4.79.0), the
commands of the chat (4.77.0 to 4.78.0), the
grid surface (4.76.0) and the
eight rows of 2026-11-25 (4.68.1 to 4.75.0, the last built first), the
provider "Claude Code" (4.68.0), the
Sequence tab (4.67.0), 31d
(4.66.0) and the seven
rows of 2026-11-24 (4.60.1 to 4.65.0), are at the top, the last built first;
under them the rows of 4.56.0 to 4.60.0 and the ten rows
of 2026-11-23 (4.43.1 to 4.51.0); under
them 4.42.0 and 4.43.0, 32b and 32a; under them 4.41.0, 11b;
under it the block 4.36.0 to 4.40.0, the six rows of step 30; the block before it, 4.20.0 to 4.35.0, is
the one from "25b-2" to "17f".

| Step | Milestone | Result |
| --- | --- | --- |
| 38 | 38a to 38d — current documentation and real demos | Done 2026-11-26 at 4.90.0, no version (docs only): [docs/plans/38-documentation.md](docs/plans/38-documentation.md). Answers 126 A (Markdown in the repository) and 127 A (MP4 behind a poster). `docs/README.md` (home), nine task guides (`structures`, `appearance`, `ligands`, `sequences`, `properties`, `scenes-movies`, `editing-analysis`, `saving`, `assistant`), `reference.md`, `troubleshooting.md`; `commands.md` by task with an index of all 350 registered commands; README, Getting started and the overview rewritten; package metadata points at the docs home. 14 pictures of the real window, 3 sheets of rendered pictures, 4 clips of 19 to 31 s (401 to 996 KB) with posters; recipes and capture scripts in `docs/media/`. `license_docs.py` also checks anchors (207 links), the way from the home to every page, and that every command has an entry. Differs from the plan: nine guides were written by five helper sessions from the code, with every printed command run headless, and reviewed here; the window steps were done by Qt mouse events in capture scripts, not by hand; WSLg cannot grab the screen, so menus are laid on the window picture and the clips have 3.7 to 6.7 real pictures per second; two pictures are over 500 KB (530 and 567 KB); no picture of the Builder, a measurement or the two surface types; the Chat picture is the set-up row only; playback on GitHub, Windows, macOS and a reader new to the window are open (order 5). Faults found in the program on the way are listed in the plan and were not repaired. |
| 33 | The secondary structure only as the drawn track (a request, not a plan slice) | Done 2026-11-26 (4.90.0): [docs/plans/33-sequence-window.md](docs/plans/33-sequence-window.md). In the Sequence alignment window the line of characters above every residue (helix, sheet, coil, unassigned, no coordinates) and its legend are gone; the consensus track at the bottom, drawn since 4.60.0, is the one place that shows secondary structure, and the check box "Secondary structure" switches that track. A row is one line high: measured offscreen with the four chains of 4hhb, 18 px for a sequence row and 35 px for the track (two lines before; that height was not measured). The tooltip of a residue still names its own secondary structure. Against the plan: plan 33 had "graphical symbols on the structure rows" as not done; the request goes the other way and takes the characters out. A residue without coordinates has no mark in the table any more, only its tooltip. Not tried in the real window on WSLg, on Windows or macOS. Suite 1185 passed, 254 skipped. |
| 1 | 1b — the surface worker | Done 2026-11-26 (4.89.0): [docs/plans/01-performance-gpu.md](docs/plans/01-performance-gpu.md). A surface of 5000 atoms or more that the window asks for is built on a thread of its own (`async_surface`, on); the result is taken on the main thread from the idle loop and from every window frame; every other scene update, sized images and movie frames wait for running builds. Against the plan: The plan named a status line: it is two lines in the log. Measured in the real window on 1aon: the GUI thread blocked 1.2 s at most (4.9 and 5.5 s before); grid surface 0.9 s (1.7 s). 4v6x not run (10 of 17 GB). A crash found by the window test and fixed before the commit: the progress report of the triangulation called Python from the worker thread. Suite 1185 passed, 254 skipped; ASan and UBSan clean on the worker, grid, preset and ball-and-stick tests and on the two window tests. Answer 129 A keeps Solid as the default; the grid stays optional. |
| 15 | 15p — the glow experiment | Done 2026-11-26 (4.88.0): [docs/plans/15-presets.md](docs/plans/15-presets.md). `set glow, 1`: what is drawn, masked by the depth, blurred at a quarter of the size in three stages (`glow.fs`) and laid on the background in `fxaa.fs`. No menu row, no preset. Against the plan: An experiment, as planned; answer 128 A keeps it viewport-only and schedules the menu entry (open, order 3). Measured: about 2.5 ms a frame at 1436 x 702 (4hhb spheres 4.2 to 6.7 ms, 1aon spheres 6.0 to 8.5 ms). GPU memory computed from sizes, not measured. Not in ray-traced pictures, sized images or stereo; one driver. Found on the way: the helper that reads the viewport in the window tests returned freed memory. |
| 15 | 15b — the outline in the viewport | Done 2026-11-26 (4.87.0): [docs/plans/15-presets.md](docs/plans/15-presets.md). With `ray_trace_mode` 1 to 3 the pass that smooths edges draws lines found in the depth; two copies of the depth a frame, so that the cartoon inside a see-through surface has its line; the setting `viewport_outline` (on) and a row in Setting > Rendering. Against the plan: The plan of 2026-11-20 named a pass of its own: it is one more step of the FXAA pass. Measured at 1436 x 702: 2 to 3 ms a frame (1oky spheres 2.8 to 5.7 ms, 1aon spheres 5.2 to 8.2 ms, 1aon cartoon 11.1 to 13.1 ms). Pictures on white and black in `docs/img/viewport-outline.jpg`. Not in stereo or sized images; in grid mode the inner line is right only in the last cell; one driver. |
| 32 | 32c — larger buttons under the object list | Done 2026-11-26 (4.86.0): [docs/plans/32-footer-icons-movie-button.md](docs/plans/32-footer-icons-movie-button.md). Five buttons with an icon of 20 px and a short text, 32 px high; two rows when one does not fit. Against the plan: As answer 121. Measured in the real window, dark and light theme, 100, 150 and 200 %: one row needs 390 px, two rows 222 px; the footer is 32 or 66 px high; at the default width of 300 px it is two rows and the list is 34 px shorter. Windows and macOS not seen. |
| 15 | 15o — the Presets menu in groups | Done 2026-11-26 (4.85.0): [docs/plans/15-presets.md](docs/plans/15-presets.md). cartoon, atoms and bonds, surface, binding; transparency and solvent; light, theme and floor under "Scene appearance". Against the plan: As answer 125 A. 69 leaves, each with one Undo snapshot; the set of presets is the one of the flat menu. The toolbar menu was walked with the arrow keys in the real window, three levels deep. The menus the viewport draws itself take no keys, as before. |
| 34, 15 | 34d and 15n — transparency | Done 2026-11-26 (4.84.0): [docs/plans/34-ball-and-stick.md](docs/plans/34-ball-and-stick.md). `ball_and_stick_transparency`, read where the representation forced opacity, also for a ball without bonds; Presets > transparency with four representations and four values. Against the plan: As answer 124 A. Frame time 1aon, all atoms as ball and stick: 20.9 and 21.9 ms opaque, 19.1 ms at 50 %. PyMOL 3.2.0a loads, ray traces and saves a session with the setting. Not built: clipping and multiple-bond pictures of their own (the stick code is shared). |
| 15 | 15m — reference recipes | Done 2026-11-26 (4.83.0): [docs/plans/15-presets.md](docs/plans/15-presets.md). space filling, illustrated atoms, licorice, bond shell; "contour cartoon"; "glossy (light only)". Against the plan: As answer 123 A. The comparison sheet is `docs/img/reference-recipes.jpg` (ray traced and viewport, 1oky, 1aon, 1bna). Frame, build and ray times of the recipes were not recorded: they add no work of their own but the surface of bond shell (1aon: 25.8 s for the first ray-traced picture, surface build included). |
| 25 | 25b-1 — surface looks | Done 2026-11-26 (4.82.0): [docs/plans/25-studio-effects.md](docs/plans/25-studio-effects.md). `preset.surface(selection, material)` and the table `SURFACES` in `preset.py`; the submenu "surface look" of the Presets menu. Each row shows the surface of the protein and the ligands as balls and sticks, sets the light through `look` and, for candy glass, frosted and clay, `surface_type 7` with `solvent_radius 3` on the objects; transparency 0.55 and 0.3 on the atoms. `_prepare` now unsets `solvent_radius` on its objects, and a scene keeps it (`cSceneSettings`). Picture `docs/img/surface-looks.jpg`: 2rh1 without the lysozyme, ray traced at 400 x 340 on white and on black, 0.14 to 0.27 s each. One test more in `api/preset.py`, three extended (`menu.py`, `scene_style.py`, the ligand presets); the suite: 1178 passed, 250 skipped. Differs from the plan: the plan had four looks that only set settings; the rows show the surface themselves (question 115); glossy has no rounder surface; no viewport look and no real window in this run. |
| 25 | 25b-3 — the grid surface as a choice | Done 2026-11-25 (4.81.0): [docs/plans/01-performance-gpu.md](docs/plans/01-performance-gpu.md). "Solid (grid)" in Setting > Surface. In `SurfaceJobRunGrid`: `GridFieldFillHoles` (a flood over the second field) for `cavity_cull`, `GridPockets` (a coarse grid of the places where a probe of the cavity radius fits) for `surface_cavity_mode` 1 and 2, the first field as the surface for `surface_solvent`. Carving worked already. 1aon, fastest of two builds: 1.67 s with culling (914,220 triangles), 1.70 s without (924,276), mode 2 in 0.80 s (361,657; the dots 5.95 s and 402,726), mode 1 in 0.88 s, the solvent surface 1.31 s, a probe of 3 A 1.42 s (668,588); the dots 5.46 s. Against the dots on 2rh1 and 4hhb: 5 and 9 closed cavities kept (dots 7 and 8); mode 1 draws 71 % and 74 % of their area, the grid's points 0.44 and 0.42 A from the dots' on average; the solvent surface 0.33 and 0.35 A. Two tests more in `api/surface_grid.py` (4 now); the suite: 1176 passed, 250 skipped. The tests of `surface_grid.py`, `preset.py` and `scene_style.py` also pass in a build with the address and undefined-behavior sanitizers (the flags of the CI job, at 4.82.0). Differs from the plan: the target of a clay surface for 1aon under 1 s is not met (1.42 s); trimming is not followed. Compiled with GCC on Linux only. |
| 31 | The ChatGPT sign-in inside "OpenAI" (a request, not a plan slice) | Done 2026-11-25 (4.80.0): [docs/plans/31-ai-agents.md](docs/plans/31-ai-agents.md). In `chat_panel.py` the list of providers leaves "ChatGPT" out; `_plan` names the sign-in of the chosen entry (for "OpenAI" the ChatGPT plan) and `_route` who gets the conversation (the plan while signed in to it, else the key). `signin.py` and the routes of `assistant.py` are unchanged. A failed sign-in no longer resets the model field. Measured without a window (Qt platform "offscreen"): the smallest width of the tab is 565 px for "OpenAI" before a sign-in, as for "Anthropic", and 731 px signed in with an e-mail address of 19 characters, the same as the former entry "ChatGPT" had; Tab reaches the key field, the button and "Stay signed in" in that order. One test more and one extended in `api/signin.py` (20 now); the suite: 1174 passed, 250 skipped. Differs from the plan: 31d named a provider per sign-in; the user chose one entry for both ways in (question 112). No real sign-in to ChatGPT was made (order 2), and no real window was opened in this run. |
| 31 | The commands the model may run (a request, not a plan slice) | Done 2026-11-25 (4.77.0, 4.77.1, 4.78.0): [docs/plans/31-ai-agents.md](docs/plans/31-ai-agents.md). 4.77.0: the four UniProt and fold commands are reviewed; `fetch_by_uniprot` and `fetch_uniprot_ligands` above ten entries go through `cmd.async_`; the switch "Download without asking". Real window: 12 entries of P00533 with the switch on, no question, the call back in 0.01 s, the group complete after 4.2 s, longest pause of the window 0.17 s; the tab's smallest width 565 px with and without the switch. 4.77.1: `safe_eval` parses first and lets constants, names, containers and + - / through; before, an attribute walk reached `os` from `set_color` in the chat. 4.78.0: 198 of the 416 other commands added after a source scan and a reading of each one with Python logic, 286 of 504 in all; arguments that reach Python or a file are checked in `_policy` (`label`, `spectrum`, `fab`, `fragment`, `load_files`, `set_bond`, `png`, `REFUSED`). 18 tests more, all in `api/agent.py` (30 now); the two of `api/constants.py` were extended. Differs from the plan of 31: the plan asked a question for every network action; the list of entries asks none and the switch can turn the question for downloads off (choice 108). |
| 31 | "Run without asking" (a request, not a plan slice) | Done 2026-11-25 (4.79.0): one check box in the Chat tab, off at every start, in place of "Download without asking". `Executor.unasked` skips the question for every reviewed command and, with "Trusted Python", for Python; the Chat tab sets it on its own executor and on the connector's. Real window: the box is off at the start and reached by Tab; with it off a `delete` through the connector asked once and was declined; with it on the same call ran with no question and the turn kept its Undo snapshot; with "Trusted Python" ticked too, Python ran with no question. One test more in `api/agent.py` (31 now); the suite: 1173 passed, 250 skipped. Differs from the plan of 31 and from decision 43: the plan asked a question for every file, network and destructive action and for all Python; the user can now turn that off for a run (choices 109 to 111). |
| 1 | 1b — the grid surface, an experiment | Done 2026-11-25 (4.76.0): [docs/plans/01-performance-gpu.md](docs/plans/01-performance-gpu.md). `surface_type 7`: `SurfaceJobRunGrid` in `layer2/RepSurface.cpp` fills a grid with the distance to the atoms enlarged by the probe, takes the surface of the probe center with the marching cubes of `layer0/marching_cubes.cpp`, fills a second grid with the distance to it and cuts that one probe radius inside. The result uses the arrays of the triangulated dots, so drawing, colors and ray tracing are shared. Cells of two point separations (1 A at `surface_quality` 0). Fastest build, triangles, peak memory: 1aon 1.67 s, 924,276, 2,570 MB against 5.18 s, 905,146, 2,648 MB; 4v6x 9.41 s, 3,919,688, 10,173 MB against 34.31 s, 3,886,165, 9,983 MB. With cells of 0.5 A: 1aon 9.67 s, 3,992,212, 10,263 MB. With a probe of 3 A today's surface gets coarse and is the faster one (1aon 1.16 s and 195,556 triangles against 1.38 s and 668,588). 2 tests (`api/surface_grid.py`); the suite 1122 passed, 251 skipped. Pictures: `docs/img/grid-surface-1aon.jpg`, `grid-surface-4v6x.jpg`. Differs from the plan: no smoothness setting of its own, `solvent_radius` is that value; no ray times in the table (they drifted from 4.6 to 15.6 s for both surfaces as the laptop got warm; one cool pair gave 4.05 and 4.08 s); memory and ray time are not better, since they follow the triangles. Left out: carving, cavities, `surface_solvent`, trimming, frame times. |
| 37 | 37g — text size beside the tabs | Done 2026-11-25 (4.75.0): [docs/plans/37-gui-followups.md](docs/plans/37-gui-followups.md). `TabFontButtons` in `pymol_qt_gui.py`, the corner widget of the command tabs: A−, A+ and Reset move the text of the tab that is shown by one point; the difference to the start size is kept per tab in the settings. The Sequence tab recalculates its scroll ranges on a font change. 1 test in `api/sequence_tab.py`. Real window with a settings folder of its own: 12, 11 and 8 points after the clicks and at the second start, where a tab starts with 9. Suite: 1120 passed, 251 skipped. |
| 37 | 37f — lists and the alignment button in the Sequence tab | Done 2026-11-25 (4.74.0). `Options` in `sequence_tab.py`: three lists that set and follow `seq_view_format`, `seq_view_label_mode` and `seq_view_gap_mode` through the window's setting callbacks, and a button for the alignment window; the choices are one table, `SEQUENCE_OPTIONS` in `pymol/_gui.py`, from which Display > Sequence Mode is built as well. 1 test. Real window: "Residue Names" in the list changed the rows and the mark in the Display menu; the button opened the window. Differs from the recommendation: a row of lists, not one menu (the user's choice 97). |
| 37 | 37e — compact mouse mode button | Done 2026-11-25 (4.73.0). Icon and the name of the mode without its count of buttons, the whole name in the tooltip; size policy Maximum, a stretch after the five buttons. Real window on WSLg: 83 px for "Viewing" and 78 px for "Editing" (139 px for "3-Button Viewing" before), the same at 100, 150 and 200 %; narrowest panel 234 px before and after. 1 test that runs in a real window only. |
| 37 | 37d — colors dragged in the palette dialog | Done 2026-11-25 (4.72.0). Qt's internal move on the list of `palette_dialog.py`; OK stores the order shown. Checks added to `test_user_palette`. A real left-button drag on the dialog: the first of five colors dropped below the fourth. |
| 37 | 37c — thirty colors a palette | Done 2026-11-25 (4.71.0). The ten named palettes grew from 7 to 22 colors to 30 by appending; what they had keeps value and place. The added colors are computed (choice 101). The menu shows ten as before, a tooltip gives the number. 2 tests more; smallest RGB distance between neighbors 0.23 (pastel). Not checked for color-vision deficiencies. |
| 23 | 23b — rows moved by dragging | Done 2026-11-25 (4.70.0): [docs/plans/23-rename-in-panel.md](docs/plans/23-rename-in-panel.md). `ObjectPanel.move(name, target, where)` behind the drag with the right button and Alt+arrows: `cmd.group`, `cmd.ungroup` or the group action "raise" for the membership, then the whole new order through `cmd.order`. A line between rows or a frame on a group shows the place; a group does not go into itself (the core would accept that). The menu of a right click opens on release. 3 tests, one with a session round trip. Real window with real right-button input: a drag above a row, a drag onto a group, a click. Not tried on Windows and macOS. |
| 37 | 37b — Delete in the Objects list | Done 2026-11-25 (4.69.0). The Delete key on the current row; a group asks (default Cancel), names what is inside, nested groups included, and goes with it. The shortcut belongs to the list alone and does not repeat. 1 test. Real window: a click and Delete, a second press, the question of a group, Delete inside the rename editor. Differs from the recommendation: no trash button (the user's choice 91); one had been built and was taken out. |
| 37 | 37a — the fetch commands keep their names | Done 2026-11-25 (4.68.1). The reported `TypeError` of File > Get by UniProt came from the old pymolish plugin, which as a startup plugin registers its own `fetch_by_uniprot`, `fetch_fold`, `fetch_uniprot_ligands` and `load_smiles`; `PluginInfo.load` no longer loads a plugin of that name. 3 tests (`api/plugins.py`, `api/test_file_dialogs.py`). Reproduced and repaired in the real window with `~/.pymol/startup` in the startup path; on this machine that path is empty and the action worked before. Differs from the plan: no test with mocked network in `api/fetching.py`, the fault was not there. |
| 31 | 31d — a Claude account through Claude Code | Done 2026-11-24 (4.68.0): [docs/plans/31-ai-agents.md](docs/plans/31-ai-agents.md). The provider "Claude Code" of the Chat tab: each turn starts the installed `claude -p` with stream-json output; the tool is served to it by `agent_server.Server` on 127.0.0.1, on a port and with a token of that turn, the token in a file of a private folder; a later turn resumes the session. `signin.py` reads `claude auth status` and starts `claude auth login`. No SDK and no extra `ai`. 5 tests more in `api/assistant.py`, 3 in `api/signin.py`; the suite: 1109 passed, 250 skipped. Tried in the real window (WSLg) with Claude Code 2.1.322 on the user's Team plan, model haiku: the row showed the account; "how many atoms, color the carbons orange" took 4 tool calls and 5.92 s, the carbons had the color index of orange; a second turn answered from the same session in 2.66 s. Differs from the plan: the plan of 31d ruled out the "reuse of a CLI's private tokens", and none is read; the first build used `--safe-mode`, which the stand-in tests passed and the real trial did not (it switches off the given MCP server too), so `--restricted` took its place. Not tried: the sign-in button with a signed-out Claude Code, Windows, macOS, a release bundle. |
| 33 | The sequence in a tab; the AI button under the object list (a request, not a plan) | Done 2026-11-24 (4.67.0). `modules/pmg_qt/sequence_tab.py` draws the rows of the core's sequence viewer in a tab between Command and Chat; the core keeps the rows and handles the mouse through two new calls, `_cmd.seq_rows` and `_cmd.seq_mouse` (`SeqPanelMouse`), so the code of the viewport's rows runs for the tab. The rows are built without `seq_view`; `SeqInViewport` keeps them out of the viewport while it is off. SEQ opens the tab, its arrow has "Show in viewport". The AI assistant button moved from the action toolbar to the row under the object list, after SEQ. 2 tests in `api/sequence_tab.py`; the suite: 1101 passed, 250 skipped. Tried in the real window (WSLg, 150 %) on 4hhb and 1ubq: click, second click, Shift+click, drag, Ctrl+click and the middle button (the view moved), Ctrl+middle (zoomed), the right button on a selected and on an unselected residue (two menus), a double click beside the rows, a selection typed as a command (marked in the tab), residue names as Sequence Mode, colors by secondary structure; the viewport with `seq_view` on and off. Measured there: the row under the object list needs 234 px (it needed 254 px at 4.42.0), the toolbar 1254 px in a window of 1262 px, no button in the overflow menu. Left out: the dimming of unaligned residues, the frame around a drag and the marks along the scroll bar; the light theme, a sequence longer than 1000 residues, Windows and macOS were not looked at. |
| 31 | 31d — sign-in in the browser | Done 2026-11-24 (4.66.0): [docs/plans/31-ai-agents.md](docs/plans/31-ai-agents.md). `modules/pymol/signin.py`, standard library only: an authorization code with PKCE that comes back to a listener on 127.0.0.1, for OpenRouter (returns a key of the user's account) and for OpenAI's "Sign in with ChatGPT" for open-source apps (pymolish is registered by the user at the first sign-in; tokens for one hour, renewed before a request). The ChatGPT route in `assistant.py` streams, sends the tool in a namespace and no output limit. Chat tab: two more providers, a row with "Continue with ...", "Stay signed in" and the account with a link to its usage page; the model field is a list filled from the account. 16 tests in `api/signin.py`, 3 more in `api/assistant.py`; the suite: 1099 passed, 250 skipped. Checked in the real window with a stand-in browser: the row, Cancel, Sign out, the keyboard order, the window's smallest width unchanged (569 px). Differs from the plan: 31d was planned as an investigation only, and it was built. Its finding: Anthropic forbids a Claude.ai login in another program, so Anthropic keeps the API key; OpenAI and OpenRouter each publish a flow for it. No real sign-in was made. |
| 21 | 21f, item 1 — smooth edges (FXAA) | Done 2026-11-24 (4.65.0). `data/shaders/fxaa.fs` (written here from the description of the method, one pass), its program on `copy.vs`, `Enable_FXAAShader`; `SceneRenderAA` cut down to it. The offscreen path was in the code and unused. `antialias_shader` 0 or 1, one check row in Setting > Rendering, off by default (choice 73), not saved in sessions as before. Measured on WSLg (integrated AMD, 1500 x 731, 1oky): 10.3 ms a frame without and 12.0 ms with, each including a copy of the frame; pictures looked at on black and white, with `transparency_mode` 3, `grid_mode`, selection markers and a label. `settings.py::testAA` passes in the real window. Differs from the plan: the plan said "about 100 lines of shader"; the file has 50 lines. Not done: stereo, images drawn at another size than the window, Windows and macOS. Four other tests of `settings.py` fail in a real window on this machine, also on the 4.19.17 build: `testTrilines` twice, `testAtomCartoonTransparencyNuc`, `testIsomeshTransparency`. |
| 21 | 21f, item 3 — background picture in the session | Done 2026-11-24 (4.64.0). A session save task writes the picture as "data:image/png;base64" text into `bg_image_filename`; the core read that form already. Real window: drawn from the file, from the text, and from a session whose file was deleted. PyMOL 3.2.0a loads, ray traces and saves such a session. Test `api/bg_image_session.py`; `jira/PYMOL-1571.py` lost its mark. |
| 21 | 21f, item 2 — sphere modes 10 and 11 | Done 2026-11-24 (4.63.1). `sphere_mode` stops at 9; the warning, the test and its two reference images are deleted. Of the five test files that carried the mark `incentive`, two are left, both for 21g. |
| 19 | The rest of step 19 | Done 2026-11-24 (4.63.0): [docs/plans/19-movie-timeline.md](docs/plans/19-movie-timeline.md). The shot list under `session_extra` entry "timeline", with the starts and the length of the movie it built; a session whose movie still has that length brings it back. The strip: a ruler of seconds for the playhead, a drag moves a shot, a drag of its right end changes its length (`move_shot_to`, `set_seconds`, which the test calls). Movie > Program: 116 rows removed. Checked in the real window on WSLg: drag, stretch, save, reinitialize, load. Differs from the plan: the count of rows; State Sweep stays. |
| 15 | 15e — effects | Done 2026-11-24 (4.62.0): [docs/plans/15-presets.md](docs/plans/15-presets.md). Presets "balls in glass" and "cartoon cylinders"; a fog row in the light menu; `ambient_occlusion_mode` 1 at scale 16 in the look "soft", off for the objects of glass, balls in glass and illustration. Scenes keep `ambient_occlusion_mode`, `ambient_occlusion_scale` and `ray_transparency_oblique_power`. Measured: a surface build of 1aon (58 996 atoms) took 6.0 and 6.7 s without ambient occlusion and 7.4 and 10.5 s with it; on 4v6x the noise was larger than the difference (52 and 110 s without, 81 and 81 s with). Differs from the plan: color steps needed no code (45 colors in the viewport under "comic", 8436 under the standard light). 15b was built in 4.87.0. |
| 31 | 31b — agent connector, toolbar button | Done 2026-11-24 (4.61.0): [docs/plans/31-ai-agents.md](docs/plans/31-ai-agents.md). `modules/pymol/agent_server.py`: MCP over Streamable HTTP with the standard library, 127.0.0.1 only, bearer token, Host and Origin checks, requests of at most 1 MB, nothing listening before `agent_server on`; one tool, the operations of `agent.Executor`, each call a turn on the GUI thread with its own Undo snapshot. Toolbar: AI assistant (`bot`), blue while the connector listens. Tests `api/agent_server.py` (5: refused strangers, handshake, calls against the session, simultaneous calls). Real window: Claude Code 2.1.322 listed the tool and called it (the state of the session, then a color change); Codex 0.163.0 was not tried beyond its configuration (no credits). Differs from the plan: no client's file is edited, the helper is a line to copy; the revision 2026-07-28 without a handshake is not answered. |
| 26 | Rock > Random | Done 2026-11-24 (4.60.1). The turn stopped the timer that had started it, so the spin changed once and stayed. Now a single-shot timer set after each turn, for the time a random 15 to 180 degrees take at the current `sweep_speed`. Real window: four changes in nine seconds with the range set to 15 to 20 degrees, still turning. |
| 24, 26, 33 | Follow-up request 2026-11-24 | Done 2026-11-24 (4.58.1 to 4.60.0). 4.58.1: ligand 2D residues keyed by their own object; a ligand extracted from 1OKY selected nothing and warned on zoom before (test added). 4.59.0: Sequence alignment button after 2D (Lucide `text-align-start`); Zoom and Rock open their menus from the whole button; Rock menu uses `sweep_mode` and `sweep_angle` 0 for spins, Random a 3 s timer; Bg and Draw icon only; spacing 8 → 10 px; bar 1236 → 1254 px measured at 150 %, no overflow. 4.60.0: consensus secondary-structure track drawn by a delegate, colors Zappo / Kyte-Doolittle / percent identity, kept in QSettings. Different from a Jalview copy: no Clustal scheme; the structure rows keep their text symbols. Suite: 1069 passed, one timing test failed under load and passed alone. |
| 31 | 31a, 31c — chat and shared agent tools | Done 2026-11-24 (4.58.0). `agent.py` (live catalog from the keyword registry and API, settings with factory defaults from the new `_cmd.get_setting_default`, scene state, bounded atoms, reviewed execution with confirmation, duplicate-safe calls, Undo snapshot, cancel) and `assistant.py` (Anthropic Messages and OpenAI Responses through the official SDKs, extra `ai`) started by another agent and finished here; a Chat tab in the command dock, Display > Panels > AI chat, `ask [prompt]`. `MainThreadCaller` now hands results back through a `Future`. 21 stand-in tests (catalog coverage, policy refusals, plugin override, duplicate call, image, timeout, rate limit, Stop before a queued mutation and during a request, snapshot failure, OpenAI shape). Real WSLg window: `ask` with a comma opens the tab, a stand-in turn colors the model through the worker thread, Undo restores it. Different from the plan: no `data/pymol/agent.md` (the instructions are a constant in `assistant.py`), no toolbar button (question 45), no Clear button (a new provider or model starts a new conversation). Not done: a live provider trial. |
| 33 | 33a–c — sequence window | Done 2026-11-24 (4.57.0), commit `f25db6d3`. All three slices shipped as one coherent feature: local MAFFT, FASTA/chain input, selection and secondary-structure tracks, fit-to-reference with results/Undo, statistics/export and persistence. 21 sequence/fitting checks passed, including a known three-row MAFFT 7.505 fixture. Real xcb window at scale 1.5 resized to 800 × 450 logical pixels; largest measured heartbeat gap 20.4 ms. A cancelled worker no longer leaves the core interrupt flag set. Stop waits for an active native fit, then skips remaining fits. No joint structure optimizer, backend bundling, native Windows/macOS run, or live scale verification on those platforms. |
| 24 | 24c — the rest of the contacts | Done 2026-11-23 (4.56.0): [docs/plans/24-ligand-2d.md](docs/plans/24-ligand-2d.md). The pocket's outline in the residues' colors, open where no residue is near; grey halos on ligand atoms the protein leaves open (own Shrake-Rupley check, 64 points, numpy; 3 of 35 atoms of staurosporine in 1OKY); metal contacts within 3.0 A; Show in 3D, one distance object per kind in the group `ligand_2d`, gone when the panel closes (also from Display > Panels), back on reopening; tooltips with each contact's distance; Tab and Enter. Measured on 1OKY: analysis 0.27 to 0.53 s, the picture 11 to 31 ms. Tried in the real window: three real Tab keys reach Lys111 with its tooltip, Enter selects its 9 atoms; dashes in the viewport; the picture in the dark theme. Different from the plan: the outline has one color per piece, not blended; a metal is drawn as the usual circle, not a small one; the dashes go from center to center (distance mode 4), and a residue drawn only as cartoon has them end in the air. Not done: a look in the light theme, tabbing the panel behind another dock (tried, but the dock stayed visible, so it proves nothing). |
| 34 | 34b follow-up — the panel menus | Done 2026-11-23 (4.52.0, 4.53.0), at the user's request: S > ball and stick shows it on a click, its hover menu has ball size (0.20 to 0.50) and bond thickness (0.08 to 0.18) only; H hides only it; C > ball and stick only colors only it. `ball_and_stick_scale` defaults to 0.25 (was 0.31), as asked. Tried in the real window at 4.52.0; the trimmed menu of 4.53.0 by the menu test and the suite only. |
| 36 | 36a — the next ligand with its contacts | Done 2026-11-23 (4.51.0): [docs/plans/36-ligand-navigation.md](docs/plans/36-ligand-navigation.md). `ligand_next [selection [, step]]`; step 0 clears. Measured: 9 ms a step on 2RH1 (10 ligands), 100 ms on 1AON (59,192 atoms, 7 ligands), so no cache. Tried in the real window: the three rows of Display > Zoom, both keys, the 2D panel following, Clear. Different from the plan: the rows are in Display > Zoom (there is no ligand or find menu); the walk's position is kept with the session, under the key of 28b; the site is every residue within 4 A, not only those with a contact; contacts are made for the state that is shown. Not done: Undo of a visit, a look in the light theme. |
| 11 | 11c — CPK colors | Done 2026-11-23 (4.50.0): `color_cpk selection [, ball_and_stick]`, rows in by element and in by rep > ball and stick. 28 elements, deep pink for the rest; colors as RGB values, no named color defined. Looked at on black and white. Different from the plan: the table could not be compared with the RasMol manual, whose pages and two other sources were unreachable in that run; only the fallback FF1493 was confirmed (question 64). The command takes "" or `ball_and_stick` as representation, no other. |
| 34 | 34c — ligands in the presets | Done 2026-11-23 (4.49.0). Twenty presets tested on 1OKY with a ligand, water, a modified residue and an added zinc ion: the ligand is `ball_and_stick`, the ion, the water and the protein keep their representations and colors, the user's sphere and stick settings survive. Beyond the plan: the view a loaded structure opens with draws ligands the same way (question 63); "atomic" reaches atoms for `ball_and_stick_color`; `visible` and the side chain helper know the representation. "simple" and "default" still draw ligands as lines. |
| 34 | 34a, 34b — the representation | Done 2026-11-23 (4.48.0): [docs/plans/34-ball-and-stick.md](docs/plans/34-ball-and-stick.md). Representation 21, settings 798 to 800, all at atom level; menu rows in show, hide, as and the color menu. Measured in the window on 1AON with all 59,192 atoms: 23.6 ms a frame, 24.2 ms as sticks plus spheres of the same sizes, 23.0 ms as sticks alone; memory not measured. Sanitizer run clean. Different from the plan: built by the stick code with a second visibility bit, so the quality settings of sticks are shared and it is never transparent; the bond radius is a setting of atoms, a bond as thin as its thinner end; no bond color of its own (question 59). Found: PyMOL 3.2.0a loads, ray traces and recalls scenes of such a session but ends when it saves one that has a setting it does not know on an atom, so those go under the session key `pymolish_unique_settings`; PyMOL drops them and does not draw the representation. |
| 35 | 35b — scenes keep the style | Done 2026-11-23 (4.47.0): [docs/plans/35-scene-appearance.md](docs/plans/35-scene-appearance.md). Measured: ray-traced geometry and the viewport picture of A are the same after B and back; 4V6X (239,306 atoms) store 40 ms against 14 without style, recall 28 ms against 13; 1.7 MB more in the session when every atom has two settings and a cartoon type, nothing measurable without. Sanitizer run clean. PyMOL 3.2.0a loads and recalls such a session, without the style. Different from the plan: the style is a seventh item of the scene's own record, no side entry (question 62); global and object settings are a fixed list of 89 in `MovieScene.cpp`, checked by a test against what `preset.py` and `stage.py` write, atom and bond settings are kept whichever they are; global light settings follow `settings`, not `rep`. Not kept: settings of single states, secondary structure. Not checked: Undo. |
| 22 | 22f — stars | Done 2026-11-23 (4.46.0). A column "stars" after the name; a delegate draws three stars and takes the clicks; the value is the object property. Different from the plan: the header reads "stars", the name of the property, so that an exported table comes back; a rating is typed like any cell (digit, then Enter) instead of a key acting at once; an exported table always has the column. Checked: the picture in the real window, dark theme; the clicks through Qt's own mouse path in the test, because a click sent through the X server does not reach a floating window under WSLg. Not checked: light theme, a fractional scale other than 150 %. |
| 22, 28 | 28b, 22d, 22e — the session key, columns, Follow, pick | Done 2026-11-23 (4.45.0). `pymol.session_extra`: `session["pymolish"]` with a version and one entry per feature; an entry of a newer version survives load and save; PyMOL 3.2.0a loads a `.pse` with the key. The table: column order, hidden and empty columns in the session; a Columns button; counted columns atoms, residues, chains, states, weight, charge; Follow; the row of a picked atom; the size between starts. Measured at 150 %: the row of buttons needs 440 px. Different from the plan: sequence length is not a counted column; the size is saved with the main window's layout. |
| 35 | 35a — one click recalls | Done 2026-11-23 (4.44.0). A left click or Enter recalls once; the list no longer listens to `itemActivated`. A right click and the arrow keys pick a row without recalling it, which is how a scene is picked for Update, Rename and Delete (question 65). Tried with clicks sent through the X server, dark theme only. |
| 24 | 24d — the picture fits | Done 2026-11-23 (4.43.2). The cause was in the drawing, not in the panel: the ring of residues goes around the mean of the ligand's atoms, rdkit centers the box around the ligand, so circles ran over the edge for carazolol in 2RH1. The molecule is drawn once to see where the mean lands and again with it in the middle. The 125 % ceiling of the panel is gone. Tried on 2RH1 docked from 259 to 600 px and floating from 300 x 300 to 800 x 1000. Not tried: dragging the edge of the floating panel with the mouse, scales other than 150 %. |
| 27 | 27d — the freeze after a change of scale | Done 2026-11-23 (4.43.1): [docs/plans/27-ui-scale.md](docs/plans/27-ui-scale.md). Reproduced on WSLg (X11, Qt 6.12, two screens): the event loop never blocks; the window manager maps the native window that was destroyed and made again 0.1 to 4.6 s late (30 changes, most of them 1.5 s), in other runs not within 3.5 s, and Qt reports it visible meanwhile. Plain hide and show is immediate; a pause before showing changes nothing; a second show does not help. So on WSLg the scale is saved for the next start and the message says why (question 61). Also fixed: Enter in the field applied the change twice. A subprocess test with a heartbeat reports per display whether the change ran live. Open: 27c. |
| 32 | 32b — a Movie button in the action toolbar | Done 2026-11-20 (4.43.0): [docs/plans/32-footer-icons-movie-button.md](docs/plans/32-footer-icons-movie-button.md). After Scenes; a click opens the Timeline panel, a second click closes it; Space on the focused button does the same. Measured at 150 %: the bar needs 1236 px (1195 before), the window opens 1244 px wide, no button is in the overflow menu. Differs from the plan: the icon is `video` and the click also closes (answers 51 and 52); the "movie" rows of the menus got the same icon and `clapperboard.svg` is deleted. |
| 32 | 32a — icons in the row under the object list | Done 2026-11-20 (4.42.0): the same plan. `mouse` with the name of the mode, `letter-text` with "SEQ", `wand-sparkles` and `square-terminal` alone; SEQ stands before Wizard. The icons of SEQ and of the command line are blue while on. Measured at 150 %: the row needs 254 px of its 292, the buttons are 23 px high (21 before); looked at in the dark and the light theme and after a live change to 200 %. Differs from the plan: the order, and "SEQ" keeps its letters (answer 50). On the way: the tooltip of SEQ is set on its action, the button takes it from there at every click. |
| 11 | 11b — palette `halo` | Done 2026-11-20 (4.41.0): [docs/plans/11-color-palettes.md](docs/plans/11-color-palettes.md). Twelve colors: turquoise, blue, cyan, indigo and deep purple of the user's brand book as published, and between them pink, yellow, lime, red, green, magenta and orange in the same tone. Listed for any background: on black the deep purple has a contrast of 1.8 and the indigo 2.7; neighbors are at least 0.56 apart. Differs from the plan: the three questions got no choice, so the recommended options were built; the menu was looked at at 100 % only. |
| 30 | 30a — the 2D picture | Done 2026-11-20 (4.36.0): [docs/plans/30-polish.md](docs/plans/30-polish.md). Residues are circles of 52 px with 14 px text; each fill is a gradient in tones for a light or a dark window; the legend has 16 px text and wraps. 1OKY: the picture went from 514 to 429 px wide. The three `qt.svg` messages per drawing are gone. Differs from the plan: the legend's text is 16 px, not 14, and the picture has less empty margin, both after a look at it in a panel 420 px wide. |
| 30 | 30b — the property table | Done 2026-11-20 (4.37.0). Values at the left; the icon `sheet`; only molecules are asked for properties and written, so a group no longer makes the core print an error at every poll. |
| 30 | 30c — the live UI scale | Done 2026-11-20 (4.37.1). Found on the way: Qt keeps the application's pixel ratio from the start, so after a live change every new icon was still made for the old scale (30 px for a place of 40 at 150 to 200 %). Icons are made for the ratio of the screens, and what draws icons draws them again after a change. Qt's warning is not printed. |
| 30 | 30d — the preset menu and colors | Done 2026-11-20 (4.38.0). 21 rows in place of 33: submenus theme, light, floor. No row but a theme colors a cartoon or a surface; the two presets for complexes color the contact area orange. More than planned: a surface drawn by a preset takes the color of the carbons of each residue (one pass, 0.03 s on the 59,192 atoms of 1AON), because an earlier preset leaves element colors behind; a modified residue of the protein is no longer colored like a ligand. |
| 30 | 30e — crystallization additives | Done 2026-11-20 (4.39.0). A > clean > "remove crystallization additives": 111 residue names in eight groups. On 1OKY three glycerols and five sulfates go, staurosporine stays. The sugars of glycosylation and NAD(P) are on the list as asked, with a note that they are no additives. |
| 30 | 30f — Undo for presets | Done 2026-11-20 (4.40.0). Checked first: Undo did nothing after a preset. Now every row of the preset menu keeps the session, and Undo and Redo put it back: five steps, 600,000 atoms over all of them. 1AON: 0.15 s to keep, 0.06 s to put back, 17.8 MB. The first piece of 21g; the limits (the whole session, not in one order with moves) are in the module. |
| 1 | 1b, nine changes so far | 4.5.10 session load 0.92 s to 0.14 s (6.6x). 4.5.12 surface build 11.97 s to 9.66 s (1.24x). 4.7.7 to 4.7.9 surface build 9.44 s to 6.24 s (1.5x). GUI frame time measured 2026-11-14 (`testing/bench_gui.py`): software rendering under WSL is the main cost. 4.7.10 atom labels fixed on drivers without geometry shaders. 4.13.3 the ray tracer's voxel table 0.68 s to 0.28 s. 4.19.15 the window draws on the GPU under WSL (1aon cartoon 46 ms to 9.8 ms per frame). 4.19.16 surfaces of very large structures (4v6x 48.6 s to 31.0 s). 4.19.40 the neighbor list is not zero-filled before it is written (1aon surface about 0.3 s of 5.5 s faster, same triangles). Outside the list of 1b, found with the same measurements: 4.19.8 to 4.19.10 `get_sasa_relative`, `util.color_by_area` and `util.chainbow`. Numbers: the ChangeLog and, against PyMOL 3, [docs/benchmark.md](docs/benchmark.md). |
| 3 | Slices 1 to 3 | Done 2026-11-08 (4.5.0): objects dock, layout persistence, Panels menu. |
| 3 | Slice 4 and the workspace layout | 4.5.11 Qt Objects panel replaces the viewport's object list. 4.5.14 action toolbar on top, command area at the bottom, toggle bar. 4.5.15 row state and colors. 4.5.16 no second prompt in the viewport. 4.5.17 menus stay on the screen under WSLg. 4.5.18 Qt menus for the viewport's right click. 4.13.4 scenes as a docked panel with thumbnails. |
| 3 | Slice 5, partly | 4.5.2 dark theme. 4.5.7 UI Scale and the dark-theme color audit. 4.5.13 no fixed point sizes in rich text. Open: spacing of the remaining dialogs. |
| 3 | Moved to other steps | The removal of the old C++ panel became step 17 (17c, 4.17.1), the timeline step 19 (4.18.0); dialog sizes and the scroll bar of the sequence viewer shipped as step 18 (4.15.1, 4.17.0). |
| 8 | 8a — safety net | Done 2026-11-13 (4.7.2): CI job with ASan and UBSan, three bugs fixed, coverage measured (about half of the core). Catch2 is compiled in CI and not run: that is 8h. |
| 8 | 8h — Catch2 in CI | Done 2026-11-16: the three build jobs ran the Catch2 tests all along, through `ctest.py`; the sanitizer job now runs them too. One defect found and fixed (4.14.1, `ColorGetName`). |
| 8 | 8i — dead `#ifdef` branches | Done 2026-11-16 (4.14.2): the branches of 12 macros nothing defines, 2,207 lines in 97 files, one commit per macro. Proof: the preprocessed text of all 197 translation units is identical before and after. Two more macros of the same kind in 4.19.19, with step 21: `NO_MMLIBS` and the atom-typing blocks behind `_PYMOL_IP_EXTRAS`. The last five in 4.19.38: `PYMOL_COMM`, `PYMOL_COLL`, `PYMOL_EDU`, `_PYMOL_IP_SPLASH`, `_PYMOL_IP_EXTRAS`, 100 lines in 10 files, same proof. |
| 8 | 8b — strings, mostly | 4.7.3 to 4.7.6: 408 of 475 `sprintf`, `strcpy` and `strcat` calls are bounded; three real defects fixed with a test. About 80 calls through a pointer close with 8c and 8e. |
| 8 | 8c — the `malloc` half | 2026-11-25 (4.76.1, 4.76.3, 4.76.8, 4.76.10, 4.76.12): 230 of 297 allocation sites and 274 of 353 frees are gone in 60 files; the buffers are `std::vector`, or `std::unique_ptr<T[]>` without initialization where a zero-fill would cost. Differs from the plan: done in four groups of files, not file by file in profile order, three of them in parallel branches; 67 sites stay, each with a reason in the plan (returned to another file, singletons of `PyMOLGlobals`, `realloc` shrinking in `RepDot.cpp`, `ccealignmodule.cpp`). Dead code deleted on the way (4.76.4, 4.76.7, 4.76.9, 4.76.11): 894 lines, 554 of them a sphere generator that was never compiled. Defects of 4.76.0 fixed: 4.76.5 `load_png` with a bad data URL, 4.76.6 `valence` with a source, 4.76.13 surface with `ambient_occlusion_mode` 3, 4.76.14 sphere normals of a part of an object, three leaks, one write into an empty buffer. Checks: suite 1154 passed; sanitizer run without a report; ray geometry of 385 combinations and a session round trip identical to 4.76.0. Not run: `compare.py`, other compilers, a window. Open: raw `new` / `delete`. |
| 8 | 8d — the mechanical part | 2026-11-25 (4.76.2, 4.76.12): 215 calls of `VLACheck`, `VLASize`, `VLAFreeP` and `VLAGetSize` on `pymol::vla` objects are member calls, in 25 files, by a script that keeps a rewrite only if the file still compiles. 611 calls on raw pointers are open. |
| 15 | 15a — menu, glass and looks | Done 2026-11-16 (4.14.0): [docs/plans/15-presets.md](docs/plans/15-presets.md). The preset menu is ordered and has 13 rows instead of 14; one solvent row replaces three twin rows; new preset glass; five looks (default, figure, soft, flat, x-ray) in the toolbar menu. Tried and left out: Metal, Plastic and Rubber of the Lighting plugin. |
| 15 | 15d — cartoon, ligand style, transparency, comic and sketch | Done 2026-11-16 (4.14.3). Only "simple" keeps the ribbon; technical, ligands and ligand sites draw cartoon. The ligand presets draw the ligand as balls on thin dark sticks. New row "cartoon transparency", reset by the next preset. New looks comic and sketch: seven looks. |
| 19 | 19 — movie timeline | Done 2026-11-18 (4.18.0): [docs/plans/19-movie-timeline.md](docs/plans/19-movie-timeline.md). Timeline panel: shot list, strip with thumbnails and playhead, record, tours, fades, easing, export with an estimate; `pymol.shots` builds an ordinary movie from the list. The step stays open for three questions and 19g. |
| 17 | 17c — the old internal GUI | Done 2026-11-18 (4.17.1). Object list, mouse mode table, movie and wizard buttons of the viewport: 2,694 lines deleted in 19 files, three settings and the option `-i` removed. |
| 18 | 18b — scroll bar of the sequence viewer | Done 2026-11-18 (4.17.0). A see-through Qt scroll bar on the strip under the sequence rows; the core keeps the offset and the selection marks. |
| 17 | 17a, 17b — legacy menu rows, Tk stand-ins | Done 2026-11-18 (4.16.0, 4.16.1): [docs/plans/17-legacy-ui.md](docs/plans/17-legacy-ui.md). Five menu rows gone; `mimic_tk.py`, `mimic_pmg_tk.py` and `legacysupport.py` deleted (316 lines), one Plugin menu, `__init_plugin__` gets `None`. |
| 17 | 17d, 17e — panel list, GL menus | Done 2026-11-20 (4.19.41, 4.19.42). 17d did not need the movie panel to go first: the list had one reader left, a scroll function nothing called. 242 lines. 17e: `PopUp.cpp`, `Pop.cpp` and the fallback in `Menu.cpp`, 1,224 lines; a program that embeds the viewport without the window sets `pymol.menu.popup` to get menus. Suite, Catch2, a sanitizer build, session round trips, right clicks in the real window. |
| 18 | 18a — dialog sizes | Done 2026-11-18 (4.15.1): [docs/plans/18-dialogs-scrollbar.md](docs/plans/18-dialogs-scrollbar.md). `loadUi` sets a form up on the dialog itself: right size, title and a layout for every form. The shortcut editor opens again. |
| 15 | 15l — spring, colors kept, two-color surface | Done 2026-11-19 (4.19.29). New preset "cartoon spring" (thick round tube); "wire" reads "cartoon wire". No preset but "default" colors the cartoon; the row "publication green" is gone. "protein-protein interaction" is every chain as an orange surface, white where chains touch. |
| 15 | 15i — visible objects, complexes | Done 2026-11-18 (4.19.1). Toolbar presets act on the objects that are switched on. New presets "protein-protein interaction" and "antibody and antigen", tried on 1BRS and 1N8Z. |
| 15 | 15g, 15h — one list, background, colors | Done 2026-11-18 (4.14.5). The looks are the last group of the one preset list and no longer set the background or the outline color; ray traced on black and on white, the outline contrasts by itself. technical, ligands and ligand sites keep the protein colors, also at modified residues. The row "simple" is gone; the function stays. |
| 15 | 15f — wire, illustration, shades | Done 2026-11-16 (4.14.4). Preset wire: the cartoon as a wire mesh (`cartoon_debug` 3, already in the core). Preset illustration: shades of blue inside a faint outlined surface, with the look flat. `util.shades` and "shades" rows in the color menus. The look flat keeps colors as they are and outlines transparent things. |
| 15 | 15j, 15k — light after illustration, publication green | Done 2026-11-18 (4.19.2, 4.19.3). The next preset after "illustration" goes back to the standard light. Preset "publication green"; its row left the menu again with 15l, the function stays. |
| 25 | 25b-2 — color themes | Done 2026-11-20 (4.35.0). Clay, blue, sage, mint, night in the Presets menu: protein color, ligand color, two-color background, and nothing else. |
| 25 | 25a-1 — floor, shadow, mirror, lights | Done 2026-11-20 (4.34.0): [docs/plans/25-studio-effects.md](docs/plans/25-studio-effects.md). `stage`: a floor under what is shown that takes the ray-traced shadow, a mirror image through it, fog that hides its far edge, `off` that puts everything back. Looks "top light", "soft shadow", "studio". The viewport shows no shadow, as decided. |
| 24 | 24a, 24b — the ligand in 2D | Done 2026-11-20 (4.32.0, 4.33.0): [docs/plans/24-ligand-2d.md](docs/plans/24-ligand-2d.md). `ligand_2d`: near residues, hydrogen bonds, salt bridges, ring stacking and cation-ring contacts, drawn by rdkit as SVG or PNG. The panel: a click on a residue selects it in 3D, a selection in 3D is ringed in the picture; a toolbar button that is off without a ligand. Our own code on rdkit and Qt. |
| 27 | 27a, 27b — UI scale, any value, live | Done 2026-11-20 (4.31.0): [docs/plans/27-ui-scale.md](docs/plans/27-ui-scale.md). A field for 50 to 300 %; the running window changes through Qt's private scale function, with the "next start" message as fallback; a question with a ten-second revert for very small and very large values. Linux only so far. |
| 22 | 22a to 22c — the property table | Done 2026-11-20 (4.27.0 to 4.29.0): [docs/plans/22-property-table.md](docs/plans/22-property-table.md). A window over the viewport, stuck to the Objects panel: row number, a dot for shown or hidden, name, one column per object property; sorts by value, filters. Cells and names are edited in place, columns added, renamed, deleted; blocks copied and pasted. `load_table` (CSV, TSV, `.xlsx` with the standard library) and `save_table`. `split_states` keeps properties. 4.27.1: the core no longer aborts when a property changes its type. |
| 28 | 28a — the packed session file | Done 2026-11-20 (4.26.0): [docs/plans/28-session-format.md](docs/plans/28-session-format.md). `save x.psex`: 1AON 19.6 MB to 1.10 MB, 4V6X 87.2 MB to 3.90 MB, faster to write and to read. First choice in Save Session As; `.pse` stays for PyMOL. |
| 26 | 26c, 26d — quick select, the layout of the bar | Done 2026-11-20 (4.30.0). Chips P, L, S, a menu with chains and more, All and "nothing"; Shift adds, Ctrl takes away. Palette became an icon; the bar is one row. With the 2D and Table buttons it is 1195 px at 150 %. Step 26 is finished. |
| 26 | 26a, 26b — Bg, Builder and Scenes as icons, Draw; the Open button | Done 2026-11-20 (4.20.0, 4.21.0): [docs/plans/26-toolbar-buttons.md](docs/plans/26-toolbar-buttons.md). The bar went from 1096 px to 904 px at 150 %, and is 959 px with Open. Open lists open file, open folder, recent, get by PDB code, by UniProt, predicted structure. |
| 15 | 15c — ChimeraX colors | Done 2026-11-20 (4.22.0). Palette `chimerax`: the ten values of ChimeraX's own list, read from its source. Listed for any background, because its purple is too dark for the contrast rule of the dark palettes. |
| 20 | The two follow-ups | Done 2026-11-20 (4.23.0). One rule in `pymol.sty` for every menu and the menu bar; a checked row is written in blue everywhere. Orient in the toolbar acts on `visible`. |
| 1 | 1b — idle threads sleep | Done 2026-11-20 (4.23.1). `OMP_WAIT_POLICY=passive` before the core loads, unless the user set it or `GOMP_SPINCOUNT`. 1aon, three surface builds: CPU 98 s to 66 s, the same wall time. The ray tracer has no OpenMP loop. |
| 23 | 23a — rename on the row | Done 2026-11-20 (4.24.0): [docs/plans/23-rename-in-panel.md](docs/plans/23-rename-in-panel.md). F2 or the "rename" rows open an editor on the row of the Objects panel; the rows call `menu.rename`, which starts the old wizard only without a window. A taken name is refused with a line in the log. |
| 17 | 17f — scene buttons of the core | Done 2026-11-20 (4.25.0). Drawing, click, release and drag code, the scene list the core kept for them, two settings (placeholders), the menu rows: 498 lines of C++. A session from 4.19.17 with the setting loads. |
| 21 | Removals | Done 2026-11-19 (4.19.18 to 4.19.26): [docs/plans/21-commercial-features.md](docs/plans/21-commercial-features.md). All Maestro file support, mmlibs atom typing, the MOE, `.vis` and `.phypo` stubs, MTZ maps, `help_setting`, `callout`, `desaturate`, the FreeMOL test. `clean` was already rebuilt in 4.12.1. |
| 21 | 21a to 21e — rebuilt commands | Done 2026-11-19 (4.19.33 to 4.19.37). `save file.stl` (binary STL from the meshes of the USD export). `assign_stereo` with rdkit, and label > stereochemistry is back. `distance` modes 5 to 7 and `pi_interactions`: the finder was already in the core, only the call was missing. `focal_blur`: average of images of a turned camera. `morph`: linear interpolation, refined by sculpting. Each old test runs without the `incentive` mark. |

## Validation of the original draft, closed rows

As written on 2026-11-08. The steps these rows belong to are finished; the rows
that still steer open work are in the [roadmap background](docs/plans/roadmap-background.md#validation-of-the-original-draft).

| Original idea or claim | Verdict and correction |
| --- | --- |
| PySide6 is the best fit | **Keep.** Qt 6 is already supported. PyQt6 is another binding to the same toolkit, not a different renderer. See step 0 for the sourced comparison. |
| Qt already provides docking | **Confirmed, partly implemented.** `PyMOLQtGUI` enables nested/tabbed docks. Workspace layout persistence was not found in the inspected GUI code. (Added in 4.5.0.) |
| Remove Tk, its adapters, GLUT and other bindings in one PR | **Split.** Qt plugin initialization still uses legacy helpers, and `legacysupport.py` imports `pmg_tk.startup`. Preserve needed functions before removing their implementation. |
| Add five performance scripts from scratch | **Reuse first.** Existing loading, shader, iteration and asynchronous-build checks provide a starting point. Some are excluded from `--run all`; headless tests do not establish GPU performance. |
| Stop updating `ChangeLog` | **Reject.** Public `cmd.*` behavior changes must still update it. Preserve historical entries. |
| Optional libraries are immediately removable | **Conditional.** COLLADA, MMTF, trajectories, and glTF have real dependencies. CI explicitly enables `json=True`; retained native glTF needs nlohmann-json. |
| PNG or glTF replaces movie encoding | **Incorrect.** Image sequences, encoded movies, and 3D scenes are different outputs. Preserve an explicit supported movie workflow. |
| `cmd.get_coords()` is a NumPy view | **Correct.** It returns selection coordinates as an array; the explicit borrowed-memory option is `get_coordset(copy=0)`, with documented lifetime hazards. |
| `cmd.add_dock()` is a 20-line task | **Defer the API.** Ownership, thread access, headless behavior, and layout restoration matter. Use existing window access first. |
| Cross-platform binaries are a small mechanical task | **Underestimated.** Resources, shared libraries, Qt plugins, architecture, and clean-machine testing need milestones. |
| Latest pins prove compatibility; LTS defines the runtime floor | **Not established.** The PySide6 6.12.0 pin is real, but a minimum version needs tests. LTS does not imply unrestricted access to all maintenance packages. |

## First concrete changes (all done)

1. Record an optimized baseline and current headless/GUI test status. Resolve
   existing failures before using those results to judge a change.
2. Promote the tested PySide6 binding to runtime metadata and establish a coherent
   Python minimum with dependencies and CI. Keep dev pins exact.
3. PR title `remove: alternative Qt bindings`; commit subject
   `remove(gui): standardize on PySide6`. Preserve used import aliases; keep Tk,
   GLUT, and renderer changes separate.
4. Deliver a first test artifact, then complete the Tk/plugin migration and other
   removals one at a time. Docks and the object table are the first visible UI work.
