# 11 — Color palettes

**2026-11-23, draft 5: 11c below adds explicit CPK coloring; planned at
4.43.0 and built the same day in 4.50.0: see the note below.** Question 56 was answered that day: standard CPK
atom colors within selected residues. Object/chain palettes already
shipped are unchanged by this plan.

**11c done 2026-11-23 in 4.50.0.** `color_cpk selection [, ball_and_stick]`
in `modules/pymol/palettes.py`, with the rows by element > CPK and by rep >
ball and stick > "CPK (balls only)". 28 elements have a color, any other is
FF1493; the colors are given as RGB values, so no named color is defined
and no palette changes. Looked at on a black and on a white background.
Not as planned: the table is the "CPK Colours" table of the RasMol manual
as known. The Jmol page named below gave no table to a text fetch, the
RasMol manual and Wikipedia's table could not be read either; only FF1493
for other elements was confirmed (question 64). Left out: representations
other than ball_and_stick as a target.

## 11c — CPK for selected residues, with an explicit color target

CPK assigns colors by **element**; coloring each amino-acid type is a
different scheme. This distinction is documented in the primary
[Jmol color reference](https://jmol.sourceforge.net/jscolors/), checked
2026-11-23. Do not invent a “CPK residue” palette.

Question 56, **answered 2026-11-23: standard CPK atom colors within selected
residues.** The alternative of one color per amino-acid type is not selected.

For CPK, add an explicit C > By element > CPK entry to the shared menus;
a residue-level selection colors all atoms of those selected residues.
Offer it also under C > Ball-and-stick so only that representation's
overrides change (step 34). An ordinary CPK action changes atom colors
normally; its label/help must distinguish it from the representation-only
action. The latter cannot change `sphere_color`, atom colors or cartoon
colors. A proposed command `color_cpk selection, representation=...` uses
the same function; confirm the final signature against `color`, `color_deep`
and existing `util.cba*` helpers before adding an unnecessary wrapper.

Audit `modules/pymol/menu.py:by_elem`, `util.cba*` and the element colors in
`layer1/Color.cpp`. Reuse their mapping if it matches the chosen documented
CPK variant; otherwise use one named data table, with a neutral fallback
for unknown elements. Do not change the active object palette or all
element definitions globally merely to color a selection.

Tests in `testing/tests/api/` cover common elements, a metal/halogen and an
unknown element; whole-residue selection, CPK vs atom-color inheritance,
ball-and-stick-only coloring with simultaneously visible spheres, custom
colors, scene recall (35b), PSE/PSEX and menu/command equivalence. Include
modified residues: their atoms still use element colors. Look at light and
dark backgrounds, without silently changing published colors to suit the theme.

Files: color helper/data, `menu.py`, command registration/help/completion
if a public command is added, tests, `docs/commands.md` and `ChangeLog`.
An `X` version. No new dependency or palette editor. The rest of this file
records the earlier object/chain palette work.

[Roadmap](../../PLAN.md) · Request 2026-11-14 · Done in 4.10.0, see
[Status](#status).
One more palette, 11b, was planned and built on 2026-11-20 (`halo`, 4.41.0): see
[the end](#11b--a-palette-from-the-users-brand-colors).

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
- **Remembered in `QSettings`** (`colors/palette`). Final: the user left the
  choice to this plan on 2026-11-14.
  - Applied when the window starts, before pymolrc runs, so a `palette ...`
    line in pymolrc wins. Not applied with `-k`, which keeps meaning "no user
    configuration".
  - Why this and not a line written into pymolrc: theme and UI scale already
    live there, it is two lines of code, and pymolish never edits a file the
    user wrote by hand (there can be several pymolrc files).
  - pymolrc still works for whoever prefers it: `palette soft` typed there
    applies at every start, with and without the GUI.
  - Ceiling: `pymolish -c` ignores the toolbar choice, so batch scripts give
    the same colors on every machine. If that is ever wanted, the upgrade is a
    generated `~/.pymolrc_palette.pml`.

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

## Status

Done 2026-11-14 in 4.10.0. Checked: `testing/tests/api/palettes.py`, the
palette case in `testing/tests/api/action_toolbar.py`, the Catch2 case in
`layerCTest/Test_Color.cpp`; in the real window vivid and pastel on black,
deep and soft on white, colorblind on both, sticks and cartoon, both themes,
and a restart with and without `-k`.

Sizes: vivid 21, deep 15, pastel 25, soft 22, colorblind 18. Lowest contrast
against the own background: vivid 4.4, deep 3.3, pastel 13.7, soft 3.3.

Differences from the plan above:

- **`util._color_cycle` stays.** `util.cbc` uses it, and per-chain palettes
  are on the Skipped list. `color_objs` no longer reads it.
- **No getter for the table.** The color name `auto` already returns the
  next entry, so `color_objs` and `recolor` use that.
- **The palette is applied again after `reinitialize` and after a session
  load.** Both rebuild the color list; without this the table pointed at
  colors that were gone.
- **The active row has a frame around its strip.** Qt shows no check mark on
  a menu row that has an icon.
- **colorblind has no contrast test.** A color cannot reach 3:1 against black
  and white at once, and the values stay as published. Yellow is weak on
  white, indigo on black.
- **pastel is the plugin list unchanged.** After about twelve objects its
  colors are hard to tell apart; the neighbor distance in the test (0.14) is
  set by this list.

### Follow-up, 4.15.0

The menu has a caption, "Palette: colors of objects and chains"
([step 16](16-background.md)).

### Follow-up, 4.13.1

Asked for on 2026-11-16 after using it.

- **The menu is a list with wide strips.** Ten colors per palette, 14 px each,
  also for the PyMOL order. The six-color square icon was too small to read.
  A `QListWidget` in the menu, because a menu icon is always a small square.
- **Picking recolors at once.** Click or arrow keys; "Recolor objects now" is
  gone. The `palette` command still recolors only with `recolor=1`.
- **`util.cbc` follows the palette**, so C > by chain and the presets do too.
  This was on the Skipped list. `util._color_cycle` stays as the PyMOL order.
- **pastel is redefined:** cyan, green, red, blue, yellow, then seven more.
  Stronger than the plugin list and all twelve can be told apart.
- **Three more palettes for a dark background:** nord, dracula, catppuccin,
  values as published, close colors left out. A fourth for a white background
  (Catppuccin Latte) was dropped: six of its fourteen colors are below 3:1
  on white.
- **The neighbor distance in the test is 0.2** (was 0.14, set by the old
  pastel list).

## 11b — a palette from the user's brand colors

Request 2026-11-20: the colors of a brand book as an object palette, under
another name, filled up to a full palette like the others. Planned
2026-11-20 at 4.39.0. The brand book is the user's file and is not in the
repo.

**Done 2026-11-20 in 4.41.0 as `halo`.** The user answered the three
questions below with "add this to code", without a choice, so the
recommended options were built: the name `halo`, the twelve colors of
option A, the brand not named.

- Measured: the data test passes with the new name (6 tests, 10 subtests)
  and so do the 8 toolbar tests. In the real window the menu has eleven
  rows, its list is 338 x 242 px at 100 % on a screen 1067 px high.
  Twelve helices, six as cartoon and six with sticks, on black and on
  white: all twelve can be told apart; the deep purple is the darkest on
  black and still seen.
- `docs/img/palette-halo.png` is 248 x 28 px. The script that drew it
  gives the shipped chimerax strip back pixel for pixel.
- Also changed: the NOTES of the `palette` help named colorblind alone
  for "any"; they name chimerax and halo too.
- Left out: the look at 150 %. The list grows by one row of 22 px, so
  no trouble is expected; that is an estimate, not a measurement.

**One more row in the palette menu: the five colors of the brand book, and
seven more in the same strong tone for the hues the brand does not have. It
is one entry of data; the menu, the completion and the test pick it up by
themselves.**

### What the brand book gives

Eight colors. White, black and a light grey (`f4f4f4`) cannot color an
object. Five are left. The contrast is the WCAG number of the test, which
asks for 3 or more.

| Color | Value | In the book | On black | On white |
| --- | --- | --- | --- | --- |
| turquoise | `00f4d6` | main | 14.9 | 1.4 |
| blue | `016afa` | main | 4.4 | 4.7 |
| cyan | `00caff` | main | 10.9 | 1.9 |
| indigo | `4300ff` | complementary | 2.7 | 7.8 |
| deep purple | `471396` | complementary | 1.8 | 11.7 |

Measured on 2026-11-20 with the functions of
`testing/tests/api/palettes.py`:

- **Half the color wheel is missing.** All five lie between turquoise and
  purple (hue 173 to 264 of 360). Five objects would be two cyans and three
  blue-violets.
- **No background fits all five.** Two are below 3 on black, two on white.
- **A dark version cannot keep both complementary colors.** Lifted to 3 on
  black with the hue kept they become `5a1fff` and `6f21e4`, 0.13 apart; the
  test asks 0.2 between neighbors, and they look the same.
- **Size of the others:** vivid 21, deep 15, pastel 12, soft 22,
  colorblind 18, nord 8, dracula 7, catppuccin 11, chimerax 10.

### The seven added colors

One for each hue the brand lacks, in the tone of its main colors (full
saturation, middle lightness): pink `ff3d9a`, red `ff4d4d`, orange `ff8a00`,
yellow `ffd900`, lime `9be800`, green `1fd655`, magenta `c61aff`.

Brand colors and added ones alternate, so that neighbors differ. The first
two objects get brand colors, and all five brand colors are among the first
ten, which is what the strip in the menu shows.

### Options

Picture of A and B on black and on white, next to vivid and chimerax:
`plan_images/palette-options.png`.

**Question 33, the name.** Lowercase letters, digits and `_`. Not the name
of a color theme (clay, blue, sage, mint, night): those stand in the menu
next to it.

- `halo` (recommended): the brand's mark is a glowing ring. Short, and it
  says nothing about hue, which fits a palette that has every hue.
- `lagoon`: after the turquoise and the blues the palette starts with.
- `prism`: after the full range of hues.

**Question 34, the colors.**

- **A (recommended): twelve colors, the five as published, "any
  background".**
  `00f4d6 016afa ff3d9a 00caff ffd900 4300ff 9be800 ff4d4d 471396 1fd655
  c61aff ff8a00`.
  Neighbors are at least 0.56 apart, the closest pair 0.23 (turquoise and
  cyan, both from the book). On black the deep purple has 1.8 and the indigo
  2.7, the other ten 4.4 or more; on white six are below 3. This is how
  colorblind (lowest 1.7 on black) and chimerax (2.2) are listed: values as
  published, any background, no contrast test.
- **B: eleven colors, "dark background".** The same without the deep purple
  and with the indigo lifted to `5a1fff` (3.1 on black). It passes the
  contrast test, but only three of the five values are the book's.

**Question 35, the source.**

- **Not named (recommended):** the user asked for another name, so nothing
  in the program, `docs/features.md` or `ChangeLog` names the brand. The
  comment in `palettes.py` says: five colors of a brand book, seven added.
- **Named** in the comment and in `docs/features.md`, as for nord, dracula
  and chimerax.

### Steps, after the answers

1. `modules/pymol/palettes.py`: the entry after `chimerax` (`:67`), the name
   in the docstring of `palette` (`:149`) and its background in NOTES
   (`:163`).
2. `testing/tests/api/palettes.py:59`: the name in the list of `test_data`.
   That test then checks the entry: 1 to 30 colors, none twice, neighbors
   more than 0.2 apart, and with B the contrast on black. No new test: the
   change is data.
3. `docs/features.md:55`: one row and one sentence;
   `docs/img/palette-<name>.png`, a strip 28 px high with 20 px per color
   like the nine there (chimerax, ten colors: 208 x 28).
4. A look in the real window: the menu with eleven rows at 100 and 150 %,
   twelve objects as cartoon and as sticks, on black and on white.
5. `ChangeLog` and the version: a new palette is a step of `X`, as chimerax
   was (4.22.0).

Commit: `ui(palette): <name>, ...`. Nothing changes in the toolbar
(`modules/pmg_qt/action_toolbar.py:457` reads `PALETTES`), the completion
(`modules/pymol/completing.py:46`) or the session code.

One case to know: a palette the user made under the chosen name is skipped
at start with the message "is a built-in palette"
(`action_toolbar.py:244`). It stays in the settings; renaming it there is
by hand.

### Skipped

- A second palette for a white background, the way vivid has deep:
  turquoise and cyan have 1.4 and 1.9 on white. Built when asked for.
- Only the brand's hues, in tints and shades: closest to the book, but
  objects could not be told apart.
- More than twelve colors: the closest pair is at 0.23 already, a
  thirteenth would be a tint of one that is there.
- A color theme (protein, ligand, background) or a window theme in these
  colors, the typeface and the mark of the brand book: not asked for.
