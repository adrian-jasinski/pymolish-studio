# pymolish-studio — shipped state

[Back to the roadmap](PLAN.md).

**Shipped state, checked 2026-11-26: 4.91.0.** Seven versions were built
that day from the planning update of the morning (15m to 15p, 32c, 34d and
the surface worker of 1b): 4.83.0 to 4.89.0; an eighth, 4.90.0, from a
request of the same day (the alignment window shows the secondary
structure only as the drawn track); 4.90.1 repaired three faults found
by CI on Windows and macOS. Questions 121 to 125 are answered and built;
128 and 129 were answered **A** on 2026-11-26. The glow menu entry of
answer 128 A shipped in 4.91.0, which finishes step 15; Solid stays the
default, with no code change. See [the decisions](PLAN-DONE.md#decisions-128-and-129)
and [current work](PLAN.md). The
documentation (step 38a to 38d, answers 126 A and 127 A) was written and
captured on 2026-11-26 at 4.90.0: it changed no program code and has no
version. The Windows workflow still produces an unsigned portable ZIP;
an unsigned per-user Inno Setup installer is planned in **5d, order 5**
(answer 137 A, 2026-11-26); signing (138) is deferred. No installer was
built or tested in this planning update. Built since
4.19.43, with the tests and GUI checks recorded in
[PLAN-DONE.md](PLAN-DONE.md):

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
| 4.68.1 | File > Get by UniProt and Get Predicted Structure no longer fail where the old pymolish plugin is a startup plugin: that plugin is not loaded (37a). |
| 4.69.0 | The Delete key deletes the current row of the Objects list; a group asks first and goes with its members (37b). |
| 4.70.0 | Rows of the Objects list are moved by a drag with the right button, or with Alt and the arrow keys: order, into a group, out of it (23b). |
| 4.71.0 | Thirty colors in each of the ten named palettes; the menu shows the first ten (37c). |
| 4.72.0 | Colors are dragged to their place in the New/Edit palette dialog (37d). |
| 4.73.0 | The mouse mode button shows the icon and the short name ("Viewing") and is as wide as that (37e). |
| 4.74.0 | The Sequence tab has the lists Mode, Labels and Gaps and a button for the alignment window (37f). |
| 4.75.0 | A−, A+ and Reset beside the tabs Command, Sequence and Chat: a text size per tab, kept (37g). |
| 4.76.0 | An experiment: `set surface_type, 7` builds the molecular surface on a grid with marching cubes (1b). 1aon 1.67 s against 5.18 s, 4v6x 9.41 s against 34.31 s, at the same count of triangles. Not a default, no menu row. |
| 4.76.1 to 4.76.14 | Step 8, no feature: 230 hand-managed buffers of the core own their memory, 215 VLA macro calls are member calls, 894 lines of dead code deleted. Fixed on the way: `load_png` with a data URL that is not base64, `valence` with a source object, a surface with `ambient_occlusion_mode` 3 and spheres of a part of an object with `sphere_mode` 6 to 8 no longer crash or corrupt memory; three leaks. |
| 4.77.0 | The model of the Chat tab and of the agent connector runs `list_uniprot_structures`, `fetch_by_uniprot`, `fetch_uniprot_ligands` and `fetch_fold`; more than ten entries load in the background. A switch "Download without asking" in the Chat tab. |
| 4.77.1 | No feature: `safe_eval` (the reader of vectors and color lists given as text) no longer runs Python. |
| 4.78.0 | The model runs 286 of the 504 commands it finds, before 88: measurements, labels, spectrum, presets, groups, maps, movie frames without a question; builder, fit, split and file commands with one. |
| 4.79.0 | A switch "Run without asking" in the Chat tab, off at every start: while it is on, the model and the agents on the connector run every reviewed command, and Python with "Trusted Python" ticked, without the question. It replaces "Download without asking" (4.77.0). |
| 4.80.0 | The provider "OpenAI" of the Chat tab has the button "Continue with ChatGPT" next to its field for an API key; while signed in the ChatGPT plan is used and the key field is hidden. The entry "ChatGPT" left the list of providers. The sign-in is that of 4.66.0: stand-in tests only, no real sign-in yet. |
| 4.81.0 | "Solid (grid)" in Setting > Surface: the grid surface of 4.76.0 with cavity culling (on by default, closed cavities under 25 A3), "Cavities and Pockets Only" and "(Culled)", and "Solvent Accessible". "Solid" stays the default. |
| 4.82.0 | Presets > surface look: glossy, candy glass, frosted, clay. A row shows the protein as a surface in that material with the ligands as balls and sticks; the three round ones use the grid surface with a probe of 3 A. Ray-traced pictures on white and black; not yet looked at in the viewport. |
| 4.83.0 | Four presets after reference pictures: space filling, illustrated atoms, licorice, bond shell; the row "illustration" is called "contour cartoon"; "glossy (light only)" in the light menu (15m). |
| 4.84.0 | Presets > transparency: cartoon, spheres, surface and ball and stick, each opaque, 25, 50 or 75 %, for whole objects; the setting `ball_and_stick_transparency` (34d, 15n). |
| 4.85.0 | The Presets menu in groups: cartoon, atoms and bonds, surface, binding; then transparency and solvent; light, theme and floor under "Scene appearance" (15o). |
| 4.86.0 | The five buttons under the object list are larger and have a short text each: mouse mode, SEQ, Chat, Wizard, Cmd; two rows in a narrow panel (32c). |
| 4.87.0 | The outline of a look in the viewport: figure, soft, flat, comic, sketch, illustrated atoms and contour cartoon; the setting `viewport_outline` (15b). |
| 4.88.0 | An experiment: `set glow, 1` lays a halo in the colors of what is drawn around it, in the viewport. No menu row in this release (15p; answer 128 A schedules it). |
| 4.89.0 | A large surface is built in the background: the window stays in use and the surface appears when it is ready; pictures and exports wait for it; the setting `async_surface` (1b). |
| 4.90.0 | The Sequence alignment window shows the secondary structure only as the drawn track at the bottom; the line of characters above every residue and its legend are gone, a row is one line high (a request, step 33). |
| 4.90.1 | No feature: F2 renames a scene on macOS too; the font buttons of a tab keep the requested size; SDF properties read the same with Windows and Unix line endings (found by CI). |
| 4.91.0 | Presets > light has a row "glow" / "no glow" beside fog: the halo of 4.88.0 from the menu, with Undo; a scene keeps it like the fog. Viewport only (answer 128 A). |

Of the ten features requested on 2026-11-20, all ten have a working
version: the tenth, the surface looks, shipped in 4.82.0 on the grid
surface of 1b (4.76.0, a menu row with its cavity settings since
4.81.0; today's surface stays the default, answers 105 A and 129 A). Steps 19, 20,
25, 26 and 29 are finished, and so are steps 32 and 34 with 32c (4.86.0)
and 34d (4.84.0). Step 15 is finished: its last piece, the glow menu
chosen in answer 128 A, shipped in 4.91.0. Of the
eleven drafts of 2026-11-23, all eleven have a working version;
the chat (31a, 31c) shipped in 4.58.0, its external connector 31b in 4.61.0,
the sign-in in the browser 31d in 4.66.0 (its ChatGPT half sits in the
provider "OpenAI" since 4.80.0), the provider "Claude Code" in
4.68.0. Only that last one was tried with a real account (two turns on
the user's Team plan); the other providers saw no paid request and no
real sign-in by this program itself until the user reported on 2026-11-26
that the Chat tab works with Claude Code and with ChatGPT, signed in; what
is left of the live trial is order 2.
