# 19 — Movie timeline

[Roadmap](../../PLAN.md) · Request 2026-11-18 · **Built 2026-11-18 in 4.18.0:**
the shot list (D), the strip (A), record (E), tours (F), effects (G), easing
(H) and export with an estimate (I). What is built, what differs from the
plan and what is still open is under "Result, 4.18.0".
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

## More ways to edit a movie (second request, 2026-11-18)

Options A to C are three ways to show keyframes. These six are other ways
to make and change a movie; each rests on a command the core already has,
named in the last column. They combine: D is the editor, A becomes its
picture, E and F fill it, G and H refine it, I ends it.

| | Option | What the user does | What it is built on |
| --- | --- | --- | --- |
| D | **Shot list.** The movie as a table, one row per step: what (show a scene, turn, rock, nutate, zoom to a selection, play the states, hold), how long in seconds, how it starts (smooth or cut). | Type a duration, reorder rows by dragging or with Alt+Up and Alt+Down, copy and paste rows, delete a row. Every cell is reachable by keyboard. | `movie.add_scenes`, `add_roll`, `add_rock`, `add_nutate`, `add_state_loop`, `add_blank`, `mview store`. The table is rebuilt into the movie after each edit. |
| E | **Record.** A Record button in the panel. | Move the molecule and press K, or click "Add view", at each pose worth keeping; the panel appends a shot of two seconds per pose. "Auto" adds a pose whenever the view has rested for half a second. Stop when done. | `mview store` on appended frames, `mview interpolate` and `smooth`. |
| F | **Guided tour.** A movie from a list of places. | Pick selections or ligand sites from a list (every ligand, every chain, the current selections), choose "fly to, hold, orbit", press Create. | `orient` or `zoom` on each selection, `mview store`, `movie.add_roll` over the hold. |
| G | **Effects lane.** Changes of the look over time, under a shot: fade a surface in or out, reveal the ligand, change a color, switch a label on. | Drop an effect on a shot and set what it acts on. | `mdo`: one command per frame that sets `transparency`, `cartoon_transparency` or shows a representation. Scenes alone can only cut between looks. `mdo` runs at playback, so long fades cost frame rate; to be measured before it ships. |
| H | **Easing per transition.** | Pick linear, ease in and out, or hold then jump, on the line between two shots. | The arguments `power`, `bias` and `linear` of `mview`, which no menu offers today. |
| I | **Export panel with an estimate.** | Choose a preset (GIF for a slide, MP4 720p, 1080p or 4K, PNG frames), draft or ray traced, loop or once. Before rendering it shows the number of frames, the time and the file size it expects. | `movie.produce` and `mpng`. The estimate times one frame and multiplies. |

Compared with the commercial timeline: D, E, F and I do not exist there in
this form. Its strength is free keyframes on many tracks, which is option
B.

**Recommended set and order:** D first (the cheapest editor, exact, and it
works without a mouse), then A as the picture of the same list, then E and
F, which only append rows to it, then I. G and H last: G needs a
measurement and H is three numbers per transition.

Slices in that order; they replace 19b and 19c below when the user picks
this set:

| Slice | Content |
| --- | --- |
| 19a | As below: `cmd.get_mview()`, the dock, a read-only strip with the playhead, the menu rows. |
| 19b | The shot list (D): the table, add, edit, reorder and delete, rebuild of the movie after each edit. Test: every row type against `get_mview` and `count_frames`. |
| 19c | The storyboard strip (A) over the same list: thumbnails, drag to reorder and to stretch. |
| 19d | Record (E) and the guided tour (F). Test: three recorded poses give three keyframes at the expected frames; a tour of two selections gives the expected length. |
| 19e | The export panel (I). Test: the estimate against a rendered 30-frame movie, within a factor of two. |
| 19f | Easing (H), then the effects lane (G) after a frame-rate measurement with `testing/bench_gui.py`. |
| 19g | The shorter Movie menu, and the core's movie panel goes (the old 19c and 19d). |

One limit holds for all of them: the shot list is derived from the
keyframes of the core, so a movie written by hand with commands the list
does not know (object motions, `mdo` scripts of the user) is shown and
played, but opens for editing only after "Start over from the scenes".

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

## Result, 4.18.0

Request: "add movie timeline and other movie options". No option was
named, so the recommended set was built, all of D to I with A as the
picture of the list.

| Part | Where | What it does |
| --- | --- | --- |
| Shot builder | `modules/pymol/shots.py` | `build(shots)` clears the movie and makes it again from the list with `mset`, `mview store` and `mdo`. Eight kinds: scene, view, zoom, turn, rock, nutate, states, hold. `tour`, `estimate`, `describe`. |
| Panel | `modules/pmg_qt/timeline.py`, dock `dock_timeline` | Buttons Add, Add view, Record, Tour, Up, Down, Delete, Clear, Play, Export; the strip; the table (Shot, Target, Seconds, Start, Effect). |
| Window | `pymol_qt_gui.py`, `_gui.py` | Movie > Timeline, Display > Panels > Timeline, polled from the window's timer. |

**Where it differs from the plan:**

- **The shot list is the model, not the keyframes of the core.** A turn or
  a rock is several keyframes; reading them back as "one turn" would be a
  guess. So the list lives in the panel and the movie is rebuilt from it
  after every edit. Consequence: the list is gone after a restart or a
  session load. The movie itself is in the session as always, plays and
  scrubs in the panel, and "Add" starts a new list. Storing the list in the
  session file would change what a PSE file contains: question 5.
- **A movie made elsewhere is never replaced silently:** the first shot
  added to it asks.
- **No new core call.** `cmd.get_mview()` (slice 19a) was only needed to
  draw keyframe marks for movies made elsewhere; the strip shows such a
  movie as one block.
- **The strip selects and scrubs; it does not drag.** Shots are reordered
  with Up and Down (Alt+Up, Alt+Down) and stretched by typing seconds.
- **Easing is the column "Start":** smooth (slow in and out), linear, or
  cut. It is `power` of `mview`.
- **Effects are four fades,** of the surface or the cartoon, in or out,
  over the whole shot. They set a global setting from `mdo`.
- **Templates are the Tour menu and the Add menu**, not a separate list.
- **One timeline at a time:** opening the panel switches the core's
  keyframe strip (`movie_panel`) off, closing it switches it on again.
- **The Movie menu is unchanged** and the core's movie panel is not
  removed: both wait for an answer (questions 6 and 7).

**Measured in the real window** (WSLg, 150 %, software renderer, 1oky):

- A movie of five shots, 840 frames: the strip with two scene thumbnails,
  the playhead after a click, the table. One capture looked at.
- Cost of a fade: stepping through frames with a surface shown gave 19.9
  frames per second in a shot without an effect and 22.2 in the shot with
  "fade in surface". No measurable cost on this structure; a much larger
  surface was not tried.
- Estimate for 1280 x 720, drawn: 840 frames, about 97 seconds, about
  241 MB of PNG frames. No movie file was rendered in this check.

Checks: `testing/tests/api/shots.py` (turn, scenes with flight and cut,
rock, nutate, states, fade, clearing, tours, script, estimate) and
`testing/tests/api/timeline.py` (add, edit, move, delete, seek, record, a
movie replaced from outside, opening by itself).

**Not done:**

- Rendering through the Export presets was not run; they call the existing
  `movie.produce`, which needs ffmpeg or ImageMagick on the machine.
- Dragging on the strip, undo, object motions, keyframe marks for movies
  made elsewhere.
- In the default window the dock shares the bottom edge with the command
  area, and its table shows two rows; it is meant to be made taller or
  floated.

## Questions

5. Keep the shot list after a restart? It would be one more entry in the
   session file (PSE); older versions would ignore it. Recommended: yes,
   but it changes file output, so it needs your word.
6. Shorten the Movie menu? Program > Camera Loop, Scene Loop and State
   Loop (58 rows) do what Add and Tour do now. Recommended: remove them.
7. Remove the keyframe strip the core draws under the viewport (19g)? It
   is the only editor for object motions and hand-made keyframes.
   Recommended: keep it until someone misses nothing in the panel.
0. Which of D to I should be built, and is the recommended order right?
   Recommended: D, A, E, F, I, then H and G.
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
