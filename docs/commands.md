# Commands

[Docs home](README.md) · Checked with version 4.90.0.

Everything the window does can also be typed. This page lists the commands
pymolish-studio adds to PyMOL, by task, and then every command by name.

**On this page:** [How commands work](#how-commands-work) ·
[Words you might search for](#words-you-might-search-for) ·
[Commands added by pymolish-studio](#commands-added-by-pymolish-studio) ·
[All commands by name](#all-commands-by-name)

## How commands work

Type a command in the line at the bottom of the window (the **Command** tab)
and press Enter. Arguments are separated by commas:

```
fetch 1ubq
show surface, chain A
png picture.png, dpi=300, ray=1
```

| To | Do |
| --- | --- |
| Read the help of a command | `help png` |
| Complete a command, a name or a file | Tab |
| List the arguments of a command | `png ?` |
| Run a file of commands | `@script.pml` or File > Run Script... |
| Run a Python script | `run script.py` |
| Call a command from Python | `cmd.png("picture.png", dpi=300, ray=1)` |

Every command is also a Python function of the same name in the module
`cmd`. The window, the menus and the plugins call these functions.

To search these pages: your browser's Find searches one page only. To search
all of them, search the repository restricted to `docs/`, or use the
[docs home](README.md), which links every guide. Inside the program,
`help <command>` and the Tab key search the commands themselves.

## Words you might search for

| You look for | It is called | Where |
| --- | --- | --- |
| opacity, see-through | transparency | [Appearance](appearance.md) |
| style, look, rendering mode | preset, representation | [Appearance](appearance.md) |
| superpose, overlay, fit | `align`, `super`, `cealign` | [Editing and analysis](editing-analysis.md), [Sequences](sequences.md) |
| alignment of sequences | `sequence_align`, the Sequence alignment window | [Sequences](sequences.md) |
| rating, favorites | stars | [Property table](properties.md) |
| spreadsheet, scores, CSV | property table, `load_table` | [Property table](properties.md) |
| binding site, pocket | `ligand_next`, Ligand 2D | [Ligands](ligands.md) |
| hydrogen bonds | polar contacts, `distance` with `mode=2` | [Editing and analysis](editing-analysis.md) |
| snapshot of a view | scene | [Scenes and movies](scenes-movies.md) |
| animation, video | movie, Timeline | [Scenes and movies](scenes-movies.md) |
| project file | session, `.psex` | [Saving](saving.md) |
| screenshot, figure | `png`, Draw, `ray` | [Saving](saving.md) |
| AlphaFold, predicted model | `fetch_fold` | [Structures](structures.md) |
| AI, chatbot, MCP | Chat, `ask`, `agent_server` | [Assistant](assistant.md) |

## Commands added by pymolish-studio

Commands that PyMOL does not have. Each one works on the command line, in
scripts as `cmd.<name>`, and has `help <name>`. They replace the commands of
the older pymolish plugin, which is no longer loaded.

### Groups

More in [Structures](structures.md).

| Command | What it does | Example |
| --- | --- | --- |
| `group_next [group]` | Shows the next member of a group and hides the others. Key: Ctrl-N. | `group_next poses` |
| `group_previous [group]` | The same, backward. Key: Ctrl-P. | `group_previous` |
| `group_enable group [, each]` | Shows the members of a group, or every n-th one. | `group_enable poses, 10` |
| `group_disable group [, each]` | Hides the members; the group stays enabled. | `group_disable poses` |
| `copy_group group [, new_group [, suffix]]` | Copies a group with all members, groups inside it included. | `copy_group poses, backup, _bak` |
| `sort_group group [, reverse]` | Sorts the members by name, ignoring case. | `sort_group poses` |
| `extract_chain selection [, chains [, group]]` | Makes one new object per chain, `<object>_<chain>`. The source is not changed. | `extract_chain poses, A+B, poses_AB` |
| `split_types [selection [, group]]` | Makes one new object per kind of molecule, `<object>_<kind>`: protein, nucleic, membrane, ligand, ions, solvent, other. The source is switched off. | `split_types 1abc` |
| `cluster_ligands selection [, count [, cutoff [, prefix]]]` | Sorts objects into groups by where they are: by a distance cutoff, or into a given number of groups. | `cluster_ligands poses` |
| `color_group_with_gradient selection [, color]` | Gives every object its own shade of one color, dark to light. | `color_group_with_gradient poses, orange` |

The group row in the Objects panel has four of them in its A menu:
duplicate group, sort members (a second click sorts Z to A), enable members,
disable members.

### Many files at once

More in [Structures](structures.md) and [Saving](saving.md).

| Command | What it does | Example |
| --- | --- | --- |
| `load_files [directory [, format [, group [, pattern [, recursive [, prefix]]]]]]` | Loads every file of one format from a folder, one object per file. Unreadable files are reported and skipped; no object is replaced. | `load_files ~/poses, sdf, poses` |
| `export_objects selection [, directory [, format [, overwrite]]]` | Saves every object of a selection (a group, a name pattern, any selection) to `<object>.<format>`. Files that exist are skipped unless `overwrite=1`. | `export_objects poses, ~/out, pdb` |

In the window: File > Open Folder... and File > Export Objects.... Both show
the command they will run.

### Structures from the internet

More in [Structures](structures.md).

| Command | What it does | Example |
| --- | --- | --- |
| `list_uniprot_structures accession` | Prints the PDB entries of a protein with method, resolution and chains. Loads nothing. | `list_uniprot_structures P04637` |
| `fetch_by_uniprot accession [, limit [, group [, async_]]]` | Downloads the PDB entries of a protein into one group. Give a limit: a well studied protein has hundreds. | `fetch_by_uniprot P00918, 5` |
| `fetch_uniprot_ligands accession [, min_weight [, limit [, group [, async_]]]]` | Loads every different small molecule found in the PDB entries of a protein into the group `<accession>_ligands`. Each is the ideal model, alone, not in its binding place. Ions and additives lighter than `min_weight` (100 Da) are left out. | `fetch_uniprot_ligands P00918, limit=20` |
| `fetch_fold query [, name [, color [, async_]]]` | Loads a predicted structure: from AlphaFold DB for a UniProt accession or an AlphaFold id, from the ESMFold server for a sequence. | `fetch_fold P04637` |
| `color_plddt [selection [, legend]]` | Colors a predicted model by confidence with the four AlphaFold DB colors and adds a legend. | `color_plddt AF_P04637_F1` |

In the window: File > Get by UniProt... and File > Get Predicted
Structure.... These commands ask rest.uniprot.org, data.rcsb.org,
files.rcsb.org, alphafold.ebi.ac.uk and api.esmatlas.com; a sequence given
to `fetch_fold` is sent to the ESMFold server.

### Molecules from SMILES

More in [Editing and analysis](editing-analysis.md).

| Command | What it does | Example |
| --- | --- | --- |
| `load_smiles smiles [, name [, conformers [, group]]]` | Builds a molecule from a SMILES in quotes, with hydrogens and minimized 3D coordinates; conformers become states. A text or CSV file gives one molecule per line (SMILES, then an optional name). | `load_smiles "CC(=O)Oc1ccccc1C(=O)O", aspirin` |

In the window: Build > From SMILES..., filled from the clipboard. Needs
rdkit: the downloadable builds have it, a pip install needs
`pip install 'pymolish[chem]'`.

### Sequence

The full walkthrough of the Sequence tab and the alignment window is in
[Sequences](sequences.md).

| Command | What it does | Example |
| --- | --- | --- |
| `search_sequence pattern [, name [, selection]]` | Selects the residues of every protein chain that match a sequence or a regular expression. | `search_sequence N[^P][ST], sequon` |
| `sequence_align filename [, output [, executable]]` | Aligns FASTA with local MAFFT; returns aligned FASTA and optionally writes it. No coordinates change. | `sequence_align sequences.fasta, aligned.fasta` |

`sequence_align` needs MAFFT on this computer:
[MAFFT installation](install.md#optional-sequence-alignment).

### Repair

More in [Editing and analysis](editing-analysis.md).

| Command | What it does | Example |
| --- | --- | --- |
| `fix_structure selection [, missing_atoms [, hydrogens [, ph [, nonstandard [, keep_water [, keep_heterogens [, name]]]]]]]` | Repairs a protein with PDBFixer and loads the result as `<object>_fixed`: missing atoms, hydrogens for a pH, nonstandard residues. The original stays. | `fix_structure 1abc, ph=5.5` |
| `minimize selection [, maxiter [, name]]` | Relaxes a protein with OpenMM (Amber14, implicit solvent), heavy atoms held near their place; the result is `<object>_min`. Needs complete residues and no ligands. | `minimize prot` |

`clean` is a PyMOL command that works here: it minimizes one small molecule
with rdkit. In the window: A > clean on an object, a group or a selection.
`fix_structure` and `minimize` need pdbfixer and openmm: the downloadable
builds have them, a pip install needs `pip install 'pymolish[fix]'`.

### Colors and looks

More in [Appearance](appearance.md).

| Command | What it does | Example |
| --- | --- | --- |
| `palette [name [, recolor]]` | Sets the colors that new objects cycle through. | `palette vivid` |
| `stage [mode [, selection]]` | A floor under what is shown; ray traced, the molecule casts its shadow on it. `stage mirror` adds a mirror image, `stage off` removes it. | `stage` |
| `show ball_and_stick, sele` / `hide` / `as` / `toggle` | A representation of its own: a ball on every atom and its bonds as thin sticks that show single, double, triple and aromatic order. Lines, sticks and spheres neither show nor hide it. Select with `rep ball_and_stick`. | `show ball_and_stick, organic` |
| `set ball_and_stick_scale`, `ball_and_stick_bond_radius`, `ball_and_stick_color`, `ball_and_stick_transparency` | Ball size (0.25), bond radius (0.12), color and transparency of `ball_and_stick` only; `unset` goes back. | `set ball_and_stick_color, atomic, resn STU` |
| `color_cpk [selection [, representation]]` | Colors by element in the CPK colors of RasMol. With `ball_and_stick` as representation only the balls and sticks are colored. | `color_cpk organic` |

### Ligands

More in [Ligands](ligands.md).

| Command | What it does | Example |
| --- | --- | --- |
| `ligand_next [selection [, step]]` | Goes to the next ligand (`step` -1: the previous one), shows it with the residues around it and its polar contacts, and zooms on the site. `step=0` clears. Keys: Ctrl-Shift-M and Ctrl-Shift-H. | `ligand_next` |
| `ligand_2d [ligand [, cutoff [, filename]]]` | Draws a ligand flat with the residues around it and its contacts, as SVG or PNG; without a file name it lists the contacts. Needs rdkit. | `ligand_2d resn STU, filename=lig.svg` |

### Property table

More in [Property table](properties.md).

| Command | What it does | Example |
| --- | --- | --- |
| `load_table filename [, object_column]` | Sets object properties from a CSV, TSV or Excel (`.xlsx`, first sheet) file: one row per object, matched by name; new headers become new properties. | `load_table scores.csv` |
| `save_table filename [, selection]` | Writes the properties of the objects as CSV. | `save_table scores.csv` |

### AI assistant

More in [Assistant](assistant.md).

| Command | What it does | Example |
| --- | --- | --- |
| `ask [prompt]` | Opens the Chat tab with a draft prompt; Send starts the conversation with the provider chosen there. | `ask color the ligand by element` |
| `agent_server [action [, port]]` | `on` lets an AI agent on this computer (Claude Code, Codex) work in this session through MCP, on 127.0.0.1 only, with a token. It prints the line that connects each client. `off` closes it. | `agent_server on` |

### Other

The commands that were listed under this heading now have their own
sections above: [Colors and looks](#colors-and-looks), [Ligands](#ligands),
[Property table](#property-table) and [AI assistant](#ai-assistant).

### PyMOL commands that needed the commercial build

These commands exist in open-source PyMOL only as stubs that raise
"Incentive-Only-Error". Here they work.

| Command | What it does | Example |
| --- | --- | --- |
| `save file.stl` | Writes the geometry on display as a binary STL file (triangles, no colors), for 3D printing. | `save model.stl` |
| `assign_stereo [selection [, state]]` | Fills the atom property `stereo` with R or S, with rdkit. Then `label`, `select stereo R` and `iterate` see it. Also in the window: L > other properties > stereochemistry. | `assign_stereo organic` |
| `pi_interactions name [, selection1 [, selection2]]` | Dashes between ring centers (pi-pi) and between a ring center and a positive charge (pi-cation). `distance` with mode 6 or 7 gives one kind only. In the window: A > find > pi interactions. | `pi_interactions pi, 1rx1` |
| `focal_blur [aperture [, samples [, ray [, filename]]]]` | A picture in which only what is near the origin of rotation is sharp. | `focal_blur 3.0, 50, ray=1` |
| `morph name, sele1 [, sele2 [, state1 [, state2 [, refinement [, steps]]]]]` | An object whose states lead from one conformation to another: straight lines, then sculpting of every intermediate state. | `morph mout, 1akeA, 4akeA` |

`assign_stereo` needs rdkit, as `clean` does. RigiMOL morphing, reading STL
and the readers for Maestro, MOE and Phase files are not part of this
program.

## All commands by name

Every command the program registers, with what it is for and the guide that
uses it. `help <name>` prints the full description and the arguments.
Commands marked **new** are the ones pymolish-studio adds.

| Command | What it does | Guide |
| --- | --- | --- |
| `abort` | Stops a running command script. | [Reference](reference.md) |
| `accept`, `decline` | Internal: answer the security question of a session file. | |
| `agent_server` | **new** Lets an AI agent on this computer use the session through MCP. | [Assistant](assistant.md) |
| `alias` | Gives a line of commands a short name. | [Reference](reference.md) |
| `align` | Fits one structure on another after aligning their sequences. | [Editing and analysis](editing-analysis.md) |
| `alignto` | Fits every loaded object on one target. | [Editing and analysis](editing-analysis.md) |
| `alphatoall` | Copies a property of the CA atoms to all atoms of their residues. | |
| `alter` | Changes atom properties (name, chain, b, color ...) with an expression. | [Editing and analysis](editing-analysis.md) |
| `alter_state` | Changes atom coordinates of one state with an expression. | |
| `angle` | Shows the angle between three atoms as a measurement object. | [Editing and analysis](editing-analysis.md) |
| `api` | Prints the Python function behind a command. | [Reference](reference.md) |
| `as`, `show_as` | Shows one representation and hides the others. | [Appearance](appearance.md) |
| `ask` | **new** Opens the Chat tab with a draft prompt. | [Assistant](assistant.md) |
| `assign_stereo` | Fills the atom property `stereo` with R or S (needs rdkit). | [Editing and analysis](editing-analysis.md) |
| `attach` | Adds one atom to the picked atom. | [Editing and analysis](editing-analysis.md) |
| `backward`, `forward` | Moves the movie one frame back or forward. | [Scenes and movies](scenes-movies.md) |
| `bg_color`, `bg_colour` | Sets the background color. | [Appearance](appearance.md) |
| `bond`, `unbond` | Creates or removes bonds between two selections. | [Editing and analysis](editing-analysis.md) |
| `button` | Redefines what a mouse button does. | [Reference](reference.md) |
| `cache` | Manages stored results such as surfaces. | |
| `capture` | Internal: copies the viewport image. No help text. | |
| `cartoon` | Sets the cartoon type of atoms (loop, tube, putty ...). | [Appearance](appearance.md) |
| `cd`, `pwd`, `ls`, `dir` | Changes, prints or lists the working directory. | [Reference](reference.md) |
| `cealign` | Fits two proteins by structure alone (CE algorithm). | [Editing and analysis](editing-analysis.md) |
| `center` | Moves the view to the middle of a selection. | [Getting started](getting-started.md) |
| `centerofmass` | Prints the center of mass of a selection. | |
| `check`, `fix_chemistry`, `h_fix`, `map_trim`, `overlap`, `sculpt_purge`, `vdw_fit` | Unsupported leftovers of PyMOL; their help says so. | |
| `clean` | Minimizes one small molecule with rdkit (MMFF94). | [Editing and analysis](editing-analysis.md) |
| `clip` | Moves the clipping planes. | [Reference](reference.md) |
| `cls` | Clears the log. | |
| `cluster_ligands` | **new** Sorts objects into groups by where they are. | [Structures](structures.md) |
| `color`, `colour` | Colors atoms or objects. | [Appearance](appearance.md) |
| `color_cpk` | **new** Colors by element in the CPK colors. | [Appearance](appearance.md) |
| `color_deep` | Colors and removes the color settings below the global level. | |
| `color_group_with_gradient` | **new** Gives every object its own shade of one color. | [Structures](structures.md) |
| `color_plddt` | **new** Colors a predicted model by confidence. | [Structures](structures.md) |
| `config_mouse`, `mouse` | Chooses the set of mouse modes, or steps through them. | [Reference](reference.md) |
| `copy` | Copies an object. | [Structures](structures.md) |
| `copy_group` | **new** Copies a group with its members. | [Structures](structures.md) |
| `copy_to` | Copies a selection into another object. | |
| `count_atoms` | Counts the atoms of a selection. | [Editing and analysis](editing-analysis.md) |
| `count_discrete`, `count_frames`, `count_states` | Counts discrete objects, movie frames or states. | |
| `create` | Makes a new object from a selection. | [Structures](structures.md) |
| `curve_new` | Makes a curve object for moving the camera along a path. | |
| `cycle_valence` | Steps the picked bond through single, double, triple. | [Editing and analysis](editing-analysis.md) |
| `delete` | Removes objects and named selections. | [Structures](structures.md) |
| `delete_states` | Removes states from an object. No help text. | |
| `deselect` | Switches off the shown selections. | [Structures](structures.md) |
| `diagnostics` | Prints system information for a bug report. | [Troubleshooting](troubleshooting.md) |
| `dihedral` | Shows the dihedral angle between four atoms. | [Editing and analysis](editing-analysis.md) |
| `disable`, `enable` | Switches objects or selections off or on. | [Structures](structures.md) |
| `distance` | Shows distances or contacts between two selections. | [Editing and analysis](editing-analysis.md) |
| `drag` | Lets the mouse move the atoms of a selection. | |
| `draw` | Makes a picture of the view with the graphics card. | [Saving](saving.md) |
| `dss` | Assigns secondary structure from the geometry. | [Sequences](sequences.md) |
| `dump` | Writes the geometry of a mesh, surface or map to a text file. | |
| `edit`, `unpick` | Picks atoms or a bond for editing; removes the picks. | [Editing and analysis](editing-analysis.md) |
| `edit_mode` | Switches the mouse to editing. | [Reference](reference.md) |
| `editing_ring` | Cut, copy and paste of selected atoms (Ctrl-X, Ctrl-C, Ctrl-V). | [Reference](reference.md) |
| `embed`, `load_embedded` | Marks data inside a command script and loads it. | |
| `export_objects` | **new** Saves every object of a selection to its own file. | [Saving](saving.md) |
| `extra_fit` | Fits several objects on one reference. | [Editing and analysis](editing-analysis.md) |
| `extract` | Moves a selection into a new object. | [Structures](structures.md) |
| `extract_chain` | **new** Makes one new object per chain. | [Structures](structures.md) |
| `fab`, `fnab` | Builds a peptide, or a nucleic acid, from a sequence. | [Editing and analysis](editing-analysis.md) |
| `feedback` | Sets how much the program prints. | [Troubleshooting](troubleshooting.md) |
| `fetch` | Downloads a structure or a map by its code. | [Structures](structures.md) |
| `fetch_by_uniprot` | **new** Downloads the PDB entries of a protein into a group. | [Structures](structures.md) |
| `fetch_fold` | **new** Loads a predicted structure. | [Structures](structures.md) |
| `fetch_uniprot_ligands` | **new** Loads the small molecules found with a protein. | [Structures](structures.md) |
| `fit`, `pair_fit` | Fits matching atoms, or given atom pairs. | [Editing and analysis](editing-analysis.md) |
| `fix_structure` | **new** Repairs a protein with PDBFixer. | [Editing and analysis](editing-analysis.md) |
| `flag` | Sets a flag on atoms (ignore, exclude from surface ...). | |
| `focal_blur` | Makes a picture that is sharp only near the center. | [Saving](saving.md) |
| `fragment` | Loads a fragment from the built-in library. | [Editing and analysis](editing-analysis.md) |
| `frame` | Goes to a movie frame. | [Scenes and movies](scenes-movies.md) |
| `full_screen` | Switches full screen on or off. | |
| `fuse` | Joins two objects with a bond. | |
| `get` | Prints the value of a setting. | [Reference](reference.md) |
| `get_angle`, `get_dihedral`, `get_distance` | Returns a measurement without drawing it. | [Editing and analysis](editing-analysis.md) |
| `get_area` | Returns the surface area of a selection. | |
| `get_bond`, `set_bond`, `unset_bond` | Reads, sets or clears a setting of bonds. | |
| `get_chains` | Prints the chain identifiers of a selection. | |
| `get_clip`, `get_position`, `get_viewport` | Prints the clipping planes, the view center or the viewport size. | |
| `get_extent` | Returns the box around a selection. | |
| `get_property`, `get_property_list` | Reads the properties of an object. | [Property table](properties.md) |
| `get_renderer` | Prints the graphics card and driver in use. | [Troubleshooting](troubleshooting.md) |
| `get_sasa_relative` | Computes the relative solvent accessible area per residue. | |
| `get_symmetry`, `set_symmetry`, `symmetry_copy` | Reads, sets or copies the unit cell and space group. | |
| `get_title`, `set_title` | Reads or sets the title of a state. | |
| `get_type` | Prints the kind of an object. | |
| `get_version` | Prints the version of the program. | [Troubleshooting](troubleshooting.md) |
| `get_view`, `set_view` | Prints the camera as a command, and sets it. | [Scenes and movies](scenes-movies.md) |
| `gradient` | Makes a gradient object from a map. | |
| `group`, `ungroup` | Puts objects into a group, or takes them out. | [Structures](structures.md) |
| `group_disable`, `group_enable` | **new** Hides or shows the members of a group. | [Structures](structures.md) |
| `group_next`, `group_previous` | **new** Shows one member of a group at a time. | [Structures](structures.md) |
| `h_add` | Adds hydrogens. | [Editing and analysis](editing-analysis.md) |
| `h_fill` | Replaces the hydrogens on the picked atom. | [Editing and analysis](editing-analysis.md) |
| `help` | Prints the help of a command. | [Reference](reference.md) |
| `hide` | Turns a representation off. | [Appearance](appearance.md) |
| `id_atom`, `identify`, `index` | Returns the ids or indices of the atoms of a selection. | |
| `indicate` | Marks a selection with dots without naming it. | |
| `intra_fit`, `intra_rms`, `intra_rms_cur` | Fits, or compares, the states of one object. | [Editing and analysis](editing-analysis.md) |
| `invert` | Inverts the stereo center at the picked atom. | [Editing and analysis](editing-analysis.md) |
| `isodot`, `isomesh`, `isosurface` | Draws a map at one level as dots, mesh or surface. | [Editing and analysis](editing-analysis.md) |
| `isolevel` | Changes the level of such an object. | [Editing and analysis](editing-analysis.md) |
| `iterate`, `iterate_state` | Reads atom properties, or coordinates, with an expression. | [Editing and analysis](editing-analysis.md) |
| `join_states` | Makes one object with many states from several objects. | |
| `label` | Labels atoms with an expression. | [Editing and analysis](editing-analysis.md) |
| `ligand_2d` | **new** Draws a ligand flat with its contacts. | [Ligands](ligands.md) |
| `ligand_next` | **new** Goes to the next ligand and shows its site. | [Ligands](ligands.md) |
| `list_uniprot_structures` | **new** Prints the PDB entries of a protein. | [Structures](structures.md) |
| `load` | Reads a file: structure, map, session, image. | [Structures](structures.md) |
| `load_files` | **new** Loads every file of one format from a folder. | [Structures](structures.md) |
| `load_png` | Shows a PNG file in the viewport. | |
| `load_smiles` | **new** Builds a molecule from a SMILES (needs rdkit). | [Editing and analysis](editing-analysis.md) |
| `load_table` | **new** Sets object properties from a CSV, TSV or Excel file. | [Property table](properties.md) |
| `load_traj` | Reads a trajectory into the states of an object. | [Editing and analysis](editing-analysis.md) |
| `loadall` | Loads every file that matches a pattern. | [Structures](structures.md) |
| `log`, `log_open`, `log_close`, `resume` | Writes the commands you run to a log file; runs one again. | [Reference](reference.md) |
| `look_at` | Turns an object or the view to face a target. | |
| `madd`, `mset` | Defines which state each movie frame shows. | [Scenes and movies](scenes-movies.md) |
| `map_double`, `map_halve` | Resamples a map finer or coarser. | |
| `map_new`, `map_set`, `map_set_border` | Makes a map, or computes with maps. | |
| `mappend`, `mdo`, `mdump` | Attaches commands to movie frames; prints them. | [Scenes and movies](scenes-movies.md) |
| `mask`, `unmask` | Makes atoms unselectable by the mouse, and back. | |
| `matrix_copy`, `matrix_transfer`, `matrix_reset` | Copies or resets the transformation of an object. | |
| `mclear` | Clears the stored movie images. | [Scenes and movies](scenes-movies.md) |
| `mcopy`, `mdelete`, `minsert`, `mmove` | Copies, removes, adds or moves movie frames. | [Scenes and movies](scenes-movies.md) |
| `mem` | Debugging: prints memory use. | |
| `meter_reset` | Resets the frames-per-second counter. | |
| `middle`, `rewind`, `ending` | Goes to the middle, start or end of the movie. | [Scenes and movies](scenes-movies.md) |
| `minimize` | **new** Relaxes a protein with OpenMM. | [Editing and analysis](editing-analysis.md) |
| `mmatrix` | Stores the view the movie starts from. | |
| `morph` | Makes states that lead from one conformation to another. | [Editing and analysis](editing-analysis.md) |
| `move`, `turn` | Moves or turns the camera along an axis. | [Reference](reference.md) |
| `movie.produce` | Writes the movie to a video file. | [Scenes and movies](scenes-movies.md) |
| `movie.load`, `movie.nutate`, `movie.pause`, `movie.rock`, `movie.roll`, `movie.screw`, `movie.sweep`, `movie.tdroll`, `movie.zoom`, `util.mrock`, `util.mroll` | Older movie helpers; most have no help text. Use the Timeline instead. | [Scenes and movies](scenes-movies.md) |
| `mplay`, `mstop`, `mtoggle` | Plays or stops the movie. | [Scenes and movies](scenes-movies.md) |
| `mpng` | Writes the movie frames as numbered PNG files. | [Scenes and movies](scenes-movies.md) |
| `mse2met` | Changes selenomethionine to methionine. | |
| `multifilesave`, `multisave` | Saves several objects or states to several files, or to one. | [Saving](saving.md) |
| `mview` | Stores camera and object positions as key frames. | [Scenes and movies](scenes-movies.md) |
| `order` | Changes the order of the names in the Objects panel. | [Structures](structures.md) |
| `orient` | Turns the view along the main axes of a selection. | [Getting started](getting-started.md) |
| `origin` | Sets the point the view turns around. | |
| `palette` | **new** Sets the colors new objects and chains take. | [Appearance](appearance.md) |
| `pbc_unwrap`, `pbc_wrap` | Unwraps or wraps molecules of a periodic box. | |
| `phi_psi` | Prints the backbone angles of a selection. | |
| `pi_interactions` | Shows pi-pi and pi-cation contacts as dashes. | [Editing and analysis](editing-analysis.md) |
| `plugin_load`, `plugin_pref_save` | Loads a plugin by name; saves the settings of the plugins. Present once the plugin system has started, as it has in the window. | [Writing a plugin](plugins.md) |
| `png` | Saves the view as a PNG picture. | [Saving](saving.md) |
| `pop` | Steps through a selection one atom at a time (for scripts). | |
| `protect`, `deprotect` | Keeps atoms from being moved by editing, and back. | |
| `protonate` | Adds hydrogens for a pH. | [Editing and analysis](editing-analysis.md) |
| `pseudoatom` | Adds a point that is not an atom, for labels and measurements. | |
| `python`, `skip` | Marks a block of Python, or a block to skip, in a command script. | [Reference](reference.md) |
| `quit` | Ends the program. | |
| `ramp_new`, `ramp_update` | Makes or changes a color ramp. | |
| `ray` | Draws the view with the ray tracer: shadows and smooth edges. | [Saving](saving.md) |
| `rebond` | Throws the bonds away and finds them again by distance. | |
| `rebuild`, `refresh`, `recolor`, `recolour` | Builds the geometry, the picture or the colors again. | [Troubleshooting](troubleshooting.md) |
| `redo`, `undo` | Takes back a row of the Presets menu, and goes forward again. | [Appearance](appearance.md) |
| `reference` | Stores or recalls reference coordinates. No help text. | |
| `refresh_wizard`, `replace_wizard` | Internal commands of the wizards. | |
| `reinitialize` | Removes everything and restores the settings. | [Reference](reference.md) |
| `remove` | Deletes the atoms of a selection. | [Editing and analysis](editing-analysis.md) |
| `remove_picked` | Deletes the picked atom or bond. | [Editing and analysis](editing-analysis.md) |
| `rename` | Makes the atom names of a residue unique. | |
| `replace` | Replaces the picked atom by another element. | [Editing and analysis](editing-analysis.md) |
| `reset` | Restores the default view. | [Getting started](getting-started.md) |
| `rms`, `rms_cur` | Computes an RMSD without moving anything. | [Editing and analysis](editing-analysis.md) |
| `rock` | Rocks the view from side to side. | [Getting started](getting-started.md) |
| `rotate`, `translate` | Turns or moves atoms or an object. | |
| `run`, `spawn`, `fork` | Runs a Python script; `spawn` runs it in a thread. | [Reference](reference.md) |
| `save` | Writes a session, a structure or another file. | [Saving](saving.md) |
| `save_table` | **new** Writes the properties of the objects as CSV. | [Property table](properties.md) |
| `scene`, `scene_order` | Stores and recalls scenes; changes their order. | [Scenes and movies](scenes-movies.md) |
| `sculpt_activate`, `sculpt_deactivate`, `sculpt_iterate` | Simple geometry clean-up by sculpting. | |
| `search_sequence` | **new** Selects the residues that match a sequence pattern. | [Sequences](sequences.md) |
| `select` | Gives a selection of atoms a name. | [Editing and analysis](editing-analysis.md) |
| `sequence_align` | **new** Aligns FASTA sequences with local MAFFT. | [Sequences](sequences.md) |
| `set`, `unset`, `unset_deep` | Changes a setting, or puts it back. | [Reference](reference.md) |
| `set_atom_property`, `set_property` | Sets a property of atoms, or of an object. | [Property table](properties.md) |
| `set_color`, `set_colour` | Defines a color by its red, green and blue. | [Appearance](appearance.md) |
| `set_dihedral`, `set_geometry`, `torsion` | Changes a dihedral angle or the expected geometry of atoms. | |
| `set_key` | Gives a key a command. | [Reference](reference.md) |
| `set_name` | Renames an object or a selection. | [Structures](structures.md) |
| `show` | Turns a representation on. | [Appearance](appearance.md) |
| `slice_new` | Makes a slice through a map. | |
| `smooth` | Smooths the motion of the states of an object. | [Editing and analysis](editing-analysis.md) |
| `sort` | Puts the atoms of an object in order. | |
| `sort_group` | **new** Sorts the members of a group by name. | [Structures](structures.md) |
| `space` | Chooses the color space (RGB, CMYK). | |
| `spectrum` | Colors atoms along a property, for example the B factor. | [Appearance](appearance.md) |
| `spheroid` | Averages the states of a trajectory into ellipsoids. | |
| `splash` | Prints the start-up notice. No help text. | |
| `split_chains`, `split_states` | Makes one object per chain, or per state. | [Structures](structures.md) |
| `split_types` | **new** Makes one object per kind of molecule. | [Structures](structures.md) |
| `stage` | **new** Puts a floor, with or without a mirror image, under the molecule. | [Appearance](appearance.md) |
| `stereo` | Switches stereo display on or off. | |
| `super` | Fits one structure on another by structure, without needing similar sequences. | [Editing and analysis](editing-analysis.md) |
| `symexp` | Makes the symmetry mates of an object near a selection. | [Editing and analysis](editing-analysis.md) |
| `system` | Runs a program of the operating system. | |
| `toggle` | Switches a representation on or off. | [Appearance](appearance.md) |
| `uniquify` | Makes an identifier (chain, segment) unique. | |
| `update` | Copies coordinates from one selection to another. | |
| `usalign` | Fits two structures by TM-score (the US-align method), for different lengths or low sequence identity. | [Editing and analysis](editing-analysis.md) |
| `util.cbc`, `util.chainbow` | Colors by chain; colors each chain as a rainbow. | [Appearance](appearance.md) |
| `util.cnc`, `util.cbag`, `util.cbac`, `util.cbam`, `util.cbay`, `util.cbas`, `util.cbaw`, `util.cbab`, `util.cbao`, `util.cbap`, `util.cbak` | Colors by element, with the carbons kept or in one color (green, cyan, magenta, yellow, salmon, white, slate, orange, purple, pink). | [Appearance](appearance.md) |
| `util.rainbow`, `util.ss` | Older forms of `spectrum` and `dss`. | |
| `valence` | Sets the order of the bonds between two selections. | [Editing and analysis](editing-analysis.md) |
| `view` | Stores and recalls a camera view by name. | [Scenes and movies](scenes-movies.md) |
| `viewport` | Sets the size of the viewport in pixels. | [Saving](saving.md) |
| `volume`, `volume_color`, `volume_panel`, `volume_ramp_new` | Draws a map as a volume; its colors and its panel. | [Editing and analysis](editing-analysis.md) |
| `window` | Shows, hides or moves the window. | |
| `wizard` | Starts a wizard. | [Editing and analysis](editing-analysis.md) |
| `zoom` | Moves the view so that a selection fills it. | [Getting started](getting-started.md) |

Also registered, for use inside command scripts: the Python words `assert`,
`class`, `def`, `del`, `exec`, `for`, `global`, `if`, `import`, `pass`,
`print`, `raise`, `try` and `while`; and the internal `_alt`, `_ctrl`,
`_ctsh`, `_special` and `_quit`, which the keyboard and the window call.

The settings (`set name, value`) are not in this list: see
[Settings](reference.md#settings).
