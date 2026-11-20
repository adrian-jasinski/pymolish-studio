"""
Property table: one row per object, with its row number, a dot that shows or
hides the object, its name and one column per object property
(cmd.set_property, the data fields of an SDF file). A window of its own that
lies over the viewport, its right edge against the Objects panel, until it
is dragged elsewhere. The table keeps no data: it shows what the core holds.
"""

from pymol.Qt import QtCore, QtGui, QtWidgets

from .object_panel import context_menu, snapshot

Qt = QtCore.Qt
UserRole = Qt.ItemDataRole.UserRole
Checked, Unchecked = Qt.CheckState.Checked, Qt.CheckState.Unchecked
FIXED = ("Row", "In", "Name")
ROW, IN, NAME = range(3)


def table_rows(cmd):
    """(name, kind, enabled, parent group, {property: value}) per object and
    group in panel order; selections and "all" are not rows."""
    rows = []
    for name, kind, enabled, parent in snapshot(cmd):
        if kind.startswith("object:"):
            names = cmd.get_property_list(name) or ()
            props = {p: cmd.get_property(p, name) for p in names}
            rows.append((name, kind, enabled, parent, props))
    return rows


def cell_text(value):
    if isinstance(value, float):
        return "%.6g" % value
    return "" if value is None else str(value)


def _sort_key(value):
    """Numbers first, by value; then text; empty cells last."""
    if value is None:
        return (2, 0, "")
    if isinstance(value, (int, float)):
        return (0, value, "")
    return (1, 0, str(value).lower())


class _Row(QtWidgets.QTreeWidgetItem):
    """A row that sorts by the values behind its cells, not by their text;
    by Row or In, the order of the Objects panel."""

    order = 0
    values = ()  # per column, from NAME on

    def __lt__(self, other):
        column = self.treeWidget().sortColumn()
        if column < NAME:
            return self.order < other.order
        return _sort_key(self.values[column - NAME]) < _sort_key(
            other.values[column - NAME]
        )


class PropertyTable(QtWidgets.QDockWidget):
    def __init__(self, cmd, window, viewport, panel):
        """viewport is the widget the table opens over, panel the dock its
        right edge sticks to."""
        super().__init__("Table", window)
        self.setObjectName("dock_table")
        self.cmd = cmd
        self.viewport, self.panel = viewport, panel
        self.rows = None
        self.columns = []  # property names, in the order they first appeared
        self.items = {}
        self._stuck = True
        self._target = None  # where place() last put the table
        self._want = None  # the size the user gave it
        self._numbering = False

        self.tree = tree = QtWidgets.QTreeWidget()
        tree.setRootIsDecorated(True)
        tree.setTreePosition(NAME)  # group members nest under the name
        tree.setAlternatingRowColors(True)
        tree.setUniformRowHeights(True)
        tree.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection
        )
        tree.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        # as in the Objects panel: a dot, lit when the object is shown
        tree.setStyleSheet(
            "QTreeView::item { padding: 3px 6px; }"
            "QTreeView::indicator { width: 10px; height: 10px; border: none;"
            " border-radius: 5px; background-color: palette(mid); }"
            "QTreeView::indicator:checked { background-color: #3ddc5a; }"
        )
        tree.setSortingEnabled(True)
        tree.sortByColumn(ROW, Qt.SortOrder.AscendingOrder)
        tree.header().setSectionsMovable(True)
        tree.header().setFirstSectionMovable(False)
        tree.model().layoutChanged.connect(self._number)  # after a sort
        tree.itemClicked.connect(self._clicked)
        tree.itemDoubleClicked.connect(self._double_clicked)
        tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        tree.customContextMenuRequested.connect(self._context_menu)
        space = QtGui.QShortcut(Qt.Key.Key_Space, tree)
        space.setContext(Qt.ShortcutContext.WidgetShortcut)
        space.activated.connect(
            lambda: tree.currentItem() and self._toggle(tree.currentItem())
        )

        self.filter = QtWidgets.QLineEdit()
        self.filter.setPlaceholderText("Filter by name or value")
        self.filter.setClearButtonEnabled(True)
        self.filter.textChanged.connect(self._apply_filter)

        body = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(body)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addWidget(self.filter)
        layout.addWidget(tree, 1)
        self.setWidget(body)

        # A window of its own: it floats and cannot be docked. Last, because
        # floating it already sends move and show events.
        self.setAllowedAreas(Qt.DockWidgetArea.NoDockWidgetArea)
        self.setFloating(True)
        self.hide()

        # follow the main window and the Objects panel
        window.installEventFilter(self)
        panel.installEventFilter(self)

    # ---- the rows ----

    # ponytail: polled from the main window's 0.5 s timer while shown, one
    # read of every property (16 ms for 1,000 objects with 20 each); the
    # upgrade path is a change notification from the C++ executive.
    def poll(self):
        if self.isVisible():
            self.refresh()

    def refresh(self):
        rows = table_rows(self.cmd)
        if rows == self.rows:
            return
        columns = [c for c in self.columns if any(c in r[4] for r in rows)]
        for row in rows:
            columns += [p for p in row[4] if p not in columns]
        shape = [(r[0], r[1], r[3]) for r in rows]
        same = columns == self.columns and shape == [
            (r[0], r[1], r[3]) for r in self.rows or ()
        ]
        self.rows, self.columns = rows, columns
        tree = self.tree
        tree.setSortingEnabled(False)  # not once per cell
        if not same:
            self._rebuild(rows)
        for order, row in enumerate(rows):
            self._fill(self.items[row[0]], order, row)
        tree.setSortingEnabled(True)
        self._apply_filter()

    def _rebuild(self, rows):
        """Recreate the items; keep collapsed groups and the row selection."""
        tree = self.tree
        collapsed = {
            n for n, i in self.items.items() if i.childCount() and not i.isExpanded()
        }
        selected = {n for n, i in self.items.items() if i.isSelected()}
        first = tree.columnCount() < len(FIXED)
        tree.clear()
        tree.setColumnCount(len(FIXED) + len(self.columns))
        tree.setHeaderLabels([*FIXED, *self.columns])
        self.items = {}
        for name, kind, _, _, _ in rows:
            item = _Row()
            item.setData(NAME, UserRole, (name, kind))
            # the dot toggles in _clicked, with Ctrl for "only this one"
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsUserCheckable)
            item.setTextAlignment(ROW, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.items[name] = item
        root = tree.invisibleRootItem()
        for name, _, _, parent, _ in rows:
            self.items.get(parent, root).addChild(self.items[name])
        for name, item in self.items.items():
            item.setExpanded(name not in collapsed)
            item.setSelected(name in selected)
        if first:  # then the user's widths are kept
            em = tree.fontMetrics().height()
            for column, width in ((ROW, 4), (IN, 3), (NAME, 14)):
                tree.setColumnWidth(column, em * width)

    def _fill(self, item, order, row):
        name, kind, enabled, _, props = row
        item.order = order
        item.values = [name.lower(), *(props.get(c) for c in self.columns)]
        item.setText(NAME, name)
        if kind != "object:group":
            item.setCheckState(IN, Checked if enabled else Unchecked)
        right = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        left = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        for column, value in enumerate(item.values[1:], len(FIXED)):
            item.setText(column, cell_text(value))
            number = isinstance(value, (int, float)) and not isinstance(value, bool)
            item.setTextAlignment(column, right if number else left)

    def _apply_filter(self):
        text = self.filter.text().lower()

        def show(item):
            # a group stays visible while any member matches
            children = [show(item.child(i)) for i in range(item.childCount())]
            cells = (item.text(c) for c in range(NAME, self.tree.columnCount()))
            visible = any(text in cell.lower() for cell in cells) or any(children)
            item.setHidden(not visible)
            return visible

        for i in range(self.tree.topLevelItemCount()):
            show(self.tree.topLevelItem(i))
        self._number()

    def _number(self, *_):
        """Row numbers 1 to n over the rows shown, in the order shown;
        groups have none."""
        if self._numbering:  # writing a number is a change of its own
            return
        self._numbering = True
        number = 0
        walk = QtWidgets.QTreeWidgetItemIterator(
            self.tree, QtWidgets.QTreeWidgetItemIterator.IteratorFlag.NotHidden
        )
        while walk.value():
            item = walk.value()
            group = item.data(NAME, UserRole)[1] == "object:group"
            number += not group
            item.setText(ROW, "" if group else str(number))
            walk += 1
        self._numbering = False

    # ---- clicks ----

    def _toggle(self, item, only=False):
        """Show or hide the object of this row; with `only`, hide the rest."""
        name = item.data(NAME, UserRole)[0]
        if only:
            self.cmd.disable("all")
            self.cmd.enable(name)
        elif item.checkState(IN) == Checked:
            self.cmd.disable(name)
        else:
            self.cmd.enable(name)
        self.refresh()

    def _clicked(self, item, column):
        if column == IN:
            ctrl = QtWidgets.QApplication.keyboardModifiers() & Qt.KeyboardModifier.ControlModifier
            self._toggle(item, bool(ctrl))

    def _double_clicked(self, item, column):
        if column == ROW:
            name = item.data(NAME, UserRole)[0]
            self.cmd.enable(name)
            self.cmd.zoom(name, animate=-1)
            self.refresh()

    def _context_menu(self, position):
        item = self.tree.itemAt(position) or self.tree.currentItem()
        if item is not None:
            popup = context_menu(self.tree, self.cmd, *item.data(NAME, UserRole))
            popup.exec(self.tree.viewport().mapToGlobal(position))
            self.refresh()

    # ---- the window ----

    def stick(self):
        """Back over the viewport, against the Objects panel (Reset Layout)."""
        self._stuck = True
        self.place()

    def place(self):
        """Over the viewport, the right edge on the left edge of the Objects
        panel (of the viewport when the panel is closed or floats). As large
        as the viewport until the user gives it a size; then that size, cut
        to the viewport's."""
        area = QtCore.QRect(
            self.viewport.mapToGlobal(QtCore.QPoint(0, 0)), self.viewport.size()
        )
        right = area.right()
        if self.panel.isVisible() and not self.panel.isFloating():
            right = self.panel.mapToGlobal(QtCore.QPoint(0, 0)).x() - 1
        want = self._want or area.size()
        width = min(want.width(), right - area.left() + 1)
        height = min(want.height(), area.height())
        self._target = QtCore.QPoint(right - width + 1, area.top())
        # the geometry without the frame: some window systems add an
        # invisible margin for the shadow to the frame
        self.setGeometry(QtCore.QRect(self._target, QtCore.QSize(width, height)))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if event.spontaneous() and self.isVisible():  # by the mouse, not by place()
            self._want = event.size()

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()
        if self._stuck:
            QtCore.QTimer.singleShot(0, self.place)  # once the window exists

    def moveEvent(self, event):
        super().moveEvent(event)
        # dragged away by its title bar: it keeps its place from now on
        if self._target is not None and self.isVisible():
            if (self.geometry().topLeft() - self._target).manhattanLength() > 60:
                self._stuck = False

    def eventFilter(self, _, event):
        if event.type() in (
            QtCore.QEvent.Type.Move,
            QtCore.QEvent.Type.Resize,
            QtCore.QEvent.Type.Show,
            QtCore.QEvent.Type.Hide,
        ):
            if self._stuck and self.isVisible():
                QtCore.QTimer.singleShot(0, self.place)
        return False
