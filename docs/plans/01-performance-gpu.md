# 1 — Performance and GPU

[Roadmap](../../PLAN.md) · 1a done, 1b in progress; timings are in the Status sections and the ChangeLog; comparison with upstream PyMOL 3 in [docs/benchmark.md](../benchmark.md)

**Improve the operation a profile identifies.** Interactive graphics already use
OpenGL. Loading, geometry generation, ray tracing, callbacks and GPU submission
are different workloads and need separate measurements.

## Status 2026-11-08

1a done: headless baseline (then `testing/bench.py`, replaced in 4.19.13 by `testing/compare.py`). GUI frame latency not measured. 1b first change in 4.5.10: session load 0.92 s to 0.14 s (C unpickler with exact fallback), numbers in the ChangeLog. Second change in 4.5.12: the surface build, which is 9.5 of the 15 s of "ray a surface", runs its dot-to-point loop in parallel (11.97 s to 9.66 s, identical geometry). The 1 sigma isosurface cost was traced to the ray tracer's voxel table, not the mesh, and left alone. Next candidates: triangulation (3.5 s) and refinement (1.9 s) of the surface build, `SolventDotNew` (1.5 s), GUI frame latency (never measured).

## Status 2026-11-14

Three more 1b changes, numbers in the ChangeLog: the surface build of 1aon went from 9.44 s to 6.24 s with the same triangles (4.7.7 start-point search of the triangulation, 4.7.8 parallel solvent dots, 4.7.9 neighbor table sized first and filled in parallel). Ray tracing that surface at 800x600: 13.1 s to 9.0 s.

GUI frame time is now measured: `testing/compare.py -- gui`. Main finding: under WSLg the GUI runs on Mesa's software renderer (50 to 120 ms per frame for 1aon); with `GALLIUM_DRIVER=d3d12` the same frames take 0.7 to 11 ms on the RTX 5070. Open decision: whether the app selects that driver itself on WSL. It draws lines 1 pixel wide, so the default would need `trilines` with it, and mesh lines stay thin.

Found while measuring, fixed in 4.7.10: atom labels were solid blocks in the GUI on every driver without `EXT_geometry_shader4` (all Mesa drivers). An upstream refactor of `RepLabel` had dropped the switch that turns shaders off for the fallback label path. Check: `testing/tests/api/label_render.py` (needs the GUI).

Next candidates: sticks on the GPU (11 ms per frame, p99 36 ms, 6 ms of it CPU), surface draw submission (7.6 ms CPU per frame), the two advancing-front passes of the triangulation (0.85 s and 0.82 s), the ray tracer's voxel table (1.0 s per ray of the 1aon surface; the 4.7.9 count-then-fill pattern may carry over to `MapSetupExpressXYVert`).

## Status 2026-11-16

1b change in 4.13.3, numbers in the ChangeLog: the ray tracer's voxel table for the camera view (`MapSetupExpressPerp`) is counted first and filled in parallel, 0.68 s to 0.28 s for the 1aon surface; a ray of that surface 4.7 s to 4.2 s. Tracing is now 3.2 s of those 4.2 s (9x on 32 threads).

Next candidates: sticks on the GPU and surface draw submission (GUI, wait for a quiet machine and the driver decision), the two advancing-front passes of the triangulation (0.85 s and 0.82 s), thread scaling of the trace loop (9x on 16 cores / 32 threads), the zero-fill of the voxel list (0.17 s).

## Status 2026-11-19

Measurements now run against upstream PyMOL 3.2 with `testing/compare.py`, both programs on Python 3.14 (`.venv314`); method, tables and reading in [docs/benchmark.md](../benchmark.md). Three things came out of it.

Decision taken (the user, 2026-11-19): on WSL the app selects the GPU itself. Done in 4.19.15: `theme.prefer_gpu_on_wsl` sets `GALLIUM_DRIVER=d3d12` when `/dev/dxg` and `d3d12_dri.so` exist; the user's own `GALLIUM_DRIVER` or `LIBGL_ALWAYS_SOFTWARE` wins. Frames of 1aon on the integrated Radeon 610M: lines 54 ms to 5.7 ms, cartoon 46 ms to 9.8 ms, surface 114 ms to 24 ms, sticks 51 ms to 20 ms; the RTX 5070 (`MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA`) is 2 to 12 times faster again. That driver draws lines one pixel wide, so `CShaderMgr::Trilines` switches lines, ribbon, nonbonded and alignment objects to the triangle path when the driver's maximum line width is 1; mesh lines, dashes and cell outlines stay one pixel wide. Two costs of the driver, measured: the first frame of a small object takes 20 to 60 ms instead of 6 to 20 ms, and after new objects appear the driver needs 9 slower frames in proportion to their number (not visible below 20 objects; 150 objects: 9 frames of 100 to 300 ms; 600 files of lines: 14 s instead of 7 s to the first frame, then 75 ms per frame instead of 324 ms).

1b change in 4.19.16: the neighbor grid (`MapType`) was capped at `hash_max`^3 = one million cells, too few for the 3 to 10 million surface dots of a ribosome. It may now have two cells per point. Surface build of 4v6x 48.6 s to 31.0 s, of 1aon four times 34.4 s to 23.2 s, same peak memory. The price: above 500000 surface dots the order-dependent dot clean-up and triangulation give a different, equivalent surface (1aon: 3.8 % of the triangles, same area, 0.2 % of the pixels of a ray-traced image). Reverting is one line in `MapGetSeparation`.

Not problems after all: "save PSE" and `alter` + `iterate` were 10 to 25 % slower than PyMOL 3 only because PyMOL 3 ran on Python 3.14 and pymolish on 3.13; on the same Python they are equal. Loading 600 files costs what their atoms cost (3 to 8 us per atom from the first file to the last).

Open, waits for the user ([PLAN.md](../../PLAN.md), "Waiting for the user"): a large surface still freezes the window while it builds (4v6x 30 s, 1aon 5 s). Options:

| | Option | What the user sees | Cost |
| --- | --- | --- | --- |
| A | Build the surface on a worker thread (recommended) | The window stays usable; the surface appears when it is ready, the status line says it is being built. | `SurfaceJob` already separates its input (coordinates, atom records) from its result, so the job can leave the GUI thread; invalidation while a job runs and the headless path (which must still wait) need care. The largest of the three. |
| B | Coarser surface above an atom count (`surface_quality` -1 above 100000 atoms) | Large structures get a rougher surface, sooner. Gain not measured yet. | A few lines; changes the look of large surfaces and of images made from them. |
| C | Only say so: "building surface" in the status line before the build starts | The window still freezes, but explains itself. | A few lines. |

Next candidates: sticks on the GPU (20 ms per frame of 1aon on the integrated GPU, the slowest representation there), lines as triangles on every driver (on llvmpipe 150 objects of lines draw in 35 ms as triangles and 75 ms as GL lines), the two advancing-front passes of the triangulation, `h_add` (1.6 s for 59k atoms, same as PyMOL 3).

## Status 2026-11-25: the grid surface experiment (4.76.0)

Built as the answer to "Grid surface: yes, as an experiment" below:
`set surface_type, 7`, `SurfaceJobRunGrid` in `layer2/RepSurface.cpp`.
Two distance grids and two runs of the marching cubes that were already
in the code; every step is a loop over grid planes, one plane a thread.

**Decision 2026-11-25, question 105: A, recommended.** Keep it as an
optional surface beside today's default. Reconsider the default after
the surface worker (order 4).

**Built 2026-11-25 in 4.81.0 (25b-3):** the row "Solid (grid)" in
Setting > Surface, and in `SurfaceJobRunGrid` the settings the experiment
ignored. `cavity_cull`: closed holes of the second field of up to 2.5 A3
per count are filled before the last marching cubes (25 A3 at the default;
2rh1 keeps 5 closed cavities where the dots keep 7, 4hhb 9 where they
keep 8). `surface_cavity_mode`: a coarse grid (cells of 2 A at the default
radius) gives the places where the large probe fits; only the places of
the small probe's center farther than the cutoff from them make the
surface, and of it what lies at the atoms (71 % and 74 % of the area the
dots draw for 2rh1 and 4hhb, the grid's points 0.44 and 0.42 A from the
dots' on average). `surface_solvent`: the first field is the surface.
Carving worked already. 1aon, fastest of two builds: 1.67 s with culling
and 914,220 triangles (1.70 s and 924,276 without), mode 2 in 0.80 s (the
dots 5.95 s), the solvent surface 1.31 s, a probe of 3 A 1.42 s; the dots
5.46 s. Left out: trimming, longer strips, a grid in blocks, frame times,
a compile on Windows and macOS.

Measured on this laptop (32 threads), mmCIF from
`~/.cache/pymolish-compare`, one process per row; "build" is `show_as
surface` until `ray 16, 16` returns, the fastest of three builds (of two
for 4v6x); memory is the peak resident size of the process, which also
ray traced one picture of 800 x 600.

| Structure | Surface | Probe | Build | Of it the surface job | Triangles | Peak memory |
| --- | --- | --- | --- | --- | --- | --- |
| 1aon, 59,192 atoms | today (type 0) | 1.4 | 5.18 s | not timed | 905,146 | 2,648 MB |
| | grid, cells 1 A | 1.4 | 1.67 s | 0.30 s | 924,276 | 2,570 MB |
| | grid, cells 0.5 A (`surface_quality 1`) | 1.4 | 9.67 s | 1.73 s | 3,992,212 | 10,263 MB |
| | today | 3.0 | 1.16 s | not timed | 195,556 | 929 MB |
| | grid, cells 1 A | 3.0 | 1.38 s | 0.29 s | 668,588 | 1,990 MB |
| 4v6x, 239,306 atoms | today | 1.4 | 34.31 s | not timed | 3,886,165 | 9,983 MB |
| | grid, cells 1 A | 1.4 | 9.41 s | 1.56 s | 3,919,688 | 10,173 MB |
| | today | 3.0 | 5.12 s | not timed | 730,230 | 2,104 MB |
| | grid, cells 1 A | 3.0 | 6.29 s | 1.40 s | 2,500,536 | 6,578 MB |

What the numbers say:

- The grid work is small (0.3 s for 1aon, 1.6 s for 4v6x). What is left
  of a build is paid after the surface job by every kind of surface: the
  atom of each vertex, the colors, the triangles for drawing and for the
  ray tracer. For the grid surface of 4v6x that is 7.9 of 9.4 s. It is the
  next thing to look at, for both surfaces, and it has not been profiled.
- That part and the memory follow the count of triangles, not the method.
  Cells of one point separation gave 4.4 times the triangles of today's
  surface and were slower and four times as heavy; cells of two give the
  same count. Today's dots end up about two separations apart.
- With a larger probe today's surface has fewer dots on a larger sphere
  and gets coarse; it is then faster than the grid, which keeps its
  density. For the rounded surface of 25b that density is the point.
- Ray tracing: the same count of primitives and the same voxel grid for
  both surfaces of 1aon; one cool pair of runs gave 4.05 and 4.08 s.
  Other runs drifted between 4.6 and 15.6 s for both, as on 2026-11-20,
  so the table has no ray times.

How it looks: [1aon](../img/grid-surface-1aon.jpg),
[4v6x](../img/grid-surface-4v6x.jpg). On a whole complex the surfaces
look alike. Close up (ubiquitin), with cells of 1 A the borders between
two colors are more jagged than on today's surface, whose vertices are
spread evenly, and narrow grooves are a little shallower; with cells of
0.5 A the two cannot be told apart. In the real window the first build
was drawn dark: marching cubes turns its triangles the other way round.
Corrected, and the test checks it.

Left out, each named in the code: carving, cavity culling and cavity
mode, `surface_solvent`, trimming; strips of more than one triangle; a
grid in blocks (above 67 million cells the cells grow instead); a
smoothness setting of its own (`solvent_radius` is that value); frame
times in the viewport. Carving, cavity culling and cavity mode are now
accepted work under answer 105 A; the other omissions remain deferred.

## Status 2026-11-19, later: a profile of the surface build

No profiler is installed, so the main thread was sampled every 2 ms of wall
time by a small preloaded library (a `SIGALRM` handler that keeps
`backtrace()`), and the addresses were resolved with `nm`. 1aon as mmCIF
(59,192 atoms), `show_as surface` and `ray 16, 16`, 6.3 s under the sampler:

| Where | Seconds | Share |
| --- | --- | --- |
| Triangulation: `FollowActives` 1.44, `TriangleFill` 0.36, `TrianglePointsToSurface` 0.12, `TriangleActivateEdges` 0.08, `TriangleAdd` 0.07 | 2.1 | 33 % |
| `SurfaceJobRun` itself (the dot loops inlined into it) | 0.73 | 12 % |
| Memory fills in libc called from `MapSetupExpress` 0.34 and `MapSetupExpressPerp` 0.26 | 0.60 | 10 % |
| `SurfaceJobEliminateCloseDots` | 0.33 | 6 % |
| Ray of 16x16 (`triangle3fv`, `BasisMakeMap`, transforms) | about 0.6 | 10 % |
| `RepSurface::recolor` | 0.15 | 3 % |

By CPU time instead of wall time, 40 % of 11 s is libgomp: the 32 threads
spin while they wait between the parallel loops. It costs no wall time
here; it is why the fans start.

1b change in 4.19.40, from the third row: the neighbor list `EList` was a
`std::vector<int>` built with its size, which zero-fills it on one thread,
and was then written completely by the parallel loop. It now has an
allocator that leaves the ints uninitialized (`MapNoInitAllocator`, 20 lines
in `Map.h`). Fastest of three builds per run:

| | Before | After |
| --- | --- | --- |
| 1aon, surface build + ray 16x16 | 5.53 s (4.19.39), 5.35, 5.46 and 5.60 s (4.19.17 on Python 3.14) | 5.16, 5.05, 5.09, 5.32 s |
| 1aon surface, ray 800x600 | 3.88, 3.84, 3.64, 4.00 s | 3.83, 3.54, 3.43, 4.07 s: inside the noise |
| 4v6x, surface build + ray 16x16 | 35.6, 38.5 s | 35.7, 35.9 s: no measurable change |
| Geometry of the 1aon surface (`get_povray`, 494 MB) | sha256 a988657cd9ae3448 | the same |

The gain is about 0.3 s (5 to 7 %), less than the 0.6 s of the profile row:
the pages are still touched for the first time, now by the loop that fills
them. The last pair of each row was measured on a warm laptop.

Check left behind: in a build without `NDEBUG` the list is filled with a
marker first and an `assert` finds any element the loop did not write. Run
in a sanitizer build of the working tree (address and undefined behavior,
asserts on): the suite (909 passed, no report) and a surface of 1aon with a
200x150 ray, which goes through both functions with millions of entries.

Next candidates, from the table: the triangulation is now a third of the
build and still one thread; `FollowActives` has the three passes inlined, so
the next step there is a profile per pass (a build with `-g`, or timers).
`SurfaceJobEliminateCloseDots` (0.33 s). The spinning of idle OpenMP threads
(`OMP_WAIT_POLICY=passive` is the knob; its effect on wall time is not
measured).

## Status 2026-11-20: what others do (web search)

Asked for: solutions that speed up something in 1b, or that keep the window
usable while something is built. Each row was held against this code; only
row 4 was measured here.

| # | Found | What it means here | Verdict |
| --- | --- | --- | --- |
| 1 | Qt's own guidance and the forum practice: compute on a worker thread, hand over plain data with a signal, upload to the GPU on the GUI thread. Rendering from a worker into a `QOpenGLWidget` is the route people report bugs with. [Qt threading basics](https://doc.qt.io/qt-6.8/thread-basics.html), [QOpenGLWidget and threads](https://forum.qt.io/post/565597) | It is option A of the table above, and `SurfaceJob` already has its input and its result apart. Nothing new to choose. | **Supports option A** (question 1). |
| 2 | The setting `async_builds` of PyMOL, which the mailing list recommends for large sessions. | It is in this code (off by default): objects and states are built on several threads, but the GUI thread waits until all are done. It shortens a freeze with many objects; it does not remove one, and one large surface gains nothing. | **Not the answer** to the freeze. |
| 3 | ChimeraX left the analytic surface (MSMS) for a grid: signed distance to the atoms enlarged by the probe, marching cubes, probes on those vertices, a second distance grid, marching cubes again. Works at any size, about 3 times the triangles at 0.5 A, 30 s for a 100,000 atom ribosome in the unoptimized version of 2013. EDTSurf is the same family. [Goddard, surface algorithms](https://www.cgl.ucsf.edu/chimera/data/surface-oct2013/surface.html), [EDTSurf](https://pmc.ncbi.nlm.nih.gov/articles/PMC2779860) | The triangulation here is an advancing front: one thread, a third of the build (profile above). Every step of the grid method is a loop over grid cells, and a parallel marching cubes is already in `layer0/marching_cubes.cpp`. The price: a different, smoother surface with more triangles, so more to draw and to ray trace. EDTSurf's code has no stated license: read the paper, do not copy the code. | **The largest candidate, and an experiment first**: build it as a second `surface_type`, time 1aon and 4v6x, compare pictures. The look changes, so it is the user's choice (question 19). |
| 4 | libgomp lets idle threads spin before they sleep (`GOMP_SPINCOUNT` 300,000 when nothing is set); `OMP_WAIT_POLICY=passive` makes them sleep at once. [libgomp manual](https://gcc.gnu.org/onlinedocs/libgomp/GOMP_005fSPINCOUNT.html) | Measured here, 1aon, three surface builds and a ray of 800x600: wall time the same (builds 5.66 to 5.90 s against 5.52 to 6.01 s), CPU time 223 and 228 s against 191 and 188 s, 16 % less. `GOMP_SPINCOUNT=10000`: 185 s. | **Cheap and measured**: set the policy at start unless the user set one (question 18). Saves heat and battery, not time. |
| 5 | GPU surfaces: QuickSES and its base (Hermosilla 2017) in CUDA, contour build-up on the GPU. [QuickSES](https://diglib.eg.org/items/bf030581-4b55-4781-8c73-712e8cc0d589/full), [Krone 2010](https://cg.ivd.kit.edu/downloads/bcb10_147.pdf) | CUDA is excluded by `AGENTS.md` §2.3; a GLSL compute version needs OpenGL 4.3, which macOS does not have (GPU compute gate below). | **Skip.** |
| 6 | Gaussian density surfaces: QuickSurf of VMD, interactive for millions of atoms on a GPU. [VMD QuickSurf](https://tcbg.illinois.edu/Research/vmd/current/ug/node73.html) | Not a solvent excluded surface: no sharp grooves, a blob. This program can already do it by hand (`map_new` with a Gaussian, then `isosurface`). | **Skip** as a default; a preset could offer it for very large structures. |
| 7 | Sticks: one quad per cylinder and a ray cast per pixel (impostors) is the standard; VTK reported 20 times fewer triangles. [VTK rendering engine](https://www.kitware.com/rendering-engine-improvements-in-vtk/), [HyperBalls](https://hal.archives-ouvertes.fr/hal-00645162) | Already the case: `stick_as_cylinders` and `render_as_cylinders` are on. What is left is cost per pixel, so the next measurement is frame time against window size and zoom, not a new technique. | **Nothing to adopt.** |

## Decisions 2026-11-20

Since the second request of that day the grid surface has a second use:
with a smoothness value it is the rounded "blob" surface of
[step 25](25-studio-effects.md) (25b). The experiment should record pictures
at two smoothness values next to its times.

| Question | Answer | What follows |
| --- | --- | --- |
| A large surface freezes the window | **A, build it on a worker thread.** | The next large item of 1b. `SurfaceJob` leaves the GUI thread; the status line says "building surface"; the surface appears when it is ready. To settle while building: what happens when the atoms change during a job (drop the result and start again), and the headless path, which must still wait. Checks: 1aon and 4v6x in the real window, the suite, the sanitizer job. |
| Idle OpenMP threads (row 4 above) | **Yes.** | `OMP_WAIT_POLICY=passive` at start, before the core loads, unless the user set the variable or `GOMP_SPINCOUNT`. One line next to the place that picks the GPU on WSL. Numbers again after the change. **Done 2026-11-20 in 4.23.1**, in `pymol/__init__.py` just before the core is imported (the GUI start is too late, and a headless run gains too). 1aon, three surface builds, three interleaved runs each: CPU 99, 101 and 93 s with the old spinning (`GOMP_SPINCOUNT=300000`, what libgomp does when nothing is set), 65, 66 and 68 s with the policy; wall time per build 5.1 to 6.1 s in both. The ray tracer has no OpenMP loop and is not touched; its times drifted from 4 to 16 s in both settings as the laptop heated up during the runs, so they are not reported. Not the same thing: `OMP_WAIT_POLICY=active` spins without end and made the builds 3 to 5 times slower here. |
| Grid surface (row 3 above) | **Yes, as an experiment; kept as an option by answer 105 A on 2026-11-25.** | Built in 4.76.0 as `surface_type 7`, with measurements and pictures above. Today's default stays; the menu row and the cavity and solvent settings shipped in 4.81.0, clay and two more looks on it in 4.82.0. Reconsider the default after the worker, order 4. Written from the description of the method, not from EDTSurf's code. |

Order: the one-line change first, the worker thread next, the experiment
last. With a worker thread the build time matters less; the experiment
then answers how much shorter the wait can get.

## Evidence and corrections

- Reuse [performance tests](../../testing/tests/performance), especially
  `pdbloading.py`, `shaders.py`, `iterate.py` and `async_builds.py`. Loading and
  shader stress checks have `no_run_all`; the shader test also requires a GUI.
- [setup.py](../../setup.py) defaults OpenMP on outside macOS.
  [Marching cubes](../../layer0/marching_cubes.cpp) already has parallel loops;
  [Ray.cpp](../../layer1/Ray.cpp) has `max_threads` and dedicated workers.
- PDB/mmCIF have native readers in
  [ObjectMolecule.cpp](../../layer2/ObjectMolecule.cpp),
  [ObjectMolecule2.cpp](../../layer2/ObjectMolecule2.cpp), and
  [CifMoleculeReader.cpp](../../layer2/CifMoleculeReader.cpp). Python's
  [importing.py](../../modules/pymol/importing.py) is not proof of Python parsing.
- Rendering spans [CGO](../../layer1/CGO.cpp), [Scene](../../layer1/Scene.cpp),
  and [shaders](../../data/shaders). GPU rendering can still be CPU-bound.
- Inspect existing [Qt worker utilities](../../modules/pymol/Qt/utils.py) and
  movie-export change `f4766ab1`. They do not establish that all `cmd` operations
  are safe on arbitrary threads.

## 1a — Baseline before cleanup or optimization

Use local fixtures and deterministic settings. Start with existing small/medium
structures; add a reproducibly generated large case only when needed. Keep fixture
preparation and downloads outside the measurement.

| Workload | Measure separately | Correctness check |
| --- | --- | --- |
| Startup and PDB/mmCIF load | Startup, I/O/decompression, parsing, bond/representation work; peak RSS | Atom/bond counts, coordinates, chains and states |
| Cartoon/sticks/surface rotation | First build, warm frame latency, CPU submission and GPU time where available | Picking, transparency, labels and reference images |
| Fixed-resolution CPU ray | End-to-end wall time and thread scaling | Image comparison with a justified tolerance |
| Map contour/isosurface | Build time, memory and repeated threshold changes | Same geometry/appearance for the same input and level |
| PSE save/reopen | Time, peak memory and file size | Objects, states, settings and views survive |
| GUI interaction | Idle CPU and latency during load, representation changes and export | Window remains usable; completion/errors are shown |

Record commit, release/debug flags, compiler, OS, CPU/GPU/driver, Python/Qt,
workload size/hash, viewport size, thread/shader settings, and warm/cold state.
Warm up, repeat at least five times, and report median/spread. Sample enough frames
for meaningful tail latency; do not infer it from five frame samples.

Compare optimized builds: Linux CI currently sets `DEBUG=1`. Record display
synchronization and GPU/software rendering; enqueue time is not completed GPU
execution. Separate profiling from final timing. Extend existing checks using
`perf_counter`, `cProfile`, or available native profilers before adding tools.

Put a result table and runnable command in each optimization PR. Until execution,
results remain **not measured**. Enforce timing budgets only after establishing a
repeatable reference machine; shared CI results may be too noisy.

## 1b — One measured bottleneck per change

1. **Algorithms and copies:** avoid rebuilding unchanged representations; find
   repeated model/coordinate copies, Python/C++ crossings and decompression.
   Cache only with a demonstrated cost and explicit invalidation rules.
2. **Existing CPU paths:** improve allocations/locality, then evaluate
   vectorization, OpenMP or worker counts. Check determinism, memory, nested
   parallelism, the GIL and PyMOL locks. Do not add pragmas to Ray by assumption.
3. **Existing GPU paths:** inspect draw calls, uploads, buffer reuse, shader
   variants and stalls. Try batching/instancing where measured, preserving
   selection and picking passes.
4. **Interaction:** coalesce redundant updates if profiling justifies it. Move
   suitable computation into existing workers/native paths; keep widgets and GL
   context operations on their owning threads. Native code can still block the
   GUI or hold the GIL.
5. **Remeasure:** keep gains exceeding observed noise without unacceptable memory
   or compatibility regressions. Reprofile before choosing another target.

Deleting fallback rendering or forcing `use_shaders` is a compatibility decision.
Audit overlays, text, CGOs, picking, stereo, image export and supported hardware
before proposing it; a Core profile is not a prerequisite for these optimizations.

## GPU compute gate

Apple documents native OpenGL support through 4.1 on Apple silicon, with OpenGL
deprecated. An OpenGL 4.3 compute requirement would exclude that native path.
Any experiment needs capability checks and a supported fallback; a new UI toolkit
does not fix this. [Apple WWDC technical presentation](https://developer.apple.com/videos/play/wwdc2020/10631/?time=1481)

Propose a bounded ray-tracing or contouring experiment only after profiling shows
that kernel dominates a real workload. A new compute framework requires the
repository's measured **5× end-to-end win**, including transfers, compilation,
synchronization and equivalent output quality. Report total application benefit,
hardware coverage and fallback/maintenance cost. A kernel-only win is insufficient.
No CUDA/OpenCL/Vulkan dependency is planned now.

## Additional ideas and completion checks

- Measure **idle wakeups** and redundant representation invalidation before
  pursuing another renderer; less work may also improve battery use.
- Track **peak memory and first useful frame**, not only total loading time.
- Profile **metadata refresh and selection synchronization** after step 3, so
  the panel cannot add expensive work to every render frame.
- Add cancellation at existing safe boundaries for long exports; do not promise
  cancellation for an indivisible native operation.

Each optimization needs a runnable regression check, before/after evidence and
relevant image/geometry or file round-trip checks. Rendering changes need real GUI
validation. Memory mapping, universal instancing, a new ray tracer and automatic
quality reduction remain deferred until measurements justify them.
