# Solve a problem

[Docs home](README.md) · Checked with version 4.90.0.

Find what you see, then the likely cause and what to do. Messages are given
as the program prints them in the log (the **Command** tab).

**On this page:** [Starting](#starting) ·
[I cannot see my molecule](#i-cannot-see-my-molecule) ·
[A menu row or command does nothing](#a-menu-row-or-command-does-nothing) ·
[Something is missing](#something-is-missing) ·
[The window](#the-window) · [Network](#network) ·
[Pictures and movies](#pictures-and-movies) · [Sessions](#sessions) ·
[Plugins and pymolrc](#plugins-and-pymolrc) ·
[Report a problem](#report-a-problem)

## Starting

| You see | Likely cause | Do |
| --- | --- | --- |
| Windows reports an unknown publisher or SmartScreen blocks Setup | The Windows installer and app are unsigned previews. | Compare the file with `SHA256SUMS` from the same release. If blocked, record the message and report it; keep security protection enabled. [Windows installation](install.md#windows-installer). |
| macOS warns before the first start | The downloadable builds are previews and are not signed. | Compare the archive with `SHA256SUMS` on the Releases page, then allow the start in the dialog of your system. |
| Windows Setup says application files are in use | pymolish or a bundled library is still running. | Save your work, close pymolish and retry. Do not force-close an unsaved session. |
| The window stays black, on WSL | The graphics driver of Windows did not start. | Start with `GALLIUM_DRIVER=llvmpipe pymolish`: it draws on the CPU. [Install](install.md#on-wsl) has the details. |
| Turning the molecule is slow, on a laptop with two graphics cards under WSL | The slower card is used. | Start with `MESA_D3D12_DEFAULT_ADAPTER_NAME=NVIDIA pymolish` (a part of the card's name). `get_renderer` prints the card in use. |
| Turning a large structure is slow anywhere | Much is drawn. | Display > Quality > Maximum Performance; hide a surface while you move; show a cartoon, not all atoms. |
| An error at the start, before the window | A line of your pymolrc file, or a plugin. | File > New PyMOL Window > "Ignore .pymolrc and plugins (-k)", or start with `pymolish -k`. If that works, see [Plugins and pymolrc](#plugins-and-pymolrc). |

## I cannot see my molecule

| You see | Likely cause | Do |
| --- | --- | --- |
| An empty viewport, but the Objects panel has a row | The view looks elsewhere. | Press **Zoom** in the toolbar, or type `zoom`. |
| The row of the object is dim | The object is switched off. | Click the row. |
| The object is on and zoomed, nothing is drawn | Every representation is hidden. | **Presets** > classified gives the look a file opens with; or S > cartoon on its row. |
| A part of the molecule is cut away | The clipping planes are close together. | Display > Clip > Nothing, or turn the mouse wheel. |
| A surface does not appear at once | A surface of 5000 atoms or more is built in the background. The log says ` Surface: building the surface of "..." in the background` and later `is ready`. | Wait; you can keep working. `set async_surface, 0` builds it the old way. |
| The view is strange after experiments | Settings were changed. | `reset` for the camera. File > Reinitialize > Original Settings for the settings; File > Reinitialize > Everything also removes the objects. |

## A menu row or command does nothing

| You see | Likely cause | Do |
| --- | --- | --- |
| A row of **Presets** changes nothing | A preset acts on the objects that are switched on. | Switch the object on (click its row), then pick the preset again. |
| A transparency row is gone after the next preset | Every preset starts from opaque. | Pick the preset first, the transparency after it. |
| Undo does not take something back | Undo covers the rows of the Presets menu and what was done since, five steps. It does not cover every change. | Save a session before a step you may regret. [Appearance](appearance.md) says what Undo restores. |
| `Error: Invalid selection name "..."` | A word in the selection is not a name or a selection word. | Check the spelling; `count_atoms <selection>` tries a selection. See [Selections](reference.md#selections). |
| A selection behaves oddly with an object called `b`, `q` or `name` | The name is also a selection word. | Rename the object (F2 on its row). |
| The next ligand is not found | The structure has no small molecule with carbon, or the object is switched off. | `count_atoms organic` says how many ligand atoms there are. |

## Something is missing

The program runs without its optional packages; only the commands that
need one stop with a message.

| Message | Missing | Do |
| --- | --- | --- |
| `this command needs rdkit: pip install 'pymolish[chem]'` | rdkit: SMILES, optimize a ligand, stereochemistry, ligand in 2D | Run that `pip` line in the environment pymolish is installed in, or use a downloadable build, which has it. |
| a message that ends in `pip install 'pymolish[fix]'` | pdbfixer and openmm: fix structure, optimize protein geometry | The same. |
| `Install the optional AI packages: pip install 'pymolish[ai]'` | The libraries for Chat with an API key or a sign-in. The downloadable builds do not contain them. | Install them, or choose the provider "Claude Code". See [Assistant](assistant.md). |
| `Install MAFFT and put it on PATH, or choose its executable in the sequence window.` | MAFFT, a separate program | [Install MAFFT](install.md#optional-sequence-alignment), or the **MAFFT…** button of the alignment window. |
| `neither "ffmpeg" nor "convert" available for ...` | A program that writes video files | Install ffmpeg. Without it, export the movie as PNG images. See [Scenes and movies](scenes-movies.md). |
| File > Export Image As > GLB... or GLTF... fails | The build was made without glTF support. | Use a downloadable build, or build with `json=True`: [Install](install.md). |
| A BinaryCIF file does not load | The build was made without msgpack. | The same page; load the mmCIF file instead. |

## The window

| You see | Likely cause | Do |
| --- | --- | --- |
| Text and buttons are too small or too large | The size of the window's content. | The percent button in the toolbar: a row, or type any value from 50 to 300 and press Enter. Below 75 % and above 200 % the program asks whether to keep the size and goes back by itself after ten seconds. |
| "The new scale applies the next time pymolish starts." | Under WSL the size cannot change in a running window. | Close the program and start it again. |
| Only the text of the log, the sequence or the chat is too small | Each tab has its own text size. | **A−**, **A+** and **Reset** at the right of the tabs. |
| A panel or the toolbar is gone | It was closed. | Display > Panels lists them; Display > Panels > Reset Layout puts everything back. |
| The window is light, or dark, and you want the other | The theme. | Display > Dark Theme. |

## Network

| You see | Likely cause | Do |
| --- | --- | --- |
| File > Get PDB... or `fetch` fails | No connection, a proxy, or the code does not exist. | Open the entry in a browser to check; download the file there and use File > Open.... |
| `fetch_by_uniprot` loads far more than expected | A well studied protein has hundreds of entries. | Give a limit: `fetch_by_uniprot P00918, 5`. `list_uniprot_structures P00918` shows them first. |
| A predicted structure does not load | AlphaFold DB has no model for that accession, or the ESMFold server is busy. | Try the other source: an accession asks AlphaFold DB, a sequence asks ESMFold. |

Which servers are asked, and what is sent, is in
[Structures](structures.md) and, for the Chat tab, in
[Assistant](assistant.md).

## Pictures and movies

| You see | Likely cause | Do |
| --- | --- | --- |
| A saved picture has a transparent background | "Ray trace with this background" is off. | Toolbar > Background > tick "Ray trace with this background", or `set opaque_background, 1`. |
| The picture is small or coarse | It has the size of the viewport. | Give a size: `png picture.png, width=2400, dpi=300, ray=1`. See [Saving](saving.md). |
| The outline of a light is in the ray-traced picture but not on screen, or the other way round | The viewport outline is a setting of its own. | Setting > Rendering > "Outline of a Look (Real Time)". |
| Edges look jagged on screen | Smoothing in the viewport is off by default. | Setting > Rendering > Antialias (Real Time). |
| An empty picture after adding a floor, when a floor was on before File > Reinitialize | The new floor first takes the old one back. | Presets > floor > no floor (or `stage off`), then the floor again. |
| A ray-traced picture takes long | Ray tracing computes shadows for every pixel. | Try with a small size first; use **Draw** for a quick picture. |

## Sessions

| You see | Likely cause | Do |
| --- | --- | --- |
| PyMOL does not open a `.psex` file | `.psex` is this program's packed session. | Save the session as `.pse`: `save work.pse`. |
| A session from this program looks different in PyMOL | PyMOL does not have `ball_and_stick`, the property table columns or the Timeline shots. | Use representations PyMOL has (sticks, spheres) before saving for it. |
| A session with a movie asks a security question on loading | Its movie contains commands that would run. | Accept only for files you trust. |

## Plugins and pymolrc

| You see | Likely cause | Do |
| --- | --- | --- |
| ` Plugin "pymolish" was not loaded: its commands are part of this program.` | The older pymolish plugin is in your start-up folder. | Remove it from the folder the message names. |
| A plugin does not show its window | It builds a Tk window. | Only plugins with Qt windows run. [Writing a plugin](plugins.md) shows how to change one. |
| `Error: unknown Setting: 'internal_gui'` at the start | Your pymolrc sets something that is gone. | Take that line out: File > Edit pymolrc. The rest of the file still runs. |

## Report a problem

1. Type `diagnostics` and copy what it prints: the version, the system, the
   graphics driver and the Python in use. It contains folder names of your
   computer; take out what you do not want to share.
2. Note the smallest steps that show the problem, with a public structure
   such as `fetch 1ubq` if you can.
3. Open an issue at
   [github.com/adrian-jasinski/pymolish-studio/issues](https://github.com/adrian-jasinski/pymolish-studio/issues).

`feedback enable, all, debugging` makes the log say much more; `feedback
disable, all, debugging` turns that off again.

## Next

- [Reference](reference.md): selections, mouse, keys, settings
- [Commands](commands.md): every command by name
