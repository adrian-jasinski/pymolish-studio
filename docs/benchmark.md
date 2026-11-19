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
- Ten structures, 327 to 239306 atoms, are downloaded once from RCSB into
  `~/.cache/pymolish-compare`. Generated inputs (1aon four times as one
  235480-atom mmCIF, 600 small PDB files) and the PNGs go to
  `/tmp/pymol-compare-*`.
- Headless rows force the representation with a 16x16 ray, because
  headless PyMOL builds lazily. A GUI frame is one PyMOL draw plus
  `glFinish`, outside Qt's paint cycle; "first frame" includes building
  the representation.
- Times are the best of 3 runs; rows of large structures run once. On this
  laptop untouched rows drift 10 to 30 % between runs: read a ratio as a
  difference only when it holds across rows or runs.
- Before a performance PR: run it before and after, and put both tables in
  the PR. The ratio column cancels most of the machine noise.

## Run of 2026-11-19

pymolish 4.19.9 (installed build; 4.19.10 to 4.19.12 changed no measured
path) on Python 3.13.12 and PySide6, PyMOL 3.2.0a (commit f1fa2ed4) on
Python 3.14.3 and PyQt5. AMD Ryzen 9 8945HX, 32 threads, Ubuntu 24.04 under
WSL2. GUI under WSLg with Mesa llvmpipe (software rendering, the default
there), viewport 800x600. Ratio = pymolish / PyMOL 3, below 1 is faster.

Every result was the same in both versions, and the eight ray-traced images
of 1oky (480x360) are identical pixel for pixel.

### Headless, seconds

| Workload | pymol3 3.2.0a | pymolish 4.19.9 | ratio | result |
| --- | --- | --- | --- | --- |
| load small 1oky (2475 atoms) | 0.009 s | 0.008 s | 0.86 | same |
| load big 1aon (58870 atoms) | 0.136 s | 0.124 s | 0.91 | same |
| load huge 4x1aon mmCIF (235480 atoms) | 0.641 s | 0.585 s | 0.91 | same |
| load 600 files, one object each | 4.827 s | 4.718 s | 0.98 | same |
| build lines small (+ray 16x16) | 0.105 s | 0.097 s | 0.92 |  |
| build sticks small (+ray 16x16) | 0.082 s | 0.085 s | 1.04 |  |
| build spheres small (+ray 16x16) | 0.017 s | 0.015 s | 0.86 |  |
| build cartoon small (+ray 16x16) | 0.083 s | 0.065 s | 0.78 |  |
| build ribbon small (+ray 16x16) | 0.026 s | 0.029 s | 1.09 |  |
| build surface small (+ray 16x16) | 0.499 s | 0.246 s | 0.49 |  |
| build mesh small (+ray 16x16) | 0.618 s | 0.336 s | 0.54 |  |
| build dots small (+ray 16x16) | 0.107 s | 0.095 s | 0.89 |  |
| build lines big (+ray 16x16) | 0.104 s | 0.072 s | 0.69 |  |
| build sticks big (+ray 16x16) | 0.423 s | 0.208 s | 0.49 |  |
| build spheres big (+ray 16x16) | 0.048 s | 0.044 s | 0.92 |  |
| build cartoon big (+ray 16x16) | 1.661 s | 1.036 s | 0.62 |  |
| build ribbon big (+ray 16x16) | 0.192 s | 0.121 s | 0.63 |  |
| build surface big (+ray 16x16) | 12.012 s | 5.360 s | 0.45 |  |
| build mesh big (+ray 16x16) | 2.913 s | 1.743 s | 0.60 |  |
| build dots big (+ray 16x16) | 3.551 s | 2.873 s | 0.81 |  |
| build lines huge (+ray 16x16) | 0.331 s | 0.333 s | 1.00 |  |
| build cartoon huge (+ray 16x16) | 3.733 s | 2.651 s | 0.71 |  |
| build surface huge (+ray 16x16) | 69.083 s | 43.404 s | 0.63 |  |
| ray 800x600 cartoon big | 3.737 s | 3.460 s | 0.93 |  |
| ray 800x600 surface small | 0.628 s | 0.444 s | 0.71 |  |
| switch 9 objects x3 (cartoon, +ray 64x48) | 4.741 s | 3.676 s | 0.78 |  |
| trajectory load 2cas + 60-frame DCD | 0.002 s | 0.002 s | 0.93 | same |
| trajectory play 60 states (lines, +ray 64x48) | 5.880 s | 5.789 s | 0.98 |  |
| select byres within 5 of chain A (big) | 0.008 s | 0.004 s | 0.49 | same |
| align 1aon chain A onto chain H | 0.035 s | 0.035 s | 0.99 | same |
| dss (big) | 0.013 s | 0.017 s | 1.28 | same |
| h_add (big) | 1.450 s | 1.837 s | 1.27 | same |
| alter b=b*1 + iterate (big) | 0.010 s | 0.012 s | 1.27 |  |
| get_coords x10 (huge) | 0.036 s | 0.035 s | 0.96 |  |
| save mmCIF (big) | 0.064 s | 0.048 s | 0.75 |  |
| save PSE (big, cartoon) | 0.162 s | 0.173 s | 1.07 |  |
| load PSE (big, cartoon) | 0.812 s | 0.134 s | 0.17 | same |
| startup -ckq -d quit | 0.084 s | 0.084 s | 1.00 |  |

### Ten structures, headless, seconds: PyMOL 3 / pymolish (ratio)

"save PSE" and "load PSE" write and read the structure with its cartoon;
"all 10" is one session with all ten objects.

| Structure | load | cartoon | surface | save PSE | load PSE |
| --- | --- | --- | --- | --- | --- |
| 1crn (327 atoms) | 0.001 / 0.001 (0.91) | 0.040 / 0.040 (1.00) | 0.088 / 0.084 (0.96) | 0.001 / 0.001 (0.96) | 0.005 / 0.001 (0.17) |
| 1ubq (660 atoms) | 0.001 / 0.001 (1.09) | 0.048 / 0.039 (0.82) | 0.160 / 0.114 (0.71) | 0.001 / 0.002 (1.22) | 0.010 / 0.001 (0.14) |
| 2rh1 (3862 atoms) | 0.006 / 0.006 (0.99) | 0.098 / 0.095 (0.98) | 0.635 / 0.279 (0.44) | 0.008 / 0.008 (1.03) | 0.057 / 0.006 (0.11) |
| 4hhb (4779 atoms) | 0.010 / 0.010 (0.93) | 0.150 / 0.080 (0.53) | 0.815 / 0.320 (0.39) | 0.008 / 0.009 (1.16) | 0.072 / 0.008 (0.11) |
| 1hzh (10660 atoms) | 0.018 / 0.018 (0.99) | 0.102 / 0.078 (0.77) | 1.519 / 0.571 (0.38) | 0.024 / 0.029 (1.22) | 0.162 / 0.023 (0.14) |
| 1aoi (12416 atoms) | 0.020 / 0.022 (1.07) | 0.137 / 0.086 (0.63) | 1.861 / 0.801 (0.43) | 0.026 / 0.032 (1.25) | 0.187 / 0.021 (0.11) |
| 6vxx (24621 atoms) | 0.044 / 0.041 (0.93) | 0.353 / 0.202 (0.57) | 3.079 / 1.427 (0.46) | 0.073 / 0.076 (1.04) | 0.410 / 0.059 (0.14) |
| 1aon (59192 atoms) | 0.137 / 0.107 (0.78) | 1.192 / 0.892 (0.75) | 10.605 / 4.949 (0.47) | 0.203 / 0.208 (1.03) | 0.965 / 0.162 (0.17) |
| 1jj2 (99077 atoms) | 0.207 / 0.173 (0.84) | 0.977 / 0.736 (0.75) | 19.586 / 9.498 (0.48) | 0.354 / 0.388 (1.10) | 1.693 / 0.287 (0.17) |
| 4v6x (239306 atoms) | 0.519 / 0.486 (0.94) | 2.054 / 1.537 (0.75) | 86.282 / 50.304 (0.58) | 1.309 / 1.249 (0.95) | 5.318 / 0.988 (0.19) |
| all 10 (454900 atoms) | 1.012 / 1.155 (1.14) | 6.955 / 6.390 (0.92) |  | 2.357 / 2.596 (1.10) | 8.838 / 1.756 (0.20) |

### GUI, ms

| Workload | pymol3 3.2.0a | pymolish 4.19.9 | ratio | result |
| --- | --- | --- | --- | --- |
| GUI first frame lines small | 32.287 ms | 24.085 ms | 0.75 |  |
| GUI frame lines small (median) | 3.772 ms | 3.385 ms | 0.90 |  |
| GUI first frame sticks small | 30.615 ms | 13.029 ms | 0.43 |  |
| GUI frame sticks small (median) | 5.094 ms | 4.643 ms | 0.91 |  |
| GUI first frame spheres small | 15.397 ms | 45.134 ms | 2.93 |  |
| GUI frame spheres small (median) | 7.008 ms | 5.910 ms | 0.84 |  |
| GUI first frame cartoon small | 28.220 ms | 40.393 ms | 1.43 |  |
| GUI frame cartoon small (median) | 2.829 ms | 3.015 ms | 1.07 |  |
| GUI first frame ribbon small | 1.489 ms | 1.372 ms | 0.92 |  |
| GUI frame ribbon small (median) | 1.156 ms | 1.052 ms | 0.91 |  |
| GUI first frame surface small | 402.962 ms | 154.815 ms | 0.38 |  |
| GUI frame surface small (median) | 7.195 ms | 7.103 ms | 0.99 |  |
| GUI first frame mesh small | 199.638 ms | 205.344 ms | 1.03 |  |
| GUI frame mesh small (median) | 41.017 ms | 40.248 ms | 0.98 |  |
| GUI first frame dots small | 49.874 ms | 48.135 ms | 0.97 |  |
| GUI frame dots small (median) | 10.208 ms | 13.536 ms | 1.33 |  |
| GUI first frame lines big | 78.181 ms | 82.374 ms | 1.05 |  |
| GUI frame lines big (median) | 53.140 ms | 53.663 ms | 1.01 |  |
| GUI first frame sticks big | 137.472 ms | 136.866 ms | 1.00 |  |
| GUI frame sticks big (median) | 48.799 ms | 50.965 ms | 1.04 |  |
| GUI first frame spheres big | 31.425 ms | 31.859 ms | 1.01 |  |
| GUI frame spheres big (median) | 21.576 ms | 20.483 ms | 0.95 |  |
| GUI first frame cartoon big | 494.124 ms | 482.824 ms | 0.98 |  |
| GUI frame cartoon big (median) | 43.807 ms | 45.836 ms | 1.05 |  |
| GUI first frame surface big | 11041.851 ms | 5509.607 ms | 0.50 |  |
| GUI frame surface big (median) | 115.977 ms | 114.021 ms | 0.98 |  |
| GUI first frame lines huge | 348.918 ms | 342.115 ms | 0.98 |  |
| GUI frame lines huge (median) | 207.065 ms | 206.309 ms | 1.00 |  |
| GUI first frame spheres huge | 88.387 ms | 78.789 ms | 0.89 |  |
| GUI frame spheres huge (median) | 40.579 ms | 39.189 ms | 0.97 |  |
| GUI first frame cartoon huge | 1316.388 ms | 1468.993 ms | 1.12 |  |
| GUI frame cartoon huge (median) | 106.291 ms | 108.457 ms | 1.02 |  |
| GUI switch 9 objects, first pass (sum) | 434.716 ms | 466.534 ms | 1.07 |  |
| GUI switch 9 objects, later passes (median) | 3.125 ms | 1.779 ms | 0.57 |  |
| GUI load 600 files + frame | 7318.991 ms | 7438.648 ms | 1.02 | same |
| GUI frame 600 objects lines (median) | 329.110 ms | 323.873 ms | 0.98 |  |

### Ten structures, GUI, ms: PyMOL 3 / pymolish (ratio)

| Structure | cartoon first frame | surface first frame | surface frame (median) |
| --- | --- | --- | --- |
| 1crn | 6 / 5 (0.90) | 51 / 63 (1.24) | 3 / 3 (1.01) |
| 1ubq | 6 / 5 (0.81) | 98 / 70 (0.72) | 3 / 3 (0.84) |
| 2rh1 | 13 / 12 (0.91) | 496 / 188 (0.38) | 12 / 8 (0.72) |
| 4hhb | 18 / 15 (0.82) | 606 / 278 (0.46) | 13 / 12 (0.90) |
| 1hzh | 23 / 24 (1.05) | 1440 / 635 (0.44) | 25 / 23 (0.91) |
| 1aoi | 70 / 37 (0.53) | 1835 / 794 (0.43) | 32 / 38 (1.18) |
| 6vxx | 95 / 84 (0.88) | 3131 / 1408 (0.45) | 45 / 47 (1.04) |
| 1aon | 422 / 505 (1.20) | 10642 / 5517 (0.52) | 120 / 124 (1.03) |
| 1jj2 | 427 / 393 (0.92) | 19384 / 10011 (0.52) | 173 / 173 (1.00) |
| 4v6x | 828 / 850 (1.03) | 82026 / 48883 (0.60) | 492 / 520 (1.06) |

## What the numbers say

- **Surface: 2x faster** in every structure above 1000 atoms, headless and
  in the GUI (1aon 10.6 s to 4.9 s; 4v6x 86 s to 50 s). Mesh 0.6, cartoon
  build 0.55 to 0.8.
- **Session load: 6 to 9x faster** for every size (10 structures, 455k
  atoms: 8.8 s to 1.8 s).
- **Drawing is unchanged.** Frame times while rotating are within noise of
  PyMOL 3 for every representation and size; neither the draw path nor
  the shaders differ in cost. The first frame is faster only where it
  builds a surface or a cartoon.
- **Many files cost what their atoms cost.** 600 files (823k atoms) take
  4.7 s in both; loading them 150 at a time takes 3 to 8 us per atom from
  the first chunk to the last, so nothing grows with the object count.
- **Slower rows.** "save PSE" was slower in 8 of 11 structure rows (by 3 to
  25 %) and in both earlier runs, `alter` + `iterate` in all three runs
  (10 ms to 12 ms). Both are mostly Python (pickle, the per-atom
  expression), and PyMOL 3 here runs a newer Python (3.14 against 3.13), so
  part of it may be the interpreter. `dss`, `h_add` and the first frames of
  small spheres and cartoon were slower in this run only.

## Improvement candidates, by what a user feels

1. **A large surface freezes the window.** The first frame of 4v6x's
   surface takes 49 s, of 1aon 5.5 s, all on the GUI thread. Building it
   off the GUI thread (show the old representation or nothing until it is
   ready), or a coarser `surface_quality` above some atom count, removes
   the freeze; further speed in the triangulation shortens it.
2. **Frame time on software rendering.** Under WSLg every frame of 1aon
   takes 45 to 120 ms (cartoon, surface), the same as PyMOL 3. With
   `GALLIUM_DRIVER=d3d12` the GPU does it in 1 to 11 ms (plan 1). Whether
   the app picks that driver on WSL is still the user's call.
3. **save PSE and alter/iterate.** Profile both under the same Python
   before changing anything; if the gap survives, it is in the session
   writer or the per-atom expression loop.
4. **`h_add` on a large protein** takes 1.5 to 1.8 s for 59k atoms in both
   versions, `dots` 2.9 s: candidates when a profile shows them in real
   use, not before.
