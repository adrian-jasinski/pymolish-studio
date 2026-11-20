# 20 — Look of the action toolbar, own palettes

[Roadmap](../../PLAN.md) · Request 2026-11-18 · **Done 2026-11-18 in 4.19.0.**
Where the request said "think about", the options are listed with the one
that was built; each can still be changed in one or two lines.

Replaced in part on 2026-11-20: "Background" becomes "Bg" with a new icon ([26a](26-toolbar-buttons.md)), and the names on the right side of the bar may go ([26d](26-toolbar-buttons.md), question 26).

**Palette and Background carry their names, Zoom, Orient and Rock are
icons only. The icons are larger and drawn with heavier lines. What is
chosen is blue. The palette menu defines palettes of the user, and the
background menu says whether ray tracing uses the background.**

## What was built

| Request | Built | Where |
| --- | --- | --- |
| Text on Palette and Background | Both show their name next to the icon. | `action_toolbar.py` |
| No text on Orient and Zoom | Zoom, Orient and Rock show only the icon; the name is the tooltip and the accessible name. Zoom keeps its arrow for the menu. | `action_toolbar.py` |
| A camera for Scenes | The Lucide icon `camera` (release 0.460.0, ISC, as the other icons). The example on flaticon.com was not used: its license needs an attribution line, and one icon family keeps the bar even. | `data/pmg_qt/icons/lucide/camera.svg`, `icons.py` |
| Blue for what is chosen | The text of the selection mode ("Residues") is blue. A checked button (Rock) and the button under the pointer turn blue, text and icon. In the bar's menus the row under the pointer has the blue of the A button, `#1e4fb8`, with white text, and the chosen row is written in blue. | `pymol.sty`, `icons.menu_icon(accent=)` |
| Ray tracing with the background | Background menu, row "Ray trace with this background". It sets `opaque_background`, the setting Draw/Ray > "transparent background" and Display > Background > Opaque use, and puts `ray_opaque_background` back to -1 so that the three agree. "Remember after restart" keeps it too. | `action_toolbar.py` |
| Own palettes | Palette menu: "New palette...", "Edit palette...", "Delete palette". A dialog with a name and a list of colors: add, change, remove, move up and down. Stored in `QSettings` (`colors/user_palettes`), listed as "Name (yours)", applied like any palette. | `palette_dialog.py`, `palettes.define`, `palettes.undefine`, `theme.py` |

## Options, and what was chosen

**Icons** (the request: bigger, or heavier lines):

| | Option | Note |
| --- | --- | --- |
| A | 20 px, line width 2 of 24. **Built.** | The lines are 1.7 px instead of 1 px: both bigger and heavier. Menus keep 16 px and 1.5. |
| B | 18 px, line width 2 | A little lighter; 28 px narrower in total. |
| C | 20 px, line width 2.5 | Heavier still; fine details of some drawings (aperture, palette) start to close up. |

`ICON` and `STROKE` at the top of `action_toolbar.py`.

**Font:**

| | Option | Note |
| --- | --- | --- |
| A | Weight 500. **Built.** | On this machine the interface font has only regular and bold, so 500 is drawn as regular. With heavier icons the bar reads calmer than with bold text, and the blue word stands out. |
| B | Weight 600, as before | Bold on this machine. 20 to 30 px wider in total. |
| C | Another typeface for the bar | Not built: one typeface for the whole window, as `AGENTS.md` asks. |

`font-weight` of `#toolbar_actions QToolButton` in `pymol.sty`.

**The blue:** the A button's `#1e4fb8` is too dark as text on the dark
window (contrast about 2:1). So it is used where it is a filled area with
white text on it, as on the A button: the row under the pointer. Blue
*text* uses the link color of the theme (`palette(link)`), a lighter blue of
the same family on the dark theme.

**Width.** The bar must fit the default window, 940 px at 150 %. With the
new texts and 20 px icons it was 973 px. Spacing between buttons went from
2 to 1 px and their side padding from 3 to 2 px: 929 px, nothing in the
overflow.

## Second round, 4.19.1

Request of the same day: the text was too small; bigger and bold, in
another simple font; more room between the buttons; the zoom button for what
is visible.

- **Font:** bold (600), 10 pt instead of 9, and a family list in `pymol.sty`:
  Inter, Segoe UI, Helvetica Neue, Ubuntu, Noto Sans, Arial. The first one
  the system has is used: Ubuntu on the development machine, Segoe UI on
  Windows, Helvetica Neue on macOS. No font file is shipped. Option A of the
  font table above (regular weight) is withdrawn.
- **Room:** 8 px between buttons (was 1) and 4 px side padding (was 2).
- **Width:** the bar is now 1096 px at 150 %, more than the old default
  window. The window therefore opens as wide as the bar needs (1104 px);
  the extra width goes to the viewport. A saved layout that is narrower
  keeps its size and shows the overflow arrow until it is widened.
- **Zoom:** a click zooms on `visible`, the atoms that are shown in objects
  that are switched on; with nothing shown, on everything. The menu has
  "Visible" and "Everything". Orient is unchanged: it still acts on
  everything (question 3).

Checked in the real window with a fresh layout: no overflow, and with a
hidden object 300 A away the camera distance after the click is 364 instead
of 1248.

## Checks

- `testing/tests/api/action_toolbar.py`: which buttons are icon-only, icon
  size, a different pixmap for the hovered state, the camera, the ray row,
  `test_user_palette` (store, list, apply, rename, delete, the rules of a
  name, the dialog).
- Real window on WSLg at 150 %, dark theme: the bar with Rock checked, the
  selection menu with a hovered and a chosen row, the palette and background
  menus, the palette dialog. Width measured.
- Not checked: the light theme, 100 and 200 %, other platforms.

## Questions

1. Blue hover in every menu of the program (right-click menus, the menu
   bar), not only in the menus of the toolbar? One rule in `pymol.sty`.
   Recommended: yes, so that there is one style.
   **Answer 2026-11-20: yes. Done in 4.23.0:** the rule is `QMenu::item:selected`, with the menu bar; a checked row is written in blue everywhere.
2. Icons: 20 px with line width 2 as built, or B or C?
3. Should Orient also act only on what is visible, like Zoom now?
   Recommended: yes. **Answer 2026-11-20: yes. Done in 4.23.0**
   (`_orient_visible`; the command `orient` is unchanged).

## Skipped

- A palette made from the colors of the loaded objects, import and export
  of palettes, a `palette_define` command (the function `palettes.define`
  can be called from a script or pymolrc).
- A note of the intended background for a palette of the user.
- A contrast check for the colors of a palette of the user.
