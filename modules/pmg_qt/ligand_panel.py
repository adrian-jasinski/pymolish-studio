"""
Ligand panel: the flat picture of pymol.ligand2d in the window. A click on
a residue selects it in the viewport, and the residues that are selected
there are ringed in the picture. A list picks among several ligands; the
picture can be saved as SVG or PNG. "Show in 3D" draws the contacts as
dashes in the viewport while the panel is open. Hovering a residue, or
Tab to it, tells its distances; Enter selects it.
"""

import math

from pymol import CmdException, ligand2d, ligand_nav
from pymol.Qt import QtCore, QtGui, QtWidgets
from pymol.Qt.utils import getSaveFileNameWithExt

Qt = QtCore.Qt


class _Picture(QtWidgets.QLabel):
    clicked = QtCore.Signal(QtCore.QPointF, bool)  # where, with Ctrl
    double_clicked = QtCore.Signal(QtCore.QPointF)
    resized = QtCore.Signal()
    entered = QtCore.Signal(bool)  # Enter on the residue of the keyboard, with Ctrl
    tip = None  # the panel's: point -> text of the tooltip, or ""
    step = None  # the panel's: Tab forward or back -> False when past the end

    def event(self, event):
        if event.type() == QtCore.QEvent.Type.ToolTip and self.tip:
            text = self.tip(QtCore.QPointF(event.pos())) or self.toolTip()
            QtWidgets.QToolTip.showText(event.globalPos(), text, self)
            return True
        return super().event(event)

    def focusNextPrevChild(self, forward):
        if self.step and self.step(forward):
            return True
        return super().focusNextPrevChild(forward)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.entered.emit(
                bool(event.modifiers() & Qt.KeyboardModifier.ControlModifier)
            )
            return
        super().keyPressEvent(event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resized.emit()

    def mousePressEvent(self, event):
        ctrl = bool(event.modifiers() & Qt.KeyboardModifier.ControlModifier)
        self.clicked.emit(event.position(), ctrl)

    def mouseDoubleClickEvent(self, event):
        self.double_clicked.emit(event.position())


class LigandPanel(QtWidgets.QDockWidget):
    def __init__(self, cmd, parent=None):
        super().__init__("Ligand 2D", parent)
        self.setObjectName("dock_ligand")
        self.cmd = cmd
        self.mol = None
        self.residues = []
        self.places = []  # the residues' centers in the picture
        self.selected = set()  # indices of the residues that are in "sele"
        self._svg, self._size, self._scale = None, (1, 1), 1.0
        self._followed = None  # the ligand of ligand_next the panel last went to
        self.current = None  # the residue Tab went to
        self._dashes = []  # the objects of "Show in 3D"

        self.choice = QtWidgets.QComboBox()
        self.choice.setToolTip("The ligand that is drawn")
        self.choice.activated.connect(lambda _: self.refresh(keep=True))
        refresh = QtWidgets.QPushButton("Refresh")
        refresh.setToolTip("Find the ligands and the contacts again")
        refresh.clicked.connect(lambda: self.refresh())
        save = QtWidgets.QPushButton("Save...")
        save.setToolTip("Save the picture as SVG or PNG")
        save.clicked.connect(lambda: self.save_dialog())
        self.in_3d = QtWidgets.QCheckBox("Show in 3D")
        self.in_3d.setToolTip(
            "The contacts as dashes in the viewport, in the group 'ligand_2d';"
            " they go when the panel closes"
        )
        self.in_3d.toggled.connect(lambda _: self._update_3d())
        row = QtWidgets.QHBoxLayout()
        row.addWidget(self.choice, 1)
        row.addWidget(self.in_3d)
        row.addWidget(refresh)
        row.addWidget(save)

        self.picture = _Picture()
        self.picture.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.picture.setToolTip(
            "Click a residue to select it in 3D (Ctrl adds); double click zooms"
            " on it. Tab walks the residues, Enter selects one."
        )
        self.picture.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.picture.tip = self._tip
        self.picture.step = self._step
        self.picture.entered.connect(self._entered)
        self.picture.clicked.connect(self._clicked)
        self.picture.double_clicked.connect(self._double_clicked)
        self.picture.resized.connect(self._render)
        # the picture is drawn as large as the panel allows
        self.picture.setMinimumSize(240, 240)
        Policy = QtWidgets.QSizePolicy.Policy
        self.picture.setSizePolicy(Policy.Ignored, Policy.Ignored)

        body = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(body)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addLayout(row)
        layout.addWidget(self.picture, 1)
        self.setWidget(body)

    def open(self):
        first = not self.isVisible() and self.width() < 420
        self.show()
        self.raise_()
        if first and not self.isFloating() and self.parent():  # room for the picture
            self.parent().resizeDocks([self], [420], Qt.Orientation.Horizontal)
        self.refresh()

    def refresh(self, keep=False):
        """Find the ligands (unless `keep`: the list was only used) and draw
        the chosen one."""
        current = self.choice.currentData()
        if not keep:
            found = ligand2d.ligands(_self=self.cmd)
            self.choice.clear()
            for label, sele in found:
                self.choice.addItem(label, sele)
            index = self.choice.findData(current)
            self.choice.setCurrentIndex(max(index, 0))
        ligand = self.choice.currentData()
        self.mol, self.residues, self.places, self._svg = None, [], [], None
        self.current = None
        try:
            if not ligand:
                self.picture.setPixmap(QtGui.QPixmap())
                self.picture.setText("No ligand in the visible objects.")
                return
            try:
                self.mol, self.residues = ligand2d.analyze(ligand, _self=self.cmd)
            except CmdException as error:  # no rdkit, or a ligand it cannot read
                self.picture.setPixmap(QtGui.QPixmap())
                self.picture.setText(str(error))
                return
            self.selected = self._in_selection()
            self._draw()
        finally:
            self._update_3d()

    def _update_3d(self):
        """The dashes of "Show in 3D": made again for the ligand drawn, gone
        when the box is off, the panel is closed or nothing is drawn."""
        ligand2d.hide_contacts(self._dashes, _self=self.cmd)
        self._dashes = []
        if self.in_3d.isChecked() and not self.isHidden() and self.residues:
            self._dashes = ligand2d.show_contacts(self.residues, _self=self.cmd)

    def hideEvent(self, event):
        super().hideEvent(event)
        if self.isHidden():  # closed, not only behind another tab
            ligand2d.hide_contacts(self._dashes, _self=self.cmd)
            self._dashes = []

    def _draw(self):
        window = self.palette().window().color()
        text = self.palette().windowText().color()
        svg, size, self.places = ligand2d.draw(
            self.mol,
            self.residues,
            selected=self.selected,
            background=window.getRgbF()[:3],
            ink=text.getRgbF()[:3],
            current=self.current,
        )
        self._svg, self._size = svg, size
        self._render()

    def _render(self):
        """The whole picture, as large as the panel has room for."""
        if self._svg is None:
            return
        width, height = self._size
        self._scale = scale = min(
            self.picture.width() / width, self.picture.height() / height
        )
        data = QtCore.QBuffer()
        data.setData(self._svg.encode())
        reader = QtGui.QImageReader(data, b"svg")
        ratio = self.devicePixelRatioF()
        reader.setScaledSize(QtCore.QSize(width, height) * (scale * ratio))  # sharp
        pixmap = QtGui.QPixmap.fromImage(reader.read())
        pixmap.setDevicePixelRatio(ratio)
        self.picture.setPixmap(pixmap)

    def _in_selection(self):
        """The residues of the picture with an atom in "sele"."""
        cmd = self.cmd
        if "sele" not in cmd.get_names("selections"):
            return set()
        return {
            i
            for i, residue in enumerate(self.residues)
            if cmd.count_atoms("sele and (%s)" % residue["sele"])
        }

    def poll(self):
        """From the window's timer: follow the selection made in 3D, and
        the ligand that ligand_next went to."""
        visited = ligand_nav.current()
        if self.isVisible() and visited and visited != self._followed:
            self._followed = visited
            if self.choice.findData(visited) < 0:
                self.refresh()  # the list is from before
            index = self.choice.findData(visited)
            if index >= 0 and visited != self.choice.currentData():
                self.choice.setCurrentIndex(index)
                self.refresh(keep=True)
        if self.isVisible() and self.mol is not None:
            selected = self._in_selection()
            if selected != self.selected:
                self.selected = selected
                self._draw()

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.Type.PaletteChange and self.mol is not None:
            self._draw()  # dark or light, as the window
        super().changeEvent(event)

    @staticmethod
    def describe(residue):
        """The text of a residue's tooltip: its kind, contacts, distances."""
        lines = ["%s %s, %s" % (*residue["label"], residue["kind"])]
        lines += ["%s %.1f \u00c5" % (name, d) for name, _, _, d in residue["pairs"]]
        lines.append("nearest atoms %.1f \u00c5" % residue["nearest"])
        return "\n".join(lines)

    def _tip(self, position):
        residue = self.mol is not None and self._residue_at(position)
        return self.describe(residue) if residue else ""

    def _point(self, index):
        """A residue's center in the coordinates of the label."""
        scale = self._scale
        x, y = self.places[index]
        left = (self.picture.width() - self._size[0] * scale) / 2
        top = (self.picture.height() - self._size[1] * scale) / 2
        return QtCore.QPoint(round(x * scale + left), round(y * scale + top))

    def _step(self, forward):
        """Tab: the next residue around the ring; False past the last one,
        so the focus goes on to the next control."""
        if self.mol is None or not self.places:
            return False
        cx = sum(x for x, _ in self.places) / len(self.places)
        cy = sum(y for _, y in self.places) / len(self.places)
        ring = sorted(
            range(len(self.places)),
            key=lambda i: math.atan2(self.places[i][1] - cy, self.places[i][0] - cx),
        )
        if self.current is None:
            at = 0 if forward else len(ring) - 1
        else:
            at = ring.index(self.current) + (1 if forward else -1)
        self.current = ring[at] if 0 <= at < len(ring) else None
        self._draw()
        if self.current is None:
            return False
        point = self.picture.mapToGlobal(self._point(self.current))
        QtWidgets.QToolTip.showText(
            point, self.describe(self.residues[self.current]), self.picture
        )
        return True

    def _entered(self, add):
        if self.current is not None:
            self._select(self.residues[self.current], add)

    def _residue_at(self, position):
        """The residue whose shape is under a point of the label, or None."""
        # the picture is centered in the label, at self._scale
        scale = self._scale
        left = (self.picture.width() - self._size[0] * scale) / 2
        top = (self.picture.height() - self._size[1] * scale) / 2
        x, y = (position.x() - left) / scale, (position.y() - top) / scale
        for residue, (px, py) in zip(self.residues, self.places):
            if math.hypot(x - px, y - py) <= ligand2d.SIZE / 2:  # in the circle
                return residue
        return None

    def _clicked(self, position, add):
        residue = self.mol is not None and self._residue_at(position)
        if residue:
            self._select(residue, add)

    def _select(self, residue, add):
        cmd = self.cmd
        target = residue["sele"]
        if add and "sele" in cmd.get_names("selections"):
            target = "sele or (%s)" % target
        cmd.select("sele", target, enable=1)
        cmd.show("sticks", "(%s) and not hydro" % residue["sele"])
        self.poll()

    def _double_clicked(self, position):
        residue = self.mol is not None and self._residue_at(position)
        if residue:
            self.cmd.zoom(residue["sele"], 6, animate=1)

    def save(self, filename):
        self.cmd.ligand_2d(self.choice.currentData(), filename=filename)

    def save_dialog(self):
        if self.mol is None:
            return
        filename = getSaveFileNameWithExt(
            self, "Save the picture", "", filter="SVG (*.svg);;PNG (*.png)"
        )
        if filename:
            self.save(filename)
