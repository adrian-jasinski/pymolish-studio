"""
Property table: one row per object, with its row number, a dot that shows or
hides the object, its name and one column per object property
(cmd.set_property, the data fields of an SDF file). Cells are edited in
place, columns are added, renamed and deleted from the header, blocks are
copied and pasted as tab-separated text. The Columns button hides columns and
adds counted ones (atoms, residues, ...); with Follow checked only the object
of the current row is shown; the row of an object an atom was picked in
becomes the current one. A window of its own that lies over the viewport, its
right edge against the Objects panel, until it is dragged elsewhere. The
table keeps no data: it shows and changes what the core holds. The order of
the columns, the hidden and the empty ones go into the session
(pymol.session_extra). The column "stars" is always there, after the name:
a rating from 0 to 3 drawn as three stars and set by a click.
"""

import csv
import math

from pymol import CmdException, session_extra, tables
from pymol.Qt import QtCore, QtGui, QtWidgets
from pymol.Qt.utils import getSaveFileNameWithExt

from .object_panel import context_menu, snapshot

Qt = QtCore.Qt
UserRole = Qt.ItemDataRole.UserRole
Checked, Unchecked = Qt.CheckState.Checked, Qt.CheckState.Unchecked
FIXED = ("Row", "In", "Name")
MOLECULE = "object:molecule"
ROW, IN, NAME = range(3)
# columns the core can count; written as ordinary properties when asked for
COMPUTED = ("atoms", "residues", "chains", "states", "weight", "charge")


def computed(cmd, name, columns=COMPUTED):
    """{column: value} of a molecule for the names of COMPUTED in `columns`."""
    sele = "%" + name
    values = {}
    if "atoms" in columns:
        values["atoms"] = cmd.count_atoms(sele)
    if "chains" in columns:
        values["chains"] = len(cmd.get_chains(sele))
    if "states" in columns:
        values["states"] = cmd.count_states(sele)
    if "weight" in columns:
        from pymol import util

        values["weight"] = round(util.compute_mass(sele, _self=cmd), 2)
    if "residues" in columns or "charge" in columns:
        seen, charge = set(), [0]
        cmd.iterate(
            sele,
            "seen.add((segi, chain, resi)); charge[0] += formal_charge",
            space={"seen": seen, "charge": charge},
        )
        if "residues" in columns:
            values["residues"] = len(seen)
        if "charge" in columns:
            values["charge"] = charge[0]
    return {c: values[c] for c in COMPUTED if c in values}  # in that order


def table_rows(cmd):
    """(name, kind, enabled, parent group, {property: value}) per object and
    group in panel order; selections and "all" are not rows."""
    rows = []
    for name, kind, enabled, parent in snapshot(cmd):
        if kind.startswith("object:"):
            # only molecules have properties: asked for those of a group or
            # a map, the core prints an error
            names = cmd.get_property_list(name) or () if kind == MOLECULE else ()
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


STARS = tables.STARS
STAR, STAR_GAP, STAR_LEFT = 16, 3, 6  # a star across, between two, before the first


def star_at(rect, x):
    """Which of the three stars of a cell is at x: 1 to 3, else 0."""
    side = min(STAR, rect.height() - 4)
    number, rest = divmod(x - rect.left() - STAR_LEFT, side + STAR_GAP)
    return int(number) + 1 if 0 <= number < 3 and rest <= side else 0


class _Cells(QtWidgets.QStyledItemDelegate):
    """Every cell but Row and In. In the column "stars" of a molecule:
    three stars, as many filled as the rating. A click on an empty star
    rates up to it, on a filled one down to the one before it. A value that
    is no rating is shown as its text and kept until it is edited."""

    def __init__(self, table):
        super().__init__(table.tree)
        self.table = table

    def rating(self, index):
        """The rating of a stars cell of a molecule (none is 0), else None."""
        table = self.table
        if STARS not in table.columns or index.column() != table.column_of(STARS):
            return None
        if table.tree.itemFromIndex(index).data(NAME, UserRole)[1] != MOLECULE:
            return None
        return tables.stars(index.data() or "0")

    def paint(self, painter, option, index):
        rating = self.rating(index)
        if rating is None:
            return super().paint(painter, option, index)
        cell = QtWidgets.QStyleOptionViewItem(option)
        self.initStyleOption(cell, index)
        cell.text = ""  # the row's background and selection, without the number
        Style = QtWidgets.QStyle
        cell.widget.style().drawControl(
            Style.ControlElement.CE_ItemViewItem, cell, painter, cell.widget
        )
        palette = cell.palette
        selected = bool(cell.state & Style.StateFlag.State_Selected)
        ink = (palette.highlightedText() if selected else palette.text()).color()
        full = ink if selected else palette.link().color()  # the accent, as the icons
        rect = option.rect
        side = min(STAR, rect.height() - 4)
        painter.save()
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        for number in range(3):
            middle = QtCore.QPointF(
                rect.left() + STAR_LEFT + number * (side + STAR_GAP) + side / 2,
                rect.center().y() + 0.5,
            )
            points = [
                middle
                + QtCore.QPointF(math.sin(k * math.pi / 5), -math.cos(k * math.pi / 5))
                * (side / 2 if k % 2 == 0 else side / 5)
                for k in range(10)
            ]
            filled = number < rating  # filled or outline: not told by color alone
            painter.setPen(QtGui.QPen(full if filled else ink, 1.2))
            painter.setBrush(full if filled else Qt.BrushStyle.NoBrush)
            painter.drawPolygon(QtGui.QPolygonF(points))
        painter.restore()

    def editorEvent(self, event, model, option, index):
        rating = self.rating(index)
        Type = QtCore.QEvent.Type
        if rating is not None and event.type() in (
            Type.MouseButtonRelease,
            Type.MouseButtonDblClick,
        ):
            star = star_at(option.rect, event.position().x())
            if star and event.button() == Qt.MouseButton.LeftButton:
                if event.type() == Type.MouseButtonRelease:
                    self.table.rate(self.table.tree.itemFromIndex(index), star, rating)
                return True  # and no editor opens on a double click
        return super().editorEvent(event, model, option, index)


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
        self.hidden = set()  # columns the Columns menu hides
        self._kept = None  # what the session keeps of the columns
        self._picked = None  # the objects of the last pick
        self._picking = False
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
        tree.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectItems
        )
        Trigger = QtWidgets.QAbstractItemView.EditTrigger
        tree.setEditTriggers(
            Trigger.DoubleClicked | Trigger.EditKeyPressed | Trigger.AnyKeyPressed
        )
        tree.setTabKeyNavigation(True)  # Tab and Shift+Tab walk the cells
        tree.setItemDelegate(_Cells(self))
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
        tree.header().sectionMoved.connect(lambda *_: self._remember())
        tree.currentItemChanged.connect(self._followed)
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

        self.columns_button = QtWidgets.QPushButton("Columns")
        self.columns_button.setToolTip("Hide and show columns; add counted ones")
        self.columns_button.setMenu(QtWidgets.QMenu(self.columns_button))
        self.columns_button.menu().aboutToShow.connect(self._fill_columns_menu)

        self.follow = QtWidgets.QCheckBox("Follow")
        self.follow.setToolTip(
            "Show only the object of the current row: Up and Down step through the objects"
        )
        self.follow.toggled.connect(
            lambda on: on and self._followed(tree.currentItem())
        )

        self.filter = QtWidgets.QLineEdit()
        self.filter.setPlaceholderText("Filter by name or value")
        self.filter.setClearButtonEnabled(True)
        self.filter.textChanged.connect(self._apply_filter)

        body = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(body)
        layout.setContentsMargins(4, 4, 4, 4)
        self.buttons = QtWidgets.QHBoxLayout()
        for text, tip, run in (
            ("Import", "Set properties from a CSV or Excel file", self.import_dialog),
            ("Export", "Write the rows and columns shown as CSV", self.export_dialog),
        ):
            button = QtWidgets.QPushButton(text)
            button.setToolTip(tip)
            button.clicked.connect(lambda _=False, run=run: run())
            self.buttons.addWidget(button)
        self.buttons.addWidget(add)
        self.buttons.addWidget(self.columns_button)
        self.buttons.addWidget(self.follow)
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
            self._follow_pick()

    def refresh(self, force=False):
        kept = session_extra.entries.get("table")
        if kept is not self._kept:  # another session was loaded, or a new one begun
            self._adopt(kept)
            force = True
        rows = table_rows(self.cmd)
        if rows == self.rows and not force:
            return
        columns = [
            c
            for c in self.columns
            if c == STARS or c in self.extra or any(c in r[4] for r in rows)
        ]
        if STARS not in columns:
            columns.insert(0, STARS)  # always there; after the name at first
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
        self._remember()

    def _adopt(self, kept):
        """The columns as a session kept them; as new without one."""
        self._kept = kept
        kept = kept if isinstance(kept, dict) else {}

        def names(key):
            value = kept.get(key)
            return (
                [n for n in value if isinstance(n, str)]
                if isinstance(value, list)
                else []
            )

        self.columns = names("columns")
        self.extra = set(names("empty")) & set(self.columns)
        self.hidden = set(names("hidden"))
        self._header = None  # build the tree again
        header = self.tree.header()
        with QtCore.QSignalBlocker(header):  # the order is in self.columns now
            for logical in range(header.count()):
                header.moveSection(header.visualIndex(logical), logical)

    def _remember(self):
        """The columns for the session: their order as shown, the hidden
        and the empty ones."""
        header = self.tree.header()
        built = self._header or []
        shown = sorted(
            built, key=lambda c: header.visualIndex(len(FIXED) + built.index(c))
        )
        kept = {
            "columns": shown,
            "hidden": sorted(self.hidden),
            "empty": sorted(self.extra),
        }
        if kept != self._kept:
            self._kept = session_extra.entries["table"] = kept

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
        for column, name in enumerate(self.columns, len(FIXED)):
            tree.setColumnHidden(column, name in self.hidden)
        self.items = {}
        for name, kind, _, _, _ in rows:
            item = _Row()
            item.setData(NAME, UserRole, (name, kind))
            # the dot toggles in _clicked, with Ctrl for "only this one"
            item.setFlags(
                (item.flags() | Qt.ItemFlag.ItemIsEditable)
                & ~Qt.ItemFlag.ItemIsUserCheckable
            )
            item.setTextAlignment(
                ROW, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            )
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
        for column, value in enumerate(item.values[1:], len(FIXED)):
            item.setText(column, cell_text(value))
        if kind == MOLECULE:
            rating = tables.stars(cell_text(props.get(STARS)) or "0")
            item.setData(
                self.column_of(STARS),
                Qt.ItemDataRole.AccessibleTextRole,
                "Stars: %d of 3" % rating if rating is not None else None,
            )

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

    def column_of(self, name):
        """The tree column of a property column."""
        return len(FIXED) + self.columns.index(name)

    def _set(self, column, text, name):
        """One cell to the core, which picks the type: a whole number, a
        number, else text; None or "" deletes the property. A rating that
        is not 0 to 3 is refused."""
        text = text.strip() if text else ""
        if column == STARS and text and tables.stars(text) is None:
            print(" Table: stars is a rating from 0 to 3, not '%s'." % text)
        else:
            self.cmd.set_property(column, text or None, name)

    def rate(self, item, star, rating):
        """A click on star 1 to 3 of a row that has `rating`."""
        new = star if star > rating else star - 1
        self._write([(item, self.column_of(STARS))], str(new))

    def _selected_cells(self):
        return [
            (self.tree.itemFromIndex(i), i.column())
            for i in self.tree.selectedIndexes()
        ]

    def _write(self, cells, text):
        """Set the property cells among `cells` (item, column) to `text`;
        None or "" deletes the property."""
        for item, column in cells:
            name, kind = item.data(NAME, UserRole)
            if column >= len(FIXED) and kind == MOLECULE:
                self._set(self.columns[column - len(FIXED)], text, name)
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
        if old in self.hidden:
            self.hidden.remove(old)
            self.hidden.add(new)
        self.refresh(force=True)
        return True

    def delete_column(self, column):
        """Delete the property from every object."""
        for name, _, _, _, props in self.rows:
            if column in props:
                self.cmd.set_property(column, None, name)
        self.extra.discard(column)
        self.hidden.discard(column)
        self.refresh(force=True)

    def set_hidden(self, column, hidden):
        """Hide or show a property column; the session keeps it."""
        (self.hidden.add if hidden else self.hidden.discard)(column)
        if column in self.columns:
            self.tree.setColumnHidden(len(FIXED) + self.columns.index(column), hidden)
        self._remember()

    def add_computed(self, columns=COMPUTED):
        """Columns the core counts, written as ordinary properties (so they
        are saved and exported). Counted now; "Refresh counted" counts the
        ones that are columns again."""
        for name, kind, _, _, _ in self.rows or ():
            if kind == MOLECULE:
                for column, value in computed(self.cmd, name, columns).items():
                    self.cmd.set_property(column, value, name)
        self.refresh(force=True)

    def _fill_columns_menu(self):
        menu = self.columns_button.menu()
        menu.clear()
        add = menu.addMenu("Add counted")
        for name in COMPUTED:
            add.addAction(name, lambda name=name: self.add_computed((name,)))
        add.addSeparator()
        add.addAction("all of them", lambda: self.add_computed())
        menu.addAction(
            "Refresh counted",
            lambda: self.add_computed([c for c in COMPUTED if c in self.columns]),
        )
        menu.addSeparator()
        for name in self.columns:
            action = menu.addAction(name)
            action.setCheckable(True)
            action.setChecked(name not in self.hidden)
            action.toggled.connect(
                lambda shown, name=name: self.set_hidden(name, not shown)
            )

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

    def import_dialog(self):
        """Import: pick a file, set the properties, say what happened."""
        self.show()
        filename = QtWidgets.QFileDialog.getOpenFileName(
            self, "Import table", "", "Tables (*.csv *.tsv *.txt *.xlsx);;All files (*)"
        )[0]
        if not filename:
            return
        try:
            matched, skipped, added = self.cmd.load_table(filename)
        except (CmdException, OSError, ValueError, KeyError) as error:
            QtWidgets.QMessageBox.warning(self, "Import table", str(error))
            return
        self.refresh(force=True)
        lines = ["%d rows matched an object." % matched]
        if skipped:
            more = ", ..." if len(skipped) > 5 else ""
            lines.append(
                "%d rows named no object: %s%s"
                % (len(skipped), ", ".join(skipped[:5]), more)
            )
        if added:
            lines.append("New columns: %s" % ", ".join(added))
        QtWidgets.QMessageBox.information(self, "Import table", "\n".join(lines))

    def export(self, filename):
        """The rows shown and the columns shown, as CSV."""
        tree = self.tree
        header = tree.header()
        columns = sorted(
            (
                c
                for c in range(NAME, tree.columnCount())
                if not header.isSectionHidden(c)
            ),
            key=header.visualIndex,
        )
        with open(filename, "w", newline="", encoding="utf-8") as handle:
            out = csv.writer(handle)
            out.writerow(["name", *(tree.headerItem().text(c) for c in columns[1:])])
            for item in self._shown():
                if item.data(NAME, UserRole)[1] != "object:group":
                    out.writerow([item.text(c) for c in columns])

    def export_dialog(self):
        filename = getSaveFileNameWithExt(
            self, "Export table", "", filter="CSV (*.csv)"
        )
        if filename:
            self.export(filename)

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
            name, kind = item.data(NAME, UserRole)
            for column, value in zip(order, line.split("\t")):
                if column >= len(FIXED) and kind == MOLECULE:
                    self._set(self.columns[column - len(FIXED)], value, name)
        self.refresh(force=True)

    # ---- clicks ----

    def _toggle(self, item, only=False):
        """Show or hide the object of this row; with `only`, hide the rest."""
        name = item.data(NAME, UserRole)[0]
        if only:
            self.cmd.disable("all")
            while item is not None:  # and the groups it is in
                self.cmd.enable(item.data(NAME, UserRole)[0])
                item = item.parent()
        elif item.checkState(IN) == Checked:
            self.cmd.disable(name)
        else:
            self.cmd.enable(name)
        self.refresh()

    def _followed(self, item, _=None):
        """Follow: only the object of the current row is shown."""
        if item is not None and self.follow.isChecked() and not self._picking:
            if item.data(NAME, UserRole)[1] != "object:group":
                self._toggle(item, only=True)

    def _follow_pick(self):
        """The row of the object an atom was picked in (pk1, else the
        active "sele") becomes the current one; once per pick."""
        cmd = self.cmd
        picked = cmd.get_object_list("?pk1")
        if not picked and "sele" in cmd.get_names("public_selections", enabled_only=1):
            picked = cmd.get_object_list("?sele")
        picked = tuple(picked or ())
        if picked == self._picked:
            return
        self._picked = picked
        item = self.items.get(picked[0]) if len(picked) == 1 else None
        editing = QtWidgets.QAbstractItemView.State.EditingState
        if item is not None and self.tree.state() != editing:
            self._picking = True  # a pick is not a step of Follow
            self.tree.setCurrentItem(item, NAME)
            self.tree.scrollToItem(item)
            self._picking = False

    def _clicked(self, item, column):
        if column == IN:
            ctrl = (
                QtWidgets.QApplication.keyboardModifiers()
                & Qt.KeyboardModifier.ControlModifier
            )
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
