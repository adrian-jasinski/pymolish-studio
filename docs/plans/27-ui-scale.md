# 27 — UI scale: any value from 50 % to 300 %, without a restart

[Roadmap](../../PLAN.md) · Request 2026-11-20 · **27a and 27b done
2026-11-20 in 4.31.0** (the field, the range, the live change on Linux, the
fallback). 27c, Windows and macOS, is open.

**2026-11-23, draft 8: a change from 150 to 120 reportedly freezes the
window. 27d below is the first repair in the roadmap, before further live
scale work.** Interpreted provisionally as 150 % → 120 % in the toolbar;
question 53 distinguishes it from resizing the window. Planned at 4.43.0;
source inspected, no freeze reproduced or root cause established in this run.

As built, and where it differs from the plan below:

- `theme.set_scale_live` (35 lines) finds the Qt library through
  `QLibraryInfo`, so it also works inside a bundle. It returns false when
  the symbol is missing or the pixel ratio did not follow; the toolbar then
  shows the old "next start" message.
- "Keep this size?" is asked only below 75 % and above 200 %, not after
  every change: a step from 150 to 140 does not need a question. The way
  back asks nothing.
- The GL widget read the pixel ratio from a window handle that the change
  destroys; in one of two runs the molecule was then drawn at the old
  ratio. It now compares the ratio when it is resized and painted. Three
  runs in the real window after that: 150, 100, 225 (kept), 50 (reverted),
  150, with the viewport's pixel size right each time and the table window
  following.
- Not built: the shortcuts Ctrl+=, Ctrl+- and Ctrl+0, and the option
  `--ui-scale`. The revert after ten seconds and an exported
  `QT_SCALE_FACTOR` are the ways out; ask if the shortcuts are wanted.
- 27c: the test `test_scale_range_and_live` prints "set_scale_live does not
  work on ..." where the change fails and passes there, so the first CI run
  on Windows and macOS says which way those systems go.

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

## 27d — investigate and fix the freeze

Start with every caller of `theme.set_scale_live`, especially
`action_toolbar._set_scale`, `_apply_scale`, `_confirm_scale`, the GL
widget's resize/pixel-ratio handling and floating-panel placement callbacks.
The current code hides visible widgets, destroys native windows and calls
the private `QHighDpiScaling::setGlobalFactor` through `ctypes`. Reentrancy,
layout callbacks and lost native/GL handles are hypotheses to inspect,
not diagnosed causes.

- Capture a stack trace and event-loop heartbeat in a disposable process
  while applying 150 → 120 → 150 repeatedly. Repeat with the 2D panel, table,
  Scenes and a floating dialog open, then with ordinary window resizing.
  Record OS/display backend, Qt version and monitor scale. No user session
  is thrown away to reproduce it.
- Fix the demonstrated cause once in the shared path; avoid nested changes
  while a scale change is in progress. Verify the GL context, viewport
  repaint, input, dock visibility and icon sharpness after each change.
- If the private path cannot be made reliable on a configuration, use the
  already accepted “applies at next start” fallback **before** entering the
  unsafe path. Never automatically restart and lose undo/plugin/Python
  state. A GUI timer cannot recover an event loop already blocked.
- A saved scale must stay valid and startup must remain usable after an
  interrupted attempt. Preserve the exported `QT_SCALE_FACTOR` rule and
  the existing Keep/Revert behavior where a live change succeeds.
- Extend `testing/tests/api/theme.py` with a subprocess GUI regression and
  external timeout/heartbeat, not only an assertion that the scale value
  changed. Log an unsupported live path separately; a test that accepts a
  fallback is not evidence that live scaling works.

27c then checks the repair/fallback on Windows and macOS; also record Linux
X11/Wayland coverage where available. Real GUI drag/repaint checks remain
necessary. A bug repair gets a `Y` version; a deliberate change to the scale
interaction needs its own documented `X` slice. No new dependency, forced
restart or speculative replacement of the complete scale system.

## The trial (2026-11-20, Linux, X11 under WSLg, PySide6 6.12)

These historical successful trials do not cover the new freeze report.

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

## Options (question 28, answered 2026-11-20: A, with D as its fallback)

That decision still requests live scaling where reliable. 27d supersedes any
assumption that an available private Qt symbol alone proves it safe.

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
