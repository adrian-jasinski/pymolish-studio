# Install from source

Most people do not need this page: the
[Releases page](https://github.com/adrian-jasinski/pymolish-studio/releases)
has ready-to-run bundles. Build from source when you want to change the code
or need a system the bundles do not cover.

The build compiles the C++ core with CMake and installs the Python package
with `pip`. It takes a few minutes the first time.

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

python3 -m venv .venv && . .venv/bin/activate
pip install --config-settings json=True .
pymolish
```

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
