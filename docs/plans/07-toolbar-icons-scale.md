# 7 — Toolbar icons and UI scale

[Roadmap](../../PLAN.md) · Request 2026-11-13

**Every button of the action toolbar gets a line icon, Undo and Redo shrink to
the icon alone, the interface starts at 150 %, and the scale is picked from a
button in the toolbar.**

## What exists

- The action toolbar (`modules/pmg_qt/action_toolbar.py`): text-only buttons.
- Lucide line icons tinted with the text color (`icons.py`), used by menus and
  the states panel. Icons for select, zoom, orient, preset, scene and ray are
  already in the set.
- One scale knob (`theme.py`): `QSettings` `ui/scale`, handed to Qt as
  `QT_SCALE_FACTOR` before the application starts. Default 100 %, steps 100 to
  300 %, picked in Display > UI Scale, plus a one-time question on wide
  unscaled screens that offers 150 %.

## Layout

```
 [i Residues v] | [undo] [redo] | [i Zoom v] [i Orient] [i Rock] [i Presets v]
                      ... [i Builder] [i Scenes] [i Draw/Ray v] [i 150% v] [... v]
```

| Button | Icon (Lucide) | Change |
| --- | --- | --- |
| Selection mode (Residues, ...) | mouse-pointer-click | icon added |
| Undo, Redo | undo-2, redo-2 (new files) | icon only; the name shows as tooltip on hover and stays the accessible name |
| Zoom, Orient, Presets | zoom-in, compass, sliders-horizontal | icon added |
| Rock | rotate-3d (new file) | icon added, still shows its on/off state |
| Builder, Scenes, Draw/Ray | hammer (new file), image, aperture | icon added, so the bar is one style |
| More | ellipsis (new file) | icon only, tooltip "More view actions" |
| Scale, new | scaling (new file) | shows the running scale; menu 100, 120, 150, 180, 200 % |

## Decisions

- **All buttons get an icon, not only the five named.** A bar with icons on the
  left and bare text on the right reads as two styles.
- **The bar must fit the default window (940 px wide) at 150 %.** With text
  on every button it needed 1002 px and More fell into Qt's overflow arrow.
  More is therefore icon-only and the button padding went from 5 to 3 px:
  907 px.
- **Icons are tinted and rebuilt on a palette change**, as in the states panel,
  so they follow Display > Dark Theme.
- **150 % is the default scale** (`ui/scale` unset). A saved value and an
  exported `QT_SCALE_FACTOR` still win. The one-time 150 % question is deleted:
  the default now answers it.
- **Replace, do not add.** The toolbar button replaces Display > UI Scale; one
  list of steps: 100, 120, 150, 180, 200 %. A saved older step (125, 175, 250,
  300 %) keeps working and shows on the button, it is just not in the menu.
- **Still applies on the next start.** Qt reads the factor once, at startup.
  `ponytail:` ceiling is a restart per change; upgrade path is a restart that
  saves and reloads the session, when changing scale proves frequent.
- **Six new data files** from the same Lucide release (0.460.0, ISC) as the
  rest of the set.

## Risk

The factor multiplies the scale the OS reports. Where the OS already scales
(Windows at 150 %, macOS Retina, GNOME/KDE with scaling), a first start is now
1.5 times larger than other applications until the user picks 100 %. It is
right where the OS reports nothing (WSLg, bare X11), which is the machine this
was asked for. Upgrade path if testers on other systems complain: default to
150 % only when the screen reports scale 1.

## Skipped, and when to add

- Live rescale without restart: see Decisions.
- Icon-only mode for the whole bar: add when the bar no longer fits a narrow
  window.
- A keyboard shortcut for the scale: the button takes Tab focus like the rest.

## Checks

`testing/tests/api/action_toolbar.py`: every button has an icon; Undo and Redo
are icon-only with their name as tooltip; the scale menu lists the five steps,
checks the saved one and saves a pick. `testing/tests/api/theme.py`: the
default scale is 150 %. Real GUI on WSLg in the dark and the light theme.

## Status

Done 2026-11-13 in 4.7.0. Real GUI checked on WSLg with fresh settings: starts
at 150 %, the bar fits the default window, icons follow the dark and the light
theme, all twelve buttons take Tab focus in order.
