# 38 — Clear, current documentation with real demonstrations

[Roadmap](../../PLAN.md) · Requested 2026-11-26 · **planned, not built**.

Initial review: committed version **4.84.0**, revision `6a76b605`, the
user docs, command registration, GUI code, tests and ChangeLog. Menu grouping
was then committed as 4.85.0 (`1cd67a3b`) during planning; use its grouped
menu when writing the guides. Further GUI edits are in progress. Refresh
the baseline when writing and recording. No application was launched for
a GUI walkthrough, tutorial example rerun, new screenshot
captured or performance measured for this plan. Media lengths and sizes
below are proposed targets, not measurements.

The result should let a new user open a structure and save a useful picture,
then find the rest by what they want to do. An experienced user should be
able to look up a command, setting, shortcut or limitation directly. Cover
the current program, including retained core functions, not just additions
to the fork.

## What needs fixing first

| Finding in the current docs | Planned correction |
| --- | --- |
| `README.md` and Getting started reuse `docs/img/window.png`, identified in the roadmap as the 4.19 window. The image still has the old toolbar and footer. | Capture the current released window; reuse the same image in both places. |
| `features.md` mixes feature discovery, release history and long instructions in table cells. The presets cell combines representations, materials, lighting, themes and transparency. | Give each workflow a readable home; keep this page as a short overview with links. Keep chronology in ChangeLog. |
| Getting started says double-click to recall a scene; `scene_panel.py` uses a click or Enter. Its S-menu example still suggests sticks, which left that menu while the command remains. | Check every menu path and mouse/keyboard instruction against the running version. Teach current visible actions and distinguish command-only alternatives. |
| `features.md` says UI scale is 100–200%; the toolbar accepts 50–300%. WSLg defers a change until restart. | Explain global UI scale separately from Command/Sequence/Chat text size and state the platform exception beside the instruction. |
| The overview says every preset draws protein as cartoon, although surface and atom presets now exist. Broad promises that everything works unchanged also hide removals and compatibility limits. | Describe preset families and link explicit compatibility notes; avoid blanket claims. |
| `commands.md` has useful new-command entries, but unrelated functions accumulate under “Other”; several tables have blank lines between rows. | Organize by task, repair tables and add a command-name index. Move long GUI walkthroughs to guides. |
| New panels and workflows have little introductory help: properties/stars, linked ligand/sequence selection, scene appearance, movie editing and Chat setup. | Add task guides with prerequisites, concrete steps, results and relevant limits. |
| Package metadata sends Documentation to `features.md`; there is no dedicated docs home. | Point readers to the new home after it exists. Audit other documentation entry links. |

Existing material is the starting point: [Getting started](../getting-started.md),
[What is different](../features.md), [Commands](../commands.md),
[Install](../install.md), [Plugins](../plugins.md) and
[benchmarks](../benchmark.md). Preserve working links and useful explanations
when moving material. Keep license notices and attribution intact.

## Front pages and deeper pages

Recommended structure: ordinary Markdown in this repository, grouped by
task. A page earns its place by answering a distinct user question; related
small topics stay as sections. Proposed filenames below are destinations,
not pages that already exist.

| Level / page | What belongs there | What belongs deeper |
| --- | --- | --- |
| Project front: `README.md` | Plain description; Download and Start here links; current window screenshot; short examples of useful tasks; links to docs, help, compatibility and project information. Keep the existing sponsorship and required notices. | Full installation commands, feature history, every preset, parameters and benchmark tables. |
| Docs home: `docs/README.md` | “Start here”, “Choose a task”, “Look up a command”, “Solve a problem”. A short recent-features strip linking appearance, ligand and sequence guides. State the version checked. | Full workflows and developer plans. |
| First successful task: `docs/getting-started.md` | Open `1ubq` or a local structure; identify the window; rotate/select; choose a look; save PNG and a session; explain how to reopen it. One path with an expected result. | Advanced settings, optional packages and every file format. |
| Task guides: `docs/*.md` | One workflow family per page, short contents list, screenshots beside the relevant actions, command equivalents and links to reference details. | Complete signatures and historical decisions. |
| Reference: `docs/commands.md`, proposed `docs/reference.md` | Commands by task and by name; selection basics, settings, mouse/keyboard controls, supported input/output and compatibility. Exact names remain searchable. | Long tutorials or copied release notes. |
| Help: proposed `docs/troubleshooting.md` | Symptom → likely cause → concrete next step: missing dependency, unavailable action, hidden object, scale/restart, graphics/startup, network, export and session compatibility. | Build internals and design discussions. |
| Project/developer material | Existing install, plugins, contributing, licenses, benchmarks, ChangeLog and roadmap, linked from a small secondary area. | These must not become prerequisites for a normal user task. |

Suggested opening text: “Open a molecular structure, inspect its parts, and
make figures or short movies.” Follow it with actual actions, not a list of
technical improvements. A static screenshot leads the README; demo thumbnails
belong beside the task they explain. No wall of animated images at the top.

Search and navigation need to work without a new website:

- Docs home links every guide directly. Each guide links back to it and ends
  with the relevant next task and command reference.
- Use headings a user would search for: “Make a surface transparent”, “Find
  the next ligand”, “Align sequences”, “Save a movie”. Include the actual
  command or menu name alongside the plain phrase.
- Keep a compact alphabetical index in the command reference; use aliases
  such as “opacity / transparency”, “alignment / fit” and “rating / stars”.
  Explain browser Find, repository search restricted to `docs/`, and the
  application's `help <command>` and Tab completion. These are different
  tools; browser Find does not search the whole documentation.
- Preserve old heading anchors where practical; otherwise leave a short
  pointer under the old heading and update incoming links in the same change.
- A hosted site with full-text search remains an explicit option below. Do
  not promise site search while the docs are repository Markdown.

## Coverage: every function has a place

First make a coverage checklist in this plan during implementation. Compare
the actual `cmd.keyword` registry and public Python API/docstrings with
`modules/pymol/keywords.py`, GUI actions/tooltips, settings, ChangeLog and
tests. Use a clean profile without startup plugins. For each user-facing
action or public command record its documentation destination and whether it
was checked. Account for aliases, optional commands and inherited functions;
registration alone does not prove that a function works.

Every current GUI action and public command needs a discoverable reference
entry or a clear pointer to its in-app help. New/changed fork commands need
full entries. Common retained functions need worked examples. Less-used
inherited functions can have concise name/purpose/help entries; do not copy
hundreds of docstrings into multiple guides. Record undocumented or broken
help as a gap, not as completed coverage. Settings get an index/pointer to
built-in help, with the commonly used and fork-specific ones explained.

| Guide / destination | Essential coverage | Source and existing checks to consult |
| --- | --- | --- |
| Getting started; proposed `structures.md` | Open files/folders, fetch PDB/UniProt/predictions, download limits and background work, naming/groups, select/split/extract, show/hide, rename/reorder/Delete. Explain predicted confidence and that fetched ideal ligands are not binding poses. | `importing.py`, `fetching.py`, `grouping.py`, Qt file dialogs and Objects panel; importing/fetching/grouping/object-panel tests. |
| Proposed `appearance.md` | Representation versus preset versus palette/theme/light; cartoon, ball-and-stick, atom and surface recipes; glossy/candy glass/frosted/clay; transparency and its whole-object scope; colors that presets keep; reset/Undo; background/floor/mirror/fog; Draw versus Ray and outlines. Include Solid versus optional Solid (grid), without making it the default. | `preset.py`, `menu.py`, `palettes.py`, toolbar, representation/settings code; preset/ball-and-stick/palette/render tests. |
| Proposed `ligands.md` | Find next/previous ligand, pocket residues and contacts, independent ball-and-stick size/color, CPK, 2D panel legend, linked residue selection, Show in 3D, SVG/PNG export; optional RDKit and limits of contact interpretation. | `ligand_nav.py`, `ligand2d.py`, Qt ligand panel; ligand-navigation/ligand2d/ligand-panel tests. |
| Proposed `sequences.md` | Sequence tab versus alignment window, Mode/Labels/Gaps and font controls; loaded chains/FASTA, MAFFT, search, linked selection, secondary structure, reference, sequence alignment versus coordinate fitting, identity/statistics/export, persistence and Undo limits. | `sequence.py`, Qt sequence tab/panel; sequence-tab/sequence-window tests. |
| Proposed `properties.md` | Open the table, object rows versus atom details, columns/filter/sort/edit, counted fields, Follow/picked atom, stars, CSV/TSV/XLSX import and CSV export, session persistence. Explain imported name matching. | Qt property table/properties dialog; property-table/session-extra tests. |
| Proposed `scenes-movies.md` | Store/recall/update/rename/reorder scenes, which appearance settings they retain; states versus movie frames; Movie toolbar, shots/tours, record views, drag/resize, fades, playback, session persistence, export and encoder requirements. | `viewing.py`, `movie.py`, scene panel/timeline/export dialog; scene-style/scene-panel/timeline/movie tests. |
| Proposed `editing-analysis.md` | Builder/SMILES, bonds and hydrogens, clean/remove additives, ligand optimization versus protein repair/relaxation and their limits; measurements/labels, polar/pi contacts, fit/super/CE alignment, morph, maps/meshes/volumes, trajectories/states, symmetry and basic selections. | `editing.py`, `creating.py`, `querying.py`, `fitting.py`, cleanup/SMILES/map APIs and wizards; corresponding API tests. |
| Proposed `saving.md` | Session versus structure versus image/movie; `.psex` versus `.pse`, fork-specific state in upstream software, PDB/mmCIF/SDF/MOL, PNG dimensions/background/Draw/Ray, batch export, optional glTF and STL output. List retained formats by actual read/write support. | `exporting.py`, Qt file dialogs, `session_extra.py`; session-psex/session-extra/exporting tests. |
| Proposed `assistant.md` | Where Chat is; provider setup, API key versus browser sign-in versus installed Claude Code, `ai` extra/bundle differences; Send/Stop/Undo, reviewed commands, confirmations, Run without asking, Trusted Python, data sent to providers; connector on/off/setup and current limitations. | `assistant.py`, `agent.py`, `agent_server.py`, Chat panel; assistant/agent/agent-server tests and live-trial status in plan 31. |
| Commands/reference; install/plugins/help | Common `cmd.*` scripting and `.pml`, selection language, help/completion, shortcuts/mouse modes and customization, optional packages, platform differences, plugin compatibility and removed functions. | `cmd.py`, command registry/docstrings, settings, keymapping, build metadata/CI, docs and system tests. |

Do not repeat live command counts as durable promises. Keep measured speed
claims with their workload, version/date and benchmark link, outside the
introductory workflow. Planned viewport outlines, glow, general Undo and
other unfinished features stay in the roadmap. Use the grouped menu of
4.85.0; update further menu/footer labels after they are committed and checked.
Changing controls must not stall the rest of
the writing.

## Plain language without losing essentials

Each guide starts with the result and prerequisites, then gives the shortest
working sequence. Explain a term on first use: a representation is how atoms
are drawn; a scene saves a view and its appearance; a session saves work to
continue later. Use actual menu labels, direct verbs and one action per step.

After the steps, give the expected result, the command equivalent where
useful, and a short “Limits and common problems” section. Keep essential
limits beside the affected action as well: an operation's target, whether it
changes coordinates or removes atoms, what Undo restores, extra packages,
network use and output compatibility. No claim that Undo covers everything.

For example, replace a long transparency table cell with: “Open Presets >
transparency > surface and choose 50%. This changes the surface of the target
objects. It keeps their colors. Choosing another preset resets this value.”
Verify final capitalization/path in the recorded version. Link the exact
setting and object/state scope below the example.

Separate the GUI steps from command syntax. Use runnable examples with named
inputs and expected outputs, rather than unexplained placeholders. Include
keyboard routes where supported. Tables are for short comparisons, not
paragraphs. A screenshot supplements instructions; it never carries the only
copy of a step, limitation or label.

## Real screenshots

Use the running application's output. No generated/mock UI, staged success
from a test provider or plan reference picture presented as the product.
Existing rendered examples (`surface-looks.jpg`, `reference-recipes.jpg`,
`stage.jpg`, `themes.jpg`) are candidates for reuse after checking their
recipe/version; label them as rendered results, not GUI screenshots. Palette
strips and the older ligand panel need checking against their current state.

| Capture | What the user should learn | Placement |
| --- | --- | --- |
| Current full window | Where the toolbar, Objects/footer and Command/Sequence/Chat tabs are. Use a readable protein/ligand example and ordinary layout. | README and Getting started; a numbered text legend in the guide. |
| Presets and transparency | How the actual menu reaches the result; a small before/after comparison on the same structure/camera. Show viewport and ray output separately where outlines differ. | Appearance; one result thumbnail on docs home. |
| Ligand 2D beside its 3D pocket | The contact legend, selected residue and Show in 3D agree. | Ligands; thumbnail on docs home. |
| Sequence tools | The tab controls, then the alignment window with matching residues highlighted in 3D, secondary structure and fit results. | Sequences; alignment thumbnail on docs home. |
| Property table | Useful named columns, stars and Follow on a selected object; no unexplained spreadsheet full of numbers. | Properties. |
| Scenes and timeline | Scene thumbnails, shots/ruler and playback/export controls. | Scenes and movies. |
| Chat setup and a completed turn | Current provider controls and a visible action/result/Undo. Label the setup screen separately if no real provider trial is available. | Assistant guide only; completed-turn image waits for a successful real trial. |

Record in proposed `docs/media/README.md`: filename, page, app version/commit,
capture date, OS, theme/UI scale, structure identifier/source, preparation
commands and click sequence. Reuse small public structures and existing test
inputs where suitable, such as `testing/data/1oky.pdb.gz` for ligand contacts;
keep a documented PDB fetch alternative for readers. Choose and verify any
new sample before promising a result. Keep source attribution with the recipe.

Use a clean temporary profile and disposable output directory, not the user's
`.pymolrc`, sessions or saved layout. Keep the text readable at the page's
display size, crop dead space, and retain enough window context to identify
the control. Hide account details and local private paths. Prefer clean
captures over later redaction; annotations must not alter the observed result.

Still images live in `docs/img/`; short clips in proposed `docs/media/`.
Prefer PNG for UI text and screenshots. Proposed delivery targets: stills
below about 500 KB when legibility permits; clips below about 5 MB; a GIF,
if used, below about 2 MB. Measure the actual sizes and playback/readability
before accepting them. Do not add a media framework or runtime dependency.

## A few short demonstrations

Recommended first set: four focused clips. Durations are estimates for
planning; show one useful action sequence with a stable starting and ending
frame. Static posters and the written steps must work without playback.

| Clip | Storyboard | Estimated length / destination |
| --- | --- | --- |
| Change a look | Pick a surface material → adjust surface transparency → change light → Undo. Keep camera/colors fixed so the effect is clear. | 15–25 seconds; Appearance. |
| Inspect a ligand | Next ligand → pocket contacts/zoom → open 2D → select a residue → show its contacts in 3D. | 15–25 seconds; Ligands. |
| Work with sequence | Open alignment window with prepared rows → select residues and show 3D highlight → fit against the reference → show fit result/Undo. Explain that sequence alignment alone does not move structures. | 20–35 seconds; Sequences. |
| Turn scenes into a movie | Recall saved looks → open Movie timeline → add a scene tour → resize a shot → play → show the export choice. Link the full export steps below. | 20–35 seconds; Scenes and movies. |

Record the GUI with an available screen recorder; the application's movie
export captures molecular animation, not the interface steps of a tutorial.
Use available capture/encoding tools; installing another tool is a separate
choice. Prefer MP4 opened from a linked PNG poster for repository Markdown.
Check playback on the actual documentation destination before settling the
format; add a direct download link as fallback. No autoplay or sound needed.
If a GIF is chosen, make it a brief cropped action; keep the written/static
equivalent and a controllable video alternative for motion-sensitive readers.

Use concise captions, a visible pointer and pauses at clicks/results. Do not
edit a failed operation into apparent success. Mark time cuts in long loads,
alignments or renders; sped-up footage is not performance evidence. A Chat
demo can follow the real provider trial in step 31; it does not hold up these
local demonstrations and must not imply unverified sign-in support.

## Delivery and checks

| Slice | Deliverable | Done when |
| --- | --- | --- |
| 38a — inventory and corrections | Complete the coverage checklist; fix stale facts, broken tables and compatibility/dependency claims in existing pages. | Entries map to current code/help; guide examples have concrete inputs; uncertainties are named. |
| 38b — front pages and navigation | README, docs home and Getting started; shorter features overview and updated documentation entry links. | A reader can find download, first picture, a task, a command and troubleshooting without reading a plan. Existing links remain usable. |
| 38c — guides and reference | Workflow pages from the coverage table, command/setting/shortcut/file reference and troubleshooting. | Every inventory item has a destination; examples/menu paths are checked in the current version and missing optional packages have useful instructions. |
| 38d — capture and publish media | Current window, focused screenshots, the four clips, posters, captions and capture recipes. | Real UI checked; readable at display size; correct results; links/playback/fallbacks work; actual sizes/version recorded. Final menu/footer captures follow their current implementation. |

These are documentation tasks: no program version or ChangeLog entry unless
a separate application change is made. Commit each completed slice with a
`docs` subject and record its state here and in the roadmap; no shipped
feature is claimed merely because the plan or screenshots exist.

Validation during implementation:

- Rerun tutorial commands from a clean session using the named inputs; open
  saved sessions and exported files. Check optional-feature examples in an
  environment that actually has their prerequisites. Record what was not tried.
- Walk GUI tutorials and keyboard routes in the real window. A screenshot
  does not establish behavior on another OS. Keep Windows/macOS scale checks
  and real Chat account trials explicitly open where they remain untested.
- Reuse `testing/tests/system/license_docs.py` for relative paths and notice
  preservation. It currently scans top-level docs and does not validate
  anchors, nested media recipes, external links or playback: check these
  separately and extend the existing check only where new structure needs it.
- Review rendered pages, tables, headings, alt text, captions and links. Try
  the documentation path from README and package metadata. Verify current
  external installation/provider links when writing those instructions.
- Have a reader unfamiliar with the UI follow the first-picture guide and
  find transparency, sequence alignment and session compatibility. If no
  reader is available, record a clean-profile walkthrough as the fallback,
  without calling it a user study.

Future visible changes update the owning guide and affected screenshot/clip
in the same feature work. Put “Checked with version …” on guides and media
recipes; keep dates out of every paragraph. Refresh changed captures only,
not the entire gallery at each release.

## Choices for the user

| No. | Choice | Options |
| --- | --- | --- |
| 126 | Documentation destination | **A, recommended:** repository Markdown with a docs home and task/name indexes; works with the existing project and adds no docs stack. **B:** a separate documentation website with full-text search, built from the same Markdown; select hosting/build/search tooling in a follow-up before adding dependencies. |
| 127 | Short-demo presentation | **A, recommended:** videos opened from static screenshot posters, GIF only for a small action where useful. **B:** small inline GIF-style loops in guides, with static/written equivalents and controllable videos; more animation and media to maintain. |

Both questions were asked during planning. Unanswered recommendations are
not decisions. The content inventory and writing structure work with either
destination; site implementation and final encodings follow the answers.

Skipped: implementing the docs or recording media in this planning task;
automatic API-site generation, a new search service, paid-account trials and
a promotional video. No existing data, images, license text or application
behavior is removed by this plan.
