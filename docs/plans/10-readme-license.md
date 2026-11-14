# 10 — README and license files

[Roadmap](../../PLAN.md) · Request 2026-11-14 · Draft; files and license text
were read, nothing was changed. Not legal advice.

**New README that says what this is: a fork of Open-Source PyMOL. PyMOL code
stays under its license, word for word; new code is MIT. Text first (10a),
images when [step 9](09-icons-logo.md) delivers them (10b).**

## What exists

| File | State |
| --- | --- |
| `README.md` | 30 lines, titled "Open-Source PyMOL", shows the PyMOL logo, sends readers to pymol.org |
| `README` | 281 lines of upstream text from 2003; says "Python license", which is wrong today |
| `LICENSE` | Upstream notice, unchanged |
| `pyproject.toml` | `license = {file = "LICENSE"}`; only author listed is Schrodinger |
| `packaging/pyinstaller.spec` | copies `LICENSE` into the bundle |
| `AGENTS.md` §5 | "Don't touch `LICENSE`" |
| `docs/` | `plugins.md`, `baseline.md`, `plans/`; plus `INSTALL`, `DEVELOPERS`, `PACKAGING`, `ChangeLog` at the root |

## What the PyMOL license requires

| Requirement (from `LICENSE`) | How this step meets it |
| --- | --- |
| Copyright notice "appears in all copies" | Upstream text stays byte for byte in `LICENSE`; it ships in the repository, the wheel and the bundle. |
| Copyright and permission notice "appear in supporting documentation" | README license section links `LICENSE`; `docs/licenses.md` links it again. |
| Name of Schrodinger not used "in advertising or publicity" | README names Schrodinger only as copyright holder and trademark owner. |
| Derivative "must be plainly distinguished" from Schrodinger's PyMOL | Title is `pymolish-studio`; second line says independent fork, not affiliated, official product at pymol.org. |
| Trademark use limited to four slogans plus footnote | README uses "Based on PyMOL(TM) technology." and ends with "PyMOL is a trademark of Schrodinger, LLC." |

The PyMOL license is permissive and compatible with MIT for added code.

## Decisions

- **Two license files.**
  - `LICENSE`: a short header (what is under which license, links to both
    files and to upstream), then the upstream notice unchanged.
  - `LICENSE-MIT`: MIT, "Copyright (c) 2026 Adrian Jasinski and pymolish-studio
    contributors".
- **Honest boundary.** New files are MIT. Changes inside upstream files are
  MIT too, but those files still carry the PyMOL notice. A distribution needs
  both files. The header says exactly that. No per-file headers are added;
  existing headers are not touched.
- **`AGENTS.md` §5** becomes: "Don't touch `AUTHORS`, copyright headers, or the
  Schrodinger notice inside `LICENSE`."
- **Third-party list:** `docs/licenses.md`, one table: component, license,
  where its text is, link. Read each license from its source, not from memory.
  Rows to cover: PyMOL, new code, Lucide, champ, molfile plugins, pocketfft,
  embedded fonts, and what bundles ship (PySide6/Qt is LGPL-3.0: the bundle
  must carry that text), numpy, GLEW, GLM, libpng, freetype, msgpack-c,
  netcdf, nlohmann-json. Steps 12 and 13 add rdkit, OpenMM, PDBFixer.
- **Old `README`:** `git mv README docs/README-upstream.txt`, content
  unchanged. Keeps its notice, ends the two-README confusion.
  `grep -rn "README'" setup.py _custom_build packaging` first.
- **`pyproject.toml`:** `license-files = ["LICENSE", "LICENSE-MIT"]` if the
  pinned setuptools supports it; add the fork maintainer to `authors`, keep
  Schrodinger. Spec copies `LICENSE-MIT` too.

## README outline (target: under 80 lines)

1. Logo (10b), name, one line: what it is.
2. "Fork of [Open-Source PyMOL](https://github.com/schrodinger/pymol-open-source).
   Independent; not affiliated with or endorsed by Schrödinger. Official
   PyMOL: pymol.org."
3. CI badge, one screenshot (10b).
4. Features: 6 to 8 bullets, each one line, each linking into `docs/`.
5. Download (Releases), install from source (link `INSTALL`).
6. Documentation table: `docs/features.md`, `docs/plugins.md`,
   `docs/licenses.md`, `PLAN.md`, `ChangeLog`.
7. License: PyMOL code → [`LICENSE`](../../LICENSE); new code → `LICENSE-MIT`;
   third parties → `docs/licenses.md`; upstream repository and its license.
8. Trademark footnote.

New doc: only `docs/features.md` (removed, added, changed versus upstream;
source: `PLAN-DONE.md` and `ChangeLog`). Steps 11 to 14 each add their section.

## Steps

- **10a, no images:** `LICENSE` header, `LICENSE-MIT`, `AGENTS.md` line,
  README, `docs/features.md`, `docs/licenses.md`, move old `README`,
  `pyproject.toml`, spec.
- **10b, after step 9:** logo at the top of the README (referenced from
  `data/pymol/icons/`, no second copy), one screenshot `docs/img/window.png`
  taken from pymolish itself.
- **Check:** one test in `testing/tests/system/`: every relative link in
  `README.md` and `docs/*.md` points at an existing file, and `LICENSE` ends
  with the upstream text (compare against a stored SHA-256 of that tail).
- PR diff of `LICENSE` must show zero removed lines.

Commit: `docs(license): new README, MIT for new code, PyMOL notice kept`.

## Skipped

- Rewriting `INSTALL`, `DEVELOPERS`, `PACKAGING`: fix only commands that are wrong.
- SPDX headers in every file, a `NOTICE` file, REUSE compliance: add if a
  packager asks.
- A documentation site: Markdown in `docs/` is enough.
