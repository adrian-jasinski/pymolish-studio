"""
Action toolbar above the viewport: what a click selects, undo/redo, the view
actions, presets, and on the right the panels, the render popup and the UI
scale. Every button has a line icon; undo and redo show only that. Replaces
the grid of quick buttons that sat next to the log.
"""

from pymol import menu as menus
from pymol.Qt import QtCore, QtGui, QtWidgets

from . import theme
from .icons import menu_icon
from .object_panel import SELECTING, fill_menu

Qt = QtCore.Qt
Style = Qt.ToolButtonStyle
Popup = QtWidgets.QToolButton.ToolButtonPopupMode


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
        self.setIconSize(QtCore.QSize(16, 16))  # the size icons.py draws
        self.cmd = cmd
        self._icons = {}  # button or action -> icons.LABELS key
        index = cmd.setting._get_index

        self.selecting = self._menu_button(
            "", "What a click in the viewport selects", icon="select"
        )
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
            "Zoom", "Zoom on everything", lambda: cmd.zoom(animate=1.0)
        )
        for label, command in (
            ("All", "zoom animate=1"),
            ("Selection (sele)", "zoom sele, animate=1"),
            ("Center", "center animate=1"),
            ("Reset view", "reset"),
        ):
            self.zoom.menu().addAction(label, lambda c=command: cmd.do(c, echo=0))
        self._action("Orient", lambda: cmd.orient(animate=1.0))
        self.rock = self._action("Rock", cmd.rock)
        self.rock.setCheckable(True)
        self.rock.setChecked(bool(cmd.get_setting_int("rock")))
        setting_callbacks[index("rock")].append(lambda v: self.rock.setChecked(bool(v)))

        self.presets = self._menu_button("Presets", "Apply a preset to everything")
        self.presets.menu().aboutToShow.connect(self._fill_presets)

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
                self._action(label, target)

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
        for target, label in self._icons.items():
            target.setIcon(menu_icon(label, color))

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

    def _set_selecting(self, value):
        self.cmd.set("mouse_selection_mode", value, quiet=0)
        self._show_selecting(value)

    def _show_selecting(self, value):
        self.selecting.setText(SELECTING[int(value)])
        self.selecting.menu().actions()[int(value)].setChecked(True)

    def _fill_presets(self):
        menu = self.presets.menu()
        menu.clear()
        fill_menu(menu, menus.presets(self.cmd, "all"), self.cmd)
