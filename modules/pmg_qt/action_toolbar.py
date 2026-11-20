"""
Action toolbar above the viewport: what a click selects, undo/redo, the view
actions, presets, the object color palette, the background, and on the right
the panels, the render popup and the UI scale. Every button has a line icon; undo and redo
show only that. Replaces the grid of quick buttons that sat next to the log.
"""

import pymol
from pymol import menu as menus
from pymol import palettes, util
from pymol.Qt import QtCore, QtGui, QtWidgets

from . import theme
from .icons import menu_icon
from .object_panel import SELECTING, fill_menu

Qt = QtCore.Qt
Style = Qt.ToolButtonStyle
Popup = QtWidgets.QToolButton.ToolButtonPopupMode


# Menu of the background button: name -> (top, bottom) as hex, bottom None
# for a plain color; None starts a new group. Each was ray traced under a
# rainbow-colored protein (docs/plans/16-background.md).
BACKGROUNDS = (
    ("Black", "000000", None),
    ("Charcoal", "1E1E1E", None),
    ("Gray", "808080", None),
    ("Light gray", "CCCCCC", None),
    ("White", "FFFFFF", None),
    None,
    ("Night blue", "0B1D33", None),
    ("Slate", "2F3E55", None),
    None,
    ("PyMOL blue", "00004D", "333380"),
    ("Night", "000000", "1B2A49"),
    ("Graphite", "3A3A3A", "101010"),
    ("Steel", "5A6B7D", "1E2630"),
    ("Studio", "FFFFFF", "C8CDD4"),
    ("Sky", "DCEBFA", "FFFFFF"),
)
# what a background is made of, and what "Remember after restart" saves
BACKGROUND_SETTINGS = (
    "bg_rgb",
    "bg_gradient",
    "bg_rgb_top",
    "bg_rgb_bottom",
    "opaque_background",
)
# toolbar icons: side in pixels, and line width on the 24 px grid of the
# drawings (menus use 16 and 1.5)
ICON = 20
STROKE = 2
ACCENT = "#1e4fb8"  # the A button of the Objects panel; also in pymol.sty


def _caption(menu, text):
    """A menu caption like the ones object_panel.fill_menu draws."""
    title = QtWidgets.QWidgetAction(menu)
    title.setDefaultWidget(QtWidgets.QLabel(text, objectName="menu_title"))
    title.setEnabled(False)
    menu.addAction(title)


def _swatch(top, bottom, active, mark):
    """Menu icon: the background as a square, with a frame in the color
    `mark` when it is the one in use (Qt draws no check mark next to an
    icon)."""
    pixmap = QtGui.QPixmap(16, 16)
    gradient = QtGui.QLinearGradient(0, 0, 0, 16)
    gradient.setColorAt(0, QtGui.QColor("#" + top))
    gradient.setColorAt(1, QtGui.QColor("#" + (bottom or top)))
    painter = QtGui.QPainter(pixmap)
    painter.fillRect(0, 0, 16, 16, gradient)
    # a thin grey edge, so black shows on a dark menu and white on a light one
    painter.setPen(
        QtGui.QPen(mark if active else QtGui.QColor(128, 128, 128), 3 if active else 1)
    )
    painter.drawRect(
        pixmap.rect().adjusted(1, 1, -2, -2)
        if active
        else pixmap.rect().adjusted(0, 0, -1, -1)
    )
    painter.end()
    icon = QtGui.QIcon(pixmap)
    icon.addPixmap(pixmap, QtGui.QIcon.Mode.Selected)  # else Qt tints it
    return icon


def _strip(colors):
    """List icon: up to ten QColors side by side. Always ten wide, so the
    names line up."""
    pixmap = QtGui.QPixmap(140, 16)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QtGui.QPainter(pixmap)
    for i, color in enumerate(colors):
        painter.fillRect(14 * i, 0, 13, 16, color)
    painter.end()
    icon = QtGui.QIcon(pixmap)
    icon.addPixmap(pixmap, QtGui.QIcon.Mode.Selected)  # else Qt tints it
    return icon


class ActionToolbar(QtWidgets.QToolBar):
    def __init__(self, cmd, setting_callbacks, panels=(), more=()):
        """setting_callbacks maps a setting index to callables the window
        runs with the new value when that setting changes. panels and more
        are (label, callback or QMenu) pairs for the right side and for the
        More menu."""
        super().__init__("Actions")
        self.setObjectName("toolbar_actions")
        self.setMovable(False)
        self.setToolButtonStyle(Style.ToolButtonTextBesideIcon)
        self.setIconSize(QtCore.QSize(ICON, ICON))
        self.cmd = cmd
        self._icons = {}  # button or action -> icons.LABELS key
        index = cmd.setting._get_index

        self.selecting = self._menu_button(
            "", "What a click in the viewport selects", icon="select"
        )
        self.selecting.setObjectName("selecting")  # its text is the choice: blue
        group = QtGui.QActionGroup(self)
        for value, name in enumerate(SELECTING):
            action = group.addAction(self.selecting.menu().addAction(name))
            action.setCheckable(True)
            action.triggered.connect(lambda _=False, v=value: self._set_selecting(v))
        setting_callbacks[index("mouse_selection_mode")].append(self._show_selecting)
        self._show_selecting(cmd.get_setting_int("mouse_selection_mode"))

        self.addSeparator()
        for text, run in (("Undo", cmd.undo), ("Redo", cmd.redo)):
            # the name stays the tooltip and the accessible name
            button = self.widgetForAction(self._action(text, run))
            button.setToolButtonStyle(Style.ToolButtonIconOnly)
        self.addSeparator()

        self.zoom = self._menu_button(
            "Zoom", "Zoom on what is visible", self._zoom_visible
        )
        self.zoom.menu().addAction("Visible", self._zoom_visible)
        for label, command in (
            ("Everything", "zoom animate=1"),
            ("Selection (sele)", "zoom sele, animate=1"),
            ("Center", "center animate=1"),
            ("Reset view", "reset"),
        ):
            self.zoom.menu().addAction(label, lambda c=command: cmd.do(c, echo=0))
        orient = self._action("Orient", lambda: cmd.orient(animate=1.0))
        self.rock = self._action("Rock", cmd.rock)
        self.rock.setCheckable(True)
        # The view actions show only their icon: the name is the tooltip and
        # the accessible name. The room goes to the text of Palette, which
        # needs the explanation more.
        self.zoom.setToolButtonStyle(Style.ToolButtonIconOnly)
        for action in (orient, self.rock):
            self.widgetForAction(action).setToolButtonStyle(Style.ToolButtonIconOnly)
        self.rock.setChecked(bool(cmd.get_setting_int("rock")))
        setting_callbacks[index("rock")].append(lambda v: self.rock.setChecked(bool(v)))

        self.presets = self._menu_button(
            "Presets", "A preset for everything, a look for the scene"
        )
        self.presets.menu().aboutToShow.connect(self._fill_presets)

        self.colors = self._menu_button(
            "Palette", "Colors of objects and chains", icon="color"
        )
        # The palettes the user defined here earlier. Like the saved choice
        # below, not with -k, which means no user configuration.
        if pymol.invocation.options.pymolrc is not None:
            for name, colors in theme.user_palettes().items():
                try:
                    palettes.define(name, colors, _self=cmd)
                except pymol.CmdException as error:
                    print(" Palette '%s' skipped: %s" % (name, error))
        # A list in the menu, not menu rows: a menu icon is a 16 px square,
        # too small to show the colors.
        self.palettes = view = QtWidgets.QListWidget()
        view.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        view.setIconSize(QtCore.QSize(140, 16))
        view.setSpacing(2)
        # the chosen row in the blue of the menus (pymol.sty)
        colors = view.palette()
        colors.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(ACCENT))
        view.setPalette(colors)
        self._fill_palettes()
        menu = self.colors.menu()
        _caption(menu, "Palette: colors of objects and chains")
        action = QtWidgets.QWidgetAction(menu)
        action.setDefaultWidget(view)
        menu.addAction(action)
        menu.addSeparator()
        menu.addAction("New palette...", self._edit_palette)
        self.edit_palette = menu.addAction(
            "Edit palette...", lambda: self._edit_palette(palettes.active)
        )
        self.delete_palette = menu.addAction("Delete palette", self._delete_palette)
        # a click and the arrow keys pick; Enter closes like a click
        view.currentItemChanged.connect(
            lambda item: self._set_palette(item.data(Qt.ItemDataRole.UserRole))
        )
        view.itemClicked.connect(menu.close)
        view.itemActivated.connect(menu.close)
        menu.aboutToShow.connect(self._show_palette)
        # Before pymolrc runs, so a "palette" line there wins. Not with -k,
        # which means no user configuration.
        saved = theme.object_palette()
        if pymol.invocation.options.pymolrc is not None and saved in palettes.PALETTES:
            cmd.palette(saved)

        self.background = self._menu_button(
            "Bg", "Background color", icon="background"
        )
        menu = self.background.menu()
        _caption(menu, "Background:")
        self._backgrounds = []  # (action, top, bottom)
        for row in BACKGROUNDS:
            if row is None:
                menu.addSeparator()
                continue
            name, top, bottom = row
            action = menu.addAction(name)
            action.triggered.connect(
                lambda _=False, t=top, b=bottom: self._set_background(t, b)
            )
            self._backgrounds.append((action, top, bottom))
        menu.addSeparator()
        # opaque_background is also what Draw > "transparent background"
        # and Display > Background > Opaque set
        self.ray_background = menu.addAction("Ray trace with this background")
        self.ray_background.setCheckable(True)
        self.ray_background.setToolTip(
            "Off: a ray-traced image has a transparent background"
        )
        self.ray_background.triggered.connect(self._set_ray_background)
        self.remember_background = menu.addAction("Remember after restart")
        self.remember_background.setCheckable(True)
        self.remember_background.toggled.connect(self._save_background)
        menu.aboutToShow.connect(self._show_background)
        # as the palette above: before pymolrc, and not with -k
        saved = theme.background()
        if saved:
            with QtCore.QSignalBlocker(self.remember_background):
                self.remember_background.setChecked(True)
            if pymol.invocation.options.pymolrc is not None:
                for key, value in zip(BACKGROUND_SETTINGS, saved):
                    cmd.set(key, value)

        spacer = QtWidgets.QWidget()
        spacer.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        self.addWidget(spacer)

        for label, target in panels:
            if isinstance(target, QtWidgets.QMenu):
                self._menu_button(label, label).setMenu(target)
            else:
                # a panel button shows only its icon; the name is the tooltip
                button = self.widgetForAction(self._action(label, target))
                button.setToolButtonStyle(Style.ToolButtonIconOnly)

        # ponytail: Qt reads the scale once, so a pick needs a restart.
        # Upgrade path: restart with the session saved and reloaded.
        self.scale = self._menu_button(
            "%d%%" % round(theme.ui_scale() * 100),
            "Size of text and controls",
            icon="ui scale",
        )
        group = QtGui.QActionGroup(self)
        for scale in theme.SCALES:
            action = group.addAction(
                self.scale.menu().addAction("%d%%" % round(scale * 100))
            )
            action.setCheckable(True)
            action.setChecked(scale == theme.ui_scale())
            action.triggered.connect(lambda _=False, s=scale: self._set_scale(s))

        self.more = self._menu_button("More", "More view actions", icon="more actions")
        # with its text the bar does not fit the default window at 150 %
        self.more.setToolButtonStyle(Style.ToolButtonIconOnly)
        for label, target in (
            ("Unpick", cmd.unpick),
            ("Deselect", cmd.deselect),
            ("Rebuild", cmd.rebuild),
            *more,
            ("Clear movie", cmd.mclear),
        ):
            self.more.menu().addAction(label, target)

        # toolbar buttons skip the Tab chain by default
        for button in self.findChildren(QtWidgets.QToolButton):
            button.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self._set_icons()

    def _action(self, text, run):
        action = self.addAction(text, run)
        self._icons[action] = text.lower()
        return action

    def _set_icons(self):
        color = self.palette().buttonText().color()
        accent = self.palette().link().color()  # as in pymol.sty
        for target, label in self._icons.items():
            target.setIcon(menu_icon(label, color, ICON, STROKE, accent))

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.Type.PaletteChange:
            self._set_icons()  # they are tinted: follow Display > Dark Theme
        super().changeEvent(event)

    def _menu_button(self, text, tip, default=None, icon=None):
        """A button with a menu; with `default`, clicking the button itself
        runs that and the arrow opens the menu. `icon` is the icons.LABELS
        key where it is not the lowercase text."""
        button = QtWidgets.QToolButton()
        button.setText(text)
        button.setToolTip(tip)
        button.setToolButtonStyle(Style.ToolButtonTextBesideIcon)
        self._icons[button] = icon or text.lower()
        button.setMenu(QtWidgets.QMenu(button))
        if default:
            button.setPopupMode(Popup.MenuButtonPopup)
            button.clicked.connect(default)
        else:
            button.setPopupMode(Popup.InstantPopup)
        self.addWidget(button)
        return button

    def _set_scale(self, scale):
        theme.set_ui_scale(scale)
        QtWidgets.QMessageBox.information(
            self, "UI Scale", "The new scale applies the next time pymolish starts."
        )

    def _fill_palettes(self):
        cmd = self.cmd
        view = self.palettes
        rows = [("default", "PyMOL default", util._color_cycle)]
        for name, (background, colors) in palettes.PALETTES.items():
            note = "%s background" % background if name in palettes.BUILTIN else "yours"
            label = "%s (%s)" % (name.capitalize(), note)
            rows.append((name, label, ["0x" + c for c in colors]))
        with QtCore.QSignalBlocker(view):
            view.clear()
            for name, label, colors in rows:
                strip = [
                    QtGui.QColor.fromRgbF(*cmd.get_color_tuple(c)) for c in colors[:10]
                ]
                item = QtWidgets.QListWidgetItem(_strip(strip), label, view)
                item.setData(Qt.ItemDataRole.UserRole, name)
        view.setFixedSize(
            view.sizeHintForColumn(0) + 4,
            (view.sizeHintForRow(0) + 4) * view.count(),  # 4: the spacing
        )

    def _set_palette(self, name):
        theme.set_object_palette(name)
        self.cmd.palette(name, recolor=1, quiet=0)

    def _edit_palette(self, name=""):
        """New palette, or with a name: change that palette of the user."""
        from .palette_dialog import PaletteDialog

        colors = palettes.PALETTES[name][1] if name else ()
        dialog = PaletteDialog(self, name, colors, taken=palettes.BUILTIN)
        if dialog.exec():
            self._save_palette(*dialog.value(), old=name)

    def _save_palette(self, name, colors, old=""):
        stored = theme.user_palettes()
        if old and old != name:  # renamed
            stored.pop(old, None)
            palettes.undefine(old, _self=self.cmd)
        palettes.define(name, colors, _self=self.cmd)
        stored[name] = list(colors)
        theme.set_user_palettes(stored)
        self._fill_palettes()
        self._set_palette(name)

    def _delete_palette(self):
        name = palettes.active
        stored = theme.user_palettes()
        stored.pop(name, None)
        theme.set_user_palettes(stored)
        self._set_palette("default")
        palettes.undefine(name, _self=self.cmd)
        self._fill_palettes()

    def _show_palette(self):
        yours = palettes.active != "default" and palettes.active not in palettes.BUILTIN
        self.edit_palette.setEnabled(yours)
        self.delete_palette.setEnabled(yours)
        with QtCore.QSignalBlocker(self.palettes):  # "palette" can be typed
            self.palettes.setCurrentRow(
                ["default", *palettes.PALETTES].index(palettes.active)
            )
        QtCore.QTimer.singleShot(0, self.palettes.setFocus)  # for the keys

    def _set_ray_background(self, on):
        cmd = self.cmd
        cmd.set("ray_opaque_background", -1)  # follow opaque_background
        cmd.set("opaque_background", int(on), quiet=0)
        self._save_background()

    def _set_background(self, top, bottom):
        cmd = self.cmd
        # bg_rgb also with a gradient: fog and the "front" color follow it
        cmd.set("bg_rgb", "0x" + top)
        if bottom:
            cmd.set("bg_rgb_top", "0x" + top)
            cmd.set("bg_rgb_bottom", "0x" + bottom)
        cmd.set("bg_gradient", int(bool(bottom)), quiet=0)
        self._save_background()

    def _save_background(self, *_):
        """Keep the background of this moment for the next start, or forget
        it. A background typed later is kept once a row is picked or the
        check box is set again."""
        keep = self.remember_background.isChecked()
        theme.set_background(
            [self.cmd.get(key) for key in BACKGROUND_SETTINGS] if keep else None
        )

    def _show_background(self):
        cmd = self.cmd

        def now(key):
            return QtGui.QColor.fromRgbF(*cmd.get_color_tuple(cmd.get(key))).name()

        gradient = cmd.get_setting_boolean("bg_gradient")
        current = (
            (now("bg_rgb_top"), now("bg_rgb_bottom"))
            if gradient
            else (now("bg_rgb"), None)
        )
        ray = cmd.get_setting_int("ray_opaque_background")
        self.ray_background.setChecked(
            bool(cmd.get_setting_int("opaque_background") if ray < 0 else ray)
        )
        mark = self.palette().highlight().color()
        for action, top, bottom in self._backgrounds:
            row = ("#" + top.lower(), "#" + bottom.lower() if bottom else None)
            action.setIcon(_swatch(top, bottom, row == current, mark))

    def _set_selecting(self, value):
        self.cmd.set("mouse_selection_mode", value, quiet=0)
        self._show_selecting(value)

    def _show_selecting(self, value):
        self.selecting.setText(SELECTING[int(value)])
        self.selecting.menu().actions()[int(value)].setChecked(True)

    def _zoom_visible(self):
        """Fill the viewport with what is shown, centered. Hidden objects
        and hidden atoms do not count; with nothing shown, with everything."""
        cmd = self.cmd
        cmd.zoom("visible" if cmd.count_atoms("visible") else "all", animate=1.0)

    def _fill_presets(self):
        menu = self.presets.menu()
        menu.clear()
        # "enabled": only the objects that are switched on. The light rows
        # at the end are for the whole scene.
        rows = menus.presets(self.cmd, "enabled")
        fill_menu(menu, rows, self.cmd)
