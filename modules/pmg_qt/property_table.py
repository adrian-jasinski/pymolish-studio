"""
Property table: one row per object, with its row number, a dot that shows or
hides the object, its name and one column per object property
(cmd.set_property, the data fields of an SDF file). Cells are edited in
place, columns are added, renamed and deleted from the header, blocks are
copied and pasted as tab-separated text. A window of its own that lies over
the viewport, its right edge against the Objects panel, until it is dragged
elsewhere. The table keeps no data: it shows and changes what the core holds.
"""

from pymol import CmdException
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


class _NoEditor(QtWidgets.QStyledItemDelegate):
    """Row and In are not edited."""

    def createEditor(self, *_):
        return None


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
        self.extra = set()  # columns added here that no object has a value for
        self._header = None  # the columns the tree was built with
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
        # cells, so that a block can be copied, pasted, emptied or edited
        tree.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectItems)
        Trigger = QtWidgets.QAbstractItemView.EditTrigger
        tree.setEditTriggers(
            Trigger.DoubleClicked | Trigger.EditKeyPressed | Trigger.AnyKeyPressed
        )
        tree.setTabKeyNavigation(True)  # Tab and Shift+Tab walk the cells
        self._no_editor = _NoEditor(tree)
        for column in (ROW, IN):
            tree.setItemDelegateForColumn(column, self._no_editor)
        tree.itemChanged.connect(self._edited)
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
        Standard = QtGui.QKeySequence.StandardKey
        for key, run in (
            (Standard.Copy, self.copy),
            (Standard.Paste, self.paste),
            (Standard.Delete, lambda: self._write(self._selected_cells(), None)),
        ):
            shortcut = QtGui.QShortcut(QtGui.QKeySequence(key), tree)
            shortcut.setContext(Qt.ShortcutContext.WidgetShortcut)
            shortcut.activated.connect(run)
        header = tree.header()
        header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header.customContextMenuRequested.connect(self._header_menu)

        add = QtWidgets.QPushButton("+ Column")
        add.setToolTip("Add an empty column")
        add.clicked.connect(lambda: self._ask_column())

        self.filter = QtWidgets.QLineEdit()
        self.filter.setPlaceholderText("Filter by name or value")
        self.filter.setClearButtonEnabled(True)
        self.filter.textChanged.connect(self._apply_filter)

        body = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(body)
        layout.setContentsMargins(4, 4, 4, 4)
        self.buttons = QtWidgets.QHBoxLayout()  # more of them with import
        self.buttons.addWidget(add)
        self.buttons.addWidget(self.filter, 1)
        layout.addLayout(self.buttons)
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

    def refresh(self, force=False):
        rows = table_rows(self.cmd)
        if rows == self.rows and not force:
            return
        columns = [
            c for c in self.columns if c in self.extra or any(c in r[4] for r in rows)
        ]
        for row in rows:
            columns += [p for p in row[4] if p not in columns]
        shape = [(r[0], r[1], r[3]) for r in rows]
        same = columns == self._header and shape == [
            (r[0], r[1], r[3]) for r in self.rows or ()
        ]
        self.rows, self.columns = rows, columns
        tree = self.tree
        tree.setSortingEnabled(False)  # not once per cell
        with QtCore.QSignalBlocker(tree):  # these are not edits
            if not same:
                self._rebuild(rows)
            for order, row in enumerate(rows):
                self._fill(self.items[row[0]], order, row)
        tree.setSortingEnabled(True)
        self._apply_filter()

    def _rebuild(self, rows):
        """Recreate the items; keep collapsed groups."""
        tree = self.tree
        collapsed = {
            n for n, i in self.items.items() if i.childCount() and not i.isExpanded()
        }
        first = tree.columnCount() < len(FIXED)
        tree.clear()
        tree.setColumnCount(len(FIXED) + len(self.columns))
        tree.setHeaderLabels([*FIXED, *self.columns])
        self._header = list(self.columns)
        self.items = {}
        for name, kind, _, _, _ in rows:
            item = _Row()
            item.setData(NAME, UserRole, (name, kind))
            # the dot toggles in _clicked, with Ctrl for "only this one"
            item.setFlags(
                (item.flags() | Qt.ItemFlag.ItemIsEditable)
                & ~Qt.ItemFlag.ItemIsUserCheckable
            )
            item.setTextAlignment(ROW, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.items[name] = item
        root = tree.invisibleRootItem()
        for name, _, _, parent, _ in rows:
            self.items.get(parent, root).addChild(self.items[name])
        for name, item in self.items.items():
            item.setExpanded(name not in collapsed)
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
        with QtCore.QSignalBlocker(self.tree):
            for item in self._shown():
                group = item.data(NAME, UserRole)[1] == "object:group"
                number += not group
                item.setText(ROW, "" if group else str(number))
        self._numbering = False

    def _shown(self):
        """The rows that are shown, top to bottom."""
        walk = QtWidgets.QTreeWidgetItemIterator(
            self.tree, QtWidgets.QTreeWidgetItemIterator.IteratorFlag.NotHidden
        )
        items = []
        while walk.value():
            items.append(walk.value())
            walk += 1
        return items

    # ---- editing ----

    def _selected_cells(self):
        return [
            (self.tree.itemFromIndex(i), i.column()) for i in self.tree.selectedIndexes()
        ]

    def _write(self, cells, text):
        """Set the property cells among `cells` (item, column) to `text`;
        None or "" deletes the property. The core picks the type: a whole
        number, a number, else text."""
        for item, column in cells:
            if column >= len(FIXED):
                self.cmd.set_property(
                    self.columns[column - len(FIXED)],
                    text.strip() if text and text.strip() else None,
                    item.data(NAME, UserRole)[0],
                )
        self.refresh(force=True)

    def _edited(self, item, column):
        """An editor closed with a new text. Applied once Qt is done with
        the editor: a refresh in the middle of its commit leaves it open."""
        name = item.data(NAME, UserRole)[0]
        text = item.text(column)
        # with several cells of the column selected, the edit goes to all
        cells = [c for c in self._selected_cells() if c[1] == column]
        if (item, column) not in cells:
            cells = [(item, column)]
        QtCore.QTimer.singleShot(0, lambda: self._apply(name, cells, column, text))

    def _apply(self, name, cells, column, text):
        cmd = self.cmd
        if column == NAME:
            new = cmd.get_legal_name(text.strip())  # spaces to _
            if new and new != name:
                if new in cmd.get_names("all"):
                    print(" Rename: the name '%s' is taken." % new)
                else:
                    try:
                        cmd.set_name(name, new)
                    except CmdException as error:  # a selection keyword
                        print(error)
            self.refresh(force=True)
        else:
            live = set(map(id, self.items.values()))  # not rebuilt meanwhile
            self._write([c for c in cells if id(c[0]) in live], text)

    def add_column(self, name):
        """An empty column; it becomes a property with its first value."""
        name = name.strip()
        if name and name not in self.columns and name not in FIXED:
            self.extra.add(name)
            self.columns.append(name)
            self.refresh(force=True)
            return True
        return False

    def rename_column(self, old, new):
        new = new.strip()
        if not new or new in self.columns or new in FIXED:
            return False
        for name, _, _, _, props in self.rows:
            if old in props:
                self.cmd.set_property(new, props[old], name)
                self.cmd.set_property(old, None, name)
        self.columns[self.columns.index(old)] = new  # it keeps its place
        self.extra.discard(old)
        self.extra.add(new)
        self.refresh(force=True)
        return True

    def delete_column(self, column):
        """Delete the property from every object."""
        for name, _, _, _, props in self.rows:
            if column in props:
                self.cmd.set_property(column, None, name)
        self.extra.discard(column)
        self.refresh(force=True)

    def _ask_column(self, old=None):
        """The dialog behind "+ Column" and "Rename column"."""
        name, ok = QtWidgets.QInputDialog.getText(
            self, "Rename column" if old else "New column", "Name:", text=old or ""
        )
        if ok and not (self.rename_column(old, name) if old else self.add_column(name)):
            QtWidgets.QMessageBox.information(
                self, "Column", "'%s' is empty or the name of a column." % name.strip()
            )

    def _header_menu(self, position):
        header = self.tree.header()
        column = header.logicalIndexAt(position)
        menu = QtWidgets.QMenu(header)
        menu.addAction("Add column...", lambda: self._ask_column())
        if column >= len(FIXED):
            name = self.columns[column - len(FIXED)]
            menu.addAction("Rename column...", lambda: self._ask_column(name))
            menu.addAction("Delete column", lambda: self._ask_delete(name))
        menu.exec(header.mapToGlobal(position))

    def _ask_delete(self, column):
        Button = QtWidgets.QMessageBox.StandardButton
        count = sum(column in row[4] for row in self.rows)
        answer = QtWidgets.QMessageBox.question(
            self,
            "Delete column",
            "Delete '%s' and its %d values? This cannot be undone." % (column, count),
            Button.Yes | Button.Cancel,
            Button.Cancel,
        )
        if answer == Button.Yes:
            self.delete_column(column)

    def _block(self):
        """The selected cells, or the current one, as (rows shown, columns
        in the order shown): what a copy takes and where a paste starts."""
        tree = self.tree
        cells = self._selected_cells()
        if not cells and tree.currentItem():
            cells = [(tree.currentItem(), tree.currentColumn())]
        visual = tree.header().visualIndex
        chosen = {id(item) for item, _ in cells}
        rows = [item for item in self._shown() if id(item) in chosen]
        columns = sorted({column for _, column in cells}, key=visual)
        return rows, columns

    def copy(self):
        """The block of the selected cells as tab-separated text."""
        rows, columns = self._block()
        lines = ["\t".join(item.text(c) for c in columns) for item in rows]
        QtWidgets.QApplication.clipboard().setText("\n".join(lines))

    def paste(self):
        """Tab-separated text into the property cells, from the first
        selected cell to the right and down the rows shown."""
        rows, columns = self._block()
        text = QtWidgets.QApplication.clipboard().text()
        if not rows or not text:
            return
        tree = self.tree
        shown = self._shown()
        shown = shown[shown.index(rows[0]) :]
        order = sorted(range(tree.columnCount()), key=tree.header().visualIndex)
        order = order[order.index(columns[0]) :]
        for item, line in zip(shown, text.rstrip("\n").split("\n")):
            for column, value in zip(order, line.split("\t")):
                if column >= len(FIXED):
                    self.cmd.set_property(
                        self.columns[column - len(FIXED)],
                        value.strip() or None,
                        item.data(NAME, UserRole)[0],
                    )
        self.refresh(force=True)

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
