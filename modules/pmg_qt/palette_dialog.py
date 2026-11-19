"""
Dialog for a palette of the user: a name and a list of colors in the order
objects and chains get them. Opened from the palette menu of the action
toolbar, which stores the result (theme.user_palettes).
"""

import re

from pymol.Qt import QtCore, QtGui, QtWidgets

Qt = QtCore.Qt
NAME = re.compile(r"[a-z][a-z0-9_]*")


class PaletteDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, name="", colors=(), taken=()):
        """`taken`: names that cannot be used (the built-in palettes)."""
        super().__init__(parent)
        self.setWindowTitle("Edit palette" if name else "New palette")
        self.taken = set(taken) | {"default"}
        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()
        self.name = QtWidgets.QLineEdit(name)
        self.name.setPlaceholderText("lowercase letters, digits, _")
        form.addRow("&Name", self.name)
        layout.addLayout(form)

        row = QtWidgets.QHBoxLayout()
        layout.addLayout(row)
        self.list = QtWidgets.QListWidget()
        self.list.setAccessibleName("Colors, in the order they are given out")
        row.addWidget(self.list)
        buttons = QtWidgets.QVBoxLayout()
        row.addLayout(buttons)
        for text, run in (
            ("&Add...", self._add),
            ("&Change...", self._change),
            ("&Remove", self._remove),
            ("&Up", lambda: self._move(-1)),
            ("&Down", lambda: self._move(1)),
        ):
            button = QtWidgets.QPushButton(text)
            button.clicked.connect(run)
            buttons.addWidget(button)
        buttons.addStretch(1)
        self.list.itemDoubleClicked.connect(lambda _: self._change())

        self.note = QtWidgets.QLabel()
        layout.addWidget(self.note)
        Box = QtWidgets.QDialogButtonBox
        self.box = Box(Box.StandardButton.Ok | Box.StandardButton.Cancel)
        self.box.accepted.connect(self.accept)
        self.box.rejected.connect(self.reject)
        layout.addWidget(self.box)
        self.name.textChanged.connect(self._check)
        for color in colors:
            self._append(color)
        self._check()

    def value(self):
        """(name, colors as "rrggbb")."""
        colors = [
            self.list.item(i).text().lstrip("#") for i in range(self.list.count())
        ]
        return self.name.text().strip(), colors

    def _append(self, color, row=None):
        color = QtGui.QColor("#" + color.lstrip("#"))
        pixmap = QtGui.QPixmap(28, 16)
        pixmap.fill(color)
        item = QtWidgets.QListWidgetItem(QtGui.QIcon(pixmap), color.name())
        self.list.insertItem(self.list.count() if row is None else row, item)
        self.list.setCurrentItem(item)
        self._check()

    def _pick(self, start):
        color = QtWidgets.QColorDialog.getColor(QtGui.QColor(start), self, "Color")
        return color.name() if color.isValid() else None

    def _add(self):
        color = self._pick("#3f93e6")
        if color:
            self._append(color)

    def _change(self):
        row = self.list.currentRow()
        if row >= 0:
            color = self._pick(self.list.item(row).text())
            if color:
                self.list.takeItem(row)
                self._append(color, row)

    def _remove(self):
        self.list.takeItem(self.list.currentRow())
        self._check()

    def _move(self, step):
        row = self.list.currentRow()
        if row >= 0 and 0 <= row + step < self.list.count():
            item = self.list.takeItem(row)
            self.list.insertItem(row + step, item)
            self.list.setCurrentItem(item)

    def _check(self, *_):
        name = self.name.text().strip()
        if not NAME.fullmatch(name):
            note = "The name starts with a letter: lowercase letters, digits, _."
        elif name in self.taken:
            note = "A built-in palette has that name."
        elif self.list.count() < 2:
            note = "Add at least two colors."
        else:
            note = ""
        self.note.setText(note)
        Ok = QtWidgets.QDialogButtonBox.StandardButton.Ok
        self.box.button(Ok).setEnabled(not note)
