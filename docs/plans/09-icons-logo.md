# 9 — Own icon and logo

[Roadmap](../../PLAN.md) · Request 2026-11-14 · Draft; source and license text
were read, nothing was built or changed. Not legal advice.

**Replace the one PyMOL image the application still shows, and stop the window
from calling itself PyMOL. Blocked on two files from the user.**

## What exists

- **One PyMOL image:** `data/pymol/icons/icon2.svg`, the upstream logo. Two
  users: `make_pymol_qicon` (`modules/pmg_qt/pymol_qt_gui.py:1219`) and
  `README.md:5`.
- **Toolbar and menu icons are not PyMOL's:** 51 Lucide files (ISC) in
  `data/pmg_qt/icons/lucide/`. They stay.
- **Bundles have no icon:** `packaging/pyinstaller.spec` calls `EXE(...)`
  without `icon=`.
- **The window still presents itself as PyMOL:**

  | Where | Text now |
  | --- | --- |
  | `pymol_qt_gui.py:129`, `:1264` | window title `PyMOL` |
  | `pymol_qt_gui.py:924` `show_about` | "The PyMOL Molecular Graphics System", `https://pymol.org`, `sales@schrodinger.com` |
  | `layer1/Ortho.cpp:2578` `OrthoSplash` | "PyMOL(TM) Molecular Graphics System", copyright lines |

## Does the license allow it

`LICENSE` has two parts.

| Clause | Effect on this step |
| --- | --- |
| Permission to "modify, distribute, and distribute modified versions" | Replacing images is allowed. |
| "don't change or remove any of the Copyright notices" | An icon is not a notice. The copyright lines in the About box and the splash text stay word for word. |
| Derivative software "must be plainly distinguished from any and all PyMOL products distributed by Schrodinger" | The license asks for this change. The PyMOL logo, the title `PyMOL` and the Schrodinger sales address are what break it today. |
| Only four slogans may use the mark without written permission | About box uses one of them: "Based on PyMOL(TM) technology." with the footnote "PyMOL is a trademark of Schrodinger, LLC." |

Open risk, user's call: the product name "pymolish" contains the mark. The
license does not cover product names. This plan does not rename anything.

## Needed from the user

| File | Form |
| --- | --- |
| Application icon | PNG, square, 1024 x 1024, transparent background, readable at 16 px |
| Logo | PNG, readable on light and dark pages (or two files) |
| Rights | One line: who made them, under which license they ship. Must not resemble the PyMOL logo. |

## Decisions

- **One master PNG, no size set.** `data/pymol/icons/pymolish.png` and
  `logo.png`. `QIcon` scales it. Ceiling: blurry at 16 px; then add one
  hand-tuned 32 px file.
- **Bundle icon from the same PNG.** `icon='../data/pymol/icons/pymolish.png'`
  in the spec. PyInstaller converts to `.ico` when Pillow is installed in the
  build job: one line in `.github/workflows/build.yml`, no committed `.ico` or
  `.icns`. Verify on the Windows artifact.
- **macOS:** the spec builds a folder, not an `.app`, so the Dock icon comes
  from `app.setWindowIcon` at run time. Nothing more to do.
- **Delete `icon2.svg`** in the same PR (`grep -rn icon2` first). It is a data
  file: this plan is the request to delete it.
- **Text:** title `pymolish-studio`; About box names the fork, links this
  repository, keeps "Copyright (C) Schrödinger, LLC." for the PyMOL part, adds
  the slogan and footnote, drops the sales address. Splash: one added line
  ("pymolish-studio, an independent fork"); upstream lines unchanged.
- **Rename `make_pymol_qicon`?** No. Plugins may import it.

## Steps

1. Add the two PNGs; point `make_pymol_qicon` at the icon.
2. Title, About box, splash line.
3. Spec `icon=`; Pillow in the build job.
4. Delete `icon2.svg`; README image is handled in [step 10](10-readme-license.md).
5. Check: one test in `testing/tests/system/` loads the PNG with `QImage`
   (works headless), asserts it is not null and square, and that
   `cmd.splash` output still contains the Schrodinger copyright line.
6. Look at it: title bar, task bar, About box on Linux; the Windows artifact.

Commit: `ui(brand): own application icon, logo and window title`.
`ChangeLog`: `cmd.splash` prints one more line.

## Skipped

- Splash image, `.desktop` file, installer icons: no installer exists yet.
- Renaming the `pymol` package, `PYMOL_DATA`, or the product: separate decision.
- Replacing the Lucide icons.
