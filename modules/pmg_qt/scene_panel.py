"""
Scenes panel: one row per scene with its thumbnail, in a dock on the left.
A click or Enter recalls a scene, F2 renames it, dragging a row or
Ctrl+Up / Ctrl+Down moves it. A right click and the arrow keys pick a row
without recalling it, for Update, Rename and Delete.
"""

from pymol.Qt import QtCore, QtGui, QtWidgets

Qt = QtCore.Qt
UserRole = Qt.ItemDataRole.UserRole


class ScenePanel(QtWidgets.QDockWidget):
    def __init__(self, cmd, parent=None):
        super().__init__("Scenes", parent)
        self.setObjectName("dock_scenes")
        self.cmd = cmd
        self.state = None  # what the list shows: names, thumbnails, current

        self.list = view = QtWidgets.QListWidget()
        view.setIconSize(QtCore.QSize(110, 62))  # half a stored thumbnail
        view.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)
        view.setToolTip("Click or Enter recalls a scene; a right click only picks it")
        # a click recalls, so it must not also start a rename
        view.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        rename = QtGui.QShortcut(Qt.Key.Key_F2, view)
        rename.setContext(Qt.ShortcutContext.WidgetShortcut)
        rename.activated.connect(self._rename)
        # Not itemActivated: a double click, and on some desktops a single
        # one, activates too, and the scene would be recalled twice.
        view.itemClicked.connect(self._recall)  # left button, not after a drag
        for key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            enter = QtGui.QShortcut(key, view)
            enter.setContext(Qt.ShortcutContext.WidgetShortcut)  # not in a rename
            enter.activated.connect(lambda: self._recall(view.currentItem()))
        view.itemChanged.connect(self._renamed)
        view.model().rowsMoved.connect(self._moved)
        for key, step in ((Qt.Key.Key_Up, -1), (Qt.Key.Key_Down, 1)):
            move = QtGui.QShortcut(Qt.Modifier.CTRL | key, view)
            move.setContext(Qt.ShortcutContext.WidgetShortcut)
            move.activated.connect(lambda step=step: self._move(step))

        buttons = QtWidgets.QHBoxLayout()
        for label, tip, action in (
            ("Add", "Store the current view as a new scene", self._add),
            ("Update", "Store the current view in the picked scene", "update"),
            ("Rename", "Rename the selected scene (F2)", self._rename),
            ("Delete", "Delete the selected scene", "clear"),
        ):
            button = QtWidgets.QPushButton(label)
            button.setToolTip(tip)
            if isinstance(action, str):
                action = lambda _=False, action=action: self._scene(action)
            button.clicked.connect(action)
            buttons.addWidget(button)

        body = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(body)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addWidget(view, 1)
        layout.addLayout(buttons)
        self.setWidget(body)

    # ponytail: polled from the main window's 0.5 s timer while the dock is
    # shown (one 220x124 thumbnail per scene is compared); upgrade path is a
    # change notification from the core.
    def poll(self):
        if self.isVisible():
            self.refresh()

    def refresh(self):
        # a rebuild would close the editor of a rename in progress
        if self.list.viewport().findChild(QtWidgets.QLineEdit):
            return
        cmd = self.cmd
        names = cmd.get_scene_list()
        state = (
            names,
            [cmd.get_scene_thumbnail(name) for name in names],
            cmd.get("scene_current_name"),
        )
        if state == self.state:
            return
        self.state = state
        self.list.blockSignals(True)
        self.list.clear()
        for name, png in zip(names, state[1]):
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(png)
            item = QtWidgets.QListWidgetItem(QtGui.QIcon(pixmap), name)
            item.setData(UserRole, name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
            self.list.addItem(item)
            if name == state[2]:
                self.list.setCurrentItem(item)
        self.list.blockSignals(False)

    def _recall(self, item):
        if item:
            self.cmd.scene(item.text(), "recall")

    def _add(self):
        self.cmd.scene("new", "store")
        self.refresh()

    def _scene(self, action):
        item = self.list.currentItem()
        if item:
            self.cmd.scene(item.text(), action)
            self.refresh()

    def _rename(self):
        if self.list.currentItem():
            self.list.editItem(self.list.currentItem())

    def _renamed(self, item):
        old, new = item.data(UserRole), item.text()
        # the core deletes a scene renamed to "" and overwrites an existing
        # name; scene_order splits names at spaces
        if new and " " not in new and new not in self.cmd.get_scene_list():
            self.cmd.scene(old, "rename", new_key=new)
        # show the scene's real name again if the new one was refused; not
        # from inside the item's own signal: the refresh deletes the item
        self.state = None
        QtCore.QTimer.singleShot(0, self.refresh)

    def _move(self, step):
        row = self.list.currentRow()
        target = row + step
        if row >= 0 and 0 <= target < self.list.count():
            # moveRow inserts before its target row
            self.list.model().moveRow(
                QtCore.QModelIndex(), row, QtCore.QModelIndex(), target + (step > 0)
            )

    def _moved(self):
        names = [self.list.item(i).text() for i in range(self.list.count())]
        self.cmd.scene_order(" ".join(names))
