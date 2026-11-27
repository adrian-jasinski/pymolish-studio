# How the pictures and clips were made

[Docs home](../README.md) · Checked with version 4.90.0.

Every picture of the window on these pages is the running program. This
page records how each one was made, so that a changed feature gets a new
picture of its own and the rest stays.

## What they were made with

| | |
| --- | --- |
| Program | pymolish-studio 4.90.0, source revision `c7967883`, PySide6 and Qt 6.12.0 |
| Date | 2026-11-26 |
| System | Ubuntu 24.04 under WSL 2 on Windows (WSLg), graphics through Mesa d3d12 |
| Theme and size | dark theme, UI scale 150 % (the values the program starts with) |
| Window | 1280 x 800 at 150 %, which is 1920 x 1200 pixels; 1470 x 800 for the movie clip, because the Timeline needs the width |
| Profile | none of the user's: started with `-k` (no pymolrc, no plugins) and `XDG_CONFIG_HOME` on an empty folder |
| Structures | `1oky`, `1ake`, `4ake` and `1zin`, fetched from the RCSB Protein Data Bank as mmCIF; the fragments `ala`, `gly` and `trp` of the program |
| Other programs | MAFFT 7.505 for the alignment, ffmpeg 6.1.1 for the clips, Pillow for the sheets of rendered pictures and the posters |

Nothing was tried on Windows or macOS: a picture shows the window on the
system above and does not say how it behaves elsewhere.

## The method

The scripts are in [capture/](capture/). Each one starts the real window,
does the steps with the mouse events of Qt (`QTest`: clicks on the real
buttons, menus and cells), and saves what the widgets draw.

```
export PYMOLISH_CAPTURE=/an/empty/folder      # gets work/ and out/
XDG_CONFIG_HOME=$PYMOLISH_CAPTURE/cfg pymolish -qk $PWD/docs/media/capture/a_appearance.py
pymolish -ckq $PWD/docs/media/capture/render.py
docs/media/capture/encode.sh $PYMOLISH_CAPTURE/out/clip-appearance appearance.mp4
```

Run them from the top folder of the repository. A scenario takes the
keyboard and the screen for up to a minute.

What is not a plain screenshot, and why:

- **Menus and separate windows are laid on the window picture.** WSLg does
  not let a program grab the screen (the picture is black), so the window
  and each open menu, dialog or floating panel are grabbed as widgets and
  put together at the place Qt shows them. A menu that reaches past the
  window stands on a plain dark ground.
- **The alignment window is placed by the script** under the viewport in
  `sequence-fit.png` and in the sequence clip. It is a window of its own,
  and where it stands on a screen is the user's choice.
- **The pointer and the caption bar of the clips are drawn on the frames.**
  A widget grab has no pointer. The pointer is drawn where the click or
  the hover of that step went; the bar at the bottom names the step. They
  cover the lowest 30 points of the window.
- **Clips show real time at a low frame rate.** One grab of the window
  takes 0.12 to 0.27 s, so the clips have 3.7 to 6.7 pictures per second
  (stored at 12 per second by repeating pictures). Nothing was cut or sped
  up. They are not a measure of how fast the program is.
- **Rendered pictures are marked as such** in their captions: they are
  ray-traced output of `render.py`, not pictures of the window.

## Pictures of the window

| File | Used in | Script | Steps | Size |
| --- | --- | --- | --- | --- |
| `img/window.png` | README, docs home, Getting started | `a_appearance.py` | The window after File > Get PDB... > 1oky > Download | 1920 x 1200, 358 KB |
| `img/appearance-presets.png` | Appearance | `a_appearance.py` | Presets, pointer on surface; cut to the right part of the window | 1080 x 870, 132 KB |
| `img/appearance-look.png` | docs home | `a_appearance.py` | The viewport after Presets > surface > glossy, in the view of render.py | 922 x 753, 259 KB |
| `img/saving-draw.png` | Saving | `a_appearance.py` | The panel of the Draw button alone | 447 x 309, 32 KB |
| `img/ligand-next.png` | Ligands | `b_ligand.py` | The viewport after Display > Zoom > Next Ligand with Contacts | 1012 x 813, 250 KB |
| `img/ligand-2d-pocket.png` | Ligands, docs home | `b_ligand.py` | Then the 2D button, a click on GLU 166 in the picture, Show in 3D | 1920 x 1200, 530 KB |
| `img/sequence-tab.png` | Sequences | `c_sequence.py` | The Sequence tab; a drag over a range of residues of 1ake | 1920 x 1200, 455 KB |
| `img/sequence-alignment.png` | Sequences, docs home | `c_sequence.py` | The alignment window alone, after Add chains… (chain A), Align sequences, Percent identity, Fit structures | 1860 x 593, 149 KB |
| `img/sequence-fit.png` | Sequences | `c_sequence.py` | The window with the alignment window laid under the viewport, after the fit | 1920 x 1200, 366 KB |
| `img/property-table.png` | Property table | `d_table.py` | The Table window alone: load_table scores.csv, a click on the header score, a click on the third star of trp | 1140 x 450, 29 KB |
| `img/objects-panel.png` | Structures | `d_table.py` | group small, ala gly; disable gly; a selection; a click on A of the group. Cut to the panel | 545 x 840, 63 KB |
| `img/scenes-panel.png` | Scenes and movies | `e_movie.py` | Scenes > Add; ligand_next; Add. Cut to the left part | 1650 x 840, 316 KB |
| `img/timeline.png` | Scenes and movies | `e_movie.py` | After the clip: Tour > Every scene, Add > Turn 360°, the turn dragged to 4 s | 2205 x 1200, 567 KB |
| `img/chat-setup.png` | Assistant | `f_chat.py` | The Chat tab, no key in the environment, no sign-in. Cut to the tab | 1920 x 282, 36 KB |

Two pictures are a little over the 500 KB aimed for (`ligand-2d-pocket.png`
and `timeline.png`): scaling them down made the files larger and the text
worse, so they stay at full size.

## Rendered pictures

Made by `capture/render.py` without a window. Each look is set by the call
its menu row makes (`preset.from_menu`, `preset.transparency`,
`preset.look`, `stage`). Before it: waters, sulfates and glycerol removed,
`color skyblue, polymer and elem C`, white opaque background, and one fixed
view in which the ligand shows in the opening of its pocket. 640 x 480 per
picture, `ray=1`.

| File | Used in | Size |
| --- | --- | --- |
| `img/appearance-surface-looks.jpg` | Appearance | 1280 x 960, 128 KB |
| `img/appearance-transparency.jpg` | Appearance | 1280 x 960, 126 KB |
| `img/appearance-floor.jpg` | Appearance | 1280 x 480, 111 KB |

Older pictures that are still used: `img/viewport-outline.jpg` (viewport
pictures of version 4.87.0, in Appearance) and the eleven palette strips
`img/palette-*.png`; the colors of the strips were compared with the
palettes of 4.90.0 and are the same (`palette-neon.png` came with 4.95.0).

## Clips

MP4 (H.264, no sound), opened from a poster picture in the guide; under
each poster is a link to the file. The poster is one frame of the clip
with a play mark drawn on it.

| File | Used in | Script | What it shows | Length, size |
| --- | --- | --- | --- | --- |
| `appearance.mp4`, poster `img/demo-appearance.jpg` | Appearance | `a_appearance.py` | Presets > surface > glossy; transparency > surface > 50%; light > studio; Undo twice | 25 s, 1280 x 800, 401 KB; poster 103 KB |
| `ligand.mp4`, poster `img/demo-ligand.jpg` | Ligands | `b_ligand.py` | Display > Zoom > Next Ligand with Contacts; the 2D button; a click on GLU 166; Show in 3D | 19 s, 1280 x 800, 410 KB; poster 179 KB |
| `sequence.mp4`, poster `img/demo-sequence.jpg` | Sequences | `c_sequence.py` | The Sequence alignment button; Add chains… with `chain A`; Align sequences; Percent identity; a drag over cells; Fit structures; Undo | 31 s, 1280 x 800, 545 KB; poster 175 KB |
| `movie.mp4`, poster `img/demo-movie.jpg` | Scenes and movies | `e_movie.py` | A click on each of two scenes; the Movie button; Tour > Every scene; Add > Turn 360°; the right end of the turn dragged from 8 to 4 s; Play; the Export menu | 31 s, 1600 x 860, 996 KB; poster 122 KB |

Checked: each file decodes from start to end with ffmpeg, and four frames
of each were looked at. Not checked: how the page of the repository on
GitHub plays an MP4 from such a link; that needs the branch to be pushed.
If it only offers the file, the link under the poster is the way to it.

There is no clip of the Chat tab. It waits for a recorded conversation
with a real provider; the picture `img/chat-setup.png` shows the set-up
row only.

## Found while taking the pictures

- After File > Reinitialize (or `reinitialize`) with a floor on, the next
  `stage` first takes the old floor back and leaves the view 2 Å deep:
  the picture is empty. `stage off` before it avoids that; `render.py`
  does so.
- File > Open Recent lists the files of the user also with `-k` and an
  empty configuration folder, so that menu is in no picture.
- The dialog of File > Export Image As > PNG... still says "New in PyMOL
  2.0 ... the Draw panel in the upper right".

## When something changes

Change the script of the picture, run it, copy the new file over the old
one, and update its row here. Leave the other pictures alone.
