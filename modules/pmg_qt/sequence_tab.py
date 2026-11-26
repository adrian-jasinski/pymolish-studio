"""The Sequence tab of the command panel: the rows of the sequence viewer of
the core (layer1/Seq.cpp, layer3/Seeker.cpp), drawn by Qt. The core keeps
the rows and handles the mouse, so an event here does what it does on the
rows in the viewport: a click adds a residue to the selection or takes it
out, a drag or a Shift+click takes a range, the middle button centers, the
right one opens the menu, a double click beside the rows selects nothing.
Over the rows: what Display > Sequence Mode sets, as three lists, and a
button for the alignment window."""

import bisect

import pymol
from pymol._gui import SEQUENCE_OPTIONS
from pymol.Qt import QtCore, QtGui, QtWidgets
from pymol.Qt.utils import getMonospaceFont

from .keymapping import get_modifiers

Qt = QtCore.Qt
MARGIN = 2  # pixels left of the first character
BUTTONS = {
    Qt.MouseButton.LeftButton: 0,
    Qt.MouseButton.MiddleButton: 1,
    Qt.MouseButton.RightButton: 2,
}


def columns(flags, c):
    """The columns of a row as lists: offsets, starts, stops, colors. A label
    row has an empty column for every residue without a label: left out, so
    that the offsets ascend as they do in the other rows."""
    lists = [c[0::4], c[1::4], c[2::4], c[3::4]]
    if flags & 1:
        keep = [i for i, (s, e) in enumerate(zip(lists[1], lists[2])) if e > s]
        lists = [[values[i] for i in keep] for values in lists]
    return lists


class Options(QtWidgets.QWidget):
    """The row over the sequence: the mode, the labels and the gaps as lists
    (the settings of Display > Sequence Mode, which they follow), and the
    alignment window. setting_callbacks is the table of the window: setting
    index -> callables it runs with the new value."""

    def __init__(self, cmd, setting_callbacks, open_alignment, parent=None):
        super().__init__(parent)
        row = QtWidgets.QHBoxLayout(self)
        row.setContentsMargins(4, 2, 4, 2)
        self.lists = {}
        for setting, title, choices in SEQUENCE_OPTIONS:
            box = QtWidgets.QComboBox()
            for label, value in choices:
                box.addItem(label, value)
            box.setAccessibleName("Sequence " + title.lower())
            box.setToolTip("%s of the sequence, here and in the viewport" % title)
            box.activated.connect(
                lambda _, box=box, setting=setting: cmd.set(
                    setting, box.currentData(), quiet=0, log=1
                )
            )

            def follow(value, box=box):
                box.setCurrentIndex(box.findData(int(value)))

            setting_callbacks[cmd.setting._get_index(setting)].append(follow)
            follow(cmd.get_setting_int(setting))
            label = QtWidgets.QLabel(title)
            label.setBuddy(box)
            row.addWidget(label)
            row.addWidget(box)
            self.lists[setting] = box
        row.addStretch(1)
        self.align = QtWidgets.QPushButton("Multiple sequence alignment…")
        self.align.setToolTip(
            "Open the alignment window: loaded chains, FASTA files, local MAFFT"
        )
        self.align.clicked.connect(lambda: open_alignment())
        row.addWidget(self.align)


# ponytail: not drawn here, unlike in the viewport: the dimming of the
# unaligned residues of an alignment, the frame around a drag, and the marks
# of the selection along the scroll bar. Add them to paintEvent when missed.
class SequenceTab(QtWidgets.QAbstractScrollArea):
    def __init__(self, cmd, parent=None):
        super().__init__(parent)
        self.cmd = cmd
        self.serial = -1  # of the rows held; the core counts its rebuilds
        # per row: text, 1 label row | 2 title in the first column, then per
        # column the character it starts at, text[start:stop] and the color,
        # then the fills as offset, length, offset, length, ...
        self.rows = []
        self.title = 0  # characters of the widest title
        self.state = []  # selected columns per row, colors, fill character
        self.setFont(getMonospaceFont())
        self.setAccessibleName("Sequence")
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)  # the arrow keys scroll
        self.horizontalScrollBar().setSingleStep(4)

    def cell(self):
        """Width and height of a character."""
        metrics = QtGui.QFontMetricsF(self.font())
        return metrics.horizontalAdvance("M"), metrics.height()

    def poll(self):
        if self.isVisible():
            self.refresh()

    def refresh(self):
        with self.cmd.lockcm:
            serial, rows, *state = pymol._cmd.seq_rows(self.cmd._COb, self.serial)
        if rows is None and state == self.state:
            return
        self.state = state
        if rows is not None:
            self.serial = serial
            self.rows = [
                (text, flags, *columns(flags, c), fills)
                for text, flags, c, fills in rows
            ]
            self.title = max(
                (
                    o[0] + e[0] - s[0]
                    for _, flags, o, s, e, _, _ in self.rows
                    if flags and o
                ),
                default=0,
            )
            self.set_ranges()
        self.viewport().update()

    def set_ranges(self):
        width, height = self.cell()
        view = self.viewport()
        columns = int((view.width() - MARGIN) / width)
        lines = int(view.height() / height)
        longest = max(
            (o[-1] + e[-1] - s[-1] for _, _, o, s, e, _, _ in self.rows if o), default=0
        )
        for bar, size, page in (
            (self.horizontalScrollBar(), longest, columns),
            (self.verticalScrollBar(), len(self.rows), lines),
        ):
            bar.setRange(0, max(0, size - page))
            bar.setPageStep(page)

    def resizeEvent(self, event):
        self.set_ranges()

    def changeEvent(self, event):
        # another text size: other characters per line, other places to hit
        if event.type() == QtCore.QEvent.Type.FontChange and hasattr(self, "state"):
            self.set_ranges()
            self.viewport().update()
        super().changeEvent(event)

    def showEvent(self, event):
        self.refresh()

    def paintEvent(self, event):
        if not self.state:  # not shown yet
            return
        painter = QtGui.QPainter(self.viewport())
        view = self.viewport().rect()
        selected, colors, fill_char = self.state
        # the colors of the residues are chosen for the viewport's background
        background, label, fill = (QtGui.QColor.fromRgb(c) for c in colors)
        painter.fillRect(view, background)
        if not self.rows:
            painter.setPen(label)
            painter.drawText(view, Qt.AlignmentFlag.AlignCenter, "No molecule is shown")
            return
        width, height = self.cell()
        ascent = QtGui.QFontMetricsF(self.font()).ascent()
        skip, top = self.horizontalScrollBar().value(), self.verticalScrollBar().value()
        end = skip + int(view.width() / width) + 1  # first character not seen

        def draw(text, offset, y):
            painter.drawText(QtCore.QPointF(MARGIN + offset * width, y + ascent), text)

        for i in range(top, min(len(self.rows), top + int(view.height() / height) + 1)):
            text, flags, offsets, starts, stops, rgb, fills = self.rows[i]
            y = (i - top) * height
            # a title stays at the left; what scrolls under it is not drawn
            first = skip + (self.title if flags else 0)
            if flags and offsets:
                painter.setPen(label)
                draw(text[starts[0] : stops[0]], self.title - (stops[0] - starts[0]), y)
            for b in range(max(1, bisect.bisect_left(offsets, first)), len(offsets)):
                if offsets[b] >= end:
                    break
                if offsets[b] == first and (flags == 2 or (flags and b > 1)):
                    continue  # a blank after the title
                color = label if flags & 1 else QtGui.QColor.fromRgb(rgb[b])
                if not flags & 1 and selected[i][b]:
                    painter.fillRect(
                        QtCore.QRectF(
                            MARGIN + (offsets[b] - skip) * width,
                            y,
                            (stops[b] - starts[b]) * width,
                            height,
                        ),
                        color,
                    )
                    color = Qt.GlobalColor.black
                painter.setPen(color)
                draw(text[starts[b] : stops[b]], offsets[b] - skip, y)
            if fill_char.strip():  # the residues an alignment or a gap leaves out
                painter.setPen(fill)
                for offset, length in zip(fills[0::2], fills[1::2]):
                    if first <= offset < end:
                        draw(fill_char[0] * length, offset - skip, y)

    def mouse(self, kind, event):
        width, height = self.cell()
        point = event.position()
        with self.cmd.lockcm:
            pymol._cmd.seq_mouse(
                self.cmd._COb,
                kind,
                BUTTONS.get(event.button(), -1),
                int(point.y() // height) + self.verticalScrollBar().value(),
                int((point.x() - MARGIN) // width) + self.horizontalScrollBar().value(),
                get_modifiers(event),
            )
        self.refresh()

    def mousePressEvent(self, event):
        if event.button() in BUTTONS:
            self.mouse(0, event)

    mouseDoubleClickEvent = mousePressEvent  # the second press of two

    def mouseMoveEvent(self, event):
        self.mouse(1, event)

    def mouseReleaseEvent(self, event):
        if event.button() in BUTTONS:
            self.mouse(2, event)

    def wheelEvent(self, event):
        # few rows, long ones: the wheel moves along the sequence
        bar = self.verticalScrollBar()
        QtWidgets.QApplication.sendEvent(
            bar if bar.maximum() else self.horizontalScrollBar(), event
        )
