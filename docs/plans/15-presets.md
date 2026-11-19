# 15 — Presets and looks

[Roadmap](../../PLAN.md) · Request 2026-11-16 · **15a done 2026-11-16 in
4.14.0, 15d in 4.14.3, 15f in 4.14.4.** 15b, 15c and 15e are open and wait for
the user. **15g and 15h done 2026-11-18 in 4.14.5, 15i (visible objects, two
presets for complexes) in 4.19.1, 15j (the light after "illustration") in
4.19.2, 15k (publication green) in 4.19.3** (the last sections before "Skipped"). They change three decisions below: the looks are part of the
one preset list, they leave the background alone, and three presets stop
recoloring the protein.

**The preset menu is ordered, has one solvent row instead of twin rows, a
glass preset and a cartoon transparency row. Every preset but "simple" draws
the protein as cartoon. Below it the toolbar menu has seven looks: light,
background and outline for the whole scene.**

## What existed

- **Presets:** `modules/pymol/preset.py`, functions that take a selection and
  set representations, colors and per-object settings. `menu.presets`
  (`modules/pymol/menu.py`) listed 14 rows in no order; the toolbar's Presets
  button and A > preset on every row show the same list.
- **Twin rows:** simple and simple (no solvent), pretty and pretty (with
  solvent), publication and publication (with solvent). Each pair differs
  only in the water.
- **Light:** only Plugin > Lighting Settings, five buttons (Default, Metal,
  Plastic, Rubber, X-Ray) that set light and nothing else.
- **`c_peptide_marketing2.pse`,** the user's example for a white background.
  It differs from the defaults in: white background, the plugin's Rubber
  light (`ambient` 0.05, `direct` 0.2, `reflect` 0.5, `shininess` 10),
  `power` 1.67, `depth_cue` off, `ray_trace_mode` 1 with `ray_trace_color`
  black, `antialias` 3, `ray_opaque_background` 1, and a white surface at
  `transparency` 0.6.

## What was tried

Every candidate was ray traced and captured from the real viewport on 1oky
(cartoon, surface, ligand).

| Tried | Result | Verdict |
| --- | --- | --- |
| The settings of the session file | Matte colors and black outlines on white | Look **figure** |
| Plugin: X-Ray | Inverted light, bright edges; unlike anything else | Look **x-ray** |
| Plugin: Metal, Plastic, Rubber | On cartoon and on surface hard to tell from each other and from the default | Not in the menu; they stay in the plugin |
| ChimeraX `lighting soft` (no key or fill light, ambient 1.5 from 64 directions) and silhouettes | PyMOL has eight lights at most: `light_count` 8, `direct` 0, `ambient` 0.35, `reflect` 0.9, soft shadows (`ray_shadow_decay_factor` 0.1). Bright, even colors; with the glass preset close to a ChimeraX picture | Look **soft** |
| Illustration style (`ray_trace_mode` 3, `ambient` 1, no direct light, no shadows) | Unshaded color areas with outlines, after David Goodsell's pictures | Look **flat** |
| Glass: transparent white surface plus `ray_transparency_oblique` 1 | The surface gets denser toward its edges, in ray-traced images and in the viewport | Preset **glass** |
| Glass: more specular light, `ray_transparency_oblique_power` 3 and 8, `ray_transparency_contrast` 1.6 | No visible gain over the row above | Not set |
| Glass: `transparency_mode` 3 | Grey rims in the viewport when combined with the oblique setting | Not set |

Second round, request of 2026-11-16 (15d and 15e), same structure:

| Tried | Result | Verdict |
| --- | --- | --- |
| The gist's `BallnStick` on the ligand: `stick_radius` 0.07, `sphere_scale` 0.18 (hydrogens 0.13), carbons `grey85` | Small balls on thin sticks; the ligand stands out from the protein's lines in every look | In **ligands** and **ligand sites** |
| The gist's black sticks | Invisible on the default black background | `grey30` instead: visible on black and on white |
| `cartoon_transparency` 0.25, 0.5, 0.75 | The ligand shows through the cartoon; viewport and ray-traced | Row **cartoon transparency** |
| `ray_trace_mode` 3 with default light | Color steps, but dark | Not used |
| `ray_trace_mode` 3, bright light (`ambient` 0.5, `direct` 0.6, `reflect` 0.3), no shadow, `antialias` 1 | Bright colors in four steps inside thick outlines; `antialias` 1 makes the lines thicker | Look **comic** |
| `ray_trace_mode` 2 | Black outlines on white, a line drawing | Look **sketch** |
| Gallery, Goodsell-like: `ray_trace_gain` 0, 0.03 | The outline looks the same as with the default 0.12 | Not set |
| `ambient_occlusion_mode` 1 on a surface | Pockets get dark, more depth on an opaque surface; black blotches on the glass surface | 15e |
| Fog on a white background (`depth_cue` 1, `fog_start` 0.45), after the gallery's Geis picture | The back of the molecule fades to white | 15e |
| `cartoon_cylindrical_helices` 1 | Helices as cylinders, a schematic drawing | 15e |
| Gallery, "Complex Stylized Protein": grey balls inside a rim-only surface (`ray_transparency_oblique_power` 20) | Works; reads only on small proteins | 15e |
| `ray_texture` 2 (in the gist) on a surface | No visible difference | Not set |

Third round, request of 2026-11-16 with six example pictures (15f):

| Tried | Result | Verdict |
| --- | --- | --- |
| `cartoon_debug` 3: the cartoon builder writes line strips instead of triangle strips | Helices, sheets and loops as a wire mesh, in the viewport and ray traced; close to the two wire pictures | Preset **wire** |
| `cartoon_fancy_helices` 0 and `cartoon_sampling` 14 with the wire | Little difference; a denser mesh only gets darker | Not set |
| `spectrum` with three colors: a light tint, the color, a dark shade | One color from light to dark along the chain | `util.shades`, rows **shades** |
| The look flat on shades of blue | `ray_trace_mode` 3 rounds every color to four steps: the shades became cyan, white and teal | flat now uses `ray_trace_mode` 1 |
| Faint surface (white, `transparency` 0.85) around the cartoon, look flat | The surface has no outline: the ray tracer leaves out everything more than 5 % transparent | See the next row |
| `ray_trace_trans_cutoff` 1 | The surface gets its silhouette line and small crease marks, as in the proteinbase pictures | In the look **flat**; preset **illustration** |
| The same cutoff in the look figure with the glass preset | Heavy black lines over the glass | Only in flat |
| A pale blue surface at `transparency` 0.7 | A little closer to the examples, but wrong after recoloring in another color | White at 0.85 |
| Dark end of the shades at 40 % of the color | Lost on a black background | 50 % |

Outlines come from the ray tracer (`ray_trace_mode`). The viewport has no
outline pass, so figure, soft and flat show their outline only in images made
with Draw/Ray > Ray. That is 15b. Comic and sketch depend on it most: in
the viewport comic is a bright light on white, and sketch is the default
light on white. The preset illustration is flat blue shapes there.

## Decisions

- **A preset says what is shown, a look says how it is lit.** Presets work on
  a selection and are in both menus. Looks are global settings, so they are
  only in the toolbar menu, under a "Look:" caption.
- **One solvent row.** It reads "show solvent" or "hide solvent", acts at
  once, and the presets picked afterwards keep the choice. It starts hidden.
  While hidden, a preset runs on the selection without its water, so
  "ligands" and "technical" also draw no contacts to hidden water. "default"
  is the exception: it shows everything, as after loading.
- **No function is removed.** `preset.simple_no_solv`, `pretty_solv`,
  `pub_solv` and the others keep their behavior; only the menu rows changed.
  The menu calls `preset.from_menu(name, selection)`.
- **A look replaces the one before it.** `preset.look(name)` first restores
  the default of every setting that any look sets (`unset` on a global
  setting does that), then sets its own. No table of defaults.
- **The next preset undoes glass.** `_prepare` now also restores
  `surface_color` and the global `ray_transparency_oblique`, as it already
  did for `two_sided_lighting`.

- **Ribbon only in "simple".** `technical`, `ligands` and the ligand sites
  presets draw the protein as cartoon (15d). "ligand sites > cartoon" is now
  that preset without its surface.
- **The ligand of the ligand presets is a ball-and-stick drawing** (15d).
  `_prepare` already restored `sphere_scale`, `stick_radius` and
  `stick_color`, so the next preset undoes it.
- **Cartoon transparency is a submenu, not a switch:** off, 25%, 50%, 75%.
  It sets `cartoon_transparency` on the objects of the menu; `_prepare`
  restores it, so it lasts until the next preset.

- **"illustration" also picks the look flat** (15f). It is the one preset
  that sets a look: without the outline the picture is not there. Another
  preset does not undo the look; the Look rows do.
- **flat keeps colors as they are** (15f): `ray_trace_mode` 1. The color
  steps are comic's.
- **Shades are a color action, not a preset:** `util.shades(color,
  selection, chains)`, in the color menus next to rainbow and next to "by
  chain". Eight colors in the menu; any color name works when typed.

## The menu after 15f

| Group | Rows |
| --- | --- |
| Reset | default · classified |
| Plain | simple · technical · ball and stick · b factor putty |
| Pictures | pretty · publication · glass · wire · illustration |
| Binding | ligands · ligand sites ▸ · protein interface |
| Option | cartoon transparency ▸ · show solvent / hide solvent |
| Look (toolbar only) | default · figure · soft · flat · comic · sketch · x-ray |

16 preset rows, two more than before step 15: three twin rows left; glass,
wire, illustration, the solvent row and cartoon transparency came.

## Slices

**15a, menu, glass and looks. Done in 4.14.0.**
- `preset.py`: `glass`, `from_menu`, `show_solvent`, `LOOKS`, `look`.
- `menu.py`: `presets` reordered, `preset_ligand_sites` through `from_menu`,
  new builder `looks`.
- `action_toolbar.py`: the Presets button appends the looks.
- Checks: `testing/tests/api/preset.py` (`testGlass`, `testMenuSolvent`,
  `testLook`), `menu.py` (`testPresets`), `action_toolbar.py`. Real window on
  WSLg: every look, glass, the menu. Ray-traced: every look, glass in three
  looks.
- Commit: `ui(presets): ordered menu, one solvent row, glass preset, looks`.

**15d, cartoon, ligand style, transparency, comic and sketch. Done in 4.14.3.**
- `preset.py`: `_ball_and_stick_ligand`; `technical`, `ligands`,
  `ligand_sites` show cartoon; `_prepare` restores `cartoon_transparency`;
  looks `comic` and `sketch`.
- `menu.py`: builder `cartoon_transparency`, one row in `presets`.
- Checks: `testing/tests/api/preset.py` (`testTechnical`, `testLigands`,
  `testLook`), `menu.py` (`testPresets`). Real window on WSLg: ligands on
  black and on white, ligand sites, technical, 50 % cartoon, comic, sketch,
  the menu. Ray-traced: the same, and every row of the table above.
- Commit: `ui(presets): cartoon in every preset, ligand balls and sticks,
  cartoon transparency, comic and sketch looks`.

**15f, wire, illustration, shades. Done in 4.14.4.**
- `preset.py`: `wire`, `illustration`; `_prepare` restores `cartoon_debug`;
  the look flat.
- `util.py`: `shades`. `menu.py`: builder `shades`, rows in `spectrum`,
  `by_chain` and `presets`.
- Checks: `testing/tests/api/preset.py` (`testWire`, `testIllustration`),
  `util.py` (`test_shades`), `menu.py` (`testShades`, `testPresets`). Real
  window on WSLg: wire, the preset after wire, illustration, shades by
  chain. Ray-traced: illustration in two colors, wire, publication and
  glass in the new flat.
- Commit: `ui(presets): wire and illustration presets, shades of one color`.

**15b, outline in the viewport. Open, the user decides.**
- A screen-space edge pass over the depth buffer after the scene is drawn,
  in `data/shaders/` and the Scene draw path of `layer1/`. New shader code,
  to be measured with `testing/compare.py -- gui` before and after.

**15c, ChimeraX object colors. Open, the user decides.**
- One more entry in `palettes.PALETTES` (tan, sky blue, plum, light green,
  salmon, ...), the pattern of [step 11](11-color-palettes.md). One line and
  the docstring.

**15e, more effects. Open, the user picks.** Each was tried (table above)
except the first, which needs code.

| Effect | What it takes |
| --- | --- |
| Color steps in the viewport, so comic looks like comic while working | One new setting and a few lines in `data/shaders/compute_color_for_light.fs` that round the light to steps. Together with 15b it makes the viewport match the ray-traced comic picture. |
| Fog toward a white background, for depth in the white looks | Two settings in a look (`depth_cue` 1, `fog_start` 0.45), or a "depth" row. Works in the viewport too. |
| Helices as cylinders, a schematic preset | One preset: `cartoon_cylindrical_helices` 1 on the publication preset; `_prepare` restores it. |
| Ambient occlusion in the soft look | `ambient_occlusion_mode` 1 in the look; glass must switch it off for its own objects. To be timed on a large surface first. |
| "Balls in glass" preset from the gallery | One preset; only for small proteins. |
| Glow and blur with distance, as in the wire example pictures | Not tried, needs code: a blur pass over the drawn picture, the same kind of pass as 15b. |

## Request 2026-11-18: one menu or two, background, colors (15g, 15h)

Done in 4.14.5; the result is under "Result" at the end of this section. The
user asked why the menu has "Preset" and "Look",
wants neither to change the background, wants the cartoon colors left alone
in the working presets, and "simple" out of the menu.

### What a look is, and how it differs from a preset

| | Preset | Look |
| --- | --- | --- |
| Acts on | the selection or the object of the menu | the whole scene |
| Sets | representations, colors, settings of that object | global settings: light, outline of ray-traced images, and today the background |
| Combines | one preset per object | one look for everything; any preset with any look (16 x 7) |
| Code | functions in `preset.py`, `menu.presets` | `preset.LOOKS`, `preset.look`, `menu.looks` |

That is why they are two lists: merged into one, "glass" in the soft light
and "glass" in the figure light would need a row each, and a preset picked
for one object would change the light of all the others. What is wrong today
is the naming, not the split: "Look" does not say what it changes, both lists
start with "default", and a look also turns the background white, which
reads like a preset.

**Options for the menu:**

| | Option | For | Against |
| --- | --- | --- | --- |
| A | **Keep two groups in the Presets menu, rename the second.** Caption "Light and outline:" instead of "Look:", its first row "standard" instead of a second "default". Recommended. | Two lines in `menu.looks`. The caption says what the rows change. | Still two groups in one menu. |
| B | One list: the looks become presets. | One thing to learn. | Loses the combinations (glass in soft light), or needs a row for each. A preset on one object changes the whole scene. |
| C | The looks leave the Presets menu and get their own toolbar button next to the palette and the background ([step 16](16-background.md)): three small buttons for the three things that are scene-wide. | The cleanest split. | One more button; the bar already hides two button texts at 150 %. |

A can become C later without a change to `preset.py`.

**Decided 2026-11-18: B, one list.**

### 15g, looks keep the background.

Facts read from the code:

- `preset._outline` (`preset.py:502`) is shared by figure, soft, flat, comic
  and sketch. Two of its six settings are background: `bg_rgb` white and
  `ray_opaque_background` 1. x-ray sets neither.
- `look("default")` unsets every key a look sets, so today it also turns the
  background black again.
- `_outline` sets `ray_trace_color` black. The default of that setting is
  `-6`, "front": the color that contrasts with the background
  (`SettingInfo.h:646`, read in `Ray.cpp:5674`). Without the black the
  outline should be black on white and white on black by itself. Read, not
  yet rendered.

Slice:

- `preset.py`: `_outline` loses `bg_rgb`, `ray_opaque_background` and
  `ray_trace_color`. Three keys out, nothing in.
- Ray trace every look on black, on white and on one gradient of step 16,
  with the presets illustration and glass. sketch on black becomes white
  lines on black; if that or another look is unusable on a dark background,
  say so in the "What was tried" table and decide there, not by setting the
  background again.
- `menu.py`: the caption and the first row of option A (or what the user
  picks).
- Decision "illustration also picks the look flat" stays; it now keeps the
  background too.
- Checks: `testing/tests/api/preset.py:120,152,160` assert a white and a
  black background after a look; they become "the background is what it was".
- `ChangeLog`: `preset.look` no longer sets the background.
- Commit: `ui(presets): looks keep the background; caption says what they set`.

### 15h, presets keep the protein colors; "simple" leaves the menu.

A cartoon takes its color from the carbon atoms, so "recoloring the cartoon"
means a preset that colors the carbons of the protein.

| Preset | Colors it sets today | Planned |
| --- | --- | --- |
| default | by element, carbons in the object color | Stays: it is the reset, also for colors. |
| classified | none | Stays. |
| simple | by chain | Row removed. |
| technical | rainbow along each chain (`util.chainbow`, `preset.py:300`); ligands by chain; other elements by element | The rainbow line goes. |
| ligands, ligand sites (six variants, one function) | rainbow along the protein chains (`:130`, `:212`); ligand carbons grey; other elements by element | The rainbow lines go. The ligand keeps its ball-and-stick colors. |
| ball and stick | none | Stays. |
| b factor putty | by B factor | Stays: the color is the picture. |
| illustration | shades of blue | Stays: the user asked for it. |
| pretty, publication | rainbow over the protein carbons; ligands by chain | Question 1 below. |
| glass, wire, protein interface | by chain | Question 1 below. |

Slice:

- `preset.py`: delete the three `util.chainbow` lines. Coloring the
  non-carbon atoms by element stays in all three: lines and sticks need it,
  and it does not touch the cartoon.
- `menu.py:747`: delete the "simple" row. The group "Plain" is then
  technical, ball and stick, b factor putty.
- Checks: `testTechnical` and `testLigands` get "the carbon colors of the
  protein are the ones from before"; `testPresets` counts one row less.
- `ChangeLog`: `preset.technical`, `preset.ligands` and `preset.ligand_sites`
  no longer color the protein.
- Commit: `ui(presets): technical and ligand presets keep the protein colors;
  simple leaves the menu`.

Known consequence: after "illustration" the protein stays blue in the next
preset. "default" resets the colors, and so does a click in the palette menu.

**Questions:**

1. Should pretty, publication, glass, wire and protein interface also stop
   coloring? Recommended: no. They are picture presets like illustration, and
   an interface needs chains in different colors. If yes: five more deleted
   lines, and pretty and publication then differ from each other only in the
   shape of the cartoon. **Answer: they keep coloring.**
2. "simple": remove only the menu row (recommended, as step 15 decided "no
   function is removed"), or also the functions `preset.simple` and
   `simple_no_solv`? Scripts that call them would then fail. **Answer: only
   the row.**

### Result, 4.14.5

- **One list, without losing the combinations.** The looks are the last
  group of `menu.presets`, under the one caption "Preset:", in the toolbar
  and in A > preset. No other preset touches the light, so glass in the soft
  light still works. The first row of the group reads "standard light" and
  restores the default light; a second "default" row would have been
  ambiguous. `menu.looks` is deleted.
- **Ray traced on 1oky, every look on black and on white,** plus
  illustration and glass in the soft light:

  | Look | On black | On white |
  | --- | --- | --- |
  | figure, soft, flat, comic | White outline, same colors | Black outline, as before |
  | sketch | White lines on black | Black lines on white, as before |
  | x-ray, standard light | No outline, unchanged | Unchanged |
  | illustration (preset) | White outline around the blue shades and the faint surface | As before |

  The outline color comes from the default of `ray_trace_color`, "front".
  No look is unusable on a dark background.
- **A ray-traced PNG has a transparent background again** unless Display >
  Background > Opaque is on: the looks used to force
  `ray_opaque_background`, which is a background setting.
- **Modified residues.** The first test run found that a phosphoserine of
  1oky (a `hetatm` inside the chain) still got ligand colors, which leaves a
  patch on the cartoon. The ligand coloring now skips guide atoms. In
  `ligands` and `ligand sites` the line `util.cbc(lig)` was dead (every atom
  it colored was colored again right after) and is deleted.
- Checks: `testing/tests/api/preset.py` (`testKeepsProteinColors`,
  `testLook`, `testIllustration`), `menu.py` (`testPresets`),
  `action_toolbar.py`. Not checked in the real window.

## Request 2026-11-18, second: visible objects, complexes (15i)

Done in 4.19.1.

- **A preset from the toolbar acts on the objects that are switched on**
  (the selection `enabled`), no longer on all. A hidden object keeps its
  look. The rows for light and outline are for the whole scene as before.
  The cartoon transparency rows now go through
  `preset.cartoon_transparency`, because `set` with a selection of several
  objects did not reach the objects.
- **Preset "protein-protein interaction"** (`preset.interaction`): each
  chain of each object in the next palette color, as cartoon inside a
  surface of the same color at `transparency` 0.75; the residues within
  4.5 A of another chain as sticks; polar contacts between chains as
  dashes. "protein interface" stays: it is the plain version without
  surfaces and contacts.
- **Preset "antibody and antigen"** (`preset.antibody`): heavy chain
  `skyblue`, light chain `lightblue`, cartoon; the antigen as a `wheat`
  surface with the residues within 4.5 A of the antibody in `orange`; the
  antibody residues that touch the antigen as sticks; polar contacts as
  dashes.
- **How an antibody chain is found:** by the start of framework 2 in its
  sequence, heavy `W[VIFY][RK]Q.PG` (also single-domain antibodies), light
  `W[YFL][QLH]Q.[PSA]G`. A chain named H or L fills a role the sequences
  left empty. Without any antibody chain the preset shows the interaction
  picture and says so in the log.
- **Tried on real structures,** ray traced on black and on white: 1N8Z
  (trastuzumab Fab with HER2: chain A found as light, B as heavy, C as
  antigen) and 1BRS (barnase with barstar).

  | Tried | Result | Verdict |
  | --- | --- | --- |
  | Other elements by element color on every atom | The surfaces are speckled red and blue | Element colors only on the atoms drawn as sticks |
  | One color per chain through `surface_color` per atom | Clean surfaces; the sticks keep their element colors | In `interaction`; `_prepare` clears it |
  | Antigen as an opaque surface, epitope by residue | The footprint of the antibody reads at once | In `antibody` |

- **Both leave the camera alone** (the contacts are made with `zoom=0`).
- Checks: `testing/tests/api/preset.py` (`testInteraction`, `testAntibody`
  with the motif, with the names H and L and without an antibody,
  `testEnabledOnly`), `menu.py`.
- Not covered: an antibody whose framework 2 differs from both patterns and
  whose chains are not named H and L (some mouse lambda chains); it then
  gets the interaction picture. T-cell receptors are not recognized.

## Request 2026-11-18, third: after "illustration" the cartoon stays flat (15j)

Fixed in 4.19.2.

- **Cause:** "illustration" switches the look "flat" on (full ambient
  light, no shading). A look is a set of global settings and no preset
  switched it off, so every preset after it drew unshaded cartoons.
- **Fix:** `preset.illustration` notes that it set the light; the next
  preset (`_prepare`) goes back to the standard light. A look picked from
  the list clears the note, so a look the user chose stays.
- Checked in the real window: illustration, then pretty, on 1N8Z.
- Check: `testing/tests/api/preset.py` (`testIllustrationLight`).
- Not changed: the colors. "illustration" colors the protein in shades of
  blue; presets that keep the colors of the protein (classified,
  technical, ball and stick, the ligand presets) show those blues until a
  coloring preset or the C menu changes them. The user's answer of
  2026-11-18: the next preset does not give back the earlier colors.
- Not kept across a session file: after loading a session saved with
  "illustration" on, the flat light stays until "standard light" is
  picked.

## Request 2026-11-18, fourth: publication in shades of green (15k)

Done in 4.19.3.

- **Preset "publication green"** (`preset.publication_green`), the row
  after "publication": the same cartoon (smooth loops, fancy helices, grey
  inside), ligands as sticks, and the carbon atoms of the protein colored
  with `util.shades("forest")`: along each chain from a light tint over
  forest green to a dark shade. It is the coloring of C > spectrum >
  shades > forest.
- Checked ray traced and in the real window on 1N8Z.
- Check: `testing/tests/api/preset.py` (`testPublicationGreen`), `menu.py`.

| Option | Taken | Why |
| --- | --- | --- |
| Name "publication green" | yes | Says what differs. |
| Name "publication 2" | no | Says nothing about the picture. |
| Shades along each chain | yes | The request: spectrum, shades. |
| One shade per chain | no | It is C > by chain > shades after any preset. |
| A row per color (blue, orange, ...) | no | One was asked for; the C menu has the other seven. |

## Skipped

- Rows for Metal, Plastic and Rubber: see the table.
- Remembering the solvent choice after a restart. Add it with `QSettings`
  when asked.
- `look` as a typed command. `preset.look("flat")` works on the command line.
- A mark on the look that is active.
- The Lighting plugin reading `LOOKS`, and its sliders following a look.
- A new color for the sticks of "ball and stick". They are white, so on a
  white background they show only where a look draws shading or an outline.
- The rest of the gist: Bondi radii, slate nitrogens, `valence_size`, its
  dash style, the orbital and density commands.
- A ball-and-stick ligand in "pretty", "publication" and "glass". They keep
  sticks.
- A mark on the active cartoon transparency.
- A cross-hatched mesh on sheets. The wire draws them as a zigzag.
- A color picker for the shades, and "shades (elem C)" rows.
- A ChimeraX representation preset. "classified" already shows cartoon,
  ligand sticks and ion spheres.

## Sources

- PyMOLWiki, [Ray](https://wiki.pymol.org/index.php/Ray): the four values of
  `ray_trace_mode`.
- ChimeraX, [lighting](https://rbvi.ucsf.edu/chimerax/docs/user/commands/lighting.html):
  what its presets soft, full and flat set.
- bobbypaton, [pymol_style.py](https://gist.github.com/bobbypaton/1cdc4784f3fc8374467bae5eb410edef):
  the `BallnStick` values.
- PyMOLWiki, [Gallery](https://pymolwiki.org/Gallery): Goodsell-like,
  Stylized Ball and Stick, Complex Stylized Protein, Tribute to Irving Geis.
- Oxford Protein Informatics Group,
  [Making Pretty Pictures in PyMOL v2](https://www.blopig.com/blog/?p=12018):
  white background, `ray_trace_mode` 1, `antialias` 3.
