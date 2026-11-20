# 27 — UI scale: any value from 50 % to 300 %, without a restart

[Roadmap](../../PLAN.md) · Request 2026-11-20 · Planned, not built. The live
change was tried in the real window and worked there.

**The scale button becomes a field that takes any whole percent from 50 to
300, and the window changes size at once.** This replaces two decisions:
the five fixed steps up to 200 % of [step 7](07-toolbar-icons-scale.md), and
"live rescale without restart: skipped" of [step 3](03-modern-ui.md).

## What exists

| Thing | State |
| --- | --- |
| The setting | `theme.ui_scale()`, saved in `QSettings` `ui/scale`, default 1.5, steps `SCALES = (1, 1.2, 1.5, 1.8, 2)`. |
| How it reaches Qt | `theme.apply_ui_scale` sets `QT_SCALE_FACTOR` before the application object exists. Qt reads it once. |
| The button | A menu of the five steps in the toolbar; a pick shows "applies the next time pymolish starts". |
| The viewport | Follows the window's pixel ratio; `display_scale_factor` (whole numbers) is rounded from it for the text the core still draws. |

## The trial (2026-11-20, Linux, X11 under WSLg, PySide6 6.12)

Qt has the function that changes the factor, `QHighDpiScaling::setGlobalFactor`.
It is exported by the Qt library but not offered by PySide6, and Qt says it
may only be called "when no windows exist". Called through `ctypes` while
the window is open, nothing changes. Called after hiding the window and
destroying its native handle (`QWindow.destroy()`, the widgets stay), then
showing the window again:

| Step | Pixel ratio of the window | Viewport | `display_scale_factor` |
| --- | --- | --- | --- |
| start, 150 % | 1.5 | 1198 x 735 | 2 |
| to 100 % | 1.0 | 799 x 490 | 1 |
| to 225 % | 2.25 | 1797 x 1102 | 2 |
| back to 150 % | 1.5 | 1198 x 735 | 2 |

The molecule stayed loaded and drawn, the OpenGL context was not recreated
(checked in a small test window: one `initializeGL`), docks and toolbar kept
their layout, the grabbed pictures are sharp at each scale. Each step takes
well under a second. Qt prints its warning line each time.

Not tried: Windows, macOS, Wayland, a floating dock, an open dialog, a
second screen with another scale.

## Options (question 28)

| | Option | Note |
| --- | --- | --- |
| A | **Live, by the trial's way; where it cannot work, the old message. Recommended.** | About 40 lines in `theme.py`. It uses a private function of Qt by its symbol name: `_ZN15QHighDpiScaling15setGlobalFactorEd` on Linux and macOS, `?setGlobalFactor@QHighDpiScaling@@SAXN@Z` on Windows (to confirm there). If the symbol is missing or the pixel ratio did not change afterwards, the value is saved and the message "applies at the next start" is shown, which is today's behavior. A Qt update can remove the symbol; the check for that is one test. Marked `ponytail:` with this ceiling. |
| B | Restart in place: save the session to a temporary file, start pymolish again with the new factor, load the session. | Public API only, works everywhere. Two to three seconds; the log, the undo history, Python variables and plugin state are lost; an unsaved session name must be carried over. About 60 lines. |
| C | Live by font size: the application font and the icon sizes are multiplied, Qt lays out again. | Public API, instant. Spacing, margins, scroll bars and the viewport's text do not follow exactly, and the style sheet has pixel values: the window looks slightly off at any scale but the one it was designed at. |
| D | Keep the restart, only widen the range and take any value. | Smallest: the field and the range, five lines. |

A with D as its fallback is what the plan below describes. If the trial on
Windows or macOS fails, those systems get B or D: that is decided with the
result in hand.

## Design

| Part | Decision |
| --- | --- |
| Control | The toolbar button keeps its icon and shows the value ("150 %"). Its menu: an editable field (a `QSpinBox`, 50 to 300, step 10, suffix " %"; any whole number can be typed), then the common steps 75, 100, 125, 150, 175, 200, 250, 300 as rows. Enter or a row applies. |
| Apply | `theme.set_ui_scale(value)`: save, then try the live change. The window keeps its place and its size in real pixels where the screen allows it; if the new size would leave the screen, it is fitted to the available area. |
| Safety | At 50 % text is small and at 300 % the window may not fit. After a live change a bar at the top asks "Keep this size?" with Keep and Revert, and reverts by itself after 10 s without an answer, as display settings of operating systems do. `pymolish --ui-scale 150` (new option, handled before Qt starts) and Ctrl+0 (back to 150 %) are the ways out if the window became unusable. |
| Shortcuts | Ctrl+= and Ctrl+- change by 10 %, Ctrl+0 resets. They are `QAction` shortcuts listed in the shortcut editor. |
| An exported `QT_SCALE_FACTOR` | Still wins at start, as today; the button then shows that value and a live change replaces it for the running program only. |
| Open dialogs and floating docks | Closed before the change (dialogs) or hidden and shown again with the window (docks). |
| Core text | `display_scale_factor` follows as it does at start (it did in the trial). |
| Default | Stays 150 %. |
| Removed | `theme.SCALES`, the message box, the `ponytail:` note about the restart (when A works on all three systems). |

## Slices

| Slice | What | Check |
| --- | --- | --- |
| 27a | The field, the range 50 to 300, any value; still applied at the next start. `--ui-scale`. | `testing/tests/api/theme.py`: a saved 0.5 and 3.0 reach Qt; out-of-range values are clamped; the option wins over the saved value. |
| 27b | The live change on Linux; Keep or Revert; shortcuts; the fallback. | A GUI test script (real window): 150 to 100 to 225 to 150, the pixel ratio follows, the viewport still draws (`grabFramebuffer` is not blank), the layout is the same; with the symbol name misspelled on purpose the fallback message appears. |
| 27c | The same on Windows and macOS, through the CI bundles and a look by the user. | The first CI run of the GUI test on both; else option B or D there. |

## Skipped

- A separate font-size setting next to the scale.
- A different scale per screen.
- Scaling the viewport's drawing separately from the window (line widths,
  label sizes): they follow the pixel ratio as today.
