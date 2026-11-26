# Reference

[Docs home](README.md) · Checked with version 4.90.0.

Things to look up: how to name atoms, the mouse and the keys, settings,
how the program starts, and what differs from PyMOL. The commands are on
their own page: [Commands](commands.md).

**On this page:** [Selections](#selections) · [Mouse](#mouse) ·
[Keyboard](#keyboard) · [Settings](#settings) ·
[Scripts and start-up](#scripts-and-start-up) ·
[File formats](#file-formats) · [Optional packages](#optional-packages) ·
[Compatibility with PyMOL](#compatibility-with-pymol) ·
[Find help](#find-help)

## Selections

A selection says which atoms a command acts on. It is the last argument of
most commands: `show surface, chain A`. Without one, a command acts on
everything.

| Write | Means |
| --- | --- |
| `1oky` | the object of that name |
| `chain A` | a chain |
| `resi 100-120` | residues by number |
| `resn STU` | residues by name |
| `name CA` | atoms by name |
| `elem S` | atoms by element |
| `polymer`, `polymer.protein`, `polymer.nucleic` | protein and nucleic acid chains |
| `organic` | small molecules with carbon: ligands |
| `inorganic` | ions and metals |
| `solvent` | water |
| `backbone`, `sidechain` | parts of a protein residue |
| `hydrogens` | hydrogen atoms |
| `ss H`, `ss S` | helices, strands |
| `b > 60` | by B factor |
| `visible`, `enabled` | what is shown, what is switched on |
| `rep ball_and_stick` | atoms that have that representation |
| `sele` | what you last selected with the mouse |

Combine them with `and`, `or`, `not` and parentheses, and widen them:

| Write | Means |
| --- | --- |
| `chain A and resi 160 and name CA` | one atom |
| `/1oky//A/160/CA` | the same atom, written as a path |
| `not polymer` | everything that is not protein or nucleic acid |
| `organic around 4` | atoms within 4 Å of the ligands, without the ligands |
| `polymer within 4 of organic` | the same, limited to the protein |
| `byres (organic around 4)` | whole residues instead of single atoms |
| `organic expand 3` | the ligands and everything within 3 Å |
| `bychain resn STU` | the whole chains that contain STU |

These were run on the structure `1oky`. `count_atoms <selection>` tells you
how many atoms a selection has, which is the quickest way to try one.
`select site, byres (organic around 4)` gives a selection a name; it then
has a row in the Objects panel. `help selections` prints the full list of
words.

A name that is also a selection word (`b`, `q`, `name`) confuses the
reader of selections: do not give objects such names.

## Mouse

The table is for the mouse mode the program starts in, 3-Button Viewing.

| Mouse | Does |
| --- | --- |
| Left button, drag | Rotate |
| Middle button, drag | Move sideways |
| Right button, drag | Zoom |
| Wheel | Make the visible slab thinner or thicker |
| Click on an atom | Select it, or take it out of the selection |
| Click on empty space | Clear the selection |
| Middle click | Center on that atom |
| Right click, or double click, on an atom | Menu for that atom, residue, chain and object |
| Right click on empty space | Menu for the view |
| Shift + left drag | Add everything in a box to the selection |
| Shift + middle drag | Take everything in a box out of the selection |
| Shift + right drag | Move the clipping planes |
| Ctrl + Shift + middle click | Set the center of rotation |

What a click selects (an atom, its residue, its chain ...) is the choice of
the toolbar button that says **Residues** at the start; the same list is
under Mouse > Selection Mode.

The button under the Objects panel that says **Viewing** opens the Mouse
menu, with the other modes: 3 Button Editing for moving atoms, 2 Button
Viewing for a mouse or trackpad without a middle button, and more.
`help mouse` and `help button` describe how to change what a button does.

## Keyboard

These keys work while the viewport has the keyboard, which it has after a
click in it.

| Key | Does |
| --- | --- |
| Ctrl-Z, Ctrl-Y | Undo and redo a row of the Presets menu |
| Ctrl-O, Ctrl-S | Open a file, save the session |
| Ctrl-A | Select everything as `sele` |
| Ctrl-C, Ctrl-X, Ctrl-V | Copy, cut and paste the selected atoms |
| Ctrl-I | Invert the selection |
| Ctrl-N, Ctrl-P | Next and previous member of a group |
| Ctrl-Shift-M, Ctrl-Shift-H | Next and previous ligand with its contacts |
| Ctrl-L | Zoom on the ligands |
| Ctrl-F | Find wizard |
| Home | Zoom on everything |
| Insert | Rock on and off |
| PgDn, PgUp | Next and previous scene |
| F1 to F12 | Recall the scene of that key; with Ctrl, store it |
| Right, Left | Next and previous state or movie frame |
| End | Play or stop the movie |
| Esc | Show or hide the text over the viewport |
| Ctrl-E | Switch the command panel between fixed and movable |

In the Objects panel: F2 renames the current row, Delete removes it, Space
switches it on or off, Alt with the arrow keys moves it, Ctrl-C copies the
names of the selected rows.

The Build menu shows the keys that add fragments and residues while you
build a molecule (Alt-A for alanine, Ctrl-Shift-C for a carbon ...).

Setting > Keyboard Shortcuts... lists every key and lets you change it.
`set_key F5, zoom` does the same from a script.

## Settings

A setting is a named value that changes how the program draws or behaves.

| To | Do |
| --- | --- |
| Change one | `set cartoon_transparency, 0.5` |
| Change one for one object or selection | `set cartoon_transparency, 0.5, 1oky` |
| Read one | `get cartoon_transparency` |
| Put one back to its default | `unset cartoon_transparency` |
| Browse and search all of them | Setting > Edit All... |
| Complete a name | `set cartoon_<Tab>` |

Many settings can be set at four levels: for everything, for an object, for
one state of an object, and for atoms. The narrower level wins. The Setting
menu has the common ones as rows with a check mark.

The program has no help text for single settings (`help` knows commands).
Help > Topics > Settings opens the list of the PyMOL wiki in your browser;
it describes the settings both programs share.

Settings that only pymolish-studio has:

| Setting | Default | What it does | Guide |
| --- | --- | --- | --- |
| `ball_and_stick_scale` | 0.25 | Ball size of `ball_and_stick`, as a part of the atom radius | [Appearance](appearance.md) |
| `ball_and_stick_bond_radius` | 0.12 | Thickness of its bonds | [Appearance](appearance.md) |
| `ball_and_stick_color` | default | Color of its balls and bonds; `atomic` colors by element | [Appearance](appearance.md) |
| `ball_and_stick_transparency` | 0 | Makes its balls and bonds see-through, per object | [Appearance](appearance.md) |
| `viewport_outline` | on | Draws the outline of a light such as figure or comic in the viewport, not only when ray traced | [Appearance](appearance.md) |
| `async_surface` | on | Builds a surface of 5000 atoms or more in the background | [Appearance](appearance.md) |
| `glow` | 0 | A halo around what is drawn, in the viewport and in saved pictures, ray traced too; Presets > light > glow | |

Settings that are gone, with the features they belonged to: `internal_gui`,
`internal_gui_width`, `internal_gui_name_color_mode`, `scene_buttons`, and
the settings that start with `collada_` and `openvr_`. A line that sets one
of them in a script or a pymolrc file prints an error and the rest of the
file still runs.

## Scripts and start-up

| File | What it is | Run it with |
| --- | --- | --- |
| `.pml` | Commands, one per line, as you would type them | `@file.pml`, File > Run Script... |
| `.py` | Python; use `from pymol import cmd` | `run file.py`, File > Run Script... |
| `.pymolrc`, `.pymolrc.pml`, `.pymolrc.py` in your home folder | Commands that run at every start | File > Edit pymolrc opens it |

In Python the package is still called `pymol`, so scripts written for PyMOL
import it as before.

Start the program from a terminal to give it files and options:

```
pymolish 1ubq.pdb script.pml
pymolish -cq script.pml
```

| Option | Does |
| --- | --- |
| `-c` | No window: run the files and quit. For batch work. |
| `-q` | No start-up notice |
| `-k` | Do not read pymolrc files and do not load plugins |
| `-d "command"` | Run a command at the start |
| `-r file.py` | Run a Python script |
| `-W 1200 -H 800` | Size of the window in pixels |
| `-y` | Quit with an error code when a script fails |

File > New PyMOL Window > "Ignore .pymolrc and plugins (-k)" starts a second
window that way, which is the quickest test of whether a problem comes from
your own configuration.

File > Log File > Open... writes the commands of a session to a file as you
work; it can be run again as a script.

## File formats

Which formats can be opened and saved, and what each keeps, is in
[Saving](saving.md#file-formats-that-are-read-and-written).

## Optional packages

The downloadable builds contain rdkit, pdbfixer and openmm. They do not
contain the provider libraries of the Chat tab, MAFFT or ffmpeg. An
installation with `pip` adds the Python packages by name.

| For | Package | Install |
| --- | --- | --- |
| Molecules from SMILES, optimize a ligand, stereochemistry, ligand in 2D | rdkit | `pip install 'pymolish[chem]'` |
| Fix a structure, relax a protein | pdbfixer, openmm | `pip install 'pymolish[fix]'` |
| Chat with an API key or a browser sign-in | anthropic, openai, keyring | `pip install 'pymolish[ai]'` |
| Align sequences | MAFFT, a separate program | [Install](install.md#optional-sequence-alignment) |
| Movies as video files | ffmpeg (or ImageMagick's `convert`), separate programs | [Scenes and movies](scenes-movies.md) |

A command that needs a missing package says which one and how to install
it; nothing else stops working.

## Compatibility with PyMOL

pymolish-studio is a fork of Open-Source PyMOL. The molecular engine, the
command language and the file formats are the same; the window is new.

| Topic | State |
| --- | --- |
| Commands and scripts | The commands of Open-Source PyMOL work, with the exceptions below. |
| Sessions | `.pse` files are read and written. `.psex` is this program's smaller file; PyMOL does not read it. See [Saving](saving.md). |
| Plugins | Plugins with Qt windows work; plugins with Tk windows do not. See [Writing a plugin](plugins.md). |
| pymolrc | Read as before. Take out lines that set `internal_gui...`. |
| Python | `import pymol` and `from pymol import cmd`, Python 3.13 or newer. Qt only through `pymol.Qt` (PySide6). |

What is not here:

- The features in the list [Removed](features.md#removed): the Tk and GLUT
  windows, the object list drawn inside the viewport, the XML-RPC server,
  COLLADA, MMTF, OpenVR, the `mpeg_encode` encoder.
- Four commands that only raised an error in the open-source build:
  `help_setting`, `callout`, `desaturate`, `load_mtz`.
- `sphere_mode` stops at 9.
- Reading STL, RigiMOL morphing and the readers for Maestro, MOE and Phase
  files, which were never part of the open-source build.

What a session of this program loses in PyMOL: the things PyMOL does not
have, such as the `ball_and_stick` representation, the columns of the
property table and the shots of the Timeline. [Saving](saving.md) has the
details.

## Find help

| You want | Use |
| --- | --- |
| The description of a command | `help <command>` |
| The arguments of a command | `<command> ?` |
| The name of a command, an object or a file | Tab |
| A task, step by step | The guides on the [docs home](README.md) |
| A word on the page you are reading | Your browser's Find |
| A word in all pages | Search the repository, restricted to `docs/` |
| A problem | [Troubleshooting](troubleshooting.md) |

The Help menu links to the pages of PyMOL (wiki, command reference,
mailing list). They describe PyMOL, not this program: what they say about
commands and selections holds, what they say about the window does not.

---

PyMOL is a trademark of Schrodinger, LLC.
