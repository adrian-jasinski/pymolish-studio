def _scenario():
    import os
    import sys

    B = os.environ["PYMOLISH_CAPTURE"].rstrip("/") + "/"  # holds work/ and out/
    sys.path.insert(0, os.path.join(os.getcwd(), "docs", "media", "capture"))
    import cap
    from cap import cmd, win, log, shot, QtWidgets, QtCore

    OUT = B + "out/"
    os.makedirs(B + "work", exist_ok=True)
    os.makedirs(B + "out", exist_ok=True)
    cmd.cd(B + "work")
    cap.LOG = open(OUT + "f.log", "w")
    cmd.fetch("1oky")

    def size():
        w = win()
        w.resize(1280, 800)
        w.activateWindow()
        w.raise_()

    def chat():
        bar = win().command_tabs.tabBar()
        cap.click(bar, bar.tabRect(2).center())

    def chat_shot():
        c = win().chat_panel
        log(
            "visible widgets",
            [
                (
                    type(w).__name__,
                    getattr(w, "text", lambda: "")()
                    if not isinstance(
                        w,
                        (
                            QtWidgets.QComboBox,
                            QtWidgets.QAbstractSpinBox,
                            QtWidgets.QTextEdit,
                            QtWidgets.QPlainTextEdit,
                        ),
                    )
                    else (
                        w.currentText() if isinstance(w, QtWidgets.QComboBox) else ""
                    ),
                )
                for w in c.findChildren(QtWidgets.QWidget)
                if w.isVisible()
                and isinstance(
                    w,
                    (
                        QtWidgets.QAbstractButton,
                        QtWidgets.QComboBox,
                        QtWidgets.QLineEdit,
                        QtWidgets.QLabel,
                    ),
                )
            ],
        )
        p = win().command_tabs.mapTo(win(), QtCore.QPoint(0, 0))
        shot(
            OUT + "chat-setup.png",
            crop=(0, p.y() - 4, win().width(), win().height() - p.y() + 4),
        )

    cap.run([(1500, size), (2000, chat), (1500, chat_shot)], cap.quit_)


_scenario()
