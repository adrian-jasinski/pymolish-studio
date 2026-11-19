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
