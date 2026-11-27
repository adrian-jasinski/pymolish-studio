# 39 — One command after cloning

[Roadmap](../../PLAN.md) · requested 2026-11-27

## Result 2026-11-27 — 4.96.1

**39a implemented; clean-machine trials remain open, order 5.** The user
selected both recommended options below. `install` and `install.cmd` use
only existing dependencies and platform tools. This is a build-tooling
change, so the patch version advances under the repository version rule.

Measured/checked in this run:

- Standalone installer checks: 11 passed; the Windows-only case was skipped
  on Linux. They cover routing, packages, preview, extras, refusal, EOF,
  failed setup/pip, paths with spaces and environment reuse.
- A real Linux C++ build installed 4.96.1 with `json=True`,
  `use-msgpackc=c++11`, `testing=True`, `jobs=6`. It reused the existing
  development virtualenv, used installed dependencies without build
  isolation, and found already-available nlohmann headers via a temporary
  `PREFIX_PATH`. This did not exercise apt or a fresh environment.
- `pip check`, Qt imports and headless glycine creation passed. The full
  suite: **1257 passed, 206 skipped, 17 subtests passed**, one existing
  Biopython deprecation warning. Ruff and shell syntax checks passed.
- Real Windows `cmd.exe` ran preview through WSL, including extras and a
  UNC checkout; no compiler, Pixi or Python was installed on Windows.
  The preview exposed and fixed a batch argument-parsing directory bug.

No timing or download-size claim. Left to try: complete setup from clean
Debian/Ubuntu and Fedora, Linux Pixi fallback, Windows x64 and Apple silicon;
compiler installation, extras, rerun and a real Qt window. macOS/Fedora
command tests use stand-ins. Other architectures/distributions receive
manual instructions. No system packages or vendor installers were changed
on the development machine in this run.

The Windows extras spelling is `--extras "chem,fix,ai"`, or `--extras ""`
for core only; cmd treats unquoted equals and commas as argument separators.
Unix retains `--extras=chem,fix,ai`. The Windows launch instructions show
both PowerShell's call operator and the cmd form. No release/CI push was
made; the implementation commit is `2574f54c`.

## Plan recorded 2026-11-27, before implementation

Starting version: **4.96.0**. This is a source installer, separate from the
downloadable Windows installer in step 5d. Inspection covered `setup.py`,
`pyproject.toml`, `pixi.toml`, CI and the existing installation guide. No
installation time, size or clean-machine success is claimed yet.

After `git clone` and `cd pymolish-studio`, run `./install` on Linux or
macOS; run `.\install.cmd` in Windows PowerShell or `install.cmd` in cmd.
Keep the scripts in the repository root so those commands need no setup.

## Choices offered before building

1. **Recommended:** Linux system packages and a local Python environment;
   reuse Pixi on Windows/macOS and when Linux lacks a suitable Python.
   Alternative: Pixi everywhere. Reuse the native dependencies already in
   `pixi.toml`; do not introduce another environment manager.
2. **Recommended:** core app, with a prompt for the existing `chem`, `fix`
   and `ai` extras. Alternative: install all three by default. Development
   tools and MAFFT remain separate.

**Accepted by the user on 2026-11-27:** both recommended options.
Command names follow the recommendation above;
the alternative is explicit interpreter commands with longer filenames.

## Implementation

1. Detect OS and architecture before changing anything. Automate Debian /
   Ubuntu with apt, Fedora with dnf, macOS Apple silicon with Pixi and
   Xcode Command Line Tools, Windows x64 with Pixi and Visual Studio C++
   Build Tools. Other systems get an explanation and manual-install link;
   no guesses at package names or automatic third-party repositories.
2. Show missing system packages and ask before installing them. Elevate
   only the package-manager command, never pip or the whole installer.
   On Linux with a suitable Python, use a repository-local virtualenv.
   Otherwise use the existing Pixi `py313` environment. Do not replace
   system Python or install Python packages globally.
3. Supply a compiler, OpenGL, GLEW, GLM, libpng, FreeType, msgpack C++
   headers, netCDF and nlohmann-json; include Linux Qt/X11 runtime libraries.
   Keep BinaryCIF, trajectories and glTF available. Let pip read Python
   requirements and build requirements from `pyproject.toml`.
4. For missing Pixi, offer its official installer on Unix or winget on
   Windows. For compilers that require an interactive vendor installation,
   show the command, offer to start it, then stop with rerun instructions.
   Never report completion while a prerequisite installer is still running.
5. Provide `--dry-run`, `--yes` and `--extras=chem,fix,ai` (including an
   empty extras value for core only). Preview must make no changes or
   downloads. `--yes` explicitly accepts required setup; optional extras
   still require selection. EOF means stop wherever consent is needed.
6. Reuse environments on rerun, preserve failures and their exit status,
   check the installed core and Qt imports, then print the exact launch
   command. Resolve the repository relative to the script, including paths
   containing spaces. Do not edit shell profiles or create desktop entries.

## Checks and delivery

- Leave runnable checks under `testing/tests/system/`: OS routing,
  commands, preview, missing dependencies, refusal, EOF, subprocess failure,
  paths with spaces, rerun and launch instructions. Stub installers/builds
  so unit checks never change the host.
- Run a real local build/headless import where dependencies are already
  available. Record native Windows/macOS checks separately from simulated
  command checks; the latter do not prove a clean-machine installation.
- Update README and `docs/install.md`, version and ChangeLog for the build
  tooling change; commit the implementation separately from the plan.
  Update the roadmap with actual results and outstanding platform checks.

## References checked for implementation

- [Pixi installation](https://pixi.prefix.dev/latest/installation/): official
  bootstrap, Homebrew/winget choices and disabling shell-profile changes.
- [Microsoft C++ Build Tools workload](https://learn.microsoft.com/en-us/visualstudio/install/workload-component-id-vs-build-tools):
  `Microsoft.VisualStudio.Workload.VCTools` and its recommended SDK/compiler.
- [Apple Command Line Tools](https://developer.apple.com/documentation/xcode/installing-the-command-line-tools/).
- [Qt Linux requirements](https://doc.qt.io/qt-6/linux-requirements.html):
  the xcb plugin needs runtime libraries as well as the PySide6 wheel.

No package-manager framework, bundled compiler, alternate build backend,
system-Python replacement, uninstaller or GUI installer in this slice.
