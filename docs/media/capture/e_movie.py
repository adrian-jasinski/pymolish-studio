def _scenario():
    import os
    import sys

    B = os.environ["PYMOLISH_CAPTURE"].rstrip("/") + "/"  # holds work/ and out/
    sys.path.insert(0, os.path.join(os.getcwd(), "docs", "media", "capture"))
    import cap
    from cap import (
        cmd,
        win,
        log,
        shot,
        widget_shot,
        later,
        QtCore,
        QTest,
    )

    Q = QtCore.Qt
    OUT = B + "out/"
    os.makedirs(B + "work", exist_ok=True)
    os.makedirs(B + "out", exist_ok=True)
    cmd.cd(B + "work")
    cap.LOG = open(OUT + "e.log", "w")
    cmd.fetch("1oky")
    rec = cap.Recorder(OUT + "clip-movie", fps=7)
    tb = lambda: win().action_toolbar
    scenes = lambda: win().scene_panel
    tl = lambda: win().timeline_panel
    st = {}

    def size():
        w = win()
        w.resize(1470, 800)
        w.activateWindow()
        w.raise_()

    def open_scenes():
        cap.click(cap.find_button(tb(), tip="Scenes"))

    def add1():
        cap.find_button(scenes(), "Add").click()

    def pocket():
        cmd.do("ligand_next")

    def add2():
        cap.find_button(scenes(), "Add").click()

    def scenes_shot():
        log("scenes", cmd.get_scene_list(), "dock area", win().dockWidgetArea(scenes()))
        shot(OUT + "scenes-panel.png", crop=(0, 60, 1100, 560))

    def presize():
        # the Timeline makes the window wider: let it, before the recording
        cap.click(cap.find_button(tb(), tip="Movie"))

    def presize2():
        cap.click(cap.find_button(tb(), tip="Movie"))
        log("window", win().width(), win().height())

    def recall(row, caption):
        def f():
            rec.caption = caption
            lst = scenes().list
            cap.click(lst.viewport(), lst.visualItemRect(lst.item(row)).center(), rec)

        return f

    def open_timeline():
        rec.caption = "The Movie button opens the Timeline"
        cap.click(cap.find_button(tb(), tip="Movie"), rec=rec)

    def tour_open():
        log(
            "timeline visible",
            tl().isVisible(),
            "floating",
            tl().isFloating(),
            win().dockWidgetArea(tl()),
            tl().geometry(),
        )
        rec.caption = "Tour > Every scene: one shot per scene"
        rec.cursor = cap.center(tl().tour)
        later(0, tl().tour.showMenu)

    def tour_pick():
        cap.menu_click(tl().tour.menu(), "Every scene", rec)

    def add_open():
        log(
            "shots",
            [(s["kind"], s.get("target"), s.get("seconds")) for s in tl().shots],
        )
        rec.caption = "Add > Turn 360°"
        rec.cursor = cap.center(tl().add)
        later(0, tl().add.showMenu)

    def add_pick():
        cap.menu_click(tl().add.menu(), "Turn 360°", rec)

    def stretch_press():
        p = tl()
        s = p.strip
        rec.caption = "Drag the right end of a block: the shot gets shorter or longer"
        total = p.total_frames()
        blocks = p.blocks()
        log(
            "blocks",
            [(b[0], b[1], b[2]) for b in blocks],
            "total",
            total,
            "strip",
            s.width(),
            s.height(),
        )
        row = len(blocks) - 1
        first, count = blocks[row][0], blocks[row][1]
        end = int((first - 1 + count) * s.width() / total) - 2
        y = s.height() - 12
        st["a"], st["b"] = (
            QtCore.QPoint(end, y),
            QtCore.QPoint(end - int(count * s.width() / total * 0.5), y),
        )
        rec.cursor = cap.gpos(s, st["a"])
        QTest.mousePress(
            s, Q.MouseButton.LeftButton, Q.KeyboardModifier.NoModifier, st["a"]
        )

    def stretch_move():
        s = tl().strip
        mid = QtCore.QPoint((st["a"].x() + st["b"].x()) // 2, st["a"].y())
        QTest.mouseMove(s, mid)
        rec.cursor = cap.gpos(s, mid)

    def stretch_release():
        s = tl().strip
        QTest.mouseMove(s, st["b"])
        rec.cursor = cap.gpos(s, st["b"])
        QTest.mouseRelease(
            s, Q.MouseButton.LeftButton, Q.KeyboardModifier.NoModifier, st["b"]
        )

    def play():
        log(
            "shots after stretch",
            [(s["kind"], s.get("target"), s.get("seconds")) for s in tl().shots],
            "frames",
            tl().total_frames(),
        )
        rec.caption = "Play"
        cap.click(tl().play, rec=rec)

    def stop_play():
        log("frame while playing", cmd.get_frame())
        cap.click(tl().play, rec=rec)
        rec.caption = "Export: MP4, GIF or more formats (needs ffmpeg)"

    def export_open():
        rec.cursor = cap.center(tl().export)
        later(0, tl().export.showMenu)

    def export_close():
        shot(OUT + "timeline-export.png")
        tl().export.menu().close()

    def stills():
        rec.stop()
        tl().strip._seek(int(tl().strip.width() * 0.45))

    def stills2():
        shot(OUT + "timeline.png")
        widget_shot(tl(), OUT + "timeline-panel.png")

    cap.run(
        [
            (1500, size),
            (2000, open_scenes),
            (1200, add1),
            (800, pocket),
            (2500, add2),
            (1500, scenes_shot),
            (500, presize),
            (1500, presize2),
            (1500, rec.start),
            (1200, recall(0, "Click a scene: the view and its look come back")),
            (3000, recall(1, "Click a scene: the view and its look come back")),
            (3000, open_timeline),
            (2000, tour_open),
            (1000, tour_pick),
            (2500, add_open),
            (1000, add_pick),
            (2500, stretch_press),
            (500, stretch_move),
            (500, stretch_release),
            (2500, play),
            (6000, stop_play),
            (1200, export_open),
            (2200, export_close),
            (800, stills),
            (1200, stills2),
        ],
        cap.quit_,
    )


_scenario()
