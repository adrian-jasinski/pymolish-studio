"""Capture helpers for the documentation screenshots and clips (plan 38d).

Run a scenario with:  XDG_CONFIG_HOME=<scratch>/cfg pymolish -qk scenario.py
Everything is a real widget grab of the running program. WSLg cannot grab
the screen, so a popup (menu, dialog, floating panel) is grabbed as its own
widget and laid on the window grab at the place Qt shows it.
"""

import os
import time
import traceback

import pymol
from pymol import cmd
from pymol.Qt import QtCore, QtGui, QtWidgets
from PySide6.QtTest import QTest

Qt = QtCore.Qt
app = QtWidgets.QApplication.instance()
LOG = None
# A separate window (a floating panel) is drawn at the place given here, in
# window coordinates: WSLg puts such a window where it likes, and where it
# stands on the screen is the user's choice anyway.
PLACE = {}


def gpos(widget, pos):
    """Global position of a point of a widget, as the composite shows it."""
    top = widget.window()
    if top in PLACE:
        return win().mapToGlobal(PLACE[top]) + widget.mapTo(top, pos)
    return widget.mapToGlobal(pos)


def log(*a):
    if LOG:
        print(*a, file=LOG, flush=True)


def win():
    return pymol.gui.get_qtwindow()


def grab_parts():
    """The window and every visible popup, as pixmaps with their places."""
    w = win()
    origin = w.mapToGlobal(QtCore.QPoint(0, 0))
    parts = [(QtCore.QPoint(0, 0), w.grab())]
    for top in app.topLevelWidgets():
        if top is w or not top.isVisible() or top.width() < 5:
            continue
        flags = top.windowFlags()
        if (
            isinstance(top, (QtWidgets.QMenu, QtWidgets.QDialog, QtWidgets.QDockWidget))
            or (flags & Qt.WindowType.Popup == Qt.WindowType.Popup)
            or flags & Qt.WindowType.ToolTip == Qt.WindowType.ToolTip
        ):
            place = PLACE.get(top, top.mapToGlobal(QtCore.QPoint(0, 0)) - origin)
            parts.append((place, top.grab()))
    return parts, origin, w.size()


def compose(parts, origin, size, cursor=None, caption=None):
    base = parts[0][1]
    dpr = base.devicePixelRatio()
    # a popup may reach past the window: the canvas grows, on a plain ground
    right = max(pos.x() + pm.width() / pm.devicePixelRatio() for pos, pm in parts)
    bottom = max(pos.y() + pm.height() / pm.devicePixelRatio() for pos, pm in parts)
    img = QtGui.QImage(
        int(round(right * dpr)),
        int(round(bottom * dpr)),
        QtGui.QImage.Format.Format_RGB32,
    )
    img.fill(QtGui.QColor("#16181c"))
    img.setDevicePixelRatio(dpr)
    p = QtGui.QPainter(img)
    for pos, pixmap in parts:
        p.drawPixmap(pos, pixmap)
    if cursor is not None:
        c = cursor - origin
        path = QtGui.QPainterPath()
        pts = [(0, 0), (0, 17), (4.5, 13), (7.5, 20), (10, 19), (7, 12), (12.5, 12)]
        path.moveTo(c.x() + pts[0][0], c.y() + pts[0][1])
        for x, y in pts[1:]:
            path.lineTo(c.x() + x, c.y() + y)
        path.closeSubpath()
        p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        p.setPen(QtGui.QPen(QtGui.QColor("black"), 1.2))
        p.setBrush(QtGui.QColor("white"))
        p.drawPath(path)
    if caption:
        f = p.font()
        f.setPointSizeF(11)
        f.setBold(True)
        p.setFont(f)
        h = 30
        r = QtCore.QRectF(0, size.height() - h, size.width(), h)
        p.fillRect(r, QtGui.QColor(0, 0, 0, 215))
        p.setPen(QtGui.QColor("white"))
        p.drawText(r, Qt.AlignmentFlag.AlignCenter, caption)
    p.end()
    return img


def composite(cursor=None, caption=None):
    """The window with every visible popup laid over it, as a QImage."""
    return compose(*grab_parts(), cursor=cursor, caption=caption)


def shot(path, crop=None, cursor=None):
    """Save the composite; crop is (x, y, w, h) in window coordinates."""
    img = composite(cursor)
    if crop:
        d = img.devicePixelRatio()
        x, y, w, h = crop
        img = img.copy(int(x * d), int(y * d), int(w * d), int(h * d))
    img.save(path)
    log("shot", path, img.width(), img.height())


def widget_shot(widget, path):
    widget.grab().save(path)
    log("widget", path)


class Recorder:
    """Frames of the window while a scenario runs. A grab takes about
    0.12 s, so frames are kept in memory and written when the recording
    stops; the real rate is in fps.txt for ffmpeg."""

    def __init__(self, folder, fps=7):
        os.makedirs(folder, exist_ok=True)
        self.folder, self.frames = folder, []
        self.cursor = None
        self.caption = None
        self.timer = QtCore.QTimer(interval=int(1000 / fps))
        self.timer.timeout.connect(self.frame)

    def frame(self):
        try:
            self.frames.append((grab_parts(), self.cursor, self.caption, time.time()))
        except Exception:
            log(traceback.format_exc())

    def start(self):
        self.timer.start()

    def stop(self):
        self.timer.stop()
        if not self.frames:
            return
        span = self.frames[-1][3] - self.frames[0][3]
        rate = (len(self.frames) - 1) / span if span else 1
        images = [
            compose(*parts, cursor=cursor, caption=caption)
            for parts, cursor, caption, _ in self.frames
        ]
        # one size for all frames: a menu that reaches past the window made
        # some of them wider
        width = max(i.width() for i in images)
        height = max(i.height() for i in images)
        for n, image in enumerate(images):
            if (image.width(), image.height()) != (width, height):
                canvas = QtGui.QImage(width, height, QtGui.QImage.Format.Format_RGB32)
                canvas.fill(QtGui.QColor("#16181c"))
                painter = QtGui.QPainter(canvas)
                image.setDevicePixelRatio(1)
                painter.drawImage(0, 0, image)
                painter.end()
                image = canvas
            image.save(os.path.join(self.folder, "f%05d.jpg" % n), "JPG", 93)
        with open(os.path.join(self.folder, "fps.txt"), "w") as handle:
            handle.write("%.3f" % rate)
        log("frames", len(self.frames), "fps %.2f" % rate, "seconds %.1f" % span)
        self.frames = []


def center(widget, pos=None):
    return gpos(widget, pos if pos is not None else widget.rect().center())


def click(widget, pos=None, rec=None, button=Qt.MouseButton.LeftButton):
    pos = pos if pos is not None else widget.rect().center()
    if rec:
        rec.cursor = gpos(widget, pos)
    QTest.mouseClick(widget, button, Qt.KeyboardModifier.NoModifier, pos)


def hover(widget, pos=None, rec=None):
    pos = pos if pos is not None else widget.rect().center()
    if rec:
        rec.cursor = gpos(widget, pos)
    QTest.mouseMove(widget, pos)


def action(menu, text):
    menu.aboutToShow.emit() if not menu.isVisible() else None
    for a in menu.actions():
        label = a.text().replace("&", "")
        if label == text or label.startswith(text + " ["):  # "... [Ctrl-Shift-M]"
            return a
    raise KeyError("%r not in %r" % (text, [a.text() for a in menu.actions()]))


def menu_hover(menu, text, rec=None):
    """Move over a row of an open menu: a submenu opens as for a user."""
    a = action(menu, text)
    hover(menu, menu.actionGeometry(a).center(), rec)
    menu.setActiveAction(a)
    return a


def menu_click(menu, text, rec=None):
    a = action(menu, text)
    click(menu, menu.actionGeometry(a).center(), rec)
    return a


def find_button(parent, text=None, tip=None):
    for b in parent.findChildren(QtWidgets.QAbstractButton):
        if (text is not None and b.text().replace("&", "") == text) or (
            tip is not None and b.toolTip() == tip
        ):
            if b.isVisible() or text is not None:
                return b
    raise KeyError(text or tip)


def run(steps, done=None):
    """steps: (delay in ms before the step, callable). A failing step is
    logged and the run goes on, so the window always quits."""
    steps = list(steps)

    def nxt():
        if not steps:
            if done:
                done()
            return
        delay, fn = steps.pop(0)

        def go():
            try:
                fn()
            except Exception:
                log("STEP FAILED", getattr(fn, "__name__", fn))
                log(traceback.format_exc())
            nxt()

        QtCore.QTimer.singleShot(delay, go)

    nxt()


def later(ms, fn):
    """For a call that blocks (a menu's exec): the run goes on meanwhile."""
    QtCore.QTimer.singleShot(ms, fn)


def quit_():
    if LOG:
        LOG.close()
    cmd.quit()
