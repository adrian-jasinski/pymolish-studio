# Benchmark: pymolish against PyMOL 3

`testing/compare.py` runs the same workloads in pymolish and in upstream
PyMOL 3, one process per version, without pymolrc, with the same settings
(`max_threads` = CPU count), and prints both side by side. It also compares
results (atom counts, RMSD, selection sizes, object counts) and the
ray-traced images; the exit code is 1 when a result differs.

```sh
pymolish -ckqy testing/compare.py            # headless, about 6 min
pymolish -ckqy testing/compare.py -- gui     # also the GUI, about 15 min
```

- The reference is `$PYMOL_REF`, default
  `~/code/pymol-open-source/.venv/bin/pymol` (the `pymol3` alias).
- **Same Python on both sides.** The reference runs on Python 3.14, so
  measure with a pymolish built for 3.14; on different interpreters the
  rows that are mostly Python (session save, `alter`, `iterate`) differ by
  10 to 25 % for that reason alone:

  ```sh
  uv venv .venv314 --python 3.14
  uv pip install --python .venv314/bin/python --config-settings use-msgpackc=no '.[dev]'
  .venv314/bin/pymolish -ckqy testing/compare.py -- gui
  ```

  The Python versions and, for the GUI, the OpenGL driver of each side are
  printed above the tables.
- Ten structures, 327 to 239306 atoms, are downloaded once from RCSB into
  `~/.cache/pymolish-compare`. Generated inputs (1aon four times as one
  235480-atom mmCIF, 600 small PDB files) and the PNGs go to
  `/tmp/pymol-compare-*`.
- Headless rows force the representation with a 16x16 ray, because
  headless PyMOL builds lazily. A GUI frame is one PyMOL draw plus
  `glFinish`, outside Qt's paint cycle; "first frame" includes building
  the representation.
- On WSL pymolish draws on the GPU and PyMOL 3 on the CPU; that is what
  each does out of the box. Set `GALLIUM_DRIVER=llvmpipe` (or `d3d12`) for
  the run to give both the same driver.
- Times are the best of 3 runs; rows of large structures run once. On this
  laptop untouched rows drift 10 to 30 % between runs, more when it is hot
  or something else runs: read a ratio as a difference only when it holds
  across rows or runs. Do nothing else on the machine during a run.
- Before a performance PR: run it before and after, and put both tables in
  the PR. The ratio column cancels most of the machine noise.

## Run of 2026-11-19

pymolish 4.19.17 and PyMOL 3.2.0a (commit f1fa2ed4), both on Python 3.14.3;
PySide6 against PyQt5. AMD Ryzen 9 8945HX, 32 threads, Ubuntu 24.04 under
WSL2 with WSLg, viewport 800x600. Ratio = pymolish / PyMOL 3, below 1 is
faster.

Every result was the same in both versions, and the eight ray-traced images
of 1oky (480x360) are identical pixel for pixel.

### Headless, seconds

| Workload | pymol3 3.2.0a | pymolish 4.19.17 | ratio | result |
| --- | --- | --- | --- | --- |
| load small 1oky (2475 atoms) | 0.009 s | 0.009 s | 1.05 | same |
| load big 1aon (58870 atoms) | 0.141 s | 0.127 s | 0.90 | same |
| load huge 4x1aon mmCIF (235480 atoms) | 0.693 s | 0.550 s | 0.79 | same |
| load 600 files, one object each | 5.353 s | 5.003 s | 0.93 | same |
| build lines small (+ray 16x16) | 0.101 s | 0.110 s | 1.09 |  |
| build sticks small (+ray 16x16) | 0.089 s | 0.061 s | 0.68 |  |
| build spheres small (+ray 16x16) | 0.019 s | 0.017 s | 0.87 |  |
| build cartoon small (+ray 16x16) | 0.110 s | 0.101 s | 0.92 |  |
| build ribbon small (+ray 16x16) | 0.029 s | 0.030 s | 1.04 |  |
| build surface small (+ray 16x16) | 0.481 s | 0.256 s | 0.53 |  |
| build mesh small (+ray 16x16) | 0.572 s | 0.334 s | 0.59 |  |
| build dots small (+ray 16x16) | 0.106 s | 0.101 s | 0.95 |  |
| build lines big (+ray 16x16) | 0.099 s | 0.089 s | 0.90 |  |
| build sticks big (+ray 16x16) | 0.390 s | 0.214 s | 0.55 |  |
| build spheres big (+ray 16x16) | 0.051 s | 0.043 s | 0.86 |  |
| build cartoon big (+ray 16x16) | 1.455 s | 1.013 s | 0.70 |  |
| build ribbon big (+ray 16x16) | 0.181 s | 0.124 s | 0.69 |  |
| build surface big (+ray 16x16) | 11.513 s | 5.372 s | 0.47 |  |
| build mesh big (+ray 16x16) | 2.591 s | 1.744 s | 0.67 |  |
| build dots big (+ray 16x16) | 3.338 s | 2.944 s | 0.88 |  |
| build lines huge (+ray 16x16) | 0.332 s | 0.266 s | 0.80 |  |
| build cartoon huge (+ray 16x16) | 3.542 s | 2.704 s | 0.76 |  |
| build surface huge (+ray 16x16) | 70.132 s | 27.491 s | 0.39 |  |
| ray 800x600 cartoon big | 4.033 s | 3.210 s | 0.80 |  |
| ray 800x600 surface small | 0.590 s | 0.326 s | 0.55 |  |
| switch 9 objects x3 (cartoon, +ray 64x48) | 4.641 s | 3.703 s | 0.80 |  |
| trajectory load 2cas + 60-frame DCD | 0.002 s | 0.002 s | 0.87 | same |
| trajectory play 60 states (lines, +ray 64x48) | 5.826 s | 5.626 s | 0.97 |  |
| select byres within 5 of chain A (big) | 0.008 s | 0.004 s | 0.49 | same |
| align 1aon chain A onto chain H | 0.034 s | 0.034 s | 0.99 | same |
| dss (big) | 0.012 s | 0.010 s | 0.83 | same |
| h_add (big) | 1.766 s | 1.619 s | 0.92 | same |
| alter b=b*1 + iterate (big) | 0.011 s | 0.015 s | 1.39 |  |
| get_coords x10 (huge) | 0.034 s | 0.033 s | 0.96 |  |
| save mmCIF (big) | 0.066 s | 0.049 s | 0.75 |  |
| save PSE (big, cartoon) | 0.152 s | 0.143 s | 0.94 |  |
| load PSE (big, cartoon) | 0.884 s | 0.119 s | 0.13 | same |
| startup -ckq -d quit | 0.074 s | 0.070 s | 0.95 |  |

### Ten structures, headless, seconds: PyMOL 3 / pymolish (ratio)

"save PSE" and "load PSE" write and read the structure with its cartoon;
"all 10" is one session with all ten objects.

| Structure | load | cartoon | surface | save PSE | load PSE |
| --- | --- | --- | --- | --- | --- |
| 1crn (327 atoms) | 0.001 / 0.001 (0.91) | 0.039 / 0.038 (0.99) | 0.087 / 0.091 (1.05) | 0.001 / 0.001 (1.28) | 0.006 / 0.001 (0.13) |
| 1ubq (660 atoms) | 0.001 / 0.001 (1.04) | 0.042 / 0.038 (0.89) | 0.149 / 0.112 (0.75) | 0.001 / 0.002 (1.52) | 0.010 / 0.001 (0.12) |
| 2rh1 (3862 atoms) | 0.007 / 0.006 (0.90) | 0.093 / 0.094 (1.01) | 0.599 / 0.225 (0.38) | 0.008 / 0.006 (0.82) | 0.062 / 0.005 (0.09) |
| 4hhb (4779 atoms) | 0.009 / 0.008 (0.90) | 0.145 / 0.082 (0.57) | 0.807 / 0.349 (0.43) | 0.008 / 0.009 (1.11) | 0.072 / 0.006 (0.08) |
| 1hzh (10660 atoms) | 0.019 / 0.018 (0.93) | 0.110 / 0.075 (0.68) | 1.514 / 0.599 (0.40) | 0.024 / 0.026 (1.10) | 0.160 / 0.018 (0.11) |
| 1aoi (12416 atoms) | 0.020 / 0.021 (1.04) | 0.133 / 0.086 (0.65) | 1.887 / 0.769 (0.41) | 0.026 / 0.029 (1.14) | 0.203 / 0.019 (0.10) |
| 6vxx (24621 atoms) | 0.042 / 0.040 (0.95) | 0.334 / 0.205 (0.61) | 3.060 / 1.411 (0.46) | 0.065 / 0.076 (1.18) | 0.393 / 0.052 (0.13) |
| 1aon (59192 atoms) | 0.101 / 0.105 (1.04) | 1.329 / 0.996 (0.75) | 10.360 / 4.977 (0.48) | 0.185 / 0.171 (0.92) | 0.992 / 0.145 (0.15) |
| 1jj2 (99077 atoms) | 0.184 / 0.186 (1.01) | 1.075 / 0.781 (0.73) | 19.301 / 9.208 (0.48) | 0.373 / 0.326 (0.87) | 1.795 / 0.261 (0.15) |
| 4v6x (239306 atoms) | 0.510 / 0.445 (0.87) | 2.198 / 1.454 (0.66) | 85.585 / 33.382 (0.39) | 1.312 / 1.136 (0.87) | 5.085 / 0.983 (0.19) |
| all 10 (454900 atoms) | 1.001 / 0.984 (0.98) | 7.890 / 6.274 (0.80) |  | 2.765 / 2.435 (0.88) | 9.084 / 1.258 (0.14) |

### GUI, ms: PyMOL 3 on the CPU (llvmpipe), pymolish on the GPU (D3D12, Radeon 610M)

| Workload | pymol3 3.2.0a | pymolish 4.19.17 | ratio | result |
| --- | --- | --- | --- | --- |
| GUI first frame lines small | 16.353 ms | 43.720 ms | 2.67 |  |
| GUI frame lines small (median) | 3.138 ms | 0.782 ms | 0.25 |  |
| GUI first frame sticks small | 19.559 ms | 20.088 ms | 1.03 |  |
| GUI frame sticks small (median) | 4.264 ms | 1.734 ms | 0.41 |  |
| GUI first frame spheres small | 9.611 ms | 10.412 ms | 1.08 |  |
| GUI frame spheres small (median) | 5.642 ms | 2.133 ms | 0.38 |  |
| GUI first frame cartoon small | 19.432 ms | 15.101 ms | 0.78 |  |
| GUI frame cartoon small (median) | 3.281 ms | 0.586 ms | 0.18 |  |
| GUI first frame ribbon small | 1.642 ms | 3.604 ms | 2.20 |  |
| GUI frame ribbon small (median) | 1.261 ms | 0.485 ms | 0.38 |  |
| GUI first frame surface small | 383.439 ms | 157.745 ms | 0.41 |  |
| GUI frame surface small (median) | 7.185 ms | 1.166 ms | 0.16 |  |
| GUI first frame mesh small | 196.534 ms | 140.244 ms | 0.71 |  |
| GUI frame mesh small (median) | 42.330 ms | 0.810 ms | 0.02 |  |
| GUI first frame dots small | 77.886 ms | 54.112 ms | 0.69 |  |
| GUI frame dots small (median) | 17.065 ms | 1.190 ms | 0.07 |  |
| GUI first frame lines big | 224.035 ms | 82.168 ms | 0.37 |  |
| GUI frame lines big (median) | 61.608 ms | 5.530 ms | 0.09 |  |
| GUI first frame sticks big | 152.014 ms | 146.797 ms | 0.97 |  |
| GUI frame sticks big (median) | 76.716 ms | 20.116 ms | 0.26 |  |
| GUI first frame spheres big | 32.955 ms | 31.866 ms | 0.97 |  |
| GUI frame spheres big (median) | 20.880 ms | 4.028 ms | 0.19 |  |
| GUI first frame cartoon big | 571.321 ms | 467.195 ms | 0.82 |  |
| GUI frame cartoon big (median) | 44.493 ms | 7.684 ms | 0.17 |  |
| GUI first frame surface big | 10389.667 ms | 5305.323 ms | 0.51 |  |
| GUI frame surface big (median) | 122.703 ms | 20.999 ms | 0.17 |  |
| GUI first frame lines huge | 347.183 ms | 357.412 ms | 1.03 |  |
| GUI frame lines huge (median) | 207.153 ms | 20.812 ms | 0.10 |  |
| GUI first frame spheres huge | 96.069 ms | 49.187 ms | 0.51 |  |
| GUI frame spheres huge (median) | 40.043 ms | 3.746 ms | 0.09 |  |
| GUI first frame cartoon huge | 1145.783 ms | 1107.102 ms | 0.97 |  |
| GUI frame cartoon huge (median) | 106.109 ms | 18.934 ms | 0.18 |  |
| GUI switch 9 objects, first pass (sum) | 419.288 ms | 424.704 ms | 1.01 |  |
| GUI switch 9 objects, later passes (median) | 2.168 ms | 2.133 ms | 0.98 |  |
| GUI load 600 files + frame | 7178.222 ms | 8834.670 ms | 1.23 | same |
| GUI frame 600 objects lines (median) | 311.637 ms | 80.806 ms | 0.26 |  |

### Ten structures, GUI, ms: PyMOL 3 / pymolish (ratio)

| Structure | cartoon first frame | surface first frame | surface frame (median) |
| --- | --- | --- | --- |
| 1crn | 6 / 80 (14.27) | 51 / 85 (1.68) | 3 / 1 (0.24) |
| 1ubq | 6 / 26 (4.69) | 98 / 86 (0.87) | 3 / 1 (0.23) |
| 2rh1 | 13 / 25 (1.89) | 469 / 204 (0.44) | 14 / 2 (0.11) |
| 4hhb | 18 / 27 (1.50) | 622 / 248 (0.40) | 12 / 2 (0.13) |
| 1hzh | 23 / 40 (1.70) | 1359 / 627 (0.46) | 25 / 4 (0.15) |
| 1aoi | 35 / 56 (1.61) | 1656 / 698 (0.42) | 32 / 6 (0.17) |
| 6vxx | 76 / 69 (0.91) | 2812 / 1292 (0.46) | 49 / 8 (0.16) |
| 1aon | 416 / 393 (0.95) | 9933 / 4805 (0.48) | 115 / 25 (0.22) |
| 1jj2 | 412 / 379 (0.92) | 17778 / 8211 (0.46) | 170 / 40 (0.24) |
| 4v6x | 809 / 702 (0.87) | 77250 / 30398 (0.39) | 506 / 126 (0.25) |

### The driver alone: pymolish on three renderers

The same pymolish, runs of the same day; the first column is what the app
used on WSL before 4.19.15 and what PyMOL 3 uses there. The RTX column
needs `MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA`.

| Frame while rotating, ms | CPU (llvmpipe) | Radeon 610M (integrated, the default) | RTX 5070 Laptop |
| --- | --- | --- | --- |
| lines, 1aon | 53.7 | 5.7 | 3.4 |
| sticks, 1aon | 51.0 | 20.3 | 12.0 |
| spheres, 1aon | 20.5 | 4.3 | 0.7 |
| cartoon, 1aon | 45.8 | 9.8 | 0.8 |
| surface, 1aon | 114.0 | 23.6 | 12.5 |
| mesh, 1oky | 40.2 | 0.8 | 2.3 |
| lines, 1aon x4 | 206.3 | 22.4 | 13.2 |
| cartoon, 1aon x4 | 108.5 | 18.7 | 1.5 |
| surface, 1jj2 | 172.9 | 35.6 | 25.7 |
| surface, 4v6x | 520.1 | 106.0 | 45.7 |

With `GALLIUM_DRIVER=llvmpipe` for both, pymolish and PyMOL 3 draw at the
same speed (run of the same day with 4.19.9: every frame row within 10 %
or within noise).

## What the numbers say

- **Surface: 2 to 2.6x faster.** About 2x in every structure above 1000
  atoms (1aon 10.4 s to 5.0 s); 2.5x for the largest since 4.19.16 (4v6x
  86 s to 33 s, 1aon four times 70 s to 27 s). Mesh 0.6 to 0.7, cartoon
  build 0.6 to 0.8, sticks of a large structure 0.55.
- **Session load: 5 to 12x faster** for every size (10 structures, 455k
  atoms: 9.1 s to 1.3 s).
- **Frames on WSL: 2.5 to 10x faster** on the integrated GPU, because the
  app now draws there (cartoon of 1aon 44 ms to 8 ms, surface 123 ms to
  21 ms, lines 62 ms to 5.5 ms). The drawing code itself costs the same
  in both programs.
- **What the GPU driver costs.** The first frame of something small takes
  20 to 80 ms instead of 6 to 20 ms. After many new objects appear, the
  driver needs 9 slower frames, in proportion to their number: nothing
  to see below 20 objects; 600 files take 8.8 s instead of 7.2 s until
  the first frame, then draw in 81 ms instead of 312 ms.
- **Many files cost what their atoms cost.** 600 files (823k atoms) take
  about 5 s in both; from the first file to the last a file costs 3 to
  8 us per atom, so nothing grows with the object count.
- **Nothing is slower in the core.** The two rows that looked slower on
  Python 3.13 ("save PSE", `alter` + `iterate`) are equal on the same
  Python: measured alone with 7 repeats, `alter` takes 6.7 ms and
  `iterate` 3.1 ms on 1aon in both. In the table above the 10 ms row
  still jumps between 1.2 and 1.4 from run to run.
- **Large surfaces are no longer triangle for triangle the same.** Up to
  500000 surface dots (6vxx with 24621 atoms and smaller, tested) the
  surface is byte for byte the one of PyMOL 3. Above that the finer
  neighbor grid of 4.19.16 changes the order in which the dot clean-up and
  the triangulation meet their neighbors: 1aon keeps the same area
  (740906 A^2), 3.8 % of its triangles differ, and 0.2 % of the pixels of
  a ray-traced 800x600 image differ by more than 32 of 255.

## Improvement candidates, by what a user feels

1. **A large surface freezes the window.** The first frame of 4v6x's
   surface takes 30 s, of 1aon 5 s, all on the GUI thread. Options (worker
   thread, coarser surface above an atom count, or only a status message)
   are in [plan 1](plans/01-performance-gpu.md), Status 2026-11-19, and
   wait for the user.
2. **Sticks are the slowest representation on the GPU:** 20 ms per frame
   of 1aon on the integrated card, where cartoon takes 8 ms and spheres
   4 ms.
3. **Lines as triangles on every driver.** On llvmpipe 150 objects of
   lines draw in 35 ms as triangles and in 75 ms as GL lines. Since
   4.19.15 the triangle path is used only where the driver cannot draw
   wide lines.
4. **Thin mesh lines on d3d12.** Mesh, dashes and cell outlines are one
   pixel wide there; lines, ribbon and nonbonded keep `line_width`.
5. **`h_add` on a large protein** takes 1.6 to 1.8 s for 59k atoms in both
   versions, `dots` 2.9 s: candidates when a profile shows them in real
   use, not before.
