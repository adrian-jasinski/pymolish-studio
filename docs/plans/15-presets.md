# 15 — Presets and looks

**Built 2026-11-26, 4.91.0: the glow menu (answer 128 A).** Presets >
light ends with "no fog"/"fog" and "no glow"/"glow"; the row calls
`preset.glow(on)` and keeps one Undo snapshot; scenes keep `glow` like
`depth_cue`. Checked headless: Undo, Redo, scene recall, session save and
load; in the window, the 4.88.0 halo test through `preset.glow` (integrated
AMD GPU, WSLg). Nothing new measured: no frame times, no picture. Left
out, as decided: ray-traced pictures, sized images, stereo. Step 15 is
finished.

**Decision 2026-11-26, question 128: A, recommended.** Keep the glow
setting and add "glow" / "no glow" to the light menu, for the viewport
only. The measurements below are from the 4.88.0 experiment.

**Built 2026-11-26, 4.83.0 to 4.88.0: 15m, 15n, 15o, 15b and 15p.** The
section "Request 2026-11-26" below is the plan as it was written that
morning; questions 123 to 125 were answered with their recommended options.

| Slice | Version | Built | Measured, and what was left out |
| --- | --- | --- | --- |
| 15m | 4.83.0 | `space_filling`, `illustrated_atoms` (spheres in the light "flat"), `licorice`, `bond_shell` (lines inside a surface at transparency 0.5); the row "contour cartoon"; "glossy (light only)" in the light menu. | Sheet: [reference-recipes.jpg](../img/reference-recipes.jpg), ray traced and from the viewport, 1oky, 1aon, 1bna. Chosen from trial pictures: flat (comic too heavy, figure too dark), 0.5 (at 0.25 the lines do not show). No frame or ray times recorded. |
| 15n (with [34d](34-ball-and-stick.md)) | 4.84.0 | Presets > transparency: cartoon, spheres, surface, ball and stick; opaque, 25, 50, 75 %; whole objects. | A row clears the value on the atoms of the object and sets it on the object; a preset now unsets all four on its objects. |
| 15o | 4.85.0 | The groups cartoon, atoms and bonds, surface, binding; transparency, solvent; "Scene appearance" with light, theme (colors and background) and floor. | 69 leaves, one Undo snapshot each. Arrow keys tried in the toolbar menu, three levels. Labels stay in small letters. |
| 15b | 4.87.0 | The outline in the viewport: `fxaa.fs` draws a line where the picture lies behind its neighbors, from two copies of the depth; follows `ray_trace_mode`, switch `viewport_outline`. | [viewport-outline.jpg](../img/viewport-outline.jpg). At 1436 x 702 on the integrated GPU (Mesa d3d12): 1oky spheres 2.8 to 5.7 ms a frame, 1aon spheres 5.2 to 8.2 ms, 1aon cartoon 11.1 to 13.1 ms. Not in stereo or in images of another size; grid mode: the line inside a see-through surface only in the last cell; no other driver tried. |
| 15p | 4.88.0 | `set glow, 1`: a halo around what is drawn (`glow.fs`, composed in `fxaa.fs`). A setting only. | [glow-experiment.jpg](../img/glow-experiment.jpg), with the bright-edge baseline (spring under "x-ray"). 4hhb spheres 4.2 to 6.7 ms a frame, 1aon spheres 6.0 to 8.5 ms, 1aon cartoon 4.6 to 9.1 ms. Memory computed, not measured: 8.1 MB for the picture offscreen, 8.1 MB for two copies of its depth, 1.0 MB for the halo. No halo in ray-traced pictures, in images of another size, in stereo. The background is no source of the glow (the mask is the depth); labels are no source but are covered by it. **Answer 128 A keeps this scope and adds a menu entry; the [follow-up](#question-128-a-glow-menu-follow-up) shipped in 4.91.0.** |

Not as planned: the labels were not capitalized; "illustrated atoms" got no
recipe values of its own (it is space filling plus an existing light); the
outline is no pass of its own but a step of the FXAA pass; frame times were
taken on one driver.

**Planning update 2026-11-26, checked against 4.82.0 (`902f8b75`).**
The request adds 15m–15p below; 15b stays open. All 24 PNG/JPG references
in the local, git-ignored `plan_images/` directory were inspected. No new
render, timing, GUI measurement or implementation was made. Recipe values
below are trial targets, not measured results. Older sections describe the
releases of their dates; this section governs the new work. Footer sizing
is [32c](32-footer-icons-movie-button.md); independent ball-and-stick
transparency is [34d](34-ball-and-stick.md).

## Request 2026-11-26 — representations first, then menu organization

Use the images as visual directions, grouped by appearance, not one preset
per image. Watermarks, captions, backgrounds, photographic blur and invented
molecular arrangements are not part of the recipes. Keep the source images
unchanged and local; make our own molecular renders for comparisons and
shipped previews. `motm` identifies the user's PDB Molecule of the Month
references, not a requirement to reproduce their composition or colors.
Use descriptive names, never “Proteinbase”, for the cartoon examples.

### 15m — reference families and candidate recipes

| Family and local references | Proposed entry / composition | Existing implementation and limit |
| --- | --- | --- |
| Space-filling atoms: `spheres1.png`, `spheres4.jpg`, `spheres6.png` | **Space filling**, new molecular preset. Soft or Glossy lighting provides matte or polished variants. | Native `spheres`, existing atom radii and sphere sizes. Preserve colors and user size overrides; no invented particles. Soft's surface ambient occlusion does not establish ambient occlusion on spheres. Deep contact shading and photographic blur are comparison limits. |
| Illustrated atoms: `motm_5yh2.jpg`, `motm_7dtw_7dtx_3qrf.png`, `motm_x.jpg`, `motm_3JRS.png` | **Illustrated atoms**, new preset: space-filling atoms with illustrated lighting and contours. The transparent example uses the same recipe plus Spheres transparency. | Compare `comic` and `figure`, choose one restrained recipe. Ray outlines exist; viewport outlines depend on 15b. Keep chain colors. No separate preset per complex, palette or opacity. |
| Outlined cartoon in a faint envelope: `proteinbase1.png`, `proteinbase2.png` | **Contour cartoon**, proposed display name for today's **illustration**. | Reuse `preset.illustration`: cartoon, faint surface, Flat light and `ray_trace_trans_cutoff`. Compare its current transparency before changing a value. Keep the callable `illustration` name. Refinement/relabel, not a duplicate; viewport contour follows 15b. |
| Soft solid shape: `surface.png`, `temp1.jpg`, `spheres3.jpg` | Existing **Clay**; surface on one object plus cartoon/tube on another for the mixed view in `temp1.jpg`. | Existing grid surface, rounded probe and surface ambient occlusion. `spheres3.jpg` reads as a fused envelope despite its filename. No new Gaussian object or shader. |
| Glossy / translucent material: `amber1.png`, `amber2.png`, `amber3.png`, `amber_sphere.png`, also `spheres6.png` | Existing **Glossy**, **Candy glass**, **Frosted**, **Balls in glass**; Space filling or Ball and stick plus Glossy light and transparency. | Expose the already callable `look('glossy')` as a light-only menu action, so polishing atoms does not invoke a surface preset. Amber is a color choice. Approximate highlights/transparency, not refraction, reflected environments, lipid construction or depth of field. |
| Smooth bonds: `new_licorice.png` | **Licorice**, new preset entry using the existing representation. | `licorice` is already sticks plus nonbonded spheres in `constants.py`. Reuse native geometry/sizes; keep actual bonds and atom colors. No renderer, rainbow recoloring or blur. |
| Bonds inside an envelope: `spheres2.jpg` | **Bond shell**, candidate new preset: translucent molecular surface over a thin bond network. | Reuse surface plus lines; compare against Balls in glass. Trial transparency in the existing 25/50/75% range. Show only real bonds, not a decorative network painted onto a surface. If too similar to Balls in glass, show that comparison for a decision rather than silently dropping it. |
| Contoured surface / interior: `surface_neo.jpg` | Existing surface plus **Figure** or **Comic** and Surface transparency. | No new preset for colors or pose. A cavity/cutaway uses existing surface/clipping controls explicitly; the image does not establish an electrostatic potential or real cut plane. |
| Bright tubes / wire: `neon1.png`, `neon2.png` | Existing **Spring** or **Wire**, trial with X-ray or strong existing highlights. | Bright edges are possible, emission is not. Do not force a black background. Compare this baseline with 15p. |
| Glow around atoms: `glow1.png`, `glow2.jpg`, `glow3.jpg` | Space filling plus a possible **Glow** effect, shared with neon. | A halo outside the silhouette needs image processing; lighting alone cannot provide it. 15p owns the experiment. No recoloring or extra atom geometry. |

**Question 123 (open):** A, recommended: four new entries, Space filling,
Illustrated atoms, Licorice and Bond shell; relabel Illustration as Contour
cartoon; reuse existing surface/light families for the rest. B: start with
Space filling and Illustrated atoms only, leaving the other two as manual
compositions. B reduces scope and needs the user's choice. For the renamed
entry, **Contour cartoon** is recommended; **Outlined cartoon** is another
descriptive option. Python entry points remain compatible.

Start with trial scripts using current commands. Compare each family on the
same structure, camera and colors, on light and dark backgrounds set by the
comparison script. Include a ligand, a multichain protein and nucleic acid
(the existing 1oky, 1aon and 1bna fixtures cover much of this). Record actual
viewport/ray pictures and build, frame and ray times where recipes add work.
References are resemblance targets, not pixel-exact acceptance images. Do
not add C++ rendering to compensate for a lighting, camera or color choice.

Implement selected recipes as small functions in `preset.py`, through
`from_menu` and `_prepare`. Preserve camera, molecular data and atom colors.
New protein presets retain established ligand/ion and solvent handling;
whole-molecule Space filling and Licorice explicitly show the same geometry
on ligands too, as today's Ball and stick does. Use current sphere/stick
sizes: ordinary presets preserve those user settings since 4.49.0. Do not
unconditionally reset them in `_prepare`; any new size override needs an
explicit reset/ownership decision first.

Lights are scene-wide even from object menus. For an automatically selected
illustration light, reuse `_lit_by_preset`: the next representation preset
clears it, while a manually selected light survives. Check the style list
in `layer3/MovieScene.cpp` for each new setting; scenes, PSE/PSEX and preset
Undo must retain it. No new style framework.

### 15n — one Transparency menu

Replace the top-level Cartoon transparency row with:

```text
Transparency
  Cartoon        > Opaque (0%) / 25% / 50% / 75%
  Spheres        > Opaque (0%) / 25% / 50% / 75%
  Surface        > Opaque (0%) / 25% / 50% / 75%
  Ball and stick > Opaque (0%) / 25% / 50% / 75%
```

These are the existing cartoon values; percentages mean transparency, not
opacity. A row changes appearance only: no showing a hidden representation,
light selection, recoloring, camera move or background change. No slider or
“all representations” row is needed for this request.

| Representation | Setting | Work |
| --- | --- | --- |
| Cartoon | `cartoon_transparency` | Reuse the object loop; preserve `preset.cartoon_transparency` as a callable. |
| Spheres | `sphere_transparency` | Existing core support; menu/helper and reset coverage. |
| Surface | `transparency` | Existing core support; test overrides from Glass and the surface recipes. |
| Ball and stick | Proposed `ball_and_stick_transparency` | **34d required.** `RepCylBond.cpp` forces zero transparency for this representation, including isolated balls. Sphere/stick transparency cannot implement this row. |

**Scope, question 124:** A, recommended: match today's cartoon control,
one value on each whole molecular object from `get_object_list(selection)`;
toolbar uses `enabled`, object menus their object. Selection menus must
state that these controls affect containing objects. B: atom/residue scope,
including a defined half-bond transition; more core work and a deliberate
change from cartoon's behavior. One ball-and-stick value covers both balls
and bonds independently of ordinary spheres/sticks. Do not expose an inert
row before 34d passes.

Under A, make the chosen value effective throughout each target object,
including lower-level overrides of that representation's transparency;
never clear another representation's settings or global user defaults.
Use an object loop for multi-object selections. The next molecular preset
resets these menu overrides on its target objects to inherited defaults,
following cartoon's lifetime; Light and solvent actions leave them alone.
Document this extension of reset behavior. Test nonzero global defaults,
existing atom overrides, multiple objects and disabled/unrelated objects.

### 15o — organize Presets after choosing recipes

Recommended hierarchy (question 125 A); all current actions remain:

```text
Presets
  Default
  Classified
  Cartoon > Pretty / Publication / Technical / B factor putty /
            Wire / Spring / Cylinders / Contour cartoon
  Atoms and bonds > Space filling / Illustrated atoms / Ball and stick /
                    Licorice
  Surface > Glossy / Candy glass / Frosted / Clay / Glass /
            Balls in glass / Bond shell
  Binding > Ligands / Ligand sites > [all current variants] /
            Protein interface / Protein-protein interaction /
            Antibody and antigen
  Transparency > [the four representations above]
  Show solvent / Hide solvent
  ── Scene appearance ──
  Light > [all current lights, Glossy (light only), Fog / No fog]
  Theme (colors and background) > [existing themes]
  Floor > [existing floor actions]
```

The last three remain direct submenus under a caption, not another nested
menu. Question 125 B: group only Cartoon and Transparency now, keeping the
other sections flat. A is recommended to accommodate the new families.
Grouping removes or renames no callable API.

**Background rule:** all new representation, light and transparency actions
leave solid/gradient/image backgrounds and export alpha unchanged. Existing
`preset.theme` deliberately sets colors and background (earlier answer 32).
Keep that separate feature with an explicit menu label; never invoke it
inside a new recipe. Ignoring example backgrounds does not require deleting
themes, floor or their APIs. Do not recreate amber/neon backgrounds.

Toolbar Presets and the existing viewport object/selection and sequence
popups share `menu.presets`; the current object A menu has no preset row.
Keep these entry points, without adding another. Recursive `_undoable` must
wrap each leaf exactly once, including deeper ligand-site and alpha rows.
Update tests matching flat labels or `theme > ...` without weakening their
assertions. Existing light/floor actions remain scene-wide. Use native Qt
keyboard navigation and accessible names.

### 15p — measured neon/glow experiment

**Question 122 answered 2026-11-26: existing rendering recipes first, then
a measured experiment for true glow.** The settings-only alternative was
not selected. This expands the historical “glow and blur left out” note
for glow alone; photographic blur/depth of field remain outside this task.

After recipe comparisons and 15b, test one optional halo effect through the
existing offscreen/FXAA path in `Scene.cpp`, `ShaderMgr` and `data/shaders/`.
Compare a source-colored silhouette glow with highlight bloom on atoms and
cartoon tubes, choosing the smallest convincing method. A molecular coverage
or emission mask must exclude background, labels and overlays: blurring
bright final-image pixels would make a white background glow. No compute
framework, new dependency or duplicate molecular objects; keep the existing
GLSL and platform constraints.

Record before/after frame time and GPU memory at the same viewport size,
on small and large structures with alpha and overlapping objects. Compare
FXAA on/off, transparent PNG, high-resolution Draw and Ray. Check Linux/WSLg,
Windows and macOS before promising parity. Ray output does not inherit a
viewport pass: shared image postprocessing versus an explicitly limited
first release is a choice to present with pictures and costs. No release
promise until the experiment establishes scope. If shipped, the effect is
off by default, survives scene/session/Undo, and preset switching clears
only effects selected by the preset. Background state stays unchanged;
an intentional halo may cover pixels around the molecule.

### Question 128 A: glow menu follow-up

Approved 2026-11-26; built in 4.91.0. Add one toggling row to
Presets > light, beside fog: "glow" when off, "no glow" when on. Reuse
the existing `glow` setting and the light menu's snapshot/Undo path in
`modules/pymol/menu.py` and `modules/pymol/preset.py`; no new renderer,
setting or dependency. It stays off by default and affects the viewport
only. Ray-traced pictures, differently sized images and stereo remain
outside this follow-up.

Check both labels and actions, keyboard access, Undo/Redo, scene/session
round trips and a real viewport toggle. Update the appearance guide to
make the viewport-only scope clear. The menu is a visible feature slice
and takes a new `X` version when implemented, not in this planning edit.

### Delivery and acceptance

| Slice | Deliverable | Required check |
| --- | --- | --- |
| 15m | Compare families, settle question 123, add selected recipes and the descriptive illustration label. | `testing/tests/api/preset.py`: visibility, colors, camera, background, disabled objects; A → B → Default; manual light survives. Viewport/ray comparisons with the current outline limitation stated. |
| 34d + 15n | Independent ball-and-stick alpha, then the common submenu; may ship as one feature slice. | `ball_and_stick.py`, `preset.py`, `menu.py`, `scene_style.py`, `snapshots.py`: all choices, independence, reset, isolated atoms, scene/session, Undo/Redo and viewport/ray images. |
| 15o | Group menus without losing actions. | `menu.py`, `action_toolbar.py`: each old/new action reachable and runnable, correct scope and one snapshot per leaf; keyboard walk in both entry points. |
| 15b | Approved viewport outline, also tested on illustrated spheres and transparent cartoon envelopes. | Pictures and frame times on black/white, including transparency; compare ray output. |
| 15p | Glow experiment and a decision from its pictures/costs. | Reproducible script and measurements before shipping a rendering option. |

For implementation, run targeted files with the existing test runner, then
the full suite. Core changes need a build, sanitizer checks and native-driver
validation. This planning update needs documentation consistency checks only;
it takes no version. Each shipped feature slice follows the version and
ChangeLog rules.

Skipped: a gallery/editor, palettes per image, copied artwork or watermark
removal, synthetic molecular arrangements, physical material/refraction
frameworks, and background changes hidden inside recipes. Glow remains a
planned experiment, not a skipped request.

## Earlier releases and decisions

**Built 2026-11-24 in 4.62.0: 15e.** Presets `balls_in_glass` ("balls in
glass": `ball_and_stick` in the atoms' colors inside a surface at
`ray_transparency_oblique_power` 20) and `cylinders` ("cartoon cylinders":
publication with `cartoon_cylindrical_helices` 1); `depth_fog`, a "fog" /
"no fog" row in the light menu; the look "soft" sets
`ambient_occlusion_mode` 1 at `ambient_occlusion_scale` 16, and glass,
balls in glass and illustration switch it off for their objects. Measured:
scale 16 was picked by eye on 1oky against 12, 20 and 25 (25 paints the
pockets black); a surface build of 1aon took 6.0 and 6.7 s without ambient
occlusion and 7.4 and 10.5 s with it, on 4v6x the noise was larger than the
difference. Left out: color steps in the viewport, because they are already
there: `ray_trace_mode` 3 switches `ray_trace_mode_3` on in
`anaglyph_header.fs` (45 colors counted in the viewport under "comic", 8436
under the standard light), so the table row "One new setting and a few
lines" below was wrong. Also left out: ambient occlusion in other looks,
glow and blur. At that date 15b was the only open slice; the request above
adds the new work.

**Plan revision 2026-11-23, drafts 3, 4 and 6, at 4.43.0 (not built):**
[34c](34-ball-and-stick.md) replaces the shared sticks/spheres ligand
recipe with independent ball-and-stick, ball scale 0.31, for ligands in all
applicable molecular presets. [35b](35-scene-appearance.md) makes stored
scenes restore the style and color overrides these presets change. The
earlier numerical recipes below describe shipped behavior, not future
defaults. The rule that presets preserve polymer cartoon/surface colors
still applies. Scene storage precedes the preset switch.

[Roadmap](../../PLAN.md) · Request 2026-11-16 · **15a done 2026-11-16 in
4.14.0, 15d in 4.14.3, 15f in 4.14.4.** 15b and 15e were approved on
2026-11-20; 15b stays open, 15e shipped in 4.62.0 and 15c in 4.22.0. **15g and 15h done 2026-11-18 in 4.14.5, 15i (visible objects, two
presets for complexes) in 4.19.1, 15j (the light after "illustration") in
4.19.2, 15k (publication green) in 4.19.3, 15l (cartoon spring, colors kept,
two-color interaction surface) in 4.19.29** (the last sections before "Skipped"). They change three decisions below: the looks are part of the
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

**Read for 15b on 2026-11-25, nothing built.** The picture that the FXAA
pass reads (`CShaderMgr::bindOffscreen`, `SceneRenderAA`) is a color
texture with a depth *renderbuffer* (`RenderTargetGL::layout` in
`layer0/GenericBuffer.cpp`), and a shader cannot read a renderbuffer. An
edge pass over the depth needs a depth texture on that target. The same
renderbuffer is handed to the pass for transparency mode 3
(`bindOffscreenOIT` takes `offscreen_rt->_rbo`), so that path has to be
given the texture too, or keep a renderbuffer of its own. The shaders are
GLSL 1.20, where a depth texture is read like any other. Only one driver
can be tried on this machine (d3d12 under WSLg, or llvmpipe).

**15b, outline in the viewport. Approved 2026-11-20, to build.** The answer:
"black, or a color that will be visible on the selected background". So the
line takes its color from the background, as the ray-traced outline does
since 15g: black on a light background, light on a dark one.
- A screen-space edge pass over the depth buffer after the scene is drawn,
  in `data/shaders/` and the Scene draw path of `layer1/`. New shader code,
  to be measured with `testing/compare.py -- gui` before and after.

**15c, ChimeraX object colors. Done 2026-11-20 in 4.22.0:** palette `chimerax`, the ten values of ChimeraX's `atomic_color_names`; listed for "any" background, since its purple is too dark for the contrast rule of the dark palettes.
- One more entry in `palettes.PALETTES` (tan, sky blue, plum, light green,
  salmon, ...), the pattern of [step 11](11-color-palettes.md). One line and
  the docstring.

Since 2026-11-20, second request: 15e is built together with the surface
looks and color themes of [step 25](25-studio-effects.md) (25b), which add
rows to the same menu and use the same code.

**15e, more effects. Approved 2026-11-20: all five of the question**
(color steps, fog, helices as cylinders, ambient occlusion in the soft look,
balls in glass). The sixth row of the table, glow and blur, was not part of
the question and stays unbuilt. Each was tried (table above) except the
first, which needs code.

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

## Request 2026-11-19: spring, colors kept, two-color surface (15l)

Done in 4.19.29. The example was a GIF of a designed binder on its target:
the target an orange surface with the contact patch in white, the binder a
thick blue tube.

- **Preset "cartoon spring"** (`preset.spring`): `cartoon tube` with
  `cartoon_tube_radius` 0.8 on the objects, ligands as sticks. A helix
  becomes a coil, hence the name. `_prepare` restores the radius, and
  already restored the cartoon type.
- **The row "wire" reads "cartoon wire".** `preset.wire` keeps its name.
- **No row but "default" colors the cartoon.** This replaces the answers
  to question 1 of 15h. A check runs every row of the menu and compares
  the colors.

  | Preset | Coloring removed |
  | --- | --- |
  | pretty, publication | rainbow over the protein carbons; the ligand colors skip the guide atom of a modified residue |
  | glass, cartoon wire, protein interface | by chain |
  | b factor putty | by B factor; the thickness still shows it |
  | illustration | shades of blue |
  | antibody and antigen | heavy and light chain blues; the antigen's sand and orange are now `surface_color` |
  | publication green | row removed: without its color it is "publication". The function stays and colors, like `preset.simple` |

- **Nucleic acids.** Their cartoon takes its colors from P and the base
  nitrogens (rendered: yellow DNA came out orange and blue). The
  by-element coloring of atoms other than carbon therefore skips nucleic
  acids in every preset (`preset.by_element`). Their lines in "technical"
  keep the colors they had; after loading those are element colors anyway.
- **"protein-protein interaction"** (`preset.interaction`): every chain
  an opaque surface, `surface_color` orange, and white on the residues
  within 4.5 A of another chain. The atom colors stay. No cartoon, sticks
  or contact dashes; "protein interface" has the sticks.
- Ray traced on 1BRS (barnase with barstar) on white: spring, wire,
  interaction, pretty, illustration, putty, each after coloring the two
  chains by hand.

| Option | Taken | Why |
| --- | --- | --- |
| Tube radius 0.5 (the default) | no | Thin next to the example. |
| Tube radius 0.8 | yes | The thickness of the example. |
| Interaction as in the GIF: largest chain a surface, the others as spring | no | The user picked every chain a surface. |
| Every chain a surface | yes | The user's answer. The white patches are mostly between the chains; a seam of white shows. |
| See-through surfaces with the cartoon inside | no | Not picked. |
| Exceptions that still color: default | yes | The user's answer: only the reset. |
| Exceptions: b factor putty, publication green, illustration | no | Not picked. |

Not done: the picture of the GIF itself (one chain a surface, its partner
a spring). Hiding the surface of one chain of an object leaves the other
chain's surface open at the contact (tried on 1BRS): the surface is that
of the whole object. With the two chains as two objects it works in two
typed steps (tried on 1BRS): `preset.interaction("all")`, which finds the
white patch, then `preset.spring("binder")`.

## Skipped

- Rows for Metal, Plastic and Rubber: see the table.
- Remembering the solvent choice after a restart. Add it with `QSettings`
  when asked.
- `look` as a typed command. `preset.look("flat")` works on the command line.
- A mark on the look that is active.
- The Lighting plugin reading `LOOKS`, and its sliders following a look.
- The old preset's white-stick limitation is superseded by step 34's
  independent colors and bond-color choice (question 59).
- The rest of the gist: Bondi radii, slate nitrogens, `valence_size`, its
  dash style, the orbital and density commands.
- The former exclusion of ball-and-stick ligands in "pretty", "publication"
  and "glass" is superseded: they are included in 34c.
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
