def _scenario():
    import os
    import sys

    B = os.environ["PYMOLISH_CAPTURE"].rstrip("/") + "/"  # holds work/ and out/
    sys.path.insert(0, os.path.join(os.getcwd(), "docs", "media", "capture"))
    import cap
    from cap import cmd, win, log, shot, QtCore

    OUT = B + "out/"
    os.makedirs(B + "work", exist_ok=True)
    os.makedirs(B + "out", exist_ok=True)
    cmd.cd(B + "work")
    cap.LOG = open(OUT + "b.log", "w")
    cmd.fetch("1oky")
    rec = cap.Recorder(OUT + "clip-ligand", fps=7)
    tb = lambda: win().action_toolbar
    panel = lambda: win().ligand_panel
    st = {}

    def size():
        w = win()
        w.resize(1280, 800)
        w.activateWindow()
        w.raise_()

    def open_display():
        rec.caption = "Display > Zoom > Next Ligand with Contacts  (Ctrl-Shift-M)"
        bar = win().menuBar()
        act = [a for a in bar.actions() if a.text().replace("&", "") == "Display"][0]
        r = bar.actionGeometry(act)
        st["display"] = act.menu()
        cap.click(bar, r.center(), rec)

    def hover_zoom():
        log("display visible", st["display"].isVisible())
        cap.menu_hover(st["display"], "Zoom", rec)

    def click_next():
        log("zoom visible", cap.action(st["display"], "Zoom").menu().isVisible())
        cap.menu_click(
            cap.action(st["display"], "Zoom").menu(), "Next Ligand with Contacts", rec
        )

    def next_shot():
        log("walk", cmd.get_names("all"))
        gl = win().pymolwidget
        p = gl.mapTo(win(), QtCore.QPoint(0, 0))
        shot(
            OUT + "ligand-next.png",
            crop=(p.x() + 150, p.y(), gl.width() - 300, gl.height()),
        )

    def open_2d():
        rec.caption = "The 2D button: the ligand drawn flat with its contacts"
        cap.click(cap.find_button(tb(), tip="Ligand in 2D with its contacts"), rec=rec)

    def click_residue():
        p = panel()
        log(
            "panel visible",
            p.isVisible(),
            "floating",
            p.isFloating(),
            "residues",
            len(p.residues),
            p.residues[:2],
        )
        rec.caption = "Click a residue in the picture: it is selected in 3D"
        target = [i for i, r in enumerate(p.residues) if "166" in str(r)]
        i = target[0] if target else 0
        scale = p._scale
        left = (p.picture.width() - p._size[0] * scale) / 2
        top = (p.picture.height() - p._size[1] * scale) / 2
        px, py = p.places[i]
        pos = QtCore.QPoint(int(left + px * scale), int(top + py * scale))
        st["pos"] = pos
        cap.click(p.picture, pos, rec)

    def show3d():
        log(
            "sele",
            cmd.count_atoms("sele") if "sele" in cmd.get_names("selections") else None,
        )
        rec.caption = "Show in 3D: the same contacts as dashes in the viewport"
        cap.click(cap.find_button(panel(), "Show in 3D"), rec=rec)

    def final():
        rec.caption = "Purple: hydrogen bonds. Red: salt bridge. Orange: cation-ring."
        log("names", cmd.get_names("all"))

    def stills():
        rec.stop()
        shot(OUT + "ligand-2d-pocket.png")

    cap.run(
        [
            (1500, size),
            (2500, rec.start),
            (1500, open_display),
            (900, hover_zoom),
            (900, click_next),
            (3000, next_shot),
            (500, open_2d),
            (3500, click_residue),
            (2800, show3d),
            (2500, final),
            (2500, stills),
        ],
        cap.quit_,
    )


_scenario()
