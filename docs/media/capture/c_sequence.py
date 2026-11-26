def _scenario():
    import os
    import sys

    B = os.environ["PYMOLISH_CAPTURE"].rstrip("/") + "/"  # holds work/ and out/
    sys.path.insert(0, os.path.join(os.getcwd(), "docs", "media", "capture"))
    import cap
    from cap import (
        cmd,
        win,
        app,
        log,
        shot,
        widget_shot,
        later,
        QtWidgets,
        QtCore,
        QTest,
    )

    Q = QtCore.Qt
    OUT = B + "out/"
    os.makedirs(B + "work", exist_ok=True)
    os.makedirs(B + "out", exist_ok=True)
    cmd.cd(B + "work")
    cap.LOG = open(OUT + "c.log", "w")
    for code in ("1ake", "4ake", "1zin"):
        cmd.fetch(code)
    cmd.orient()
    rec = cap.Recorder(OUT + "clip-sequence", fps=7)
    tb = lambda: win().action_toolbar
    panel = lambda: win().sequence_panel
    st = {}

    def size():
        w = win()
        w.resize(1280, 800)
        w.activateWindow()
        w.raise_()

    def seq_tab():
        bar = win().command_tabs.tabBar()
        cap.click(bar, bar.tabRect(1).center())

    def seq_drag():
        t = win().sequence_tab
        log("seqtab", t.width(), t.height(), "cell", t.cell())
        v = t.viewport()
        t.cell()[0] if isinstance(t.cell(), (tuple, list)) else 10
        y = int(t.cell()[1] * 1.5) if isinstance(t.cell(), (tuple, list)) else 30
        a, b = QtCore.QPoint(260, y), QtCore.QPoint(520, y)
        QTest.mousePress(v, Q.MouseButton.LeftButton, Q.KeyboardModifier.NoModifier, a)
        QTest.mouseMove(v, QtCore.QPoint(400, y))
        QTest.mouseMove(v, b)
        QTest.mouseRelease(
            v, Q.MouseButton.LeftButton, Q.KeyboardModifier.NoModifier, b
        )

    def seq_shot():
        log(
            "sele after drag",
            cmd.count_atoms("sele") if "sele" in cmd.get_names("selections") else None,
        )
        shot(OUT + "sequence-tab.png")
        cmd.deselect()
        bar = win().command_tabs.tabBar()
        cap.click(bar, bar.tabRect(0).center())

    def open_window():
        rec.caption = "The Sequence alignment button opens the alignment window"
        cap.click(cap.find_button(tb(), tip="Sequence alignment"), rec=rec)

    def place():
        p = panel()
        log(
            "panel floating",
            p.isFloating(),
            p.geometry(),
            [k for k in vars(p.form).keys() if not k.startswith("_")],
        )
        p.setFloating(True)
        p.resize(1240, 395)
        cap.PLACE[p] = QtCore.QPoint(20, 400)
        cmd.orient()
        cmd.move("z", -90)
        cmd.move("y", 34)

    def add():
        rec.caption = "Add chains…: the selection  chain A"
        b = cap.find_button(panel(), "Add chains…")
        rec.cursor = cap.center(b)
        later(0, b.click)

    def add_fill():
        d = [
            t
            for t in app.topLevelWidgets()
            if isinstance(t, QtWidgets.QInputDialog) and t.isVisible()
        ]
        log("input dialogs", len(d))
        d[0].setTextValue("chain A")
        st["dlg"] = d[0]

    def add_ok():
        st["dlg"].accept()

    def align():
        log("rows", [r.get("name") for r in panel().model.rows])
        rec.caption = "Align sequences (MAFFT on this computer): no structure moves"
        cap.click(cap.find_button(panel(), "Align sequences"), rec=rec)

    def color():
        p = panel()
        combos = [
            c
            for c in p.findChildren(QtWidgets.QComboBox)
            if c.count() and c.itemText(c.count() - 1) == "Percent identity"
        ]
        rec.caption = "Color: Percent identity"
        rec.cursor = cap.center(combos[0])
        combos[0].setCurrentIndex(3)
        log(
            "rows after align",
            [(r.get("name"), len(r.get("sequence", ""))) for r in p.model.rows],
        )

    def window_shot():
        pass

    def select_cells():
        p = panel()
        view = p.findChild(QtWidgets.QTableView)
        st["view"] = view
        m = view.model()
        rec.caption = "Drag over cells: the residues are selected in 3D"
        a = view.visualRect(m.index(0, 10)).center()
        b = view.visualRect(m.index(0, 30)).center()
        v = view.viewport()
        rec.cursor = cap.gpos(v, a)
        QTest.mousePress(v, Q.MouseButton.LeftButton, Q.KeyboardModifier.NoModifier, a)
        QTest.mouseMove(v, QtCore.QPoint((a.x() + b.x()) // 2, a.y()))
        QTest.mouseMove(v, b)
        QTest.mouseRelease(
            v, Q.MouseButton.LeftButton, Q.KeyboardModifier.NoModifier, b
        )
        rec.cursor = cap.gpos(v, b)

    def after_select():
        log(
            "sele after cells",
            cmd.count_atoms("sele") if "sele" in cmd.get_names("selections") else None,
        )
        st["view"].clearSelection()

    def fit():
        p = panel()
        rec.caption = "Fit structures onto the reference 1ake (method align): this moves the objects"
        cap.click(cap.find_button(p, "Fit structures"), rec=rec)

    def fit_shot():
        p = panel()
        texts = [w.toPlainText() for w in p.findChildren(QtWidgets.QPlainTextEdit)] + [
            w.toPlainText() for w in p.findChildren(QtWidgets.QTextEdit)
        ]
        log("results", texts)
        rec.caption = "The result: RMSD and matched atoms for each moved object"
        cmd.orient()
        cmd.move("z", -90)
        cmd.move("y", 34)

    def fit_still():
        shot(OUT + "sequence-fit.png")
        widget_shot(panel(), OUT + "sequence-alignment.png")

    def undo():
        rec.caption = "Undo puts the structures back"
        cap.click(cap.find_button(panel(), "Undo"), rec=rec)

    def end():
        rec.stop()

    cap.run(
        [
            (1500, size),
            (2500, seq_tab),
            (1200, seq_drag),
            (1200, seq_shot),
            (800, rec.start),
            (1200, open_window),
            (1500, place),
            (1500, add),
            (1200, add_fill),
            (1200, add_ok),
            (2000, align),
            (4500, color),
            (2500, window_shot),
            (300, select_cells),
            (2500, after_select),
            (500, fit),
            (5000, fit_shot),
            (2500, fit_still),
            (500, undo),
            (3000, end),
        ],
        cap.quit_,
    )


_scenario()
