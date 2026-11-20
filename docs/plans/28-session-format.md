# 28 — Session format: is a new one needed?

[Roadmap](../../PLAN.md) · Request 2026-11-20 ("think if we need a new
session format ... e.g. psex") · **28a done 2026-11-20 in 4.26.0.** 28b (the
one session key for new data) is built with its first user, the table
columns of 22d or the shot list of step 19: a module nothing calls is not
written ahead.

Result of 28a, measured with the shipped code: 1AON 19.6 MB to 1.10 MB,
4V6X 87.2 MB to 3.90 MB (18 and 22 times smaller). The pickle is written
with protocol 4, which stores the packed bytes as they are: that is the
difference to the 1.4 MB of the trial below, which used the protocol of a
`.pse`. Save 0.20 s against 0.30 s (1AON), 0.78 s against 1.53 s (4V6X);
load 0.04 s against 0.21 s and 0.20 s against 0.99 s. `load` goes by the
first bytes, so a renamed file loads. Not done: a file association in the
bundles (they have none for `.pse` either).

**Short answer: no new format is needed to store the new options, a `.pse`
can carry them today. A new file type is still worth having for size: the
same content, packed, is 14 times smaller. Recommended: `.psex`, which is
exactly that, and becomes what Save Session writes; `.pse` stays for
exchange with PyMOL.**

## What a `.pse` is

A Python pickle of one dictionary: settings, colors, the objects with their
atoms and coordinates, selections, view, scenes, movie. The core fills it
(`get_session`), then every function in `pymol._session_save_tasks` may add
keys; on load every function in `_session_restore_tasks` gets the dictionary
([exporting.py](../../modules/pymol/exporting.py) line 436,
[importing.py](../../modules/pymol/importing.py) line 164). Scenes, the
palette and the wizard already travel this way. `pse_binary_dump` writes
atoms and coordinates as packed bytes instead of Python lists;
`session_compression` (zlib, marked deprecated upstream) packs the pickle.

## Measured (2026-11-20)

**New data in a `.pse`.** A session with an extra key (a table definition
and a shot list) and with object properties was saved here and loaded:

| Loaded by | Result |
| --- | --- |
| pymolish 4.19.43 | Objects, properties and the extra key are back. |
| PyMOL 3.2.0a (the user's `pymol3`) | Loads without a message; the objects and even the properties are there; the extra key is ignored. Both with and without `pse_binary_dump`. |

So extra keys cost nothing and break nothing.

**Size and time**, structure only (no surfaces are stored; a session keeps
what is shown, not the triangles):

| Structure | Atoms | `.pse` today | binary dump | binary + zlib 6 | binary + lzma 1 | binary + lzma 6 | mmCIF, gzip (for scale) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1AON | 59,192 | 19.6 MB, 0.4 s | 10.5 MB, 0.0 s | 2.1 MB, +0.2 s | **1.4 MB, +0.2 s** | 1.3 MB, +2.4 s | 1.1 MB |
| 4V6X | 239,306 | 87.2 MB, 2.5 s | 42.9 MB, 0.3 s | 7.4 MB, +0.9 s | **4.7 MB, +0.7 s** | 4.2 MB, +11.6 s | 3.9 MB |

Binary dump with lzma at level 1 is 14 to 18 times smaller than today's
file and saves faster than today (0.2 s against 0.4 s for 1AON), because the
pickle of packed bytes is so much quicker than the pickle of lists. It is
within 30 % of the gzipped mmCIF, which holds less (no settings, no scenes):
little is left to gain by a different layout. zstd would be faster still but
is in the standard library only from Python 3.14; the floor is 3.13.

## Options (question 29, answered 2026-11-20: B with B1)

| | Option | Note |
| --- | --- | --- |
| A | No new file type. New data goes into `.pse` as extra keys; `pse_binary_dump` becomes the default. | Smallest: one default changes. Files are half the size, not a fourteenth. A `.pse` from pymolish still opens in PyMOL. |
| B | **`.psex`: the same dictionary, binary dump, lzma level 1, behind an 8-byte mark. Save Session writes `.psex`; "Save as .pse" stays for PyMOL. Recommended.** | About 30 lines in `exporting.py` and `importing.py`, no dependency (`lzma` is in the standard library). One code path builds the dictionary for both file types. |
| C | A new container: a zip with the structures as mmCIF or BinaryCIF and everything else as JSON. | Readable by other programs and by eye. Every kind of object, setting, scene and movie needs a writer and a reader of its own: thousands of lines, and two session formats to keep in step for good. The size gain over B is under 30 %. Not recommended. |

**What a `.pse` from pymolish contains** (a second choice inside B):

| | Option | Note |
| --- | --- | --- |
| B1 | **The new data too, as extra keys. Recommended.** | Nothing is lost when someone saves as `.pse` and opens it in pymolish again; PyMOL ignores the keys (measured). The two file types differ only in packing. |
| B2 | A `.pse` is written without the pymolish keys, as the request suggests. | The file is what PyMOL itself would write. Saving as `.pse` then drops the table columns, the shot list and the stored background picture; the save dialog must warn. A little more code (a list of keys to leave out). |

## Design (option B, B1)

| Part | Decision |
| --- | --- |
| File | The bytes `PSEX` and a format number (1) and three reserved bytes, then the lzma stream (`lzma.compress(data, preset=1)`) of the pickle that `get_session(binary=1)` gives. The mark lets `load` tell the type without trusting the file name, and a later change of packing (zstd when 3.14 is the floor) is a new format number. |
| Writing | `save name.psex` and File > Save Session. The dialog offers "pymolish session (*.psex)" first and "PyMOL session (*.pse)" second. |
| Reading | `load name.psex`, File > Open, a dropped file, Open Recent, the file association of the bundles. `.pse` and `.pze` load as before. |
| One key for everything new | `session["pymolish"]`, a dictionary with a `version` and one entry per feature: `table` ([step 22](22-property-table.md): column order and hidden columns), `shots` ([step 19](19-movie-timeline.md): the shot list), not `background_image` ([21f](21-commercial-features.md) decided on 2026-11-20 to store the picture as text in the setting itself; that stands, the answer to question 29 did not move it), later `stage` and `ligand_2d` if they need one. One save task and one restore task in a new `modules/pymol/session_extra.py` hand each entry to its owner. Object properties need no entry: the core saves them. |
| Unknown entries | Kept and written back untouched, so an older pymolish does not strip what a newer one saved. |
| Safety | A session is a pickle, and loading a pickle can run code: true for `.pse` today and unchanged by this plan. The existing warning on files from others stays; `.psex` adds no new risk and removes none. |
| Old sessions | Every `.pse` ever written loads as before. Nothing is converted by itself. |
| `session_compression` | The setting stays as it is (a placeholder would be needed to remove it, and upstream sessions set it). `.psex` does not read it. |

## Slices

| Slice | What | Check |
| --- | --- | --- |
| 28a | `.psex` write and read, the mark, the dialog filter, Open Recent, `pse_binary_dump` on for it. | `testing/tests/api/session_psex.py`: round trip of a session with two objects, a scene, a movie and a property; the file of 1UBQ is under a fifth of the `.pse`; a `.pse` renamed to `.psex` and the reverse both load or fail with a clear message; a truncated file raises `CmdException`. |
| 28b | `session_extra.py` with the `pymolish` key; unknown entries survive. | An entry written by a fake "newer" version is still there after load and save. `compare.py`: PyMOL 3 loads the `.pse` written with the key. |
| then | Steps 19 and 22d put their data under the key; 21f as decided there. | In their own plans. |

## Skipped

- Option C, and with it sessions other programs can read: `save x.cif`,
  `x.pdb`, `x.usdz` are the exchange formats.
- Saving the built surfaces and meshes so a big session opens without
  rebuilding: a real saving of time, but tens of MB per surface. Ask again
  when the surface on a worker thread ([1b](01-performance-gpu.md)) is in.
- Incremental or automatic saving, session history.
- Encryption, signing.
