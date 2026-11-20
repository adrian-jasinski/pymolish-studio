"""
Dark/light palette for the Qt GUI. The 3D viewport and its internal menu are
drawn by PyMOL itself and are dark already; this makes the Qt panels match.
"""

import json
import os

from pymol.Qt import QtCore, QtGui, QtWidgets

Role = QtGui.QPalette.ColorRole
Group = QtGui.QPalette.ColorGroup

_DARK = {
    Role.Window: (53, 53, 53),
    Role.WindowText: (220, 220, 220),
    Role.Base: (35, 35, 35),
    Role.AlternateBase: (45, 45, 45),
    Role.ToolTipBase: (35, 35, 35),
    Role.ToolTipText: (220, 220, 220),
    Role.Text: (220, 220, 220),
    Role.Button: (53, 53, 53),
    Role.ButtonText: (220, 220, 220),
    Role.BrightText: (255, 80, 80),
    Role.Link: (90, 160, 240),
    Role.Highlight: (42, 130, 218),
    Role.HighlightedText: (255, 255, 255),
    Role.PlaceholderText: (140, 140, 140),
}


def dark_palette():
    p = QtGui.QPalette()
    for role, rgb in _DARK.items():
        p.setColor(role, QtGui.QColor(*rgb))
    grey = QtGui.QColor(127, 127, 127)
    for role in (Role.WindowText, Role.Text, Role.ButtonText, Role.HighlightedText):
        p.setColor(Group.Disabled, role, grey)
    p.setColor(Group.Disabled, Role.Highlight, QtGui.QColor(80, 80, 80))
    return p


def _settings():
    return QtCore.QSettings("pymolish", "pymolish-studio")


def is_dark():
    return _settings().value("theme/dark", True) in (True, "true", 1, "1")


# Multiplies whatever scale the OS reports. Needed where the OS reports none
# (WSLg, bare X11: a 2560x1600 laptop panel shows up as 96 dpi, scale 1).
MIN_SCALE, MAX_SCALE = 0.5, 3.0
DEFAULT_SCALE = 1.5
# the rows of the scale menu; any whole percent can be typed
SCALES = (0.75, 1, 1.25, 1.5, 1.75, 2, 2.5, 3)


def ui_scale():
    try:
        scale = float(_settings().value("ui/scale", DEFAULT_SCALE))
    except (TypeError, ValueError):
        return DEFAULT_SCALE
    return min(max(scale, MIN_SCALE), MAX_SCALE)


def set_ui_scale(scale):
    _settings().setValue("ui/scale", min(max(float(scale), MIN_SCALE), MAX_SCALE))


def set_scale_live(app, window, old, new, symbol=None):
    """Change the scale of the running program from `old` to `new`; true
    when the window now has it. False means: saved, and it applies at the
    next start, as before 4.31.

    ponytail: Qt reads the factor once and offers no call to change it.
    QHighDpiScaling::setGlobalFactor is exported by the Qt library but
    private, so it is called by its symbol name; Qt accepts it once the
    native windows are gone, which hide() and destroy() arrange while the
    widgets, the layout and the OpenGL context stay. Tried on Linux (X11),
    PySide6 6.12. A Qt without the symbol, or one where the ratio does not
    follow, gives False. Upgrade path: a public call, if Qt gets one."""
    import ctypes
    import sys

    Path = QtCore.QLibraryInfo.LibraryPath
    lib_dir = QtCore.QLibraryInfo.path(Path.LibrariesPath)
    if sys.platform == "win32":
        library = os.path.join(QtCore.QLibraryInfo.path(Path.BinariesPath), "Qt6Gui.dll")
        symbol = symbol or "?setGlobalFactor@QHighDpiScaling@@SAXN@Z"
    elif sys.platform == "darwin":
        library = os.path.join(lib_dir, "QtGui.framework", "Versions", "A", "QtGui")
        symbol = symbol or "_ZN15QHighDpiScaling15setGlobalFactorEd"
    else:
        library = os.path.join(lib_dir, "libQt6Gui.so.6")
        symbol = symbol or "_ZN15QHighDpiScaling15setGlobalFactorEd"
    try:
        set_factor = getattr(ctypes.CDLL(library), symbol)
    except (OSError, AttributeError):
        return False
    set_factor.argtypes = [ctypes.c_double]
    set_factor.restype = None

    before = window.devicePixelRatio()
    shown = [w for w in app.topLevelWidgets() if w.isVisible()]
    # the same size on the screen, in the new units, where the screen allows
    size = window.size() * (old / new)
    for widget in shown:
        widget.hide()
    for native in app.topLevelWindows():
        native.destroy()
    set_factor(new)
    room = window.screen().availableGeometry().size()
    window.resize(size.boundedTo(room))
    for widget in shown:
        widget.show()
    return abs(window.devicePixelRatio() - before * new / old) < 0.02


def object_palette():
    """The palette picked in the toolbar: see pymol.palettes."""
    return str(_settings().value("colors/palette", "default"))


def set_object_palette(name):
    _settings().setValue("colors/palette", name)


def user_palettes():
    """The palettes defined in the toolbar: {name: ["rrggbb", ...]}."""
    try:
        value = json.loads(_settings().value("colors/user_palettes", "{}"))
    except (TypeError, ValueError):
        return {}
    return value if isinstance(value, dict) else {}


def set_user_palettes(value):
    _settings().setValue("colors/user_palettes", json.dumps(value))


def background():
    """The background kept by the toolbar's "Remember after restart" row:
    the values of BACKGROUND_SETTINGS, or None when the row is off."""
    values = _settings().value("colors/background")
    return list(values) if values else None


def set_background(values):
    if values:
        _settings().setValue("colors/background", list(values))
    else:
        _settings().remove("colors/background")


def apply_ui_scale(environ=os.environ):
    """Call before QApplication exists: Qt reads the factor once, at startup.
    A factor the user exported wins over the saved one."""
    scale = ui_scale()
    if scale != 1 and not any(
        v in environ for v in ("QT_SCALE_FACTOR", "QT_SCREEN_SCALE_FACTORS")
    ):
        environ["QT_SCALE_FACTOR"] = "%g" % scale


def prefer_x11_on_wsl(environ=os.environ):
    """Call before QApplication exists. WSLg's Wayland compositor does not
    keep popups on the screen, so a menu at the window edge runs off it and
    its submenus cannot be reached. Through X11 Qt places menus itself: they
    stay inside the screen and submenus open to the left when they must."""
    if "WSL_DISTRO_NAME" in environ and environ.get("DISPLAY"):
        environ.setdefault("QT_QPA_PLATFORM", "xcb;wayland")


# where distributions install Mesa's drivers
_DRI_DIRS = (
    "/usr/lib/x86_64-linux-gnu/dri",
    "/usr/lib/aarch64-linux-gnu/dri",
    "/usr/lib64/dri",
    "/usr/lib/dri",
)


def prefer_gpu_on_wsl(environ=os.environ, exists=os.path.exists):
    """Call before the OpenGL context exists. Through X11, Mesa under WSLg
    draws on the CPU (llvmpipe) unless it is told to use its d3d12 driver,
    which draws on the GPU of Windows: a frame of 1aon takes 50 to 120 ms on
    the CPU. That driver draws lines one pixel wide; CShaderMgr::Trilines
    makes up for it."""
    # ponytail: a d3d12 driver that is installed but fails to start leaves
    # the viewport without a context (Mesa does not fall back from a named
    # driver); GALLIUM_DRIVER=llvmpipe is the way out. If that shows up in
    # the field, restart without the variable when the context is invalid.
    if (
        "WSL_DISTRO_NAME" in environ
        and "LIBGL_ALWAYS_SOFTWARE" not in environ
        and exists("/dev/dxg")
        and any(exists(d + "/d3d12_dri.so") for d in _DRI_DIRS)
    ):
        environ.setdefault("GALLIUM_DRIVER", "d3d12")


class _RoundMenus(QtCore.QObject):
    def eventFilter(self, watched, event):
        if (
            event.type() == QtCore.QEvent.Type.Polish
            and isinstance(watched, QtWidgets.QMenu)
            and not watched.testAttribute(_TRANSLUCENT)
        ):
            watched.setAttribute(_TRANSLUCENT)
            watched.setWindowFlags(
                watched.windowFlags()
                | QtCore.Qt.WindowType.FramelessWindowHint
                | QtCore.Qt.WindowType.NoDropShadowWindowHint
            )
        return False


_TRANSLUCENT = QtCore.Qt.WidgetAttribute.WA_TranslucentBackground


def round_menus(app):
    """The stylesheet rounds the corners of every menu; this makes the
    window behind those corners see-through, for each menu before it is
    first shown, wherever it was created."""
    app.installEventFilter(_RoundMenus(app))


class _DialogDocks(QtCore.QObject):
    def eventFilter(self, watched, event):
        if event.type() == QtCore.QEvent.Type.Show and isinstance(
            watched, QtWidgets.QDockWidget
        ):
            flags = watched.windowFlags()
            # a dock being dragged bypasses the window manager: leave it alone
            if flags & _TYPE == _TOOL and not flags & _BYPASS:
                watched.setWindowFlags(flags & ~_TYPE | QtCore.Qt.WindowType.Dialog)
                watched.show()
        return False


_TYPE = QtCore.Qt.WindowType.WindowType_Mask
_TOOL = QtCore.Qt.WindowType.Tool
_BYPASS = QtCore.Qt.WindowType.X11BypassWindowManagerHint


def float_docks_as_dialogs(app, environ=os.environ):
    """A floating dock is a Qt.Tool window, a "utility" window on X11. WSLg
    never places those: the dock is drawn in the screen corner, cannot be
    moved and gets no clicks. As a dialog it is an ordinary window."""
    if "WSL_DISTRO_NAME" in environ and app.platformName() == "xcb":
        app.installEventFilter(_DialogDocks(app))


def apply(app, dark):
    # Fusion + palette darkens every Qt-drawn menu and widget. The color
    # scheme hint darkens what the OS draws (macOS menu bar, Windows title
    # bars and system menus); it is a no-op on Linux (checked with 6.12).
    scheme = QtCore.Qt.ColorScheme
    app.styleHints().setColorScheme(scheme.Dark if dark else scheme.Light)
    app.setStyle("Fusion")
    app.setPalette(dark_palette() if dark else app.style().standardPalette())


def set_dark(dark):
    _settings().setValue("theme/dark", bool(dark))
    app = QtWidgets.QApplication.instance()
    apply(app, dark)
    for w in (
        app.topLevelWidgets()
    ):  # styled widgets ignore palette changes until repolished
        w.setStyleSheet(w.styleSheet())
