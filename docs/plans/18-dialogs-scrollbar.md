# 18 — Dialog sizes and the scroll bar of the sequence viewer

[Roadmap](../../PLAN.md) · Request 2026-11-18 · **Planned, nothing built.**
Two leftovers of [step 3](03-modern-ui.md): "spacing of the remaining
dialogs" and "sequence viewer still drawn by the core".

**Dialogs open too small because the form sits inside the dialog without a
layout: one fix in `load_form` covers all 23 forms. The scroll bar under the
sequence is drawn by the core with a bevel from the 1990s: it gets a flat
look in the one file that draws every scroll bar of the viewport.**

## 18a — Dialogs open at the right size

### What exists

- `PyMOLQtGUI.load_form` (`modules/pmg_qt/pymol_qt_gui.py:554`) makes a
  `QDialog` and calls `QUiLoader().load(uifile, dialog)`
  (`modules/pymol/Qt/utils.py:266`). Qt then creates the form as a **child
  widget** of the dialog. The dialog itself has no layout.
- Measured on 2026-11-18 with every form in `modules/pmg_qt/forms/`, Qt
  platform `offscreen`, scale 100 %:

  | Finding | Forms |
  | --- | --- |
  | The dialog has no layout | all 23 |
  | The dialog opens at the size written in the `.ui` file, not at the size its content needs | Plugin Manager: 499 x 435, content needs 576 x 605. `colors`, `load_mae`, `render` and `movieexport` are also narrower than their content. |
  | The `.ui` file has height 0, the dialog opens at 100 x 30 | `export_objects`, `fix_structure`, `load_folder` |
  | The dialog opens at Qt's fallback 640 x 480 | `askpartial`, `change_confirm`, `create_shortcut`, `help_shortcut`, `load_mtz`, `shortcut_menu` |

- Three more signs of the same cause in the user's screenshots: the title
  bar says "PyMOL" instead of "Plugin Manager" (the title belongs to the
  child), the content is cut off instead of following the dialog's edge,
  and under WSLg at 150 % the window opened at about 130 x 70 pixels.
- Windows that do not use `load_form`: Lighting Settings and APBS
  (`data/startup/`), the shortcut editor (`resize(700, 700)`), advanced
  settings, the plugin info dialog (`resize(600, ...)`), the volume editor,
  the text editor.

### Slice

- First reproduce in the real window on WSLg at 150 %: note the opening
  size of the Plugin Manager, so the fix is measured against it.
- `load_form`: when it made the dialog itself, give the dialog a layout
  without margins that holds the form, and copy the form's window title.
  About five lines. Qt then sizes the dialog to its content at every UI
  scale, and the content follows the edge.
- Open every window of the two lists above at 100, 150 and 200 %. A window
  that is still wrong gets its own line in a table here; a fixed
  `resize(...)` goes where the layout does the job.
- Checks: a test in `testing/tests/api/` loads every form through
  `load_form` and asserts a layout, a title and a size not below the
  content's minimum. Real window at 150 %: Plugin Manager, Fetch, Export
  Movie, Properties.
- Commit: `fix(ui): dialogs open at the size of their content`.

### Options

| | Option | Note |
| --- | --- | --- |
| A | Fit the content, as above. | Recommended. One place. |
| B | A, and remember size and position of each dialog in `QSettings` (`saveGeometry`). | About six more lines in `load_form`. Useful if the user often resizes the same dialog; otherwise state that can go stale after a monitor change. |
| C | Edit the sizes in the 23 `.ui` files. | Does not survive another UI scale. Not recommended. |

## 18b — A modern scroll bar under the sequence

### What exists

- `layer1/ScrollBar.cpp`, 350 lines. The handle is four rectangles: a light
  edge, a dark edge, a shadow line and the fill, each written twice (CGO and
  immediate mode). The track is filled with a fixed color.
- Four users: the sequence viewer (`Seq.cpp`, 16 pixels high,
  `Seq.h:86`), the core's movie panel (`Movie.cpp`), the scene buttons
  (`Scene.cpp`) and the old object list (`Executive.cpp`, removed in
  [step 17](17-legacy-ui.md)).
- The text of the sequence viewer is also drawn by the core, in whole scale
  steps (open in step 3).

### Options

| | Option | Size | Note |
| --- | --- | --- | --- |
| A | **Restyle in `ScrollBar.cpp`:** one flat handle, no bevel, a thinner bar (16 to 8 pixels), a track that is the background a little lighter or darker, the handle brighter while it is dragged. | Negative: three of the four rectangles go, twice. | Recommended. All scroll bars of the viewport change together. The colors come from the background, so it works on black, white and gradients. |
| A+ | A, with rounded ends. | Two half circles as triangle fans, about 20 lines. | Only if A looks unfinished in the real window. |
| B | A real `QScrollBar` under the viewport that moves the sequence. | Two new core calls (range, offset), about 80 lines. | Native look and theme; only for the sequence viewer; two widgets must agree on the width. |
| C | The sequence viewer as a Qt panel. | Large: `Seeker.cpp` (1,998 lines) builds the rows, clicks select atoms. | Solves text size at 125 %, scroll bar, search. Stays an open item of step 3; not part of this step. |

### Slice (option A)

- `ScrollBar.cpp`: `drawImpl` and `drawHandle` draw one rectangle each.
  `Seq.h`: `ScrollBarWidth` 8.
- Checks: real window with a long chain and the sequence viewer on, on a
  black and on a white background, at 100 and 200 %: drag, click on the
  track, mouse wheel. The movie panel with a 100-frame movie. No test file:
  it is drawing; the suite and the sanitizer job must pass.
- Commit: `ui(seq): flat scroll bar in the viewport`.

## Questions

1. Dialogs: A or B?
2. Scroll bar: A (recommended), or go straight to B?

## Skipped

- Restyling the dialogs' content (margins, labels): the audit "one dialog at
  a time" of step 3 continues there.
- Scroll bars of Qt widgets: they already follow the theme.
- A bigger or scalable font in the sequence viewer: option C.
