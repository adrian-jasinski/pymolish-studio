# 40 — pymolish in a web browser

[Roadmap](../../PLAN.md) · requested 2026-11-27

## Result 2026-11-27 — research only, no version

Nothing is built. This page compares the ways to run pymolish in a browser
with an interface like the desktop window, and asks two questions
(140, 141). Measured in this run, on `feature16` at 4.97.0:

- The Qt window is **12,072 lines of Python in 23 files** of
  `modules/pmg_qt/` (largest: `pymol_qt_gui.py` 1,596, `builder.py` 1,555,
  `object_panel.py` 958).
- The old OpenGL panel drawn by the C++ core is gone (step 17). A browser
  build of the core alone therefore shows a bare viewport: every panel,
  menu and dialog would have to be built again.
- The core still uses desktop OpenGL outside shaders: **110 `glBegin`
  calls** and **55 fixed-function calls** (`glMatrixMode`, `glLightfv`,
  `glPushMatrix`) in `layer*/`. Shaders are `#version 120`; the bezier
  shaders are `#version 400` tessellation, which WebGL 2 does not have.
  Only 4 `PURE_OPENGL_ES_2` mentions remain (in `ShaderMgr.cpp`).

Not checked: no build was tried, no streaming server was run, no latency
or download size was measured. Numbers below that are not in this list are
estimates and say so.

## What "native-like" needs

The same panels, menus, keyboard shortcuts, command line, mouse modes,
plugins and file formats as the desktop window, and rotation that does not
lag. No option gives all of that; the two real options trade them.

## Options

### A — Stream the real window (recommended first)

The unchanged Linux build runs in a container on a server; the browser
shows its window and sends mouse and keyboard back.

- **How:** [Selkies](https://github.com/selkies-project/selkies) (MPL-2.0;
  WebRTC or WebSocket, GPU or software encoding, two-way clipboard). The
  [linuxserver.io Selkies base image](https://docs.linuxserver.io/selkies/)
  wraps one desktop app; the Dockerfile is an estimated 10 to 20 lines that
  install the existing Linux bundle and start it. Alternatives: KasmVNC,
  [Xpra HTML5](https://github.com/Xpra-org/xpra-html5) (older and slower in
  its own 2019 measurements).
- **Native feel:** identical. It *is* the desktop window: every panel,
  dialog, plugin, the Chat tab and Claude Code, rdkit and openmm.
- **Costs:** a server per active user (CPU software rendering is enough for
  small structures; large surfaces need a GPU); network latency on every
  rotation; files live on the server (upload/download through the browser);
  some shortcuts (Ctrl+W, Ctrl+T) belong to the browser unless the tab is
  full-screen or an installed web app.
- **Effort:** estimate 1 to 3 days for a working container, one CI job to
  build the image from the bundle CI already makes.

### B — Run pymolish inside the browser (WebAssembly)

The C++ core and the Python `cmd` layer compile to WebAssembly and run in
[Pyodide](https://pyodide.org); drawing goes through WebGL 2.

- **Proof it can work:** [PyMOL-Wasm](https://github.com/yakomaxa/PyMOL-Wasm)
  (58 stars, last commit 2026-08-31, [demo](https://yakomaxa.github.io/PyMOL-Wasm/)).
  PyMOL 2.6 built with Emscripten and exodide, loaded by Pyodide, old
  OpenGL translated by [gl4es](https://github.com/ptitSeb/gl4es), driven
  by a plain HTML page. Its README lists crashes (`show cell`,
  `set orthoscopic`), wrong picking after a resize, a size limit for large
  structures; the modified PyMOL source is not published. It shows the
  route and why a fork of the core outside the core's repository rots.
- **New since then:** Pyodide 314 (June 2026) and PEP 783 let Emscripten
  wheels (`pyemscripten_2026_0_wasm32`, Python 3.14) be published on PyPI
  and installed at run time, so the core can ship as an ordinary wheel.
- **The blocker is the window, not the core:** PySide6 does not run in the
  browser. Qt calls it "on the backburner" ([PYSIDE-962](https://bugreports.qt.io/browse/PYSIDE-962));
  the only 2026 sign is a "preliminary discussion" with QuantStack
  ([Qt for Python notes](https://wiki.qt.io/Qt_for_Python_DevelopmentNotes)).
  So the 12,072 lines of Qt are rewritten in HTML/TypeScript. It can look
  close to the desktop, but it is a second interface to keep in step with
  the first.
- **Core work:** shaders to GLSL ES 3.00 (the shader preprocessor already
  exists), the 110 `glBegin` and 55 fixed-function calls replaced or
  shimmed with gl4es, threads off (ray tracing and surfaces single-
  threaded), files through the browser's file system. No tessellation
  shaders, no Claude Code or other subprocesses, no openmm; rdkit only if
  its Pyodide build works with ours.
- **Native feel:** rotation is instant and it works offline from a static
  page (GitHub Pages, no server cost), but every panel is a copy.
- **Effort:** estimate 2 to 4 weeks for a viewport that loads, draws and
  rotates a PDB; estimate several months for an interface near the desktop.

### Not chosen

| Option | Why not |
| --- | --- |
| Qt for WebAssembly (C++ Qt) | Our window is Python (PySide6); this needs it rewritten in C++. |
| Qt WebGL streaming plugin | Qt 5 only; not in Qt 6. |
| Qt VNC platform plugin + noVNC | No OpenGL, so no viewport. |
| Core on a server, new HTML UI that shows its pictures | Needs a server *and* a rewritten UI: the costs of A and B together. |
| Switch to a web viewer ([Mol*](https://molstar.org), [Patinae / PyMOL-RS](https://zmactep.github.io/pymol-rs/), Rust + WebGPU, claims the PyMOL command set) | Not pymolish; none of our panels, presets or sessions. Worth watching as a reference for B. |

## Same repository or a separate one

- **A — in this repository.** It is packaging of the same build, like the
  Windows installer (5d): one `packaging/web/Dockerfile`, one CI job, the
  image tagged with the version. A separate repository would copy the
  release pipeline to hold two files.
- **B — split.** The core changes (`__EMSCRIPTEN__` paths, ES shaders, a
  CI job that builds the wasm wheel) stay **here**: they touch `layer0` to
  `layer4`, and a separate fork of the core goes stale (PyMOL-Wasm is
  frozen at 2.6). The browser interface (HTML/TypeScript, npm) goes to a
  **separate repository** that pins a wheel version: npm would break the
  dependency rule of this repository (`AGENTS.md` 2.2), and the web page
  has its own release pace.

## Slices (if chosen)

- **40a** — container with Selkies and the Linux bundle; CI builds the
  image. Check: open a PDB, rotate, a dialog, copy and paste, upload and
  download a file; measure latency on LAN and from outside.
- **40b** — wasm proof of the core: `pymolish` wheel built for Pyodide,
  one page that loads a PDB, shows cartoon and rotates. Measure download
  size and frame rate. Stop here if it is not usable.
- **40c** — the browser interface in a separate repository, panel by
  panel, starting with the command line and the Objects panel.

## Questions

- **140 — Which route?** **A** stream the desktop window (recommended:
  identical interface, days of work, answers whether people use it in a
  browser). **B** WebAssembly in the browser (no server, instant rotation,
  months, a second interface). **A then B:** A now, 40b as a proof later.
- **141 — Where does it live?** For A: in this repository (recommended).
  For B: core build here, browser interface in a new repository
  (recommended), or everything here (npm in this repository).
