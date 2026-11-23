"""
Ligand panel: the flat picture of pymol.ligand2d in the window. A click on
a residue selects it in the viewport, and the residues that are selected
there are ringed in the picture. A list picks among several ligands; the
picture can be saved as SVG or PNG.
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

        self.choice = QtWidgets.QComboBox()
        self.choice.setToolTip("The ligand that is drawn")
        self.choice.activated.connect(lambda _: self.refresh(keep=True))
        refresh = QtWidgets.QPushButton("Refresh")
        refresh.setToolTip("Find the ligands and the contacts again")
        refresh.clicked.connect(lambda: self.refresh())
        save = QtWidgets.QPushButton("Save...")
        save.setToolTip("Save the picture as SVG or PNG")
        save.clicked.connect(lambda: self.save_dialog())
        row = QtWidgets.QHBoxLayout()
        row.addWidget(self.choice, 1)
        row.addWidget(refresh)
        row.addWidget(save)

        self.picture = _Picture()
        self.picture.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.picture.setToolTip(
            "Click a residue to select it in 3D (Ctrl adds); double click zooms on it"
        )
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

    def _draw(self):
        window = self.palette().window().color()
        text = self.palette().windowText().color()
        svg, size, self.places = ligand2d.draw(
            self.mol,
            self.residues,
            selected=self.selected,
            background=window.getRgbF()[:3],
            ink=text.getRgbF()[:3],
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
        if not residue:
            return
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
