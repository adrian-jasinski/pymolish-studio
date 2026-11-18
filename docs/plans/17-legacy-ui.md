# 17 — Legacy menu rows and the old internal GUI

[Roadmap](../../PLAN.md) · Request 2026-11-18 · **Planned, nothing built.**
The request answers the open question of [step 3](03-modern-ui.md): the old
C++ panel is not needed any more.

**First the menu rows that lead nowhere go (17a, 17b): small and safe. Then
the C++ code that draws the old panel goes file by file (17c), each file its
own removal with the full suite and the sanitizer job. Every slice leaves a
working program, so the work can stop after any of them: after 17a the panel
is already hidden and only reachable by typing `set internal_gui`.**

## What exists

**Menu rows** (`modules/pymol/_gui.py`):

| Row | Line | What it does today |
| --- | --- | --- |
| Display > Internal GUI | 418 | Shows the old object list inside the viewport, next to the Qt Objects panel. |
| Display > Internal Prompt | 419 | A second command prompt drawn in the viewport. |
| Display > Internal Feedback | 420 | 0, 1, 3 or 5 lines of the log drawn in the viewport. The window starts with 0. |
| Display > Overlay | 424 | 0, 1, 3 or 5 lines of the log drawn over the molecule. |
| Setting > Overlay Text | 781 | The same setting once more, as a check box. |
| Plugin > Legacy Plugins | `pymol_qt_gui.py:1007` | An empty submenu. It collects the rows of plugins written for the Tk window; Tk was removed in 4.1. |

**The old panel in C++.** It is five things drawn with bitmap letters at the
right edge of the viewport. Line counts are the ranges of the functions
named, read on 2026-11-18, not a measured diff.

| File | Panel code | Stays |
| --- | --- | --- |
| `layer3/Executive.cpp` | `CExecutive::click`, `release`, `drag`, `draw`, `reshape` (14769 to about 16400): the object list and its A/S/H/L/C buttons. About 1,600 lines. | The executive itself. `ExecutiveUpdatePanelList` (1547) until 17d: the core's movie panel uses the same row list. |
| `layer1/Control.cpp` | `CControl::draw`, `click`, `drag`, `release`, `reshape`: the row of movie buttons. About 560 of 857 lines. | `ControlRock`, `ControlRocking`, `ControlIdling`, the three `ControlSdof*` functions (3D mouse). |
| `layer1/ButMode.cpp` | `CButMode::draw`, `click`, the fast draw: the mouse mode table. About 320 of 748 lines. | `ButModeGet`, `Set`, `Translate`, the rate functions: every mouse click goes through them. |
| `layer1/Wizard.cpp` | `CWizard::draw`, `click`, `drag`, `release` (480 to 869): the wizard buttons. About 390 lines. | Wizard events and the prompt text in the viewport. |
| `layer4/PopUp.cpp`, `layer4/Menu.cpp` | The menus drawn in OpenGL, 969 lines. Since 4.5.18 the window shows Qt menus instead; the GL menus remain for a start without the window's hook. | To be decided in 17e. |
| `layer1/Ortho.cpp` | The right margin, `OrthoDrawInternalGUIBG`, `OrthoLayoutPanel`: 62 mentions of the settings. | The text console (feedback, prompt, overlay). |

**Settings:** `internal_gui` (99), `internal_gui_width` (98),
`internal_gui_control_size` (322, also the row height of the scene buttons,
`Scene.cpp:2698`), `internal_gui_mode` (341, also the colors of the GL
menus), `internal_gui_name_color_mode` (768).

**Other places that read them:** `layer5/PyMOL.cpp` (window size, option
defaults), `layer4/Cmd.cpp:4941` (`viewport`), `layer1/P.cpp:1815`,
`layer0/PyMOLOptions.h`, `layer1/Setting.cpp` (side effects),
`modules/pymol/invocation.py` (`-i`, the `-A` modes), `modules/pymol2/`,
`modules/pmg_qt/pymol_gl_widget.py:148` (dragging the panel's edge),
`pymol_qt_gui.py:1266`, `docs/getting-started.md:89`.

## Risks, and what answers each

| Risk | Answer |
| --- | --- |
| `pymolish -x` (no external GUI) hides the toolbar and the command dock and counts on the old panel for the object list. | Question 1. |
| The core's movie panel (the keyframe rows under the viewport) lines its rows up with the old object list. Without the list the rows have no names. | The panel list stays until the Qt timeline of [step 19](19-movie-timeline.md) replaces the movie panel (17d). |
| A pymolrc or a session file sets one of the five settings. The user's own pymolrc sets `internal_gui_width` and `internal_gui_control_size`. | 17c tests both first: a PSE saved with the settings must load, and a `set` of a removed name must print one line and go on. If either fails, the setting keeps its row in `SettingInfo.h` and only its readers go. |
| `SettingInfo.h` is positional. | The rule of `AGENTS.md` §2.1: a removed row leaves `REC__( idx,  ),`. |
| The scene buttons in the viewport use `internal_gui_control_size`. | They get a constant (18, the default). The Scenes dock replaced them for daily use; removing them is not in this step. |
| Something outside the panel calls a panel function. | Per file: `grep -rn` for every function before it goes, build, full suite, sanitizer job, a PSE round trip, the real window. |
| A plugin written for the Tk window registers rows through the shims. | Question 3. Only `~/.pymol/startup/pymolish` is installed on the development machine, and it is to be removed anyway. |

"If it is too much, keep it but hide it": that is the state after 17a. 17c
is worth doing only if each file comes out cleanly; a file that does not is
left as it is and listed here with the reason.

## Slices

**17a, menu rows of the old panel and console.**
- `_gui.py`: delete Display > Internal GUI, Internal Prompt, Internal
  Feedback, Overlay, and Setting > Overlay Text. The settings stay and can be
  typed.
- `pymol_qt_gui.py:1265`: the comment no longer points at a menu row.
  `docs/getting-started.md:89` the same.
- Check: the menu test finds none of the five labels. Real window: Display
  has two separators less.
- Commit: `remove(ui): menu rows of the internal GUI, prompt, feedback and
  overlay`.

**17b, the empty Legacy Plugins submenu.**
- Smallest version: the submenu is created when the first old-style plugin
  adds a row, not before. A few lines in `initializePlugins`
  (`pymol_qt_gui.py:995`).
- Larger version, question 3: delete the Tk shims
  (`modules/pmg_qt/mimic_tk.py` 128 lines, `mimic_pmg_tk.py` 87 lines, the
  Tk parts of `modules/pymol/plugins/legacysupport.py`) and
  `Plugin.legacyinit`. The Plugin Manager imports `tkMessageBox` and
  `installPlugin` from `legacysupport` in four places; those move to Qt
  message boxes first.
- Check: Plugin menu in the real window, with and without `-k`; the two
  bundled plugins (APBS, Lighting Settings) still appear.
- Commit: `simplify(ui): no empty Legacy Plugins menu`.

**17c, the panel code, one removal per file.** Order by risk, lowest first:
1. `pymol_gl_widget.py`: the edge drag of the old panel. `invocation.py`
   and `pymol2`: `internal_gui` is always 0.
2. `Control.cpp`: draw and mouse functions.
3. `ButMode.cpp`: draw and click.
4. `Wizard.cpp`: draw and mouse functions.
5. `Executive.cpp`: draw and mouse functions; the panel list stays.
6. `Ortho.cpp`: the right margin; `PyMOL.cpp`, `Cmd.cpp`, `Setting.cpp`,
   `P.cpp`, `PyMOLOptions.h`: the readers. Then the settings.
- Each: title `remove: <thing>`, the commit body lists what went and why
  nothing depends on it. Numbers before and after: lines, size of `_cmd`.
- Checks: full Python suite, the Catch2 tests, the sanitizer job, a PSE from
  before the change loads, real window with a wizard (measurement), mouse
  modes, rock, a 3D mouse is not available on the development machine and is
  reported as not tested.

**17d, the panel list.** After step 19d has removed the core's movie panel:
`ExecutiveUpdatePanelList` and the `PanelRec` list, if nothing else reads
them by then (the open item "group open/closed shared with the core" of
step 3 may).

**17e, the GL menus.** `PopUp.cpp` and `Menu.cpp`: check whether any start
mode still reaches them (`-x` keeps the Qt hook, `-c` draws nothing). If
none does: one removal, 969 lines, and `internal_gui_mode` with it.

## Questions

1. `pymolish -x` after the removal: (A) it shows the viewport alone, with
   the object list one key away as a floating Objects panel (recommended);
   (B) `-x` goes away and prints a hint; (C) the panel code stays for `-x`
   only, which keeps all of it.
2. The text console in the viewport (`internal_feedback`, `internal_prompt`,
   `overlay`): keep the code and only remove the rows (recommended: full
   screen and `-x` have no other command line), or plan its removal too?
3. Old-style plugins: only hide the empty submenu (recommended first), or
   delete the Tk shims, after which a plugin written for the Tk window no
   longer adds its rows?

## Deleted

Filled in as slices ship.

## Skipped

- The scene buttons and the sequence viewer drawn by the core. The scroll
  bar they share is in [step 18](18-dialogs-scrollbar.md).
- A compatibility layer that maps the removed settings to the Qt panel.
- Rewriting `menu.py`, which the old panel also read: step 14 decided that.
