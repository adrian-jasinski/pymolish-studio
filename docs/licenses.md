# Licenses

pymolish-studio. Contains PyMOL(TM) source code.

pymolish-studio is an independent fork. It is not a Schrodinger product and is
not affiliated with or endorsed by Schrodinger, LLC.

This page lists every part of pymolish-studio, its license and where the
license text is. It is a list, not legal advice. Each license was read from
the file or package named in the "Text" column.

## pymolish-studio itself

| Part | License | Text |
| --- | --- | --- |
| Code from [Open-Source PyMOL](https://github.com/schrodinger/pymol-open-source), Copyright (C) Schrodinger, LLC | Open-Source PyMOL license | [LICENSE](../LICENSE) |
| Code added by pymolish-studio: new files, and changes inside files from Open-Source PyMOL | MIT | [LICENSE-MIT](../LICENSE-MIT) |
| Application icon and logo, `data/pymol/icons/` | Made for this project. No license is recorded for them yet. | none |

A file from Open-Source PyMOL that pymolish-studio changed is under both
licenses, so a copy of the software needs both files.

## In the source tree

These parts are in the repository and in every wheel and bundle.

| Part | Where | License | Text |
| --- | --- | --- | --- |
| [Lucide](https://lucide.dev) icons, 51 files | `data/pmg_qt/icons/lucide/` | ISC; parts from Feather under MIT | [LICENSE](../data/pmg_qt/icons/lucide/LICENSE) |
| champ | `contrib/champ/` | Open-Source PyMOL license | [LICENSE](../contrib/champ/LICENSE) |
| VMD molfile plugins | `contrib/uiuc/plugins/` | University of Illinois Open Source License | [LICENSE](../contrib/uiuc/plugins/LICENSE) |
| pocketfft | `contrib/pocketfft/` | BSD 3-Clause, Max-Planck-Society | [LICENSE.md](../contrib/pocketfft/LICENSE.md) |
| TNT and JAMA | `include/tnt/` | Public domain (NIST) | top of each header |
| CE alignment | `layer0/ccealignmodule.cpp` | BSD 2-Clause, Jason Vertrees | top of the file |
| TM-align, ported from US-align | `layer2/USalign.cpp` | Permission notice of the Zhang lab | top of the file |
| DejaVu font, from Bitstream Vera | `layer1/FontTTF.h` | Bitstream Vera Fonts Copyright; DejaVu changes are public domain | top of the file |
| Gentium font | `layer1/FontTTF2.h` | SIL Open Font License 1.0 | top of the file |

The note in [contrib/README](../contrib/README) applies to everything in
`contrib/`.

## Used at run time

A wheel does not contain these parts; `pip` installs numpy and PySide6 next to
it, and the native libraries come from the system. A bundle contains all of
them.

| Part | Use | License | Text in a bundle |
| --- | --- | --- | --- |
| [PySide6 and Qt 6](https://doc.qt.io/qtforpython-6/licenses.html) | GUI | LGPL-3.0-only (also offered under GPL-2.0-only and GPL-3.0-only) | `pymol/pymol_path/licenses/`, from [packaging/licenses](../packaging/licenses) |
| [numpy](https://numpy.org) | arrays | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 | `numpy-*.dist-info/licenses/` |
| [GLEW](https://glew.sourceforge.net) | OpenGL extensions | BSD 3-Clause; generated parts under the Mesa and MIT licenses | not included |
| [GLM](https://github.com/g-truc/glm) | vector math, headers only | MIT | not included |
| [libpng](http://www.libpng.org/pub/png/libpng.html) | PNG files | libpng license | not included |
| [FreeType](https://freetype.org) | text | FreeType License (FTL) | not included |
| [msgpack-c](https://github.com/msgpack/msgpack-c) | BinaryCIF files, optional, headers only | Boost Software License 1.0 | not included |
| [netCDF](https://www.unidata.ucar.edu/software/netcdf/) | VMD molfile plugins, optional | BSD 3-Clause, UCAR/Unidata | not included |
| [nlohmann-json](https://github.com/nlohmann/json) | glTF export, optional, headers only | MIT | not included |

Qt is used under the LGPL: a bundle keeps the Qt libraries as separate files
that can be replaced. The Qt source is at
[download.qt.io](https://download.qt.io/official_releases/qt/).

Portions of this software are copyright (c) 1996-2023 The FreeType Project
(www.freetype.org). All rights reserved.

A bundle also contains the Python interpreter and the libraries the parts
above depend on, such as HDF5, curl, zlib and zstd on Linux. Their license
texts are not collected in the bundle yet.

All other names are trademarks of their respective owners.

---

PyMOL is a trademark of Schrodinger, LLC.
