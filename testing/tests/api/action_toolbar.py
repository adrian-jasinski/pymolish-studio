"""
Action toolbar: selection mode menu and label, rock state, zoom, presets
menu, panel and More entries, an icon on every button, the palette menu, the
background menu, the UI scale menu.
Headless (offscreen QApplication).
"""

import pytest
import os
from collections import defaultdict

from pymol import cmd, testing


@pytest.fixture(autouse=True)
def app():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from pymol.Qt import QtWidgets

    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def test_toolbar():
    from pymol.Qt import QtCore, QtWidgets
    from pmg_qt.action_toolbar import ActionToolbar

    hits = []
    callbacks = defaultdict(list)
    bar = ActionToolbar(
        cmd,
        callbacks,
        panels=[("Builder", lambda: hits.append("builder"))],
        more=[("Get View", lambda: hits.append("view"))],
        files=[
            ("Open file...", lambda: hits.append("open")),
            ("Open Recent...", QtWidgets.QMenu("Open Recent...")),
            None,
            ("Get PDB entry...", lambda: hits.append("pdb")),
        ],
    )
    texts = {a.text(): a for a in bar.actions()}

    # Open is the first button: a click opens a file, the menu has the rest
    assert bar.widgetForAction(bar.actions()[0]) is bar.open
    rows = bar.open.menu().actions()
    assert [a.text() for a in rows] == [
        "Open file...",
        "Open Recent...",
        "",
        "Get PDB entry...",
    ]
    assert rows[1].menu() and rows[2].isSeparator()
    bar.open.click()
    rows[3].trigger()
    assert hits == ["open", "pdb"]
    del hits[:]
    assert bar.open.focusPolicy() == QtCore.Qt.FocusPolicy.TabFocus

    # selection mode: menu sets the setting, the setting sets the label
    assert bar.selecting.text() == "Residues"
    bar.selecting.menu().actions()[2].trigger()
    assert cmd.get_setting_int("mouse_selection_mode") == 2
    assert bar.selecting.text() == "Chains"
    for callback in callbacks[cmd.setting._get_index("mouse_selection_mode")]:
        callback(0)
    assert bar.selecting.text() == "Atoms"

    # rock follows the setting
    assert not bar.rock.isChecked()
    for callback in callbacks[cmd.setting._get_index("rock")]:
        callback(1)
    assert bar.rock.isChecked()
    # its menu: rock, a spin about each axis, random axes, stop
    rocks = {a.text(): a for a in bar.rock.menu().actions()}
    angle = cmd.get_setting_float("sweep_angle")
    rocks["Spin about X"].trigger()
    assert cmd.get_setting_int("rock") and cmd.get_setting_int("sweep_mode") == 1
    assert cmd.get_setting_float("sweep_angle") == 0
    rocks["Rock"].trigger()
    assert cmd.get_setting_int("sweep_mode") == 0
    assert cmd.get_setting_float("sweep_angle") == angle  # back to the rock
    rocks["Random"].trigger()
    assert bar._random.isActive() and cmd.get_setting_float("sweep_angle") == 0
    for _ in range(3):  # it keeps turning: 4.59.0 stopped after two
        mode = cmd.get_setting_int("sweep_mode")
        bar._random_turn()
        assert cmd.get_setting_int("sweep_mode") != mode
        # 15 to 180 degrees at 10 degrees a second (sweep_speed 0.75)
        assert bar._random.isActive() and 1500 <= bar._random.interval() <= 18000
    rocks["Stop"].trigger()
    for callback in callbacks[cmd.setting._get_index("rock")]:
        callback(0)
    assert not cmd.get_setting_int("rock") and not bar._random.isActive()
    cmd.set("sweep_speed", 0.75)

    cmd.fragment("ala")
    view = cmd.get_view()
    cmd.turn("x", 90)
    cmd.move("z", -30)
    bar.zoom.menu().actions()[0].trigger()
    texts["Orient"].trigger()
    assert cmd.get_view() != view

    # the zoom button fills the viewport with what is shown: a hidden
    # object far away does not count
    cmd.set("animation", 0)
    cmd.fragment("gly", "far")
    cmd.translate([500, 0, 0], "far")
    cmd.zoom("ala")
    near = cmd.get_view()[11]  # camera distance
    cmd.zoom("all")
    assert cmd.get_view()[11] < near * 3  # further away
    cmd.disable("far")
    bar.zoom.menu().actions()[0].trigger()
    assert cmd.get_view()[11] == pytest.approx(near, abs=5e-2)
    assert [a.text() for a in bar.zoom.menu().actions()][:2] == [
        "Visible",
        "Everything",
    ]
    # Orient too: the hidden object does not pull the view toward it
    texts["Orient"].trigger()
    assert cmd.get_view()[11] == pytest.approx(near, abs=2.0)
    cmd.enable("far")
    texts["Orient"].trigger()
    assert cmd.get_view()[11] < near * 3
    cmd.delete("far")

    bar.presets.menu().aboutToShow.emit()
    rows = [a.text() for a in bar.presets.menu().actions()]
    assert "technical" in rows
    assert "simple" not in rows
    # 30d: themes, lights and the floor each in a submenu, filled when opened
    subs = {a.text(): a.menu() for a in bar.presets.menu().actions() if a.menu()}
    assert {"theme", "light", "floor"} <= set(subs) and "figure" not in rows
    subs["light"].aboutToShow.emit()
    assert "figure" in [a.text() for a in subs["light"].actions()]

    texts["Builder"].trigger()
    more = {a.text(): a for a in bar.more.menu().actions()}
    more["Get View"].trigger()
    assert hits == ["builder", "view"]


def test_icons():
    from pymol.Qt import QtCore, QtGui, QtWidgets
    from pmg_qt.action_toolbar import ActionToolbar

    bar = ActionToolbar(
        cmd,
        defaultdict(list),
        panels=[
            ("Builder", lambda: None),
            ("Scenes", lambda: None),
            ("Movie", lambda: None),
            ("Draw", QtWidgets.QMenu()),
        ],
    )
    buttons = [
        b
        for b in bar.findChildren(QtWidgets.QToolButton)
        if b.objectName() != "qt_toolbar_ext_button"  # Qt's overflow arrow
    ]
    assert len(buttons) == 21
    # every button has an icon, but the letter chips of quick select
    assert [b.text() for b in buttons if b.icon().isNull()] == [
        "P",
        "L",
        "S",
        "\u22ef",
        "All",
    ]
    IconOnly = QtCore.Qt.ToolButtonStyle.ToolButtonIconOnly
    assert sorted(b.toolTip() for b in buttons if b.toolButtonStyle() == IconOnly) == [
        "Background color",
        "Builder",
        "Draw",
        "More view actions",
        "Movie",
        "Orient",
        "Palette: colors of objects and chains",
        "Redo",
        "Rock or spin the view",
        "Scenes",
        "Select nothing",
        "Undo",
        "Zoom",
    ]
    # the rest keep a text
    texts = [b.text() for b in buttons if b.toolButtonStyle() != IconOnly]
    assert "Presets" in texts and "Draw" not in texts
    assert bar.background.toolTip() == "Background color"
    # every menu opens from the whole button, with the same triangle
    Popup = QtWidgets.QToolButton.ToolButtonPopupMode
    assert bar.zoom.popupMode() == Popup.InstantPopup
    assert bar.rock.popupMode() == Popup.InstantPopup
    # bolder and larger than the menu icons, and blue while hovered or
    # checked; the text of the selection mode is styled by its name
    assert bar.iconSize().width() == 20
    icon = bar.colors.icon()
    Mode = QtGui.QIcon.Mode
    normal = icon.pixmap(20, 20, Mode.Normal).toImage()
    active = icon.pixmap(20, 20, Mode.Active).toImage()
    assert normal != active
    assert bar.selecting.objectName() == "selecting"
    from pmg_qt import icons

    assert icons.LABELS["scenes"] == "camera"
    assert icons.LABELS["movie"] == "video"
    assert icons.LABELS["background"] == "paint-roller"


def test_background(request):
    from unittest import mock
    from pmg_qt import action_toolbar, theme

    request.addfinalizer(cmd.reinitialize)
    saved = []
    with (
        mock.patch.object(theme, "background", return_value=None),
        mock.patch.object(theme, "set_background", saved.append),
    ):
        bar = action_toolbar.ActionToolbar(cmd, defaultdict(list))
        menu = bar.background.menu()
        rows = {a.text(): a for a in menu.actions() if a.text()}
        names = [row[0] for row in action_toolbar.BACKGROUNDS if row]
        assert list(rows) == [
            *names,
            "Ray trace with this background",
            "Remember after restart",
        ]

        def color(key):
            return cmd.get_color_tuple(cmd.get(key))

        # every row sets what the table says; a plain row ends a gradient
        for name, top, bottom in filter(None, action_toolbar.BACKGROUNDS):
            rows[name].trigger()
            rgb = tuple(int(top[i : i + 2], 16) / 255 for i in (0, 2, 4))
            assert cmd.get_setting_boolean("bg_gradient") == bool(bottom)
            for a, b in zip(color("bg_rgb_top" if bottom else "bg_rgb"), rgb):
                assert a == pytest.approx(b, abs=5e-3), name
        assert saved == [None] * len(names)  # nothing is kept

        # the row in use is the only one with a frame: its icon differs
        rows["White"].trigger()
        menu.aboutToShow.emit()
        pixel = {
            n: rows[n].icon().pixmap(16, 16).toImage().pixelColor(2, 2).name()
            for n in ("White", "Sky", "Black")
        }
        assert pixel["White"] != "#ffffff"
        assert pixel["Black"] == "#000000"

        # ray tracing with or without the background: one setting,
        # the one Draw and Display > Background use
        cmd.set("ray_opaque_background", 0)
        rows["Ray trace with this background"].trigger()
        assert cmd.get_setting_int("ray_opaque_background") == -1
        assert cmd.get_setting_int("opaque_background") == 1
        menu.aboutToShow.emit()
        assert rows["Ray trace with this background"].isChecked()
        rows["Ray trace with this background"].trigger()
        assert cmd.get_setting_int("opaque_background") == 0

        # "Remember" keeps the settings now and after each pick
        del saved[:]
        rows["Remember after restart"].setChecked(True)
        rows["Studio"].trigger()
        assert len(saved) == 2
        assert len(saved[1]) == len(action_toolbar.BACKGROUND_SETTINGS)
        rows["Remember after restart"].setChecked(False)
        assert saved[-1] is None

    # the next start: applied only when a pymolrc may run (not -k)
    with (
        mock.patch.object(theme, "background", return_value=saved[1]),
        mock.patch.object(theme, "object_palette", return_value="default"),
        mock.patch.object(action_toolbar.pymol.invocation.options, "pymolrc", []),
    ):
        cmd.reinitialize()
        bar = action_toolbar.ActionToolbar(cmd, defaultdict(list))
    assert bar.remember_background.isChecked()
    assert cmd.get_setting_boolean("bg_gradient")
    assert color("bg_rgb_bottom")[0] == pytest.approx(0xC8 / 255, abs=5e-3)


def test_user_palette(request):
    from unittest import mock
    from pymol import CmdException, palettes
    from pymol.Qt import QtCore
    from pmg_qt import action_toolbar, theme
    from pmg_qt.palette_dialog import PaletteDialog

    role = QtCore.Qt.ItemDataRole.UserRole
    stored = {}
    request.addfinalizer(cmd.reinitialize)
    request.addfinalizer(
        lambda: [palettes.PALETTES.pop(n, None) for n in ("mine", "other")]
    )
    request.addfinalizer(lambda: cmd.palette("default"))
    with (
        mock.patch.object(theme, "user_palettes", lambda: dict(stored)),
        mock.patch.object(theme, "set_user_palettes", stored.update),
        mock.patch.object(theme, "set_object_palette"),
    ):
        bar = action_toolbar.ActionToolbar(cmd, defaultdict(list))
        view = bar.palettes
        rows = {a.text(): a for a in bar.colors.menu().actions() if a.text()}
        assert list(rows) == ["New palette...", "Edit palette...", "Delete palette"]
        bar.colors.menu().aboutToShow.emit()
        assert not bar.edit_palette.isEnabled()  # a built-in is active

        # what the dialog hands back is stored, listed and applied
        cmd.fragment("ala")
        bar._save_palette("mine", ["ff8800", "0088ff", "33cc66"])
        assert stored == {"mine": ["ff8800", "0088ff", "33cc66"]}
        names = [view.item(i).data(role) for i in range(view.count())]
        assert names[-1] == "mine"
        assert view.item(view.count() - 1).text() == "Mine (yours)"
        assert palettes.active == "mine"
        assert cmd.count_atoms("elem C & color mine_01") == 3
        bar.colors.menu().aboutToShow.emit()
        assert bar.edit_palette.isEnabled()
        assert bar.delete_palette.isEnabled()

        # edited with a new name: the old one is gone
        stored.clear()
        bar._save_palette("other", ["112233", "445566"], old="mine")
        assert list(stored) == ["other"]
        assert "mine" not in palettes.PALETTES
        assert palettes.active == "other"

        bar._delete_palette()
        assert palettes.active == "default"
        assert "other" not in palettes.PALETTES

    # the rules of a palette of the user
    for name, colors in (
        ("vivid", ["ff0000", "00ff00"]),
        ("Bad Name", ["ff0000", "00ff00"]),
        ("mine", ["ff0000"]),
        ("mine", ["ff0000", "nothex"]),
    ):
        pytest.raises(CmdException, palettes.define, name, colors)
    pytest.raises(CmdException, palettes.undefine, "vivid")

    # the dialog: OK only with a free name and two colors
    import shiboken6

    dialog = PaletteDialog(None, "", (), taken=palettes.BUILTIN)
    request.addfinalizer(lambda: shiboken6.delete(dialog))
    ok = dialog.box.button(dialog.box.StandardButton.Ok)
    assert not ok.isEnabled()
    dialog.name.setText("vivid")
    dialog._append("ff8800")
    dialog._append("#0088ff")
    assert not ok.isEnabled()  # a built-in name
    dialog.name.setText("mine")
    assert ok.isEnabled()
    dialog.list.setCurrentRow(1)
    dialog._move(-1)
    assert dialog.value() == ("mine", ["0088ff", "ff8800"])
    dialog._remove()
    assert not ok.isEnabled()


def test_palette():
    from unittest import mock
    from pymol import palettes
    from pymol.Qt import QtCore
    from pmg_qt import action_toolbar, theme

    Qt = QtCore.Qt

    # -k (how the tests run): the saved palette is not applied
    with mock.patch.object(theme, "object_palette", return_value="deep"):
        bar = action_toolbar.ActionToolbar(cmd, defaultdict(list))
    assert palettes.active == "default"
    view = bar.palettes
    role = Qt.ItemDataRole.UserRole
    # 16a: the menu says what it colors, above the list
    caption = bar.colors.menu().actions()[0].defaultWidget()
    assert caption.text() == "Palette: colors of objects and chains"
    assert caption.objectName() == "menu_title"
    names = [view.item(i).data(role) for i in range(view.count())]
    assert names == ["default", *palettes.PALETTES]
    assert view.item(2).text() == "Deep (white background)"
    # wide enough to tell the colors apart: ten of them, 14 px each
    assert view.item(2).icon().availableSizes()[0].width() == 140
    assert view.width() >= view.sizeHintForColumn(0)
    try:
        # picking recolors what is loaded and is saved
        cmd.fragment("ala")
        with mock.patch.object(theme, "set_object_palette") as save:
            view.setCurrentRow(names.index("deep"))
        save.assert_called_once_with("deep")
        assert palettes.active == "deep"
        assert cmd.count_atoms("elem C & color deep_01") == 3

        # typed: the list follows when the menu opens, nothing is saved
        cmd.palette("soft")
        with mock.patch.object(theme, "set_object_palette") as save:
            bar.colors.menu().aboutToShow.emit()
        save.assert_not_called()
        assert view.currentItem().data(role) == "soft"
        assert cmd.count_atoms("elem C & color deep_01") == 3

        # without -k the saved palette is back at start
        cmd.palette("default")
        with (
            mock.patch.object(theme, "object_palette", return_value="deep"),
            mock.patch.object(action_toolbar.pymol.invocation.options, "pymolrc", []),
        ):
            action_toolbar.ActionToolbar(cmd, defaultdict(list))
        assert palettes.active == "deep"
    finally:
        cmd.palette("default")


def test_scale():
    from unittest import mock
    from pymol.Qt import QtWidgets
    from pmg_qt import action_toolbar, theme

    with mock.patch.object(theme, "ui_scale", return_value=1.8):
        bar = action_toolbar.ActionToolbar(cmd, defaultdict(list))
    assert bar.scale.text() == "180%"
    # a field for any whole percent from 50 to 300, then the common steps
    assert (
        bar.scale_box.minimum(),
        bar.scale_box.maximum(),
        bar.scale_box.value(),
    ) == (50, 300, 180)
    rows = [a.text() for a in bar.scale.menu().actions() if a.text()]
    assert rows == ["75%", "100%", "125%", "150%", "175%", "200%", "250%", "300%"]

    def pick(run, live):
        """Run a pick with the live change mocked; what was asked of it."""
        with (
            mock.patch.object(theme, "set_ui_scale") as save,
            mock.patch.object(theme, "set_scale_live", return_value=live) as change,
            mock.patch.object(
                action_toolbar.QtWidgets.QMessageBox, "information"
            ) as told,
            mock.patch.object(bar, "_confirm_scale") as confirm,
            mock.patch.object(
                action_toolbar.QtCore.QTimer, "singleShot", lambda _, f: f()
            ),
        ):
            run()
        return save.call_args_list, change.call_args_list, told.called, confirm.called

    # a row: saved and changed live, no message
    save, change, told, confirm = pick(
        bar.scale.menu().actions()[3].trigger, True
    )  # 100%
    assert save[0].args == (1.0,) and change[0].args[2:] == (1.8, 1.0)
    assert not told and not confirm and bar.scale.text() == "100%"
    # a typed value
    bar.scale_box.setValue(137)
    save, change, told, confirm = pick(bar.scale_box.editingFinished.emit, True)
    assert save[0].args == (1.37,) and bar.scale.text() == "137%"
    # the same value again: nothing happens
    assert pick(bar.scale_box.editingFinished.emit, True)[0] == []
    # 27d: Enter in the field asks twice before the first change ran; the
    # window is rebuilt once
    bar.scale_box.setValue(120)
    calls = []
    with mock.patch.object(
        action_toolbar.QtCore.QTimer, "singleShot", lambda _, f: calls.append(f)
    ):
        bar.scale_box.editingFinished.emit()
        bar.scale_box.editingFinished.emit()
    assert len(calls) == 2
    save, change, told, confirm = pick(lambda: [f() for f in calls], True)
    assert len(save) == len(change) == 1 and change[0].args[2:] == (1.37, 1.2)
    # where the display cannot do it, the message says why
    with (
        mock.patch.object(theme, "set_ui_scale"),
        mock.patch.object(theme, "set_scale_live", return_value=False),
        mock.patch.object(theme, "live_scale_blocker", return_value="No."),
        mock.patch.object(action_toolbar.QtWidgets.QMessageBox, "information") as told,
        mock.patch.object(action_toolbar.QtCore.QTimer, "singleShot", lambda _, f: f()),
    ):
        bar._set_scale(1.37)
    assert (
        told.call_args.args[2]
        == "No. The new scale applies the next time pymolish starts."
    )
    # where the live change cannot work: saved, and the old message
    save, change, told, confirm = pick(lambda: bar._set_scale(1.5), False)
    assert save[0].args == (1.5,) and told and not confirm
    # very small or very large asks whether the window is still usable
    assert pick(lambda: bar._set_scale(3.0), True)[3]
    assert pick(lambda: bar._set_scale(0.5), True)[3]
    assert not pick(lambda: bar._set_scale(2.0), True)[3]


def test_quick_select():
    from unittest import mock

    from pymol.Qt import QtCore, QtWidgets
    from pmg_qt.action_toolbar import ActionToolbar

    Modifier = QtCore.Qt.KeyboardModifier
    bar = ActionToolbar(cmd, defaultdict(list))

    def held(modifier):
        return mock.patch.object(
            QtWidgets.QApplication, "keyboardModifiers", return_value=modifier
        )

    # nothing loaded: nothing selected, nothing raised
    bar.chips["P"].click()
    bar.chips["None"].click()
    assert "sele" not in cmd.get_names("selections")

    cmd.load(testing.datafile("1oky.pdb.gz"), "m")
    cmd.fragment("ala", "hidden")
    cmd.disable("hidden")
    for letter, expression in (
        ("P", "polymer.protein"),
        ("L", "organic"),
        ("S", "solvent"),
    ):
        bar.chips[letter].click()
        # only in the objects that are switched on
        assert cmd.count_atoms("sele") == cmd.count_atoms("m and " + expression) > 0
    bar.chips["All"].click()
    assert cmd.count_atoms("sele") == cmd.count_atoms("m")

    bar.chips["L"].click()
    ligand = cmd.count_atoms("sele")
    with held(Modifier.ShiftModifier):  # add
        bar.chips["S"].click()
    assert cmd.count_atoms("sele") == ligand + cmd.count_atoms("m and solvent")
    with held(Modifier.ControlModifier):  # take away
        bar.chips["L"].click()
    assert cmd.count_atoms("sele") == cmd.count_atoms("m and solvent")

    # "...": the chains of the objects that are switched on, and more
    more = bar.chips["\u22ef"].menu()
    more.aboutToShow.emit()
    rows = {a.text(): a for a in more.actions()}
    assert [t for t in rows if t.startswith("Chain ")] == [
        "Chain %s" % c for c in cmd.get_chains("m")
    ]
    rows["Chain A"].trigger()
    assert cmd.count_atoms("sele") == cmd.count_atoms("m and chain A")
    bar.chips["L"].click()
    rows["Invert"].trigger()
    assert cmd.count_atoms("sele") == cmd.count_atoms("m and not organic")
    before = cmd.count_atoms("sele")
    rows["Nucleic acid"].trigger()  # none here: the selection stays
    assert cmd.count_atoms("sele") == before

    bar.chips["None"].click()
    assert cmd.count_atoms("sele") == 0


def test_ligand_button():
    from pmg_qt.action_toolbar import ActionToolbar

    bar = ActionToolbar(cmd, defaultdict(list), panels=[("2D", lambda: None)])
    action = bar.panel_actions["2D"]
    bar.set_ligand(False)
    assert (
        not action.isEnabled()
        and action.toolTip() == "No ligand in the visible objects"
    )
    bar.set_ligand(True)
    assert action.isEnabled() and "2D" in action.toolTip()
    ActionToolbar(cmd, defaultdict(list)).set_ligand(True)  # a bar without the button
