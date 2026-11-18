# 18 — Dialog sizes and the scroll bar of the sequence viewer

[Roadmap](../../PLAN.md) · Request 2026-11-18 · **Done 2026-11-18: 18a in
4.15.1, 18b in 4.17.0** (see "18a result" and "18b result").
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

### 18a result, 4.15.1

- **Fixed one level lower than planned,** in `pymol.Qt.utils.loadUi`, which
  `load_form` and the APBS plugin both call. A `QUiLoader` subclass returns
  the given widget for the top of the form, so layout, title and size land
  on the dialog itself. This is what the function's docstring always said
  ("load .ui file into widget") and what plugins written for PyQt expect.
  The named children, layouts included, are set as attributes.
- `load_form` then opens a form at least as large as its content needs. A
  form without a size in its `.ui` file fits its content by itself.
- The 'floating' panels, the plugin rows and the Draw/Ray popup use the same
  loader and get the form's title and layout too.
- **Found on the way:** Setting > Edit keyboard shortcuts did not open at
  all. `shortcut_menu_gui.py` looked for the keys in `vars(Qt)`; in PySide6
  they are members of `Qt.Key`. One line.
- Measured in the real window on WSLg at 150 %: Plugin Manager 576 x 616
  (all four tabs, title "Plugin Manager"), Fetch 300 x 364, Movie Export
  255 x 436, Save PNG 283 x 196, Colors 364 x 329, Properties 400 x 500,
  Advanced Settings 400 x 500, Shortcuts 700 x 700; none below its content.
  The Draw/Ray popup is unchanged.
- Check: `testing/tests/api/forms.py` loads every form.
- Not opened in the real window: APBS, Lighting Settings, the volume editor,
  the import dialogs for trajectories, maps and MTZ files. 100 and 200 %
  were not tried.
- `forms/shortcut_menu.ui` is loaded by nothing. Left in place: deleting a
  file of `data` or `forms` is the user's call.

### Options

| | Option | Note |
| --- | --- | --- |
| A | Fit the content, as above. Chosen (not answered, the recommendation). | Recommended. One place. |
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

### 18b result, 4.17.0

**The user chose B, a Qt scroll bar.** Built as an overlay, not as a second
widget under the viewport:

- **Where:** a `QScrollBar` that is a child of the GL widget and sits
  exactly on the strip the core leaves under the sequence rows. The plan
  said "under the viewport"; with the sequence at the top of the viewport
  that would have put the bar a whole window away from what it scrolls.
- **The marks of the selection stay.** The core also draws, in that strip, a
  mark for every selected residue along the whole sequence. The bar's track
  is transparent and its handle see-through, so the marks show under it.
  The table above did not know about the marks; an opaque bar would have
  removed them.
- **Core:** `CSeq` lost its `ScrollBar`; it keeps the first visible column
  (`NSkip`) and clamps it. One call, `SeqScroll`, reads the state and the
  box of the strip and sets the offset; `_cmd.seq_scroll` exposes it
  without the API lock, like `get_movie_playing`, because the window calls
  it after every frame from the thread that draws.
- **Window:** `pymol_gl_widget.py` places the bar after each frame, so the
  mouse wheel over the rows, a resize and a new object keep it right; it
  hides when everything fits or the viewer is off.
- **Keyboard:** Tab reaches the bar; arrows, Page Up/Down, Home and End
  scroll, as on any Qt scroll bar.
- `ScrollBar.cpp` stays for the core's movie panel, the scene buttons and
  the old object list; it goes with them (steps 17 and 19).
- Measured in the real window on WSLg at 150 % with 1oky (436 columns, 59
  visible): bar at (3, 40) 629 x 19, range 0 to 377, page 59; setting the
  bar to 188 moved the core to 188; setting the core to 7 moved the bar to
  7; with `seq_view` off the bar is hidden. Two captures looked at.
- Check: `testing/tests/api/seq_scroll.py` covers the call without a
  window. The widget itself needs a GL context and has no test file.
- Not tried: `seq_view_location` at the bottom, `seq_view_overlay`, 100 and
  200 %.

## Questions

1. Dialogs: A or B? **Not answered; A is built.**
2. Scroll bar: A (recommended), or go straight to B? **Answer: B.**

## Skipped

- Restyling the dialogs' content (margins, labels): the audit "one dialog at
  a time" of step 3 continues there.
- Scroll bars of Qt widgets: they already follow the theme.
- A bigger or scalable font in the sequence viewer: option C.
