def _scenario():
    import os
    import sys

    B = os.environ["PYMOLISH_CAPTURE"].rstrip("/") + "/"  # holds work/ and out/
    sys.path.insert(0, os.path.join(os.getcwd(), "docs", "media", "capture"))
    import cap
    from cap import cmd, win, app, log, shot, widget_shot, later, QtWidgets, QtCore
    from pmg_qt import file_dialogs

    OUT = B + "out/"
    os.makedirs(B + "work", exist_ok=True)
    os.makedirs(B + "out", exist_ok=True)
    cmd.cd(B + "work")
    cap.LOG = open(OUT + "a.log", "w")
    VIEW = (
        -0.4173,
        0.9038,
        0.0948,
        0.0234,
        -0.0936,
        0.9953,
        0.9084,
        0.4176,
        0.0179,
        0.0,
        0.0,
        -173.1179,
        81.868,
        19.0457,
        2.1404,
        136.4874,
        209.7483,
        -20.0,
    )
    rec = cap.Recorder(OUT + "clip-appearance", fps=8)
    st = {}
    tb = lambda: win().action_toolbar
    pm = lambda: tb().presets.menu()

    def size():
        w = win()
        w.resize(1280, 800)
        w.activateWindow()
        w.raise_()

    def fetch_dialog():
        file_dialogs.file_fetch_pdb(win())
        d = [
            t
            for t in app.topLevelWidgets()
            if isinstance(t, QtWidgets.QDialog) and t.isVisible()
        ][0]
        st["dlg"] = d
        d.findChild(QtWidgets.QLineEdit, "input_code").setText("1oky")

    def fetch_go():
        st["dlg"].findChild(QtWidgets.QAbstractButton, "button_ok").click()

    def window_shot():
        log("names", cmd.get_names())
        shot(OUT + "window.png")
        cmd.set_view(VIEW)

    def open_presets(caption):
        def f():
            rec.caption = caption
            rec.cursor = cap.center(tb().presets)
            later(0, tb().presets.showMenu)

        return f

    def hover(path):
        def f():
            m = pm()
            for name in path[:-1]:
                m = cap.action(m, name).menu()
            cap.menu_hover(m, path[-1], rec)

        return f

    def pick(path):
        def f():
            m = pm()
            for name in path[:-1]:
                m = cap.action(m, name).menu()
            cap.menu_click(m, path[-1], rec)

        return f

    def undo():
        rec.caption = "Undo takes the last row back: the light"
        cap.click(cap.find_button(tb(), tip="Undo"), rec=rec)

    def caption(text):
        def f():
            rec.caption = text

        return f

    def presets_still():
        rec.stop()
        later(0, tb().presets.showMenu)

    def presets_still2():
        cap.menu_hover(pm(), "surface")

    def presets_still3():
        shot(OUT + "appearance-presets.png", crop=(560, 0, 720, 580))
        pm().close()

    def look():
        # back to the glossy surface for the thumbnail
        later(0, tb().presets.showMenu)

    def look2():
        cap.menu_hover(pm(), "surface")

    def look3():
        cap.menu_click(cap.action(pm(), "surface").menu(), "glossy")

    def look_shot():
        gl = win().pymolwidget
        p = gl.mapTo(win(), QtCore.QPoint(0, 0))
        shot(
            OUT + "appearance-look.png",
            crop=(p.x() + 180, p.y() + 20, gl.width() - 360, gl.height() - 40),
        )
        st["draw"] = cap.find_button(tb(), tip="Draw")
        later(0, st["draw"].showMenu)

    def draw_shot():
        widget_shot(st["draw"].menu(), OUT + "saving-draw.png")
        st["draw"].menu().close()

    cap.run(
        [
            (1500, size),
            (500, fetch_dialog),
            (1200, fetch_go),
            (5000, window_shot),
            (800, rec.start),
            (1200, open_presets("Presets > surface > glossy")),
            (900, hover(["surface"])),
            (900, pick(["surface", "glossy"])),
            (2600, open_presets("Presets > transparency > surface > 50%")),
            (900, hover(["transparency"])),
            (900, hover(["transparency", "surface"])),
            (900, pick(["transparency", "surface", "50%"])),
            (2600, open_presets("Presets > light > studio")),
            (900, hover(["light"])),
            (900, pick(["light", "studio"])),
            (2600, undo),
            (2500, caption("Undo again: the transparency")),
            (300, lambda: cap.click(cap.find_button(tb(), tip="Undo"), rec=rec)),
            (2500, presets_still),
            (700, presets_still2),
            (900, presets_still3),
            (500, look),
            (700, look2),
            (800, look3),
            (2500, look_shot),
            (900, draw_shot),
        ],
        cap.quit_,
    )


_scenario()
