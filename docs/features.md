# Features

What pymolish-studio adds, changes and removes compared with Open-Source
PyMOL(TM), the project it is a fork of. The numbers in brackets are
pymolish-studio versions; [ChangeLog](../ChangeLog) has the details of each.

## Interface

- **One GUI toolkit:** Qt 6 through PySide6 (4.1.0).
- **Dark theme**, on by default. Display > Dark Theme switches it (4.5.2).
- **Scale button** in the toolbar, 100 to 200 %, for the size of text and
  controls. The interface starts at 150 % (4.7.0).
- **Workspace:** action toolbar with line icons above the viewport, log and
  command line below it (4.5.14, 4.7.0). The window layout is saved on exit
  and restored on start (4.5.0).
- **Objects panel:** objects, selections and groups in a Qt panel. A click
  on a row shows or hides the object, a double click zooms on it, and each
  row has the Action, Show, Hide, Label and Color menus (4.5.11, 4.5.15).
- **States panel:** first, previous, play, next, last, a counter to jump to
  a state, and a speed button. It appears when there is more than one state
  or movie frame (4.6.0).
- **Menus:** the right-click menu of the viewport is a Qt menu at the mouse
  pointer; all menus have rounded corners and line icons (4.5.18).
- **Own name and icon:** window title, About box and application icon say
  pymolish-studio (4.8.0).

## Speed

Measured on one machine; method and all numbers are in
[baseline.md](baseline.md).

| Work | Before | After | Version |
| --- | --- | --- | --- |
| Load a 17 MB session (`.pse`) | 0.92 s | 0.14 s | 4.5.10 |
| Build the surface of 1aon (58870 atoms), with a small ray | 11.97 s | 9.66 s | 4.5.12 |
| The same surface build | 9.44 s | 6.24 s | 4.7.7 to 4.7.9 |

## Builds

- **Bundles** for Linux, Windows and macOS (arm64) that run without an
  installed Python, published with wheels and `SHA256SUMS` on the
  [Releases page](https://github.com/adrian-jasinski/pymolish-studio/releases)
  (4.4.0, 4.5.1). They are unsigned preview builds.
- **Name:** the package and the launcher are `pymolish`. The Python module
  is still `import pymol` (4.5.5).
- **Python 3.11 or newer** (4.1.0).

## Removed

| Removed | Version | Use instead |
| --- | --- | --- |
| PyQt5, PyQt6 and PySide2 support | 4.1.0 | PySide6 |
| Tk GUI, Pmw and the Tk plugin manager | 4.3.0 | The Qt GUI. Plugins that build Tk windows no longer work. |
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

- The `cmd` API and the plugin loader: see [plugins.md](plugins.md).
- Reading and writing PDB, mmCIF, SDF/MOL and PSE sessions; PNG export.
- Ray tracing, movies, the POV-Ray renderer, the VMD molfile plugins.

Open and planned work is in the [roadmap](../PLAN.md).

---

PyMOL is a trademark of Schrodinger, LLC.
