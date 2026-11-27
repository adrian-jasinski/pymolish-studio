"""
Object color palettes: the order in which new objects get their carbon
color and util.cbc colors chains. "palette" swaps the table the loaders walk
(AutoColor in layer1/Color.cpp); the colors are named colors, <palette>_01
and up.
"""

import pymol

from . import util

cmd = __import__("sys").modules["pymol.cmd"]
from .cmd import _cmd  # noqa: E402

# name -> (background the colors are picked for, hex colors in cycle order).
# testing/tests/api/palettes.py checks contrast and neighbor distance.
#
# Every palette has 30 colors. Its comment describes the first ones, the
# palette as it was designed or published. The ones after "added" came in
# 4.71.0 to fill it up: picked in OKLCH inside the palette's own range of
# lightness and chroma, each the farthest from all colors already in it, and
# put in an order in which neighbors differ. They belong to no published set.
PALETTES = {
    # Material Design accent colors, near-duplicates removed
    "vivid": (
        "dark",
        "00e676 40c4ff ff4081 ffd740 b388ff ff6e40 18ffff 69f0ae e040fb 448aff"
        " b2ff59 ff80ab ffff00 7c4dff ff9100 00b0ff ea80fc 76ff03 ff1744 ffc400"
        " aeea00"
        # added, see above
        " a8579e 19b180 b66007 af1aec 62881c 716cc8 ab9807 d51588 aac254",
    ),
    # Material Design 800 and 900 tones, near-duplicates removed
    "deep": (
        "white",
        "1565c0 c62828 2e7d32 6a1b9a e65100 00838f ad1457 283593 00695c 827717"
        " 4e342e d81b60 b8860b 37474f 8d6e63"
        # added, see above
        " 369fb6 a017a1 7b8ccd 773555 b560f3 214606 77528d 921904 d063a7 715af2"
        " c5786e 7b33ca 59a276 a255b3 66015f",
    ),
    # cyan, green, red, blue, yellow, then purple, orange, mint, pink, lime,
    # tan and steel
    "pastel": (
        "dark",
        "8fe3ef a5e6a0 ff9e9e 9dbcff fff09a c9a8ff ffc48a 8ff0cf ffa8d8 d2f08c"
        " d9b99b b0bfd0"
        # added, see above
        " 3be1e9 c8cd98 5ffcfd d8ccfe ffa06f b6fdfd 8dd07f ffc2c8 3ccef5 9dc8a2"
        " fee5fc eed469 cde4fb 3cd6be dbe6c9 ebaf51 d5acd2 bdc35a",
    ),
    # 12 hues at half saturation and equal luminance, then 10 darker ones
    "soft": (
        "white",
        "6192c3 da6d6d 4e9d76 cd67cd 73994d 7f7fff b28559 4d9a9a d56aa0 4f9f4f"
        " ad73e7 929249 4b68bd a15840 307866 ac4592 427930 7555d4 7d6a32 367488"
        " b34762 9a49b6"
        # added, see above
        " 098bf6 885870 9e8bb9 d54a01 77589c ee6517 927199 bd2910",
    ),
    # Okabe-Ito, then Paul Tol's bright and muted sets, values as published.
    # Left out: black, the greys, and Tol colors close to an earlier entry.
    # Only the first seven are designed as one set.
    "colorblind": (
        "any",
        "e69f00 56b4e9 009e73 f0e442 0072b2 d55e00 cc79a7 4477aa 228833 ccbb44"
        " ee6677 aa3377 332288 88ccee 44aa99 999933 ddcc77 882255"
        # added, see above
        " c09cff 7c5723 6dfdcc ab2610 45d079 681b05 936ce2 29420e e29f91 0a6e65"
        " fecbfb 703fb0",
    ),
    # The accent colors of three editor themes, values as published, ordered
    # so that neighbors differ; colors close to another entry are left out.
    # Nord: frost and aurora
    "nord": (
        "dark",
        "88c0d0 bf616a a3be8c ebcb8b 81a1c1 d08770 b48ead 5e81ac"
        # added, see above
        " feb2f3 598a7a deacae 5ee4fd b8df87 15bcc4 9e65ab 70e9c6 f3a767 5fbc86"
        " e385a3 14a1c8 bb91e0 ad6f1c 8ca1f2 12aa8f 8f85d7 c6a141 bbaff6 98946a"
        " b7d2f6 708a30",
    ),
    "dracula": (
        "dark",
        "8be9fd 50fa7b ff79c6 f1fa8c bd93f9 ffb86c ff5555"
        # added, see above
        " 9291d1 bcf005 faabb4 5dbfcd fc4b93 9fd49d 07b928 ca8092 36a2e4 bcb068"
        " 25dfda f78d70 bcbcff fdd81f d498c5 19ce7d e8dc93 a1bd04 71f6c9 d75ee4"
        " 66aa81 fcc4f9 cc8923",
    ),
    # Catppuccin Mocha
    "catppuccin": (
        "dark",
        "89b4fa a6e3a1 f38ba8 f9e2af cba6f7 fab387 94e2d5 f5c2e7 74c7ec b4befe f5e0dc"
        # added, see above
        " f69075 82c473 c4f4cf 3dcaa6 cccdaf e2a148 d4b3ba b8b64a 8ffbfb a3b69e"
        " 43e1f6 a5afca e3ca5f c5daf2 d4a487 02c6da 8accbe f19cdd daf28d",
    ),
    # The colors UCSF ChimeraX gives to models 1 to 10, values as in its
    # source (atomic_color_names): tan, sky blue, plum, light green, salmon,
    # light gray, deep pink, gold, dodger blue, purple. Made for its black
    # background, but the purple is too dark to pass as "dark" here.
    "chimerax": (
        "any",
        "d2b48c 87ceeb dda0dd 90ee90 fa8072 d3d3d3 ff1493 ffd700 1e90ff 800080"
        # added, see above
        " 08ad46 7060aa 9cc713 c173a1 114e89 a2572d 7236f8 1c5c1f 74989d a505d0"
        " 527579 cb46f8 5f4450 9575f7 ad8c31 1f1bd8 b82d79 67cba1 5529a8 66771d",
    ),
    # Five colors of a brand book, values as published (turquoise, blue,
    # cyan, indigo, deep purple), and between them seven in the same tone for
    # the hues it lacks. No background suits all twelve: the indigo and the
    # purple are dark on black, six others are light on white.
    "halo": (
        "any",
        "00f4d6 016afa ff3d9a 00caff ffd900 4300ff 9be800 ff4d4d 471396 1fd655"
        " c61aff ff8a00"
        # added, see above
        " 8413d1 7a0105 b764b6 297513 1790db a51a85 20ce9f 6a0e5b fc86ad 00378b"
        " 7e9503 876df7 b90522 cb95f9 ca6c12 5554b4 c1b52b dc2ec0",
    ),
    # The usual web values of neon sign colors: green, pink, cyan, yellow,
    # orange, purple, blue, red, lime, hot pink, mint and fuchsia
    "neon": (
        "dark",
        "39ff14 ff10f0 00ffff ffff33 ff5f1f bc13fe 1f51ff ff073a ccff00 ff69b4"
        " 00ff9f fe4164"
        # added, see above
        " 8fff40 7d26ff ffd900 5940ff 40ffcf ff00aa 40d6ff ff007b 0dc2ff ff40cf"
        " ffb640 4069ff ff8c00 9c40ff 40acff d940ff 0084ff 4096ff",
    ),
}
PALETTES = {name: (bg, colors.split()) for name, (bg, colors) in PALETTES.items()}
BUILTIN = tuple(PALETTES)  # define() adds the palettes of the user


def define(name, colors, background="any", _self=cmd):
    """Add or replace a palette of the user: `colors` are at least two hex
    colors ("ff8800" or "#ff8800") in the order they are given out. The name
    becomes the prefix of the color names (<name>_01, ...). The palette is
    known until the program ends; the toolbar keeps its own for later."""
    import re

    name = str(name).strip()
    if not re.fullmatch(r"[a-z][a-z0-9_]*", name) or name == "default":
        raise pymol.CmdException(
            "palette name '%s': lowercase letters, digits, _" % name
        )
    if name in BUILTIN:
        raise pymol.CmdException("'%s' is a built-in palette" % name)
    colors = [str(c).lstrip("#").lower() for c in colors]
    if len(colors) < 2 or not all(re.fullmatch("[0-9a-f]{6}", c) for c in colors):
        raise pymol.CmdException("a palette needs two or more colors like ff8800")
    PALETTES[name] = (background, colors)
    if active == name:  # its colors may have changed
        apply(_self)
        _self.recolor()


def undefine(name, _self=cmd):
    """Forget a palette of the user. Its colors stay defined, so objects
    that have them keep them."""
    if name in BUILTIN or name not in PALETTES:
        raise pymol.CmdException("'%s' is not a palette of the user" % name)
    if active == name:
        palette("default", _self=_self)
    del PALETTES[name]


active = "default"  # process-wide, like the table in Color.cpp


def cycle():
    """The colors of the active palette in order: names, or the color
    indices of the PyMOL order."""
    if active == "default":
        return util._color_cycle
    return ["%s_%02d" % (active, i + 1) for i in range(len(PALETTES[active][1]))]


def apply(_self=cmd):
    """Register the colors of the active palette and hand them to the
    loaders. Also runs after reinitialize and a session load: both rebuild
    the color list, so the indices change."""
    indices = []
    if active != "default":
        for name, color in zip(cycle(), PALETTES[active][1]):
            _self.set_color(name, [int(color[j : j + 2], 16) for j in (0, 2, 4)])
            indices.append(_self.get_color_index(name))
    with _self.lockcm:
        _cmd.set_auto_colors(_self._COb, indices)  # empty: the PyMOL order


def session_restore(session, _self=cmd):
    apply(_self)
    return True


def palette(name="", recolor=0, quiet=1, *, _self=cmd):
    """
    DESCRIPTION

        "palette" sets the colors that new objects cycle through and that
        util.cbc gives to chains. Without arguments it lists the palettes and
        marks the active one.

    USAGE

        palette [ name [, recolor ]]

    ARGUMENTS

        name = default, vivid, deep, pastel, soft, colorblind, nord, dracula,
        catppuccin, chimerax, halo or neon. "default" is the PyMOL order (green, cyan,
        light magenta, ...).

        recolor = 0/1: also color the carbons of the loaded objects, from the
        first palette color on {default: 0}

    EXAMPLE

        palette vivid
        palette soft, 1

    NOTES

        deep and soft are made for a white background, colorblind, chimerax
        and halo for any, the others for a dark one. The colors are named <palette>_01, <palette>_02, ... and can
        be used like any color. A "palette" line in pymolrc applies at every
        start.

    SEE ALSO

        color, set_color, util.color_objs, util.cbc
    """
    global active
    if name:
        if name != "default" and name not in PALETTES:
            raise pymol.CmdException(
                "unknown palette '%s', choose from: default %s"
                % (name, " ".join(PALETTES))
            )
        active = name
        apply(_self)
        _self.set("auto_color_next", 0)
        if not int(quiet):
            print(" palette: new objects use '%s'" % name)
    elif not int(recolor):
        for name in ("default", *PALETTES):
            print(" %s %s" % ("*" if name == active else " ", name))
    if int(recolor):
        _self.set("auto_color_next", 0)
        for name in _self.get_names("public_nongroup_objects"):
            if _self.get_type(name) == "object:molecule":
                color = str(_self.get_color_index("auto"))
                _self.set_object_color(name, color)
                _self.color(color, "?%s & elem C" % name)


# CPK colors by element: the table "CPK Colours" of the RasMol manual, the
# scheme behind the usual CPK pictures (carbon light grey, oxygen red,
# nitrogen light blue, sulfur yellow). An element that is not in it gets
# deep pink, as there. One table, used by color_cpk only: no named color is
# defined or changed.
CPK_OTHER = "ff1493"
CPK = {
    "c8c8c8": "C",
    "f00000": "O",
    "ffffff": "H",
    "8f8fff": "N",
    "ffc832": "S",
    "00ff00": "Cl B",
    "ffa500": "P Fe Ba",
    "0000ff": "Na",
    "228b22": "Mg",
    "a52a2a": "Zn Cu Ni Br",
    "808090": "Ca Mn Al Ti Cr Ag",
    "daa520": "F Si Au",
    "a020f0": "I",
    "b22222": "Li",
    "ffc0cb": "He",
}
CPK = {symbol: color for color, symbols in CPK.items() for symbol in symbols.split()}


def color_cpk(selection="all", representation="", quiet=1, *, _self=cmd):
    """
    DESCRIPTION

        "color_cpk" colors atoms by element in the CPK colors of RasMol:
        carbon light grey, oxygen red, hydrogen white, nitrogen light
        blue, sulfur yellow, phosphorus orange, and so on; an element
        without a color of its own is deep pink. All atoms of the residues
        in the selection are colored. This is a coloring by element, not
        by kind of residue.

    USAGE

        color_cpk [ selection [, representation ]]

    ARGUMENTS

        selection = str: atoms; their whole residues are colored {default: all}

        representation = str: empty for the colors of the atoms, which every
        representation without a color of its own follows; ball_and_stick
        for the balls and sticks of that representation only: the atoms,
        spheres, sticks and the cartoon keep their colors {default: ""}

    EXAMPLE

        color_cpk organic
        color_cpk resn STU, ball_and_stick
        unset ball_and_stick_color, resn STU    # the atoms' colors again

    SEE ALSO

        color, set, util.cbag
    """
    representation = str(representation or "")
    if representation not in ("", "ball_and_stick"):
        raise pymol.CmdException(
            "representation is empty or ball_and_stick, not '%s'" % representation
        )
    atoms = _self.get_unused_name("_cpk")
    _self.select(atoms, "byres (%s)" % selection, 0)
    try:
        elements = set()
        _self.iterate(atoms, "elements.add(elem)", space={"elements": elements})
        for element in sorted(elements):
            color = "0x" + CPK.get(element.capitalize(), CPK_OTHER)
            target = "?%s & elem %s" % (atoms, element or "''")
            if representation:
                _self.set("ball_and_stick_color", color, target, quiet=1)
            else:
                _self.color(color, target, quiet=1)
        count = _self.count_atoms("?" + atoms)
    finally:
        _self.delete(atoms)
    if not int(quiet):
        what = "the balls and sticks of" if representation else ""
        print(" color_cpk: CPK colors on %s %d atoms." % (what, count))
    return count
