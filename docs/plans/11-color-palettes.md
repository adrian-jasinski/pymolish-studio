# 11 — Color palettes

[Roadmap](../../PLAN.md) · Request 2026-11-14 · Draft; source was read,
nothing was built or measured.

**Five named palettes replace the order in which new objects get their color
(today green, cyan, light magenta, ...). Picked in the toolbar, remembered,
applied again at start.**

## What exists

- **The order is a fixed C table:** `AutoColor[40]` in `layer1/Color.cpp:35`.
  `ColorGetNext` (`:140`) walks it with setting `auto_color_next`. Six loaders
  reach it through `AtomInfoUpdateAutoColor` (`layer2/AtomInfo.cpp:1340`).
  It colors carbons; other elements keep element colors.
- **A second copy in Python:** `util._color_cycle`, used by `util.color_objs`
  (`modules/pymol/util.py:787`).
- **Toolbar pattern to copy:** the UI scale button in
  `modules/pmg_qt/action_toolbar.py:87`: menu button, checkable action group.
  Lucide `palette.svg` is already shipped.
- **Saved GUI choices:** `QSettings` in `modules/pmg_qt/theme.py` (`theme/dark`,
  `ui/scale`).
- **pymolrc:** user-written files run at start (`modules/pymol/invocation.py:118`),
  skipped with `-k`.
- **Palette data to reuse:** the pymolish plugin has six lists of 25 colors
  (pastels, neon, earth, ocean, warm, cool), MIT, same author.

## Decisions

- **One table, replaceable.** `AutoColor` becomes a `std::vector<int>` with one
  setter, bound as `_cmd.set_auto_colors(indices)`. About 25 lines of C++. It
  stays process-wide, as today. `util._color_cycle` is deleted;
  `color_objs` asks the same table.
- **One command:** `palette [name [, recolor]]`.
  - no argument: list the palettes and mark the active one
  - `name`: new objects cycle through that palette
  - `recolor=1`: also recolor the carbons of existing objects, in panel order
  - `palette default` restores the PyMOL order

  New public `cmd.palette`: `ChangeLog` entry. Lives in a new file
  `modules/pymol/palettes.py` (data and command together).
- **Colors are named colors:** `<palette>_01` ... registered with
  `cmd.set_color` on first use, so sessions save them like any custom color.
- **The five palettes**, at most 30 colors each:

  | Name | Made for | Source |
  | --- | --- | --- |
  | `vivid` | dark background | bright, saturated |
  | `deep` | white background, print | dark, saturated |
  | `pastel` | dark background | plugin `PASTELS` |
  | `soft` | white background | mid-lightness pastels |
  | `colorblind` | both | Okabe-Ito plus Paul Tol's sets, as published; shorter than 30 on purpose |

  Exact RGB values are chosen in the implementation PR and judged by the test
  below, not by eye alone. The menu label names the background.
- **Toolbar:** `Palette` menu button after `Presets`, icon only (the bar is
  full at 150 %). Entries: `PyMOL default` and the five, checkable, each with a
  strip of its first six colors as icon; separator; `Recolor objects now`.
  Reachable with Tab like the other buttons.
- **Remembered in `QSettings`** (`colors/palette`), applied when the window
  starts, before pymolrc runs, so a `palette ...` line in pymolrc wins.
  - Why not write into pymolrc: it is the user's hand-written file, there can
    be several, and theme and scale already live in `QSettings`.
  - Consequence: `pymolish -c` does not pick the GUI choice up. Scripts stay
    reproducible; add `palette soft` to the script or pymolrc.
  - Upgrade path if headless must follow the GUI: write a generated
    `~/.pymolrc_palette.pml`; the `.pymolrc*` pattern loads it.

## Steps

1. C++: vector, setter, binding. Catch2 case: set three indices, `ColorGetNext`
   returns them in order and wraps.
2. `palettes.py`: data, `palette`, register in `api.py` and `keywords.py`;
   delete `util._color_cycle`.
3. Toolbar button, `QSettings`, apply at start.
4. Tests in `testing/tests/api/palettes.py`:
   - each palette has 1 to 30 colors, all distinct
   - contrast against its background is at least 3:1 (WCAG formula, a few lines)
   - neighbors in the cycle differ by a minimum RGB distance
   - `palette vivid`, load three fragments: object colors are entries 1 to 3
   - `palette default`: back to 26, 5, 154
5. Look at it: both backgrounds, cartoon and sticks, light and dark theme.
6. `docs/features.md`: one table with a swatch image per palette.

Commit: `ui(color): five object color palettes in the toolbar`.

## Skipped

- Palette editor and user-defined palettes: `cmd.set_color` plus a list is the
  manual route; add when someone asks.
- Per-chain palettes (`util.cbc`): objects only for now.
- Switching palette automatically with `bg_rgb`.
- The plugin's neon, earth, ocean, warm and cool lists: five is the request.
