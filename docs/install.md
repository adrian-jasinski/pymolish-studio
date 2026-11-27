# Install from source

Most people do not need this page: the
[Releases page](https://github.com/adrian-jasinski/pymolish-studio/releases)
has ready-to-run bundles. Build from source when you want to change the code
or need a system the bundles do not cover.

The build compiles the C++ core with CMake and installs the Python package
with `pip`. It takes a few minutes the first time.

## One command after cloning

```sh
git clone https://github.com/adrian-jasinski/pymolish-studio.git
cd pymolish-studio
./install
```

On Windows, the last command is `.\install.cmd` in PowerShell or
`install.cmd` in cmd. No Python installation is needed beforehand there.

The script lists missing system packages and asks before installing them.
Run it as your normal user: only Linux system-package commands use `sudo`.
It then offers the existing chemistry, structure-repair and Chat libraries,
installs the app, checks dependencies and the headless core and Qt imports,
and prints the launch command. It does not open a window during setup.

| System | How it installs |
| --- | --- |
| Debian / Ubuntu | apt for the compiler, native libraries and Qt runtime libraries. Python 3.13+ with headers, `venv` and `ensurepip` uses `.venv-install`; otherwise Pixi supplies Python and native libraries on x64. |
| Fedora | The same flow, with dnf package names. |
| macOS, Apple silicon | Pixi supplies Python and native libraries. If Apple Command Line Tools are missing, the script offers to open `xcode-select --install`; finish that installer and rerun. |
| Windows x64 | Pixi supplies Python and native libraries. Missing Pixi or Visual Studio C++ Build Tools can be installed with winget. Finish prerequisite setup, open a new terminal when instructed, and rerun. Existing Visual Studio without C++ needs its **Desktop development with C++** workload added in Visual Studio Installer. |

Pixi is already used by this project's builds. On Unix, if it is missing,
the script offers to run the [official Pixi installer](https://pixi.prefix.dev/latest/installation/)
into `~/.pixi/bin`, without editing shell profiles. If a dependency cannot
be installed automatically, the script stops with instructions. Intel Macs,
Windows ARM and other Linux distributions use the manual instructions
below; the current Pixi manifest does not cover those architectures.

The Linux command routes and failure handling have automated checks.
Windows command preview has also run in cmd.exe; complete clean-machine
installation on Windows/macOS and native Fedora trials remain to be done.

Preview makes no changes or downloads:

```sh
./install --dry-run
```

For unattended required setup and explicitly chosen extras:

```sh
./install --yes --extras=chem,fix,ai
./install --yes --extras=          # core only
```

Windows uses a quoted extras argument because cmd splits commas and equals:

```powershell
.\install.cmd --dry-run
.\install.cmd --yes --extras "chem,fix,ai"
.\install.cmd --yes --extras ""
```

`--yes` accepts required setup; it does not select optional libraries.
`chem` adds SMILES and ligand cleaning, `fix` adds structure repair and
relaxation, and `ai` adds Chat provider libraries. Nothing installs a provider
CLI, signs you in or configures an account. MAFFT remains separate below.

Rerun the same command after a failed setup or a `git pull`. Existing local
environments are reused. A failure never counts as a successful install;
fix the reported error before retrying. A Linux/macOS build running out of
memory can use `JOBS=2 ./install`. Network access and free disk space for
the compiler, environment and build are required; sizes vary by system.

Launch with the exact command printed at the end. Typically, from this
folder it is `.venv-install/bin/pymolish` on the Linux virtualenv route,
or `pixi run -e py313 pymolish` on the Pixi route (use `~/.pixi/bin/pixi`
if the bootstrap installed Pixi outside PATH). Keep the checkout in place:
these environments belong to it. No desktop shortcuts are created.

## Manual installation

## What you need

| Needed | For |
| --- | --- |
| C++17 compiler (gcc 8 or newer), Python 3.13 or newer with `pip` | the build; `pip` fetches CMake itself |
| OpenGL, GLEW, GLM, libpng, FreeType | drawing, pictures, text |
| PySide6, numpy | the window and arrays; `pip` installs them |

| Optional | For | Switch |
| --- | --- | --- |
| msgpack-c 2.1.5 or newer | BinaryCIF files | `use-msgpackc=no` builds without it |
| netCDF | trajectory formats of the VMD plugins | `vmd-plugins=no` builds without it |
| nlohmann-json 3.10 or newer | glTF and GLB export | off unless `json=True` |
| Catch2 | C++ tests | off unless `testing=True` |

Give a switch to `pip` as `--config-settings name=value`.

## Linux (Ubuntu)

These are the packages the CI build installs; add `build-essential` if you
have no compiler.

```sh
sudo apt-get install libfreetype6-dev libglew-dev libglm-dev libpng-dev \
    libmsgpack-dev libnetcdf-dev nlohmann-json3-dev catch2

python3.13 -m venv .venv && . .venv/bin/activate
pip install --config-settings json=True .
pymolish
```

Install Python 3.13 or newer, with its development headers and venv support,
first. The default `python3` on an older distribution may be too old.
The automatic installer also supplies the Qt/X11 runtime libraries needed
on minimal desktops; the script's package list names them.

### On WSL

Under WSL (Windows Subsystem for Linux) pymolish draws on the graphics card
of Windows by itself (4.19.15). It does so by setting `GALLIUM_DRIVER=d3d12`
for Mesa when the variable is not set. Two variables change that:

| To | Set before starting |
| --- | --- |
| Use the faster card of a laptop with two (Mesa takes the integrated one) | `MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA` (part of the card's name) |
| Draw on the CPU as before, for example when the window stays black | `GALLIUM_DRIVER=llvmpipe` |

## Windows and macOS

The native libraries come from conda-forge through
[pixi](https://pixi.sh); `pixi.toml` lists them. This is how CI builds.

```sh
pixi run -e py313 pip install --config-settings json=True .
pixi run -e py313 pymolish
```

## Optional sequence alignment

The sequence window works without MAFFT; its **Align sequences** action and
`sequence_align` command require a local MAFFT installation. No sequences
are uploaded. On Debian/Ubuntu, install `mafft` from the system package
manager. For macOS and Windows, use the
[official downloads](https://mafft.ddbj.nig.ac.jp/alignment/software/).
Keep the Windows distribution together and choose its `mafft.bat` entry
point with the window's **MAFFT…** button. On any platform, an executable
on PATH is discovered automatically; the chooser overrides it.

MAFFT is not bundled or downloaded by pymolish. The Linux integration was
tested with MAFFT 7.505; Windows batch launch and macOS still need native
platform checks. MAFFT's core uses a BSD-style license; separately offered
extensions have other terms and are neither needed nor distributed here.

## Working on the code

An editable install: Python edits under `modules/` take effect on the next
start. After a C++ or shader edit run the same command again; CMake rebuilds
only what changed.

```sh
pip install cmake numpy setuptools
pip install --no-build-isolation --config-settings testing=True -e '.[dev]'
```

| Task | Command |
| --- | --- |
| Run all tests, no window | `pymolish -ckqy testing/testing.py --run all` |
| Run one test file | `pymolish -ckqy testing/testing.py --run testing/tests/api/<file>.py` |
| Compare speed with upstream PyMOL 3, see [benchmark.md](benchmark.md) | `pymolish -ckqy testing/compare.py -- gui` |
| Build a bundle into `dist/pymolish/` | `pyinstaller --noconfirm packaging/pyinstaller.spec` |

Useful when a build misbehaves:

- `--config-settings jobs=N` or `JOBS=N` limits parallel compile jobs.
- `PREFIX_PATH` is a colon-separated list of directories to search for
  headers and libraries, for example `$HOME/msgpack-c:/opt/local`.
- `CXX`, `CXXFLAGS` and `LDFLAGS` choose the compiler and its flags.
- `export CMAKE_CXX_COMPILER_LAUNCHER=ccache` uses ccache.

Next: [Contributing](../CONTRIBUTING.md).
