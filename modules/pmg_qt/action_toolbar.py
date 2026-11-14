"""
Action toolbar above the viewport: what a click selects, undo/redo, the view
actions, presets, and on the right the panels and the render popup. Replaces
the grid of quick buttons that sat next to the log.
"""

from pymol import menu as menus
from pymol.Qt import QtCore, QtGui, QtWidgets

from .object_panel import SELECTING, fill_menu

Qt = QtCore.Qt
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
        self.cmd = cmd
        index = cmd.setting._get_index

        self.selecting = self._menu_button("", "What a click in the viewport selects")
        group = QtGui.QActionGroup(self)
        for value, name in enumerate(SELECTING):
            action = group.addAction(self.selecting.menu().addAction(name))
            action.setCheckable(True)
            action.triggered.connect(lambda _=False, v=value: self._set_selecting(v))
        setting_callbacks[index("mouse_selection_mode")].append(self._show_selecting)
        self._show_selecting(cmd.get_setting_int("mouse_selection_mode"))

        self.addSeparator()
        self.addAction("Undo", cmd.undo)
        self.addAction("Redo", cmd.redo)
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
        self.addAction("Orient", lambda: cmd.orient(animate=1.0))
        self.rock = self.addAction("Rock", cmd.rock)
        self.rock.setCheckable(True)
        self.rock.setChecked(bool(cmd.get_setting_int("rock")))
        setting_callbacks[index("rock")].append(lambda v: self.rock.setChecked(bool(v)))

        self.presets = self._menu_button("Presets", "Apply a preset to everything")
        self.presets.menu().aboutToShow.connect(self._fill_presets)

        # only shown while there is something to play, see set_movie_visible
        self.movie = [self.addSeparator()] + [
            self._tip(self.addAction(label, command), tip)
            for label, tip, command in (
                ("<", "Previous frame", cmd.backward),
                ("Stop", "Stop the movie", cmd.mstop),
                ("Play", "Play the movie", cmd.mplay),
                (">", "Next frame", cmd.forward),
            )
        ]
        self.set_movie_visible(False)

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
                self.addAction(label, target)

        self.more = self._menu_button("More", "More view and movie actions")
        for label, target in (
            ("Unpick", cmd.unpick),
            ("Deselect", cmd.deselect),
            ("Rebuild", cmd.rebuild),
            *more,
            ("First frame", cmd.rewind),
            ("Last frame", cmd.ending),
            ("Clear movie", cmd.mclear),
        ):
            self.more.menu().addAction(label, target)

        # toolbar buttons skip the Tab chain by default
        for button in self.findChildren(QtWidgets.QToolButton):
            button.setFocusPolicy(Qt.FocusPolicy.TabFocus)

    def _menu_button(self, text, tip, default=None):
        """A button with a menu; with `default`, clicking the button itself
        runs that and the arrow opens the menu."""
        button = QtWidgets.QToolButton()
        button.setText(text)
        button.setToolTip(tip)
        button.setMenu(QtWidgets.QMenu(button))
        if default:
            button.setPopupMode(Popup.MenuButtonPopup)
            button.clicked.connect(default)
        else:
            button.setPopupMode(Popup.InstantPopup)
        self.addWidget(button)
        return button

    @staticmethod
    def _tip(action, tip):
        action.setToolTip(tip)
        return action

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

    def set_movie_visible(self, visible):
        for action in self.movie:
            action.setVisible(visible)
