# 16 — Background menu and palette caption

[Roadmap](../../PLAN.md) · Request 2026-11-18 · **Planned, nothing built.**

**The palette menu gets a caption that says what it colors. A new toolbar
button next to it sets the background: five plain colors, two blues and a
few gradients. With [15g](15-presets.md) it becomes the one place that
changes the background.**

## What exists

- **Palette menu:** `modules/pmg_qt/action_toolbar.py:88`, an icon-only
  button; its menu is one `QListWidget` with a color strip per palette. No
  caption: the list starts with "PyMOL default". The tooltip of the button
  ("Colors of objects and chains") is the only explanation.
- **Captions in the other menus:** a row of kind 2 in `menu.py` ("Preset:",
  "Look:"), drawn by `fill_menu` (`object_panel.py:159`) as a disabled
  `QWidgetAction` with a `QLabel` named `menu_title`.
- **Background today:** Display > Background has four radio rows (White,
  Light Grey, Grey, Black) next to "Opaque" and "Alpha Checker"
  (`modules/pymol/_gui.py:457`). The looks of step 15 also set white.
- **Settings:** `bg_rgb`; `bg_gradient` with `bg_rgb_top` (default
  `0x00004D`) and `bg_rgb_bottom` (`0x333380`); the command `bg_color`.
  The viewport and the ray tracer both read the gradient
  (`SceneRender.cpp`, `Ray.cpp`). No menu row switches the gradient on.
- **Toolbar width:** at 150 % the bar does not fit the default window with
  the texts of Palette and More, so both are icon-only.

## Decisions

- **The caption is the same widget as in the other menus:** a `menu_title`
  label above the list. No new style.
- **The background button is icon-only** and sits right after the palette.
  Its tooltip is "Background color".
- **Plain menu rows with a swatch icon, not a list widget.** A background is
  one color or two; a 16 px square shows it. Menu rows are reachable by
  keyboard without extra code.
- **No new command and no new setting.** A row runs `bg_color` and sets
  `bg_gradient`; a gradient row sets `bg_rgb_top` and `bg_rgb_bottom`.
- **One place.** The four color rows of Display > Background are deleted;
  "Opaque" and "Alpha Checker" stay there.
- **The values are a table in `action_toolbar.py`**, its only user.

## Options

**Caption of the palette menu** (item 3):

| | Text | Note |
| --- | --- | --- |
| A | "Palette: colors of objects and chains" | Recommended: names the thing and says what it does. |
| B | "Object colors:" | Shortest; does not say that chains follow. |
| C | "Colors of new objects and of chains:" | Most exact, longest. |

**Rows of the background menu** (item 4). Candidates; none is rendered yet,
see 16b.

| Group | Name | Colors (top to bottom for a gradient) | Why |
| --- | --- | --- | --- |
| Plain | Black | `000000` | The default. |
| Plain | Charcoal | `1E1E1E` | Softer than black; close to the dark theme of the window. |
| Plain | Gray | `808080` | ChimeraX's `gray`. |
| Plain | Light gray | `CCCCCC` | The old "Light Grey" row (`grey80`). |
| Plain | White | `FFFFFF` | Figures and slides. |
| Blue | Night blue | `0B1D33` | Dark, colors stay strong. |
| Blue | Slate | `2F3E55` | Blue-gray, mid dark. |
| Gradient | PyMOL blue | `00004D` to `333380` | The defaults of the gradient settings, never reachable from a menu. |
| Gradient | Night | `000000` to `1B2A49` | Black fading to navy. |
| Gradient | Graphite | `3A3A3A` to `101010` | Neutral dark, like the gradient of the old Chimera. |
| Gradient | Steel | `5A6B7D` to `1E2630` | Blue-gray. |
| Gradient | Studio | `FFFFFF` to `C8CDD4` | White to cool light gray, for the white-background palettes. |
| Gradient | Sky | `DCEBFA` to `FFFFFF` | Pale blue to white. |

Thirteen rows is the upper limit. 16b drops what looks bad; a row is cheap
to add later.

## Slices

**16a, palette caption.**
- `action_toolbar.py`: a `menu_title` action before the list action.
- Check: the palette case of `testing/tests/api/action_toolbar.py` finds the
  caption as the first action. Real window at 150 %: the menu is not wider
  than the list.
- Commit: `ui(color): the palette menu says what it colors`.

**16b, try the backgrounds.** No commit except this file.
- Load 1oky (cartoon, surface, ligand), as step 15 did. For every candidate:
  capture the real viewport and ray trace once, with the default object
  colors, with one palette for a dark and one for a white background, and
  with the looks figure and comic after 15g.
- Look for: palette colors that vanish (yellow on white, indigo on dark
  blue), banding in a gradient, fog (`depth_cue`) fading to the wrong color
  on a gradient, outlines after 15g.
- Result: a "What was tried" table here, and the final rows.

**16c, the menu.**
- `action_toolbar.py`: the table, the button, a caption "Background:", the
  rows with swatches (a vertical gradient painted into the 16 px pixmap).
  The row that matches the current settings is marked when the menu opens.
- `icons.py`: `"background": "image"` (the Lucide file is already in
  `data/pmg_qt/icons/lucide/`).
- `_gui.py:461`: the four radio rows go.
- Checks: `testing/tests/api/action_toolbar.py`: every row sets what its
  table entry says; a gradient row switches `bg_gradient` on and a plain row
  switches it off. Real window at 150 %: the bar still fits the default
  window; Tab reaches the button; arrow keys and Enter pick a row.
- Commit: `ui(color): background menu in the toolbar, plain colors and
  gradients`.

## Questions

1. Which caption: A, B or C?
2. Remember the background after a restart, like the palette (`QSettings`,
   applied before pymolrc so a `bg_color` line there still wins)?
   Recommended: yes, three lines in `theme.py`. A session file still brings
   its own background.
3. Remove the four rows from Display > Background (recommended), or keep
   both places?
4. A row "Other..." that opens the color dialog of Qt? Recommended: not now;
   `bg_color` takes any color when typed.

## Skipped

- A background image (`bg_image_filename`): no row.
- A gradient editor, horizontal or radial gradients. The core draws top to
  bottom only.
- A typed `background` command with the names of the table.
- Pairing: picking a palette "for a white background" does not switch the
  background, and the other way round.
- A transparent-background row. "Opaque" stays in Display > Background.

## Sources

- ChimeraX, [set](https://rbvi.ucsf.edu/chimerax/docs/user/commands/set.html)
  and [graphics tools](https://rbvi.ucsf.edu/chimerax/docs/user/tools/graphics.html):
  `set bgColor` with white, gray and black. ChimeraX has no gradient
  background, according to a developer answer on its
  [mailing list](https://mail.cgl.ucsf.edu/mailman/archives/list/chimerax-users@cgl.ucsf.edu/thread/3JTJPPAHD32AK64LIVUJCJZ4PXRHN5HO/).
- UCSF Chimera, [features](https://rbvi.ucsf.edu/chimera/features.html): a
  solid color, a vertical gradient or an image.
- RCSB, [Mol* common actions](https://rcsb.org/docs/3d-viewers/mol*/common-actions):
  preset colors, a custom color, a transparent option.
