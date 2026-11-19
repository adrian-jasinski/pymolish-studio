# Baseline: build loop and size

Measured 2026-11-08 on commit a3105772 (code version 4.1.0). Rerun the build
loop after any build change and paste the new numbers into the PR.

## Machine

| | |
| --- | --- |
| CPU | AMD Ryzen 9 8945HX, 16 cores / 32 threads |
| RAM | 17 GB |
| GPU | NVIDIA RTX 5070 Laptop, driver 621.01 (unused: all numbers below are headless) |
| OS | Ubuntu 24.04 under WSL2, Linux 6.6.87 |
| Toolchain | gcc 13.3, CMake 3.28, Python 3.12.4 in `.venv`, PySide6 6.12.0 |
| Build | release (`DEBUG` unset), `use-msgpackc=no`, VMD plugins on, OpenMP on, no ccache, no Ninja |

## Build loop (5a)

Command for every row except the test suite:

```sh
uv pip install --no-build-isolation --config-settings use-msgpackc=no -e '.[dev]'
```

| Step | Wall time |
| --- | --- |
| Cold build, `build/` removed | 54.4 s |
| Editable install from an existing `build/` (first editable switch) | 70.6 s |
| Editable reinstall, nothing changed | 30.3 s |
| Non-editable reinstall, nothing changed | 27.2 s |
| One C++ file touched (`layer2/RepSphere.cpp`), non-editable | 7.9 s |
| One shader touched (`data/shaders/sphere.fs`), non-editable | 10.4 s |
| One Python file touched, non-editable reinstall | 9.6 s |
| One Python file touched, editable | 0 s (no command needed, `pymol.__file__` points into `modules/`) |
| Headless suite `pymol -ckqy testing/testing.py --run all` | 14.2 s wall, 997 tests |
| `build/` size | 36 MB |
| Wheel `pymol-*-cp312-linux_x86_64.whl` | 8.3 MB |
| PyInstaller one-folder bundle, Linux (PySide6 pruned of Quick/Qml/Pdf/Network) | 292 MB unpacked, 114 MB tar.gz |

Notes:
- The editable route is validated: the suite passes with the same 4 MMTF-only
  errors as the wheel install (msgpack headers not installed on this machine).
- A no-op reinstall costs 27 to 30 s in both modes, while a reinstall after
  touching one file, measured back-to-back, costs 8 to 10 s. The difference is
  outside CMake (uv resolution and setuptools overhead) and was not
  investigated. For Python edits use the editable install and skip the
  reinstall entirely.
- `--config-settings jobs=N` and `JOBS=N` now limit CMake parallelism on
  Linux and macOS; before this change the option was parsed and ignored.
- ccache: not installed here, so not measured. CMake honors
  `CMAKE_CXX_COMPILER_LAUNCHER=ccache` from the environment without code changes.

## Size after the cleanup steps (4.1.0 to 4.4.8)

Lines of C++ and Python per directory, fork point `3250e7a3` versus `4.4.8`.
Overall diff since the fork point: 255 files, +1584 / -46358 lines.

| Directory | Before | After |
| --- | --- | --- |
| layer0 | 38039 | 37616 |
| layer1 | 343734 | 341395 |
| layer2 | 73405 | 73063 |
| layer3 | 42170 | 41946 |
| layer4 | 7975 | 7866 |
| layer5 | 5926 | 4469 |
| modules/pymol | 52641 | 50020 |
| modules/pmg_qt | 7247 | 7104 |
| modules/pmg_tk | 5479 | removed |
| modules/chempy | 21797 | 21219 |
| contrib | 45668 | 39295 |
| Wheel (Linux, cp312) | 8.3 MB | 8.2 MB |

Native dependencies dropped: libxml2, mmtf-cpp, OpenVR, VTK-m, GLUT, Tk/Pmw.

## Other measurements

Performance against upstream PyMOL 3: [benchmark.md](benchmark.md). The
pymolish-to-pymolish timings of steps 1a and 1b are in the ChangeLog.

### Isosurface at 1σ: not the mesh

`isosurface` of `emd_1155.ccp4` at 1σ plus `ray 64, 64`: 10.8 s and 7.7 GB
peak, 0.7 GB afterwards. Building the object takes 0.00 s; a second `ray`
with the mesh already built takes 8 s again. Ray feedback: 3 221 521
triangles, 2.5 s converting them to primitives, 6.7 s filling the ray
tracer's voxel table (`MapSetupExpressPerp` lists every vertex in up to 27
neighbor cells, about 62 M rows for the 0.9 M-triangle protein surface). So
the cost belongs to CPU ray tracing of multi-million-triangle scenes, not to
marching cubes or mesh storage, and the OpenGL display path does not pay it.
Not optimized: a 1σ contour of a whole EM map is noise, 2σ takes 1.3 s.


### Bundle size with rdkit (4.11.3)

Linux bundle built on this machine with `packaging/pyinstaller.spec`,
2026-11-14, same tree, without and with the `chem` extra installed:

| | unpacked | tar.gz |
| --- | --- | --- |
| without rdkit | 287 MB | 109 MB |
| with rdkit 2026.9.2 (and the Pillow it needs) | 344 MB | 129 MB |

| with rdkit, pdbfixer 1.12.0 and openmm 8.6.1 (4.12.2) | 419 MB | 142 MB |

rdkit adds 57 MB unpacked and 20 MB to the download; pdbfixer and openmm add
75 MB and 13 MB. 64 MB of that is the `openmm` package with its force-field
files; the OpenCL plugins of the wheel are left out. `fix_structure` runs in
the bundle with the Reference and CPU platforms. `load_smiles` runs in
the bundle with no change to the spec except the two license texts. rdkit
2026.9.2 has wheels for Python 3.13 and 3.14.

### minimize (4.12.3)

`fix_structure`, then `minimize` with 500 steps, CPU platform, 32 threads,
2026-11-14. Amber14 with GBn2 implicit solvent, heavy atoms restrained.

| Protein | Atoms with hydrogens | No cutoff | 2.0 nm cutoff | 1.0 nm cutoff |
| --- | --- | --- | --- | --- |
| 12CA, 260 residues | 4009 | 126 to 272 s | 52 s | 4.3 to 5.9 s |
| AlphaFold P04637, 393 residues | 6220 | 397 s | not run | 7.3 s |

The heavy-atom RMSD to the start is the same with and without the cutoff
(0.14 A for 12CA), so the command uses 1.0 nm. `fix_structure` takes 0.7 s
on both. One force evaluation of 12CA: 1.2 s without a cutoff, 0.05 s with.

### Batch load (4.11.1)

`load_files` on a folder of 502 small PDB files (24 atoms each, 2 of them
unreadable), measured 2026-11-14: 0.30 to 0.57 s without a window, 0.42 s in
the window under WSLg. A plain `cmd.load` loop over the same files takes
0.31 s, so the command adds nothing measurable. Under the one-second limit
of step 12b: the load loop stays on the GUI thread.
