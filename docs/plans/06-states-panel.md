# 6 — States panel

[Roadmap](../../PLAN.md) · Request 2026-11-13 with a reference picture

**One small panel to move through the states of a trajectory or the frames of a
movie: first, previous, play/stop, next, last, jump to a number, and the
playback speed.** It sits in the Objects dock above the toggle bar and shows
only while there is more than one state or frame.

## What exists

- Commands for everything: `cmd.rewind`, `backward`, `mtoggle`, `forward`,
  `ending`, `frame`, `get_frame`, `count_frames`, `get_movie_playing`, and the
  `movie_fps` setting. Without a movie (`mset`) a frame is a state, so the same
  commands drive both. No C++ change and no new command.
- Two half-solutions this panel replaces: the "State 1/2500" label above the
  toggle bar, and the Previous/Stop/Play/Next text buttons that appear in the
  action toolbar (first and last frame are in its More menu).
- Lucide line icons tinted with the text color (`icons.py`); play, stop, rewind
  and skip-forward are already in the set.

## Layout

```
 States                              [30 fps v]
 [ 1/2500      ^v] [|<] [<<] [ > ] [>>] [>|]
 [mouse mode            ] [Wizard] [SEQ] [>_]      <- toggle bar, unchanged
```

| Control | Widget | Does |
| --- | --- | --- |
| Title | `QLabel` | "States", or "Frames" while a movie is defined |
| Counter | `QSpinBox` 1..n with suffix `/n` | shows the position; type a number and Enter, arrows or the wheel to jump (`cmd.frame`) |
| First, Last | `QToolButton` | `cmd.rewind`, `cmd.ending` |
| Previous, Next | `QToolButton`, auto-repeat while held | `cmd.backward`, `cmd.forward` |
| Play / Stop | `QToolButton`, icon follows the playing state | `cmd.mtoggle` |
| Speed | `QToolButton` with a menu: 1, 5, 10, 15, 30, 60 fps | sets `movie_fps`; the button shows the current value, also one set by command |

## Decisions

- **In the Objects dock, not a new dock.** Six controls do not need their own
  title bar, and the picture has them above the toggle bar.
- **Replace, do not add.** The state label and the toolbar's four movie buttons
  plus First/Last frame in More are deleted; "Clear movie" stays in More.
- **Polled.** The panel is refreshed from the window's existing 0.5 s timer and
  from its own 0.1 s timer only while a movie plays, so the counter runs
  smoothly. `ponytail:` ceiling is up to 0.5 s delay after a state change made
  by command; upgrade path is a change notification from the C++ executive
  (same as the object list).
- **Native widgets, keyboard reachable.** Every button takes Tab focus and
  Space; the counter is a spin box. Icons are rebuilt on a palette change so
  they follow Display > Dark Theme.
- **Two new data files:** `skip-back.svg` and `fast-forward.svg` from the same
  Lucide release (0.460.0, ISC) as the rest of the set.

## Skipped, and when to add

- A scrub slider: add when stepping and typing a number prove too slow on long
  trajectories.
- A close button (the picture has one): the panel hides itself with a single
  state; add a Display > Panels entry if someone wants it gone with many.
- Per-object state controls and loop/sweep options: Movie menu has them.

## Checks

`testing/tests/api/object_panel.py`: hidden with one state, shown with several;
counter range and suffix; first/next/last and the counter change the frame;
play/stop follows `get_movie_playing`; the speed menu sets `movie_fps` and the
button follows the setting. Real GUI on WSLg with a multi-state object.

## Status

Planned 2026-11-13.
