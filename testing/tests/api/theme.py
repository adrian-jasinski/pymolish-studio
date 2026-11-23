"""
Dark palette has readable text on all groups and apply() switches back.
The saved UI scale reaches Qt unless the user exported their own.
Headless (offscreen QApplication).
"""

import os

from pymol import testing


def test_palette():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from pymol.Qt import QtWidgets
    from pmg_qt import theme

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    p = theme.dark_palette()
    for group in (theme.Group.Active, theme.Group.Inactive, theme.Group.Disabled):
        bg = p.color(group, theme.Role.Window).lightness()
        fg = p.color(group, theme.Role.WindowText).lightness()
        assert fg - bg > 60
    theme.apply(app, True)
    assert app.palette().window().color().lightness() < 100
    menu = QtWidgets.QMenu()
    assert menu.palette().window().color().lightness() < 100
    theme.apply(app, False)
    assert app.palette().window().color().lightness() > 150
    assert app.style().objectName() == "fusion"


def test_ui_scale():
    from unittest import mock
    from pmg_qt import theme

    with mock.patch.object(theme, "ui_scale", return_value=1.5):
        env = {}
        theme.apply_ui_scale(env)
        assert env == {"QT_SCALE_FACTOR": "1.5"}
        env = {"QT_SCALE_FACTOR": "2"}
        theme.apply_ui_scale(env)
        assert env["QT_SCALE_FACTOR"] == "2"
    with mock.patch.object(theme, "ui_scale", return_value=1.0):
        env = {}
        theme.apply_ui_scale(env)
        assert env == {}


def test_prefer_x11_on_wsl():
    from pmg_qt import theme

    env = {"WSL_DISTRO_NAME": "Ubuntu", "DISPLAY": ":0"}
    theme.prefer_x11_on_wsl(env)
    assert env["QT_QPA_PLATFORM"] == "xcb;wayland"
    env = {"WSL_DISTRO_NAME": "Ubuntu", "DISPLAY": ":0", "QT_QPA_PLATFORM": "w"}
    theme.prefer_x11_on_wsl(env)
    assert env["QT_QPA_PLATFORM"] == "w"  # the user's choice wins
    for env in ({"DISPLAY": ":0"}, {"WSL_DISTRO_NAME": "Ubuntu"}):
        theme.prefer_x11_on_wsl(env)
        assert "QT_QPA_PLATFORM" not in env


def test_prefer_gpu_on_wsl():
    from pmg_qt import theme

    gpu = {"/dev/dxg", "/usr/lib64/dri/d3d12_dri.so"}.__contains__
    env = {"WSL_DISTRO_NAME": "Ubuntu"}
    theme.prefer_gpu_on_wsl(env, gpu)
    assert env["GALLIUM_DRIVER"] == "d3d12"
    env = {"WSL_DISTRO_NAME": "Ubuntu", "GALLIUM_DRIVER": "llvmpipe"}
    theme.prefer_gpu_on_wsl(env, gpu)
    assert env["GALLIUM_DRIVER"] == "llvmpipe"  # the user's choice wins
    for env, exists in (
        ({}, gpu),  # not WSL
        ({"WSL_DISTRO_NAME": "Ubuntu", "LIBGL_ALWAYS_SOFTWARE": "1"}, gpu),
        ({"WSL_DISTRO_NAME": "Ubuntu"}, {"/dev/dxg"}.__contains__),  # no driver
        ({"WSL_DISTRO_NAME": "Ubuntu"}, {"/usr/lib/dri/d3d12_dri.so"}.__contains__),
    ):
        theme.prefer_gpu_on_wsl(env, exists)
        assert "GALLIUM_DRIVER" not in env


def test_syntax_colors_readable_on_dark():
    from pmg_qt.syntax import readable

    for name in ("blue", "darkBlue", "black", "brown", "darkGreen"):
        assert readable(name, True).lightness() >= 170
        assert readable(name, False).lightness() < 170


def test_default_ui_scale():
    from unittest import mock
    from pmg_qt import theme

    with mock.patch.object(theme, "_settings") as settings:
        settings.return_value.value.side_effect = lambda key, default: default
        assert theme.ui_scale() == 1.5
        settings.return_value.value.side_effect = lambda key, default: "bad"
        assert theme.ui_scale() == 1.5
        settings.return_value.value.side_effect = lambda key, default: "1.2"
        assert theme.ui_scale() == 1.2


def test_float_docks_as_dialogs():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from pymol.Qt import QtCore, QtWidgets
    from pmg_qt import theme

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    mask = QtCore.Qt.WindowType.WindowType_Mask
    f = theme._DialogDocks()
    app.installEventFilter(f)
    try:
        win = QtWidgets.QMainWindow()
        dock = QtWidgets.QDockWidget("d", win)
        dock.setFloating(True)
        dock.show()
        assert dock.windowFlags() & mask == QtCore.Qt.WindowType.Dialog
        assert dock.isVisible() and dock.isFloating()
        win.addDockWidget(QtCore.Qt.DockWidgetArea.TopDockWidgetArea, dock)
        dock.setFloating(False)  # docked again: no longer a window
        assert not dock.isWindow()
    finally:
        app.removeEventFilter(f)

    # only where WSLg draws X11 windows
    with_filter = []
    fake = type("A", (), {"platformName": lambda s: "xcb"})()
    fake.installEventFilter = with_filter.append
    theme.float_docks_as_dialogs(fake, {})
    assert with_filter == []


def test_scale_range_and_live():
    """Any scale from 0.5 to 3 is kept; outside values are cut. The live
    change works on this platform, or says that it did not."""
    import sys
    from unittest import mock

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from pymol.Qt import QtWidgets
    from pmg_qt import theme

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    store = {}
    settings = mock.Mock()
    settings.value = lambda key, default=None: store.get(key, default)
    settings.setValue = store.__setitem__
    with mock.patch.object(theme, "_settings", return_value=settings):
        for asked, kept in ((0.5, 0.5), (1.37, 1.37), (3.0, 3.0), (0.2, 0.5), (7, 3.0)):
            theme.set_ui_scale(asked)
            assert theme.ui_scale() == kept
        store["ui/scale"] = "25"  # a value written by hand
        assert theme.ui_scale() == 3.0

    from pymol.Qt import QtCore, QtGui
    from pmg_qt import icons

    class Tinted(QtWidgets.QWidget):  # like the toolbar: it draws icons
        drawn = 0

        def changeEvent(self, event):
            if event.type() == QtCore.QEvent.Type.PaletteChange:
                Tinted.drawn += 1
            super().changeEvent(event)

    def icon_side():
        icon = icons.menu_icon("undo", QtGui.QColor("black"))
        return icon.availableSizes()[0].width()

    window = QtWidgets.QMainWindow()
    window.setCentralWidget(Tinted())
    window.resize(400, 300)
    window.show()
    before = window.devicePixelRatio()
    side = icon_side()
    said = []
    handler = QtCore.qInstallMessageHandler(
        lambda kind, context, text: said.append(text)
    )
    # a Qt without the function: False, nothing touched
    assert (
        theme.set_scale_live(app, window, 1.0, 2.0, symbol="no_such_function") is False
    )
    assert window.devicePixelRatio() == before and window.isVisible()
    Tinted.drawn = 0
    done = theme.set_scale_live(app, window, 1.0, 2.0)
    QtCore.qInstallMessageHandler(handler)
    try:
        # 30c: Qt's "QHighDpiScaling::setFactor: Should only be called when
        # no windows exist" is not printed
        assert not [text for text in said if "QHighDpiScaling" in text]
        if done:
            assert window.devicePixelRatio() == before * 2
            assert (
                window.isVisible() and window.size().width() == 200
            )  # the same size on the screen
            # 30c: what draws icons is told to draw them again, and an
            # icon made now has the pixels of the new scale
            assert Tinted.drawn >= 1
            assert icon_side() == 2 * side
        else:  # not an error: the program then says "at the next start"
            print("set_scale_live does not work on", sys.platform, app.platformName())
            assert (
                sys.platform != "linux"
                or app.platformName() != "xcb"
                or theme.live_scale_blocker(app)
            )
    finally:
        if done:
            assert theme.set_scale_live(app, window, 2.0, 1.0)
        window.close()


# 27d: a window like the program's, its scale changed four times, with a
# heartbeat. The parent reads what the child says and gives it a minute.
_SCALE_CHILD = r"""
import time
from pymol.Qt import QtCore, QtWidgets
from pmg_qt import theme

theme.prefer_x11_on_wsl()
app = QtWidgets.QApplication([])
window = QtWidgets.QMainWindow()
window.setCentralWidget(QtWidgets.QTextEdit("scale"))
window.resize(500, 300)
window.show()
start = time.monotonic()
beat = QtCore.QTimer(interval=100)
beat.timeout.connect(lambda: print("beat %.2f" % (time.monotonic() - start), flush=True))
beat.start()
steps = [(1.5, 1.2), (1.2, 1.5)] * 2


def step():
    if not steps:
        print("done", flush=True)
        return app.quit()
    old, new = steps.pop(0)
    why = theme.live_scale_blocker(app)
    if why or not theme.set_scale_live(app, window, old, new):
        print("unsupported on %s: %s" % (app.platformName(), why or "no change"), flush=True)
        steps.clear()
        return step()
    asked = time.monotonic()

    def shown():
        if window.windowHandle().isExposed():
            print("live %s to %s shown after %.2f" % (old, new, time.monotonic() - asked), flush=True)
            QtCore.QTimer.singleShot(200, step)
        else:
            QtCore.QTimer.singleShot(20, shown)

    shown()


QtCore.QTimer.singleShot(300, step)
app.exec()
"""


def test_scale_change_keeps_the_window_alive():
    """27d: the event loop keeps running through a change of scale and the
    window is back on the screen within two seconds, or the display is
    reported as one where the change waits for the next start."""
    import subprocess
    import sys

    env = dict(os.environ, QT_SCALE_FACTOR="1.5")
    env.pop("QT_SCREEN_SCALE_FACTORS", None)
    env.pop("QT_QPA_PLATFORM", None)  # the display the program would use
    if sys.platform == "linux" and not (
        env.get("DISPLAY") or env.get("WAYLAND_DISPLAY")
    ):
        env["QT_QPA_PLATFORM"] = "offscreen"
    run = subprocess.run(
        [sys.executable, "-c", _SCALE_CHILD],
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    lines = run.stdout.splitlines()
    assert "done" in lines, run.stdout[-1000:] + run.stderr[-1000:]
    beats = [float(line.split()[1]) for line in lines if line.startswith("beat")]
    assert max(b - a for a, b in zip(beats, beats[1:])) < 2
    said = [line for line in lines if line.startswith(("unsupported", "live"))]
    print("\n".join(said))  # which way this display goes: not the same thing
    if not said[0].startswith("unsupported"):
        assert len(said) == 4 and max(float(line.split()[-1]) for line in said) < 2


def test_live_scale_blocker():
    from pmg_qt import theme

    xcb = type("A", (), {"platformName": lambda s: "xcb"})()
    other = type("A", (), {"platformName": lambda s: "wayland"})()
    assert theme.live_scale_blocker(xcb, {"WSL_DISTRO_NAME": "Ubuntu"})
    assert theme.live_scale_blocker(xcb, {}) == ""
    assert theme.live_scale_blocker(other, {"WSL_DISTRO_NAME": "Ubuntu"}) == ""
    # blocked: nothing is touched, the caller says "at the next start"
    from unittest import mock

    with mock.patch.dict(os.environ, {"WSL_DISTRO_NAME": "Ubuntu"}):
        assert theme.set_scale_live(xcb, None, 1.5, 1.2) is False
