# 19 — Movie timeline

[Roadmap](../../PLAN.md) · Request 2026-11-18 · **Planned, nothing built.**
Replaces row 8 of the workspace table in [step 3](03-modern-ui.md)
("Timeline. Not planned").

**A docked panel under the viewport that shows the movie as a storyboard:
the scenes as blocks with their thumbnails, as wide as they last in seconds.
It is a view of the keyframes the core already stores, built from the
existing movie commands. No second movie engine and nothing new in the
session file.**

## What exists

Step 3 said "no timeline feature exists in this code base". That was too
short: there is no Qt timeline, but the core has the parts.

| Part | Where | State |
| --- | --- | --- |
| Movie panel of the core | `layer1/Movie.cpp` (`CMovie::draw`, `click`, `drag`, `release`, from line 1488), `ExecutiveMotionDraw` (`Executive.cpp:682`) | A strip under the viewport once a movie has frames (`movie_panel`): one row for the camera and one per object, a tick per keyframe, dragging with modifier keys, a frame scroll bar. The rows take their names from the old object list, which [step 17](17-legacy-ui.md) removes. |
| Its menus | `menu.camera_motion`, `menu.obj_motion` (`menu.py:112`, `:130`) | Qt menus since 4.5.18: store, store with scene, store with state, clear, interpolate, smooth. |
| Commands | `mset`, `mview`, `mdo`, `frame`, `mplay`, `mstop`; `movie.add_roll`, `add_rock`, `add_nutate`, `add_scenes`, `add_state_loop`, `add_state_sweep`; `movie.produce` | Complete. `mview store, scene=...` ties a keyframe to a scene. |
| Keyframe data | `CViewElem` (`layer1/View.h`): level (keyframe or interpolated), scene name, state, timing, power | Python can read it only through `get_session`, the whole session. One small query is missing. |
| Movie menu | `_gui.py:243` to 385 | Append, Program > Camera Loop / Scene Loop / State Loop with fixed pairs of angle and seconds: 58 command rows. |
| Play controls | States panel in the Objects dock ([step 6](06-states-panel.md)) | First, previous, play, next, last, jump, speed. |
| Scene thumbnails | Scenes dock (4.13.4) | One picture per scene. |
| Export | File > Export Movie (`movieexport.ui`) | Works. |

## The commercial product, and what to do differently

Schrödinger's PyMOL 3 has a Timeline panel: tracks for the camera, scenes,
states, objects and settings; keyframes placed and dragged with the mouse; a
right-click menu with cut, copy, delete and five interpolation modes; clips
for the movie programs; several compositions per session. It is a keyframe
editor in the manner of video software, counted in frames.

Nothing of it is copied. This plan differs on purpose:

| | Theirs | Planned here | Why |
| --- | --- | --- | --- |
| Unit | Frames | Seconds; the frame rate is asked at export | A length in seconds survives a change of frame rate. |
| What you see | Tracks with keyframe marks | Scene blocks with thumbnails: a storyboard | Most molecule movies are a walk through views. A picture per step reads faster than marks on a line. |
| Motion | Clips on tracks | A second lane with three kinds of bar: roll, rock, nutate | The existing `movie.add_*` functions, nothing more. |
| Start | An empty timeline | Templates that fill it in one click: turntable, rock, tour of all scenes, zoom to the ligand and back, play all states | They replace the 58 fixed rows of Movie > Program. |
| Script | Not shown | "Copy as commands": the movie as `mset` and `mview` lines | A movie can be kept in a script and repeated. |
| Several movies per session | Compositions | No | One movie per session, as the core has it. |

## Options

| | Option | Size | Note |
| --- | --- | --- | --- |
| A | **Storyboard,** as above, in the slices below. | A new file `modules/pmg_qt/timeline.py`, one small core query, later a shorter Movie menu and less of `Movie.cpp`. | Recommended. |
| B | Keyframe tracks in Qt: the core's movie panel rebuilt as a panel, one row for the camera and one per object. | About the same as A without the templates. | Shows every movie exactly, also hand-made ones. Less friendly; close to the commercial layout. |
| C | Keep the core's movie panel, add a menu row that shows and hides it, restyle its scroll bar ([18b](18-dialogs-scrollbar.md)). | A few lines. | Works today, but its rows depend on the old object list, so it blocks the end of step 17. |

A movie that was not built from scenes (hand-written `mview` on single
frames, object motions) has no blocks to show. In A the panel then shows the
keyframes as plain marks that can be played and scrubbed but not edited, and
says so in one line. That part is B in small.

## Decisions

- **The core stays the model.** The panel reads the keyframes and writes
  them back with `mset` and `mview`. A typed command, a loaded session and
  the panel always agree, and nothing new is saved in a PSE file.
- **A dock like the others:** `dock_timeline` at the bottom, movable,
  closable, in Display > Panels and in Reset Layout.
- **Shown from three places:** Display > Panels > Timeline, a first row
  "Timeline" in the Movie menu, and the film icon that is already in
  `icons.py`. It opens by itself when a movie gets its first frame
  (question 2).
- **Keyboard:** Space plays, Left and Right move the playhead by a frame,
  Ctrl+Left and Ctrl+Right jump to the previous and next block, Delete
  removes the selected block, Shift+Left and Shift+Right make it shorter
  or longer.
- **Play, speed and the frame number stay in the States panel.** The
  timeline does not repeat them.

## Slices

**19a, read only.**
- One query in the core, exposed as `cmd.get_mview()`: for the camera, a
  list of (frame, scene name, state) for every keyframe. `Movie.cpp` has
  `MovieGetSpecLevel`; the binding goes into `layer4/Cmd.cpp`.
- `timeline.py`: the dock, a painted strip (blocks, thumbnails from the
  Scenes dock, a ruler in seconds), the playhead. A click or a drag on the
  ruler runs `cmd.frame`. The plain marks for a movie without scenes.
- Menu rows in Display > Panels and Movie.
- Checks: a test for `get_mview` after `movie.add_scenes` (frames and scene
  names) and after an empty `mset` (no keyframes); a test of the dock's block list for
  the same movie. Real window: a three-scene movie, scrubbing, a session
  saved and loaded.
- Commit: `ui(movie): timeline panel, read only`.

**19b, editing.**
- "+" adds the current view as a scene and as a block at the end. Dragging a
  block changes the order; dragging its edge changes its length; Delete
  removes it. Each edit rebuilds the movie from the block list with `mset`
  and `mview store, scene=...` and reinterpolates.
- Undo: question 3.
- Checks: tests for add, move, resize and delete against `get_mview`. Real
  window, mouse and keyboard.
- Commit: `ui(movie): add, move, stretch and delete scenes on the timeline`.

**19c, motion lane, templates, script.**
- The second lane; the five templates; "Copy as commands"; an Export button
  that opens the existing dialog.
- `_gui.py`: Movie > Program shrinks to what the templates do not cover.
  The list of removed rows goes to the user before the commit, as step 14
  did with its audit table.
- Commit: `ui(movie): motion lane and templates; shorter Movie menu`.

**19d, the core's movie panel goes.**
- `Movie.cpp`: `CMovie::draw`, `click`, `drag`, `release`, `reshape`;
  `ExecutiveMotionDraw`, `ExecutiveMotionMenuActivate`; `menu.movie_panel`;
  the settings `movie_panel` and `movie_panel_row_height` (positional
  placeholders, as in step 17). This unblocks 17d.
- Title `remove: movie panel of the core`; suite, sanitizer job, PSE round
  trip, lines before and after.

## Questions

1. A, B or C?
2. Open the timeline by itself when a movie gets frames (recommended), or
   only from the menu?
3. Undo for timeline edits: none in 19b (recommended; the block list can be
   rebuilt from the scenes, and an empty `mset` starts over), or wire it into Undo
   and Redo of the toolbar?
4. Object motions (a ligand that moves by itself, `mview` with `object=`):
   leave them to the commands and show them as plain marks (recommended),
   or a lane per object in a later slice?

## Skipped

- Compositions, sub-tracks for settings, moving objects with a gizmo.
- Interpolation modes per keyframe in the panel. `mview` has `power`,
  `bias` and `linear`; they stay typed.
- Sound, titles and text overlays.
- A new encoder or export format: `movie.produce` as it is.
- Zooming the strip. It fits the panel's width; add a zoom when a movie is
  too long to read.

## Sources

- Schrödinger, [Timeline panel](https://learn.schrodinger.com/public/pymol/2023-4/Content/pymol/Features/timeline.htm)
  and [Scenes panel](https://learn.schrodinger.com/public/pymol/2023-4/Content/pymol/Features/scenes.htm):
  tracks, keyframes, clips, compositions, the interpolation modes.
- PyMOLWiki, [Movie panel](https://www.pymolwiki.org/Movie_panel) and
  [Mview](https://wiki.pymol.org/index.php/Mview): the panel of the core and
  the command behind it.
