# pymolish-studio — finished plans

Steps of the [roadmap](PLAN.md) whose last milestone has shipped. Open work
stays in `PLAN.md`; the detailed plans stay in `docs/plans/`. Step numbers and
order numbers are the ones the roadmap used.

## Finished steps

| Step | Detailed plan | Recommendation |
| --- | --- | --- |
| 0 | [UI engine research](docs/plans/00-ui-engine.md) | PySide6 + Qt Widgets; preserve the renderer while simplifying bindings. |
| 2 | [Code and dependencies](docs/plans/02-cleanup-dependencies.md) | One feature removal per PR; trace dependencies before deleting. |
| 4 | [Features and external libraries](docs/plans/04-extensibility.md) | Preserve `cmd` and the existing loader; document small integration patterns. |
| 5 | [Builds and test binaries](docs/plans/05-builds-binaries.md) | Improve incremental builds and deliver test artifacts before large changes. |
| 6 | [States panel](docs/plans/06-states-panel.md) | First, previous, play/stop, next, last, jump and speed in the Objects dock; replaces the state label and the toolbar's movie buttons. |
| 7 | [Toolbar icons and UI scale](docs/plans/07-toolbar-icons-scale.md) | Line icons on every action toolbar button, Undo and Redo icon-only, 150 % default scale, scale button in the toolbar; replaces Display > UI Scale. |
| 9 | [Own icon and logo](docs/plans/09-icons-logo.md) | Allowed and asked for by the license. One master PNG; window title and About box stop saying PyMOL. New art (blue, green and violet ribbon) in 4.19.27. |
| 10 | [README and license files](docs/plans/10-readme-license.md) | New README naming the fork; PyMOL notice kept word for word, new code MIT, third parties listed; two allowed slogans with the trademark footnote. |
| 11 | [Color palettes](docs/plans/11-color-palettes.md) | Five palettes replace the object color order; toolbar button; remembered in `QSettings`. |
| 12 | [pymolish plugin commands, native](docs/plans/12-native-commands.md) | Command bodies ported, not the framework: 58 plugin commands became 18 (19 since 4.12.9, `fetch_uniprot_ligands`), in five files; two dialogs, five menu entries, no new top menu. rdkit is the optional extra `chem`. |
| 13 | [Clean, fix and optimize structures](docs/plans/13-structure-cleanup.md) | Four layers, each shipped alone: remove water, ions and ligands; `clean` for ligands (rdkit); `fix_structure` (PDBFixer); `minimize` (OpenMM). PDBFixer and OpenMM are the optional extra `fix`. |
| 20 | [Look of the action toolbar, own palettes](docs/plans/20-toolbar-look.md) | Names on Palette and Background, icon-only view actions, larger and heavier icons, blue for what is chosen, a camera for Scenes, ray tracing with or without the background, palettes of the user. |
| 18 | [Dialog sizes and the scroll bar of the sequence viewer](docs/plans/18-dialogs-scrollbar.md) | The form loader sets a form up on the dialog itself; the sequence viewer scrolls with a Qt scroll bar. |
| 17 | [Legacy menu rows and the old internal GUI](docs/plans/17-legacy-ui.md) | Menu rows that led nowhere, the Tk stand-ins, then the C++ code of the old panel and of the GL menus: 316 lines of Tk stand-ins and 4,160 lines of panel and menu code deleted in five slices, each a working program. |
| 16 | [Background menu and palette caption](docs/plans/16-background.md) | A toolbar button with 13 backgrounds, plain and gradient, remembered only when asked; the palette menu says what it colors. |
| 14 | [Action and right-click menus](docs/plans/14-menus.md) | One builder for objects and groups, one for selections; the A menu of an object has 10 rows, the rest under "more"; right click on a row gives rename, duplicate and delete at once. `menu.py` 1,869 to 1,745 lines. 14d (4.19.2): "select" and "split" rows by chain and by kind of molecule, new command `split_types`; presets left the A menus; "split by state" moved there in 4.19.3. 14e (4.19.31, 4.19.32): one list in Show, cartoon styles and hydrogens as hover menus, Show 21 to 15 rows, Hide 22 to 17. |

## Finished work, in execution order

The letters identify milestones in the detailed plans. Order 5 (measured
optimization and workspace increments) is still open and stays in the roadmap.

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

Decided by the user on 2026-11-20. Recorded in the plans; "to build" means
nothing is built yet.

| # | Decision | Where it goes |
| --- | --- | --- |
| 1 | A large surface is built on a worker thread (option A). | 1b, order 6 of the roadmap. To build. |
| 3 | The icon and the logo were generated with ChatGPT; the user owns them. They get "a license that is good for trade marks". | Done in 4.19.43: `data/pymol/icons/LICENSE`, a notice outside the two code licenses (unchanged copies travel with the program and may refer to it; a changed version needs its own). `docs/licenses.md`, plan 9. |
| 4 | The release builds stay on GitHub Actions for now. | 5c is shelved; nothing was built for it. Plan 5. |
| 5 | The outline of the looks is drawn in the viewport too: black, or a color that shows on the chosen background. | 15b, order 5. To build. |
| 6 | The ChimeraX object colors become a palette. | 15c, order 1. To build. |
| 7 | All five effects of 15e. | Order 2. To build. |
| 13 | "Decide by yourself." Decided as recommended: the shot list goes into the session file; the 58 Program rows of the Movie menu go; the keyframe strip of the core stays for now. | Step 19, order 3. To build. |
| 15 | As recommended: blue hover in every menu; Orient acts only on what is visible. | Step 20, order 1. To build. |
| 16 | As recommended: FXAA for smooth edges; `sphere_mode` capped at 9, its test and two reference images deleted; the background image stored in the session file. | 21f, order 4. To build. |
| 18 | As recommended: idle OpenMP threads sleep at once. | 1b, order 1. To build. |
| 17 | As recommended: undo by snapshots for edits, the coordinate ring for moves (option C). | 21g, order 8. To build. |
| 19 | Yes: the grid surface is tried as an experiment, then judged on numbers and pictures. | 1b, order 7. To build. |

14 was answered by "release 17" (4.19.42). No question is open.

## Finished milestones of open steps

Steps 1, 3, 8, 15, 19 and 21 stay in the roadmap. These parts of them have
shipped.

| Step | Milestone | Result |
| --- | --- | --- |
| 1 | 1b, nine changes so far | 4.5.10 session load 0.92 s to 0.14 s (6.6x). 4.5.12 surface build 11.97 s to 9.66 s (1.24x). 4.7.7 to 4.7.9 surface build 9.44 s to 6.24 s (1.5x). GUI frame time measured 2026-11-14 (`testing/bench_gui.py`): software rendering under WSL is the main cost. 4.7.10 atom labels fixed on drivers without geometry shaders. 4.13.3 the ray tracer's voxel table 0.68 s to 0.28 s. 4.19.15 the window draws on the GPU under WSL (1aon cartoon 46 ms to 9.8 ms per frame). 4.19.16 surfaces of very large structures (4v6x 48.6 s to 31.0 s). 4.19.40 the neighbor list is not zero-filled before it is written (1aon surface about 0.3 s of 5.5 s faster, same triangles). Outside the list of 1b, found with the same measurements: 4.19.8 to 4.19.10 `get_sasa_relative`, `util.color_by_area` and `util.chainbow`. Numbers: the ChangeLog and, against PyMOL 3, [docs/benchmark.md](docs/benchmark.md). |
| 3 | Slices 1 to 3 | Done 2026-11-08 (4.5.0): objects dock, layout persistence, Panels menu. |
| 3 | Slice 4 and the workspace layout | 4.5.11 Qt Objects panel replaces the viewport's object list. 4.5.14 action toolbar on top, command area at the bottom, toggle bar. 4.5.15 row state and colors. 4.5.16 no second prompt in the viewport. 4.5.17 menus stay on the screen under WSLg. 4.5.18 Qt menus for the viewport's right click. 4.13.4 scenes as a docked panel with thumbnails. |
| 3 | Slice 5, partly | 4.5.2 dark theme. 4.5.7 UI Scale and the dark-theme color audit. 4.5.13 no fixed point sizes in rich text. Open: spacing of the remaining dialogs. |
| 3 | Moved to other steps | The removal of the old C++ panel became step 17 (17c, 4.17.1), the timeline step 19 (4.18.0); dialog sizes and the scroll bar of the sequence viewer shipped as step 18 (4.15.1, 4.17.0). |
| 8 | 8a — safety net | Done 2026-11-13 (4.7.2): CI job with ASan and UBSan, three bugs fixed, coverage measured (about half of the core). Catch2 is compiled in CI and not run: that is 8h. |
| 8 | 8h — Catch2 in CI | Done 2026-11-16: the three build jobs ran the Catch2 tests all along, through `ctest.py`; the sanitizer job now runs them too. One defect found and fixed (4.14.1, `ColorGetName`). |
| 8 | 8i — dead `#ifdef` branches | Done 2026-11-16 (4.14.2): the branches of 12 macros nothing defines, 2,207 lines in 97 files, one commit per macro. Proof: the preprocessed text of all 197 translation units is identical before and after. Two more macros of the same kind in 4.19.19, with step 21: `NO_MMLIBS` and the atom-typing blocks behind `_PYMOL_IP_EXTRAS`. The last five in 4.19.38: `PYMOL_COMM`, `PYMOL_COLL`, `PYMOL_EDU`, `_PYMOL_IP_SPLASH`, `_PYMOL_IP_EXTRAS`, 100 lines in 10 files, same proof. |
| 8 | 8b — strings, mostly | 4.7.3 to 4.7.6: 408 of 475 `sprintf`, `strcpy` and `strcat` calls are bounded; three real defects fixed with a test. About 80 calls through a pointer close with 8c and 8e. |
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
| 21 | Removals | Done 2026-11-19 (4.19.18 to 4.19.26): [docs/plans/21-commercial-features.md](docs/plans/21-commercial-features.md). All Maestro file support, mmlibs atom typing, the MOE, `.vis` and `.phypo` stubs, MTZ maps, `help_setting`, `callout`, `desaturate`, the FreeMOL test. `clean` was already rebuilt in 4.12.1. |
| 21 | 21a to 21e — rebuilt commands | Done 2026-11-19 (4.19.33 to 4.19.37). `save file.stl` (binary STL from the meshes of the USD export). `assign_stereo` with rdkit, and label > stereochemistry is back. `distance` modes 5 to 7 and `pi_interactions`: the finder was already in the core, only the call was missing. `focal_blur`: average of images of a turned camera. `morph`: linear interpolation, refined by sculpting. Each old test runs without the `incentive` mark. |

## Validation of the original draft, closed rows

As written on 2026-11-08. The steps these rows belong to are finished; the rows
that still steer open work are in the roadmap.

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
