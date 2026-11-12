"""
Objects panel: the Qt replacement for the object list and the wizard buttons
of the viewport's internal GUI. One row per object or selection (group members
nested) with a visibility checkbox and the A/S/H/L/C menus from pymol.menu.
Everything is Qt text, so it follows the application font, the theme and
Display > UI Scale, and the dock is resized by dragging its edge.
"""

import re

from pymol import CmdException, _cmd
from pymol import menu as menus
from pymol.Qt import QtCore, QtGui, QtWidgets

Qt = QtCore.Qt
Checked, Unchecked = Qt.CheckState.Checked, Qt.CheckState.Unchecked
UserRole = Qt.ItemDataRole.UserRole

BUTTONS = (
    ("A", "Action"),
    ("S", "Show"),
    ("H", "Hide"),
    ("L", "Label"),
    ("C", "Color"),
)

# pymol.menu function per row type and button; same table as the C++ panel
# (layer3/Executive.cpp, CExecutive::click). None: no such button.
_MOL = ("mol_show", "mol_hide", "mol_labels", "mol_color")
_SIMPLE = ("simple_action", "cgo_show", "cgo_hide", None, "general_color")
MENUS = {
    "all": ("all_action",) + _MOL,
    "selection": ("sele_action",) + _MOL,
    "object:molecule": ("mol_action",) + _MOL,
    "object:group": ("group_action",) + _MOL,
    "object:map": ("map_action", "map_show", "map_hide", None, "general_color"),
    "object:mesh": ("mesh_action", "mesh_show", "mesh_hide", None, "mesh_color"),
    "object:surface": (
        "surface_action",
        "surface_show",
        "surface_hide",
        None,
        "mesh_color",
    ),
    "object:slice": (
        "slice_action",
        "slice_show",
        "slice_hide",
        None,
        "slice_color",
    ),
    "object:measurement": (
        "simple_action",
        "measurement_show",
        "measurement_hide",
        None,
        "measurement_color",
    ),
    "object:cgo": _SIMPLE,
    "object:alignment": _SIMPLE,
    "object:volume": (
        "simple_action",
        "volume_show",
        "volume_hide",
        None,
        "vol_color",
    ),
    "object:ramp": ("ramp_action", None, None, None, "ramp_color"),
    "object:": ("simple_action", None, None, None, None),  # callback objects
}


def snapshot(cmd):
    """Rows (name, kind, enabled, parent group) in panel order, "all" first."""
    enabled = set(cmd.get_names("public", enabled_only=1))
    parent = {}
    for group in cmd.get_names("public_group_objects"):
        with cmd.lockcm:
            members = _cmd.get_group_members(cmd._COb, group)
        for member in members.split():
            parent[member] = group
    rows = [("all", "all", bool(enabled), "")]
    for name in cmd.get_names("public"):
        rows.append((name, cmd.get_type(name), name in enabled, parent.get(name, "")))
    return rows


def menu_entries(cmd, name, kind, button):
    """The pymol.menu list behind one A/S/H/L/C button, or None."""
    function = MENUS.get(kind, MENUS["object:"])[button]
    if not function:
        return None
    if kind == "object:surface" and button == 4:
        return menus.mesh_color(cmd, name, "surface")
    return getattr(menus, function)(cmd, name)


def describe(cmd, name, kind):
    """(type, atoms, states) for tooltips and copied rows; None if unknown."""
    target = name if kind == "all" else "%" + name
    try:
        atoms = cmd.count_atoms(target) if kind != "object:group" else None
        states = cmd.count_states(target)
    except CmdException:  # maps, CGOs and friends have no atoms
        atoms = states = None
    return kind.replace("object:", "") or "object", atoms, states


SELECTING = (
    "Atoms",
    "Residues",
    "Chains",
    "Segments",
    "Objects",
    "Molecules",
    "C-alphas",
)


def status_text(cmd):
    """What the internal GUI shows under its object list: mouse mode, what a
    click selects, and the current state."""
    return "%s \N{MIDDLE DOT} Selecting %s \N{MIDDLE DOT} State %d/%d" % (
        cmd.get("button_mode_name"),
        SELECTING[cmd.get_setting_int("mouse_selection_mode")],
        cmd.get_state(),
        cmd.count_states(),
    )


_COLOR_CODE = re.compile(r"\\(\d{3}|---)")


def plain_label(text):
    """Menu labels carry \\RGB color markup (digits 0-9 per channel). Returns
    the text without it and the first color, or None."""
    match = re.search(r"\\(\d)(\d)(\d)", text)
    color = (
        QtGui.QColor(*(int(c) * 255 // 9 for c in match.groups())) if match else None
    )
    return _COLOR_CODE.sub("", text).strip().replace("&", "&&"), color


def _swatch(color):
    pixmap = QtGui.QPixmap(12, 12)
    pixmap.fill(color)
    return QtGui.QIcon(pixmap)


def fill_menu(menu, entries, cmd):
    """Fill a QMenu from a pymol.menu list of [kind, label, command]:
    kind 0 separator, 1 item, 2 title; command is a command string, a
    submenu list, or a callable returning one (filled when first opened)."""

    def fill_once(sub, command):
        if sub.isEmpty():
            fill_menu(sub, command() if callable(command) else command, cmd)

    for entry in entries:
        kind = entry[0]
        if kind == 0:
            menu.addSeparator()
            continue
        text, color = plain_label(entry[1])
        command = entry[2] if len(entry) > 2 else ""
        if kind == 2:
            menu.addSection(text)
            continue
        if isinstance(command, str):
            action = menu.addAction(text)
            action.triggered.connect(lambda _=False, c=command: cmd.do(c, echo=0))
        else:
            sub = menu.addMenu(text)
            sub.aboutToShow.connect(lambda s=sub, c=command: fill_once(s, c))
            action = sub.menuAction()
        if color:
            action.setIcon(_swatch(color))


class WizardPanel(QtWidgets.QGroupBox):
    """Title, buttons and menus of the active wizard (wizard.get_panel()).
    Hidden while no wizard runs."""

    changed = QtCore.Signal()

    def __init__(self, cmd):
        super().__init__("Wizard")
        self.cmd = cmd
        self.panel = None
        self.buttons = QtWidgets.QVBoxLayout(self)
        self.hide()

    def refresh(self):
        wizard = self.cmd.get_wizard()
        panel = wizard.get_panel() if wizard else None
        if panel == self.panel:
            return
        self.panel = panel
        while self.buttons.count():
            self.buttons.takeAt(0).widget().deleteLater()
        for kind, label, code in panel or ():
            text = plain_label(label)[0]
            if kind == 1:  # title
                self.setTitle(text)
                continue
            button = QtWidgets.QPushButton(text)
            if kind == 3:  # popup: code names a menu of the wizard
                popup = QtWidgets.QMenu(button)
                popup.aboutToShow.connect(lambda m=popup, c=code: self._fill(m, c))
                popup.triggered.connect(lambda _: self.changed.emit())
                button.setMenu(popup)
            else:
                button.clicked.connect(lambda _=False, c=code: self._run(c))
            self.buttons.addWidget(button)
        self.setVisible(bool(panel))

    def _fill(self, popup, code):
        popup.clear()
        fill_menu(popup, self.cmd.get_wizard().get_menu(code) or (), self.cmd)

    def _run(self, code):
        self.cmd.do(code, echo=0)
        self.changed.emit()


class ObjectPanel(QtWidgets.QDockWidget):
    def __init__(self, cmd, parent=None):
        super().__init__("Objects", parent)
        self.setObjectName("dock_objects")
        self.cmd = cmd
        self.rows = []
        self.items = {}

        self.tree = tree = QtWidgets.QTreeWidget()
        tree.setHeaderLabels(["Name"] + [letter for letter, _ in BUTTONS])
        tree.setUniformRowHeights(True)
        tree.setStyleSheet("QTreeView::item { padding: 2px 0; }")
        tree.setExpandsOnDoubleClick(False)
        tree.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection
        )
        header = tree.header()
        header.setStretchLastSection(False)
        header.setMinimumSectionSize(tree.fontMetrics().height() * 3 // 2)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
        for column, (_, tip) in enumerate(BUTTONS, 1):
            header.setSectionResizeMode(
                column, QtWidgets.QHeaderView.ResizeMode.ResizeToContents
            )
            tree.headerItem().setToolTip(column, tip)
            tree.headerItem().setTextAlignment(column, Qt.AlignmentFlag.AlignCenter)
        tree.itemChanged.connect(self._toggled)
        tree.itemClicked.connect(self._clicked)
        tree.itemDoubleClicked.connect(self._double_clicked)
        tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        tree.customContextMenuRequested.connect(self._context_menu)
        tree.viewport().installEventFilter(self)

        copy = QtGui.QShortcut(QtGui.QKeySequence.StandardKey.Copy, tree)
        copy.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        copy.activated.connect(self.copy_selected)

        self.filter = QtWidgets.QLineEdit()
        self.filter.setPlaceholderText("Filter by name")
        self.filter.setClearButtonEnabled(True)
        self.filter.textChanged.connect(self._apply_filter)

        self.status = QtWidgets.QLabel()
        self.status.setWordWrap(True)
        self.wizard = WizardPanel(cmd)
        self.wizard.changed.connect(self.refresh_soon)

        body = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(body)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addWidget(self.filter)
        layout.addWidget(tree, 1)
        layout.addWidget(self.wizard)
        layout.addWidget(self.status)
        self.setWidget(body)

    # ponytail: polled from the main window's 0.5 s timer (names, types and
    # visibility only, no atom data); upgrade path is a change notification
    # from the C++ executive.
    def poll(self):
        self.wizard.refresh()
        if self.wizard.panel:
            self.show()  # a wizard is unusable without its buttons
        if self.isVisible():
            self.refresh()
            self.status.setText(status_text(self.cmd))

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.Type.PaletteChange:
            self.rows = []  # theme toggled: rebuild with the new chip color
        super().changeEvent(event)

    def refresh_soon(self):
        QtCore.QTimer.singleShot(0, self.poll)

    def refresh(self):
        rows = snapshot(self.cmd)
        if rows == self.rows:
            return
        rebuilt = [(r[0], r[1], r[3]) for r in rows] != [
            (r[0], r[1], r[3]) for r in self.rows
        ]
        self.rows = rows
        with QtCore.QSignalBlocker(self.tree):
            if rebuilt:
                self._rebuild(rows)
            for name, _, enabled, _ in rows:
                self.items[name].setCheckState(0, Checked if enabled else Unchecked)
        if rebuilt:
            self._apply_filter()

    def _rebuild(self, rows):
        """Recreate the items; keep collapsed groups and the row selection."""
        collapsed = {
            n for n, i in self.items.items() if i.childCount() and not i.isExpanded()
        }
        selected = {n for n, i in self.items.items() if i.isSelected()}
        self.tree.clear()
        self.items = {}
        chip = self.palette().button()  # makes the letters read as buttons
        for name, kind, _, _ in rows:
            item = QtWidgets.QTreeWidgetItem(
                ["(%s)" % name if kind == "selection" else name]
            )
            item.setData(0, UserRole, (name, kind))
            for column, function in enumerate(MENUS.get(kind, MENUS["object:"]), 1):
                if function:
                    letter, tip = BUTTONS[column - 1]
                    item.setText(column, letter)
                    item.setToolTip(column, tip)
                    item.setBackground(column, chip)
                    item.setTextAlignment(column, Qt.AlignmentFlag.AlignCenter)
            self.items[name] = item
        root = self.tree.invisibleRootItem()
        for name, _, _, parent in rows:
            self.items.get(parent, root).addChild(self.items[name])
        for name, item in self.items.items():
            item.setExpanded(name not in collapsed)
            item.setSelected(name in selected)

    def _apply_filter(self):
        text = self.filter.text().lower()

        def show(item):
            # a group stays visible while any member matches
            children = [show(item.child(i)) for i in range(item.childCount())]
            visible = text in item.data(0, UserRole)[0].lower() or any(children)
            item.setHidden(not visible)
            return visible

        for i in range(self.tree.topLevelItemCount()):
            show(self.tree.topLevelItem(i))

    def _toggled(self, item, column):
        name = item.data(0, UserRole)[0]
        if item.checkState(0) == Checked:
            self.cmd.enable(name)
        else:
            self.cmd.disable(name)
        self.refresh_soon()

    def _clicked(self, item, column):
        if column:
            rect = self.tree.visualRect(self.tree.indexFromItem(item, column))
            self._popup(
                item, column - 1, self.tree.viewport().mapToGlobal(rect.bottomLeft())
            )

    def _double_clicked(self, item, column):
        if column == 0:
            self.cmd.zoom(item.data(0, UserRole)[0], animate=-1)

    def _popup(self, item, button, position):
        entries = menu_entries(self.cmd, *item.data(0, UserRole), button)
        if entries:
            popup = QtWidgets.QMenu(self.tree)
            fill_menu(popup, entries, self.cmd)
            popup.exec(position)
            self.refresh_soon()

    def _context_menu(self, position):
        """Right click or the Menu key: the five menus of the row as submenus."""
        item = self.tree.itemAt(position) or self.tree.currentItem()
        if item is None:
            return
        name, kind = item.data(0, UserRole)
        popup = QtWidgets.QMenu(self.tree)
        for button, (_, title) in enumerate(BUTTONS):
            if MENUS.get(kind, MENUS["object:"])[button]:
                sub = popup.addMenu(title)
                sub.aboutToShow.connect(
                    lambda s=sub, b=button: (
                        s.isEmpty()
                        and fill_menu(
                            s, menu_entries(self.cmd, name, kind, b), self.cmd
                        )
                    )
                )
        popup.exec(self.tree.viewport().mapToGlobal(position))
        self.refresh_soon()

    def eventFilter(self, watched, event):
        # counts are looked up when asked for, never while polling
        if event.type() == QtCore.QEvent.Type.ToolTip:
            item = self.tree.itemAt(event.pos())
            if item and self.tree.columnAt(event.pos().x()) == 0:
                kind, atoms, states = describe(self.cmd, *item.data(0, UserRole))
                parts = [kind]
                if atoms is not None:
                    parts.append("%d atoms" % atoms)
                if states is not None:
                    parts.append("%d states" % states)
                QtWidgets.QToolTip.showText(event.globalPos(), ", ".join(parts))
                return True
        return super().eventFilter(watched, event)

    def copy_selected(self):
        lines = ["Name\tType\tShown\tAtoms\tStates"]
        for name, kind, enabled, _ in self.rows:
            if self.items[name].isSelected():
                row = (name, *describe(self.cmd, name, kind))
                row = row[:2] + (enabled,) + row[2:]
                lines.append("\t".join("" if v is None else str(v) for v in row))
        QtWidgets.QApplication.clipboard().setText("\n".join(lines))
