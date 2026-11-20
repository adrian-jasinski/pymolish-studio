"""
Thin-line icons for menu entries and toolbar buttons. The drawings are Lucide icons (ISC license,
data/pmg_qt/icons/lucide/LICENSE), tinted with the color of the text they sit
next to.
"""

import functools
import os

from pymol.Qt import QtCore, QtGui, QtWidgets

# menu label (pymol.menu, color markup removed) -> icon file
LABELS = {
    "new": "circle-plus",
    "pseudoatom": "circle-dot",
    "zoom": "zoom-in",
    "orient": "compass",
    "center": "crosshair",
    "origin": "locate-fixed",
    "reset": "rotate-ccw",
    "movie": "clapperboard",
    "scene": "image",
    "enable": "eye",
    "show": "eye",
    "disable": "eye-off",
    "hide": "eye-off",
    "(all)": "layers",
    "(visible)": "scan-eye",
    "ray": "aperture",
    "delete": "trash-2",
    "delete all": "trash-2",
    "delete selection": "trash-2",
    "remove": "trash-2",
    "remove atoms": "trash-2",
    "reinitialize": "refresh-cw",
    "update": "refresh-cw",
    "quit": "log-out",
    "drag": "move",
    "drag object matrix": "move",
    "drag object coords": "move",
    "atom": "atom",
    "residue": "hexagon",
    "chain": "link",
    "segment": "spline",
    "object": "box",
    "molecule": "share-2",
    "fragment": "puzzle",
    "fragment+joint(s)": "puzzle",
    "actions": "zap",
    "color": "palette",
    "background": "paint-roller",
    "preset": "sliders-horizontal",
    "label": "tag",
    "ss": "dna",
    "clean": "sparkles",
    "select": "mouse-pointer-click",
    "split": "scissors",
    "create object": "copy-plus",
    "copy to object": "copy",
    "duplicate": "copy",
    "extract object": "scissors",
    "rename": "pencil",
    "rename selection": "pencil",
    "find": "search",
    "compute": "calculator",
    "clear": "eraser",
    "play": "play",
    "stop": "square",
    "rewind": "skip-back",
    "next": "skip-forward",
    # states panel
    "first": "skip-back",
    "previous": "rewind",
    "forward": "fast-forward",
    "last": "skip-forward",
    # action toolbar
    "open file": "folder-open",
    "select nothing": "ban",
    "undo": "undo-2",
    "redo": "redo-2",
    "rock": "rotate-3d",
    "presets": "sliders-horizontal",
    "builder": "hammer",
    "scenes": "camera",
    "table": "sheet",
    "2d": "hexagon",
    "draw": "aperture",
    "ui scale": "scaling",
    "more actions": "ellipsis",
    "more": "ellipsis",
    # the row under the object list
    "mouse mode": "mouse",
    "seq": "letter-text",
    "wizard": "wand-sparkles",
    "command line": "square-terminal",
}


@functools.lru_cache(maxsize=None)
def _pixmap(name, color, ratio, size=16, stroke=1.5):
    path = os.path.expandvars("$PYMOL_DATA/pmg_qt/icons/lucide/%s.svg" % name)
    with open(path) as handle:
        svg = handle.read()
    # the files draw 2 px lines on a 24 px grid in "currentColor"
    svg = svg.replace("currentColor", color).replace(
        'stroke-width="2"', 'stroke-width="%s"' % stroke
    )
    data = QtCore.QBuffer()
    data.setData(svg.encode())
    reader = QtGui.QImageReader(data, b"svg")
    side = round(size * ratio)
    reader.setScaledSize(QtCore.QSize(side, side))
    pixmap = QtGui.QPixmap.fromImage(reader.read())
    pixmap.setDevicePixelRatio(ratio)
    return pixmap


def menu_icon(label, color, size=16, stroke=1.5, accent=None):
    """The icon for a menu label, drawn in `color` (a QColor); None if the
    label has none. "delete object" falls back to the icon of "delete".
    `size` is the side in pixels and `stroke` the line width on the 24 px
    grid of the drawing. With `accent`, the icon is drawn in that color
    while the pointer is over its button and while the button is checked."""
    name = LABELS.get(label) or LABELS.get(label.split(" ")[0])
    if name:
        # of the screens: the application's own value is one Qt keeps from
        # the start, and a live change of the UI scale leaves it as it was
        ratio = max(s.devicePixelRatio() for s in QtWidgets.QApplication.screens())
        icon = QtGui.QIcon(_pixmap(name, color.name(), ratio, size, stroke))
        if accent is not None:
            pixmap = _pixmap(name, accent.name(), ratio, size, stroke)
            Mode, State = QtGui.QIcon.Mode, QtGui.QIcon.State
            icon.addPixmap(pixmap, Mode.Active, State.Off)
            icon.addPixmap(pixmap, Mode.Normal, State.On)
            icon.addPixmap(pixmap, Mode.Active, State.On)
        return icon
