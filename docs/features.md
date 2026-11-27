# What is different

[Docs home](README.md) · Checked with version 4.90.0.

This page is for people who know Open-Source PyMOL(TM) and want to know what
pymolish-studio changed. New to both? Start with
[Getting started](getting-started.md).

The short version: the molecular engine, the command language and the main
file formats are the same. The window is new, there are new commands and
panels, some slow operations are faster, and old interfaces and unused
features are removed. The history, version by version, is in the
[ChangeLog](../ChangeLog).

**On this page:** [The window](#the-window) ·
[New things to do](#new-things-to-do) · [Speed](#speed) ·
[Getting it](#getting-it) · [Removed](#removed) · [Kept](#kept)

## The window

| What | How it is now | More |
| --- | --- | --- |
| Toolkit and theme | One window, Qt 6. Dark by default; Display > Dark Theme switches it. | |
| Layout | Toolbar with icons on top, viewport in the middle, the Objects panel on the right, the tabs Command, Sequence and Chat at the bottom. Panels can be moved, floated and closed; the layout is remembered. | [Getting started](getting-started.md#2-know-the-window) |
| Size | The percent button in the toolbar sets the size of text and controls, 50 to 300 %; it starts at 150 %. Under WSL a change waits for the next start. A−, A+ and Reset set the text size of each bottom tab on its own. | [Troubleshooting](troubleshooting.md#the-window) |
| Objects panel | Objects, selections and groups as rows with the A, S, H, L and C menus. Rows are filtered, renamed (F2), deleted (Delete) and moved (right-button drag, or Alt with the arrow keys). | [Structures](structures.md) |
| Selecting | A toolbar button for what a click selects, and buttons that select the protein, the ligands, the water and more. | [Structures](structures.md) |
| Presets | A toolbar menu in groups: cartoon, atoms and bonds, surface, binding; transparency; light, theme and floor for the whole scene. Presets keep the colors. Undo takes a preset back. | [Appearance](appearance.md) |
| Palettes and background | Toolbar buttons for the colors of objects and chains (eleven palettes and your own) and for the background. | [Appearance](appearance.md) |
| Menus | Right-click menus open at the pointer as normal menus. The A menu is shorter; less used rows are under "more". | |
| States | A strip under the object list (first, previous, play, next, last, jump, speed) when there is more than one state or movie frame. | [Scenes and movies](scenes-movies.md) |

## New things to do

| What | In short | Guide |
| --- | --- | --- |
| Ball and stick | A representation of its own, used for ligands by the presets and when a structure is loaded. | [Appearance](appearance.md) |
| Surface looks | Glossy, candy glass, frosted and clay surfaces; glass around a cartoon; an optional surface built on a grid. | [Appearance](appearance.md) |
| Lights, themes, floor | Lights with outlines (figure, comic, sketch ...), color themes, a floor with shadow or mirror image. | [Appearance](appearance.md) |
| Ligands | The next ligand with its pocket and contacts; the ligand drawn in 2D with the same contacts. | [Ligands](ligands.md) |
| Sequences | A Sequence tab, and an alignment window with local MAFFT, linked selection and fitting. | [Sequences](sequences.md) |
| Property table | Objects as rows, properties as columns; import from CSV or Excel, stars, Follow. | [Property table](properties.md) |
| Scenes and Timeline | A Scenes panel with pictures; a movie as a list of shots with tours, fades and export. | [Scenes and movies](scenes-movies.md) |
| Many structures | Load a folder, export many objects, fetch by UniProt accession, predicted structures, commands for groups. | [Structures](structures.md) |
| Clean and repair | Remove waters, ions, ligands or crystallization additives; optimize a ligand (rdkit); fix and relax a protein (PDBFixer, OpenMM). | [Editing and analysis](editing-analysis.md) |
| SMILES | Build a molecule from a SMILES. | [Editing and analysis](editing-analysis.md) |
| Packed sessions | `.psex`: the content of a `.pse` in a fraction of the size. | [Saving](saving.md) |
| AI assistant | A Chat tab that runs reviewed commands in the session, and a connector for agents on this computer. | [Assistant](assistant.md) |
| Commands that needed the commercial build | `save file.stl`, `assign_stereo`, `pi_interactions`, `focal_blur`, `morph`. | [Commands](commands.md#pymol-commands-that-needed-the-commercial-build) |

Every new command is listed in [Commands](commands.md).

## Speed

Measured against upstream PyMOL 3.2 on the same machine, same workloads,
both on Python 3.14, 2026-11-19. Method and all numbers:
[benchmark.md](benchmark.md).

| Work | PyMOL 3.2 | pymolish |
| --- | --- | --- |
| Build the surface of 1aon (59192 atoms) | 10.4 s | 5.0 s |
| Build the surface of a ribosome, 4v6x (239306 atoms) | 86 s | 33 s |
| Build the cartoon of the spike trimer 6vxx (24621 atoms) | 0.33 s | 0.21 s |
| Load a session (`.pse`) of 10 structures, 455k atoms | 9.1 s | 1.3 s |
| A frame of the 1aon cartoon while rotating, on WSL | 44 ms (CPU) | 8 ms (GPU, 4.19.15) |
| Ray-traced images | same | same |

## Getting it

- **Ready-to-run bundles** for Linux, Windows and macOS (arm64) on the
  [Releases page](https://github.com/adrian-jasinski/pymolish-studio/releases).
  No Python needed. Unsigned preview builds (4.4.0, 4.5.1).
- **The program is called `pymolish`.** In Python it is still
  `import pymol`, so scripts keep working (4.5.5).
- **Python 3.13 or newer** when you build it yourself (4.12.8; it was
  3.11 since 4.1.0):
  [Install from source](install.md).

## Removed

Each row was unused, outdated or had a better replacement.

| Removed | Version | Use instead |
| --- | --- | --- |
| PyQt5, PyQt6 and PySide2 support | 4.1.0 | PySide6 |
| Tk GUI, Pmw and the Tk plugin manager | 4.3.0 | The Qt GUI. Plugins that build Tk windows no longer work. |
| Stand-ins for Tk in plugins (`app.menuBar`, `app.root`, fake `tkMessageBox`), the "Legacy Plugins" menu | 4.16.1 | `pymol.plugins.addmenuitemqt`; see [Writing a plugin](plugins.md). |
| Menu rows Internal GUI, Internal Prompt, Internal Feedback, Overlay | 4.16.0 | The settings of the same names, typed. |
| The object list, mouse mode table, movie buttons and wizard buttons drawn inside the viewport; the settings `internal_gui`, `internal_gui_width`, `internal_gui_name_color_mode`; the option `-i` | 4.17.1 | The Objects panel. Take `set internal_gui...` lines out of your pymolrc. |
| GLUT GUI | 4.3.1 | The Qt GUI |
| `chempy.fast` | 4.4.1 | Nothing; it was unused |
| VTK-m isosurface backend | 4.4.2 | The internal marching cubes |
| `mpeg_encode` movie encoder | 4.4.3 | ffmpeg or convert |
| XML-RPC server (`-R`), built-in HTTP server, web examples | 4.4.4 | Nothing |
| OpenVR support | 4.4.5 | Nothing |
| COLLADA (`.dae`) export and import | 4.4.6 | glTF export |
| MMTF import and export | 4.4.7 | BinaryCIF |
| Startup image in the viewport | 4.6.1 | The notice is still printed to the log |

## Kept

- The `cmd` API and the plugin loader: [Writing a plugin](plugins.md).
  What does not work as in PyMOL is listed in
  [Compatibility with PyMOL](reference.md#compatibility-with-pymol).
- Reading and writing PDB, mmCIF, SDF/MOL and PSE sessions; PNG export.
- `.psex`, a packed session: the content of a `.pse` in a fraction of the
  size (1AON: 19.6 MB as `.pse`, 1.1 MB as `.psex`), written faster. PyMOL
  itself reads `.pse`, which stays available.
- Ray tracing, movies, the POV-Ray renderer, the VMD molfile plugins.

What comes next is in the [roadmap](../PLAN.md).

---

PyMOL is a trademark of Schrodinger, LLC.
