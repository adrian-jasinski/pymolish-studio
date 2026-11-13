# 8 — Modern C++ in the core

[Roadmap](../../PLAN.md) · Request 2026-11-13 · Draft; counts are `grep` counts,
nothing was built, timed or changed for this plan

**Modernize the C-style C++ of the core one idiom and one file at a time, behind
tests and sanitizers. No from-scratch rewrite. Vendored C stays C.**

## What exists

- **The core is already C++.** `layer0/` to `layer5/` and `layerGraphics/` hold
  165 `.cpp` files, 219,000 lines, and no `.c` file. MSVC builds with
  `/std:c++17`; GCC and Clang use their default. The work is "C written in
  C++", not a language port.
- **Real C is vendored only:** `contrib/champ` (10 files, 7,500 lines) and the
  VMD molfile plugins in `contrib/uiuc` (30 files, 23,500 lines).
- **Upstream started the same migration and left it half done:**

  | Old idiom | Sites | Modern form already in the tree | Sites |
  | --- | --- | --- | --- |
  | `VLAlloc`, `VLACheck`, ... macros | 902 | `pymol::vla<T>` | 222 |
  | `Alloc`, `Calloc`, `FreeP`, `malloc`, `free` | 714 | `std::vector` | 676 |
  | raw `new` / `delete` | 589 | `std::unique_ptr` | 102 |
  | `sprintf`, `strcpy`, `strcat`, `strncpy` | 517 | `std::string` | 465 |
  | fixed buffers (`OrthoLineType`, `WordType`, ...) | 221 | | |
  | `ok_assert` / `ok_raise` chains, `goto` | 246 | `pymol::Result` | 419 |
  | C pointer casts | 572 | | |
  | `#define` (includes header guards) | 1,917 | | |

  About 3,800 sites plus the macros.
- **Safety net today:** 167 Python test files, 23 Catch2 files,
  `testing/bench.py`. No sanitizer build. Test coverage of the core was never
  measured.

## Decisions

- **No rewrite from scratch.** 219,000 lines whose behavior is defined by the
  code itself, not by a specification; a rewrite loses function by
  construction. Small behavior-neutral steps do not.
- **Vendored C is not touched.** The molfile plugins track VMD; rewriting them
  gains nothing and makes every plugin update a manual port. Champ: same.
- **The CPython C API code stays as it is** (2,479 `PyObject` uses, mostly
  `layer4/Cmd.cpp`). The API is C. pybind11 would be a new dependency for no
  user-visible gain.
- **One idiom per PR, behavior-neutral,** commit type `simplify(<scope>)`. A
  modernization PR never changes an algorithm, and a speed PR never sweeps
  idioms. A regression then has one cause.
- **Speed stays step 1's job.** Modernization does not make code faster by
  itself and can make it slower (`std::vector` zero-fills where `malloc` did
  not; `std::string` allocates inside loops). The two steps share an order
  instead: files are modernized in profile order, so a hot function is cleaned
  just before or after it is optimized, and `bench.py` gates both.
- **Delete first.** A line removed under step 2 is a line not modernized.
- **Session layout is frozen.** Structs written by `pse_binary_dump`
  (`layer2/AtomInfoHistory.h`) keep their layout; PSE files must load and save
  as before.
- **No public change.** `cmd.*`, settings and file formats are untouched, so
  `ChangeLog` needs no entry.

## Order

| Slice | Work | Why here |
| --- | --- | --- |
| 8a | Safety net: one Linux CI job with `-fsanitize=address,undefined` running the Python suite and Catch2; one `gcov` run that lists core files the suite never enters | Without it "no lost function" cannot be shown. A file with no coverage gets a test before it is touched. |
| 8b | `sprintf` / `strcpy` / fixed buffers to `std::string` and `snprintf` | The only idiom that is a memory-safety bug class. Mechanical. |
| 8c | `Alloc` / `FreeP` / `malloc` and raw `new` / `delete` to `std::vector` and `std::unique_ptr` | Removes manual cleanup paths, which makes 8e possible. |
| 8d | VLA macros to `pymol::vla<T>` or `std::vector`; delete the macro layer when its last user is gone | Finishes upstream's migration; ends in a deletion. |
| 8e | `ok` chains and `goto` cleanup to `pymol::Result` and early return | Needs 8c: early return is only safe once ownership is automatic. |
| 8f | Function-like macros to `constexpr` / inline functions; C casts to named casts | Lowest value; do it only in files already open for another slice. |
| 8g | `ov/` (3,700 lines of hand-written hash maps and string interning) to `std::unordered_map`, if `bench.py` is not slower | The one slice that deletes a directory. Measure before deciding. |

Inside a slice, go file by file in profile order: `Executive.cpp`,
`Selector.cpp`, `ObjectMolecule.cpp`, `CGO.cpp`, `Ray.cpp`, `RepSurface.cpp`
first.

## Risk

- **Tests prove only what they cover.** Rendering and GUI paths do not run
  headless. Slices that touch `layer1/` need the real GUI check, and 8a's
  coverage list decides where a test comes first.
- **Upstream merges.** Every modernized file stops taking upstream patches
  cleanly. No upstream remote is configured today; if merges from
  `schrodinger/pymol-open-source` are still wanted, restrict the work to files
  this fork already changed heavily.
- **Size.** This is not one step finished in a week. Each slice is many PRs.
  No date or line-count target is promised.

## Skipped, and when to add

- **C++20 / 23** (`std::span`, `std::format`): add when a slice needs one and
  the three CI compilers support it. It is a one-line build flag.
- **Splitting the large files** (`Executive.cpp` is 17,700 lines) or
  redesigning the object class hierarchy: only when a change inside is blocked
  by it.
- **`clang-tidy` `modernize-*` automatic fixes:** decide in 8a. It is a new
  pinned dev tool, and whole-tree automatic fixes break the one-idiom,
  reviewable-diff rule; per-file use may pay off in 8f.

## Checks

Every PR: the full Python suite, Catch2, the sanitizer job, `bench.py` within
noise of the baseline in [docs/baseline.md](../baseline.md), and a PSE load and
save round trip. `layer1/` changes: real GUI.

## Status

Draft. Not started.
