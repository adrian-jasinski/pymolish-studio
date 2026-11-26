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
    )

    OUT = B + "out/"
    os.makedirs(B + "work", exist_ok=True)
    os.makedirs(B + "out", exist_ok=True)
    cmd.cd(B + "work")
    cap.LOG = open(OUT + "d.log", "w")
    open(B + "work/scores.csv", "w").write(
        "name,score,series\nala,-5.2,a\ngly,-4.1,a\ntrp,-7.9,b\nhis,-6.0,b\n"
    )
    for name in ("ala", "gly", "trp"):
        cmd.fragment(name)
    cmd.orient()
    tb = lambda: win().action_toolbar
    table = lambda: win().property_table
    st = {}

    def size():
        w = win()
        w.resize(1280, 800)
        w.activateWindow()
        w.raise_()

    def open_table():
        cap.click(cap.find_button(tb(), tip="Table"))

    def load():
        t = table()
        log(
            "table visible",
            t.isVisible(),
            "floating",
            t.isFloating(),
            t.geometry(),
            "columns",
            t.columns,
        )
        cmd.do("load_table scores.csv")

    def sort():
        t = table()
        log("columns", t.columns, "hidden", t.hidden)
        h = t.tree.header()
        col = t.column_of("score")
        x = h.sectionViewportPosition(col) + h.sectionSize(col) // 2
        cap.click(h.viewport(), QtCore.QPoint(x, h.height() // 2))

    def star():
        t = table()
        from pmg_qt import property_table as pt

        log(
            "order",
            [
                t.tree.topLevelItem(i).text(pt.NAME)
                for i in range(t.tree.topLevelItemCount())
            ],
        )
        if "stars" not in t.columns:
            log("no stars column")
            return
        item = t.items.get("trp") or t.tree.topLevelItem(0)
        rect = t.tree.visualRect(t.tree.indexFromItem(item, t.column_of("stars")))
        side = min(pt.STAR, rect.height() - 4)
        x = rect.left() + pt.STAR_LEFT + 2 * (side + pt.STAR_GAP) + side // 2
        cap.click(t.tree.viewport(), QtCore.QPoint(x, rect.center().y()))

    def table_shot():
        log("stars of trp", cmd.get_property("stars", "trp"))
        t = table()
        t.resize(760, 300)

    def table_shot2():
        widget_shot(table(), OUT + "property-table.png")
        cap.PLACE[table()] = QtCore.QPoint(200, 70)
        shot(OUT + "property-table-window.png")
        cap.click(cap.find_button(tb(), tip="Table"))

    def group():
        cmd.group("small", "ala gly")
        cmd.disable("gly")
        cmd.select("sele", "trp and name CA+CB")

    def a_menu():
        p = win().object_panel
        log("items", list(p.items.keys()))
        item = p.items.get("small")
        rect = p.tree.visualRect(p.tree.indexFromItem(item, 1))
        st["pos"] = rect.center()
        later(0, lambda: cap.click(p.tree.viewport(), rect.center()))

    def a_shot():
        menus = [
            t
            for t in app.topLevelWidgets()
            if isinstance(t, QtWidgets.QMenu) and t.isVisible()
        ]
        log(
            "menus",
            len(menus),
            [a.text() for a in menus[0].actions()] if menus else None,
        )
        shot(OUT + "objects-panel.png", crop=(840, 62, 640, 560))
        for m in menus:
            m.close()

    cap.run(
        [
            (1500, size),
            (1500, open_table),
            (1500, load),
            (1500, sort),
            (1000, star),
            (1000, table_shot),
            (800, table_shot2),
            (800, group),
            (1200, a_menu),
            (1200, a_shot),
        ],
        cap.quit_,
    )


_scenario()
