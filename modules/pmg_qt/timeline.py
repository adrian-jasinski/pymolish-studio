"""
Timeline panel: the movie as a list of shots. A strip shows the shots as
blocks as wide as they last, with the playhead; the table under it edits
them. Every edit rebuilds the movie of the core (pymol.shots.build), so the
movie that plays, exports and is saved in a session is an ordinary one.

The list lives in this panel only. A movie made with commands or loaded
from a session has no list: it plays and scrubs here, and "Add" starts a
new one (docs/plans/19-movie-timeline.md).
"""

from pymol import shots
from pymol.Qt import QtCore, QtGui, QtWidgets

Qt = QtCore.Qt
COLUMNS = ("Shot", "Target", "Seconds", "Start", "Effect")
KIND, TARGET, SECONDS, START, EFFECT = range(5)
# label, width, height, file filter
EXPORTS = (
    ("MP4 1280 x 720", 1280, 720, "MPEG 4 movie (*.mp4)"),
    ("MP4 1920 x 1080", 1920, 1080, "MPEG 4 movie (*.mp4)"),
    ("MP4 3840 x 2160", 3840, 2160, "MPEG 4 movie (*.mp4)"),
    ("GIF 640 x 480", 640, 480, "Animated GIF (*.gif)"),
)


def _duration(seconds):
    return "%d:%02d" % divmod(int(round(seconds)), 60)


class Strip(QtWidgets.QWidget):
    """The shots as blocks on a time axis; click or drag to move the
    playhead."""

    def __init__(self, panel):
        super().__init__(panel)
        self.panel = panel
        self.frame = 1
        self.setMinimumHeight(56)
        self.setToolTip("Click or drag: go to that moment")
        self.setAccessibleName("Movie strip")

    def paintEvent(self, event):
        panel = self.panel
        painter = QtGui.QPainter(self)
        palette = self.palette()
        width, height = self.width(), self.height()
        painter.fillRect(self.rect(), palette.base())
        total = panel.total_frames()
        if not total:
            painter.setPen(palette.placeholderText().color())
            painter.drawText(
                self.rect(),
                Qt.AlignmentFlag.AlignCenter,
                "No movie. Add a shot, record views, or start a tour.",
            )
            return
        blocks = panel.blocks() or [(1, total, "Movie made with commands", None)]
        current = panel.table.currentRow()
        for row, (first, count, text, pixmap) in enumerate(blocks):
            x0 = int((first - 1) * width / total)
            x1 = int((first - 1 + count) * width / total)
            box = QtCore.QRect(x0, 0, max(2, x1 - x0 - 1), height - 1)
            selected = row == current and panel.shots
            painter.fillRect(box, palette.highlight() if selected else palette.button())
            painter.setPen(palette.mid().color())
            painter.drawRect(box)
            left = box.left() + 4
            if pixmap is not None and box.width() > 60:
                thumb = pixmap.scaledToHeight(
                    height - 8, Qt.TransformationMode.SmoothTransformation
                )
                painter.drawPixmap(left, 4, thumb)
                left += thumb.width() + 4
            role = palette.highlightedText() if selected else palette.buttonText()
            painter.setPen(role.color())
            painter.drawText(
                QtCore.QRect(left, 0, box.right() - left - 2, height),
                Qt.AlignmentFlag.AlignVCenter | Qt.TextFlag.TextSingleLine,
                painter.fontMetrics().elidedText(
                    text, Qt.TextElideMode.ElideRight, max(0, box.right() - left - 2)
                ),
            )
        x = int((self.frame - 0.5) * width / total)
        painter.setPen(QtGui.QPen(palette.text().color(), 2))
        painter.drawLine(x, 0, x, height)

    def _seek(self, event):
        total = self.panel.total_frames()
        if total:
            x = event.position().x()
            frame = 1 + int(max(0, min(self.width() - 1, x)) * total / self.width())
            self.panel.seek(frame)

    mousePressEvent = _seek
    mouseMoveEvent = _seek


class TimelinePanel(QtWidgets.QDockWidget):
    def __init__(self, cmd, parent=None):
        super().__init__("Timeline", parent)
        self.setObjectName("dock_timeline")
        self.cmd = cmd
        self.shots = []
        self.starts = []
        self._built = 0  # movie length after our last build
        self._thumbs = {}  # scene name -> (png bytes, pixmap)
        self._rest = None  # view while it rests, for Record
        self._had_movie = False  # to open once when a movie appears

        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        bar = QtWidgets.QHBoxLayout()
        layout.addLayout(bar)

        def button(text, tip, run=None, menu=False):
            b = QtWidgets.QToolButton()
            b.setText(text)
            b.setToolTip(tip)
            b.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
            b.setFocusPolicy(Qt.FocusPolicy.TabFocus)
            if menu:
                b.setMenu(QtWidgets.QMenu(b))
                b.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)
            if run:
                b.clicked.connect(run)
            bar.addWidget(b)
            return b

        self.add = button("Add", "Add a shot after the selected one", menu=True)
        self.add.menu().aboutToShow.connect(self._fill_add)
        self.add_view = button(
            "Add view", "Add the view of now as a shot", lambda: self.append("view")
        )
        self.record = button(
            "Record", "Add a shot each time the view comes to rest after you moved it"
        )
        self.record.setCheckable(True)
        self.record.toggled.connect(self._record)
        self.tour = button("Tour", "A movie that visits places", menu=True)
        for label, what in (
            ("Every scene", "scenes"),
            ("Every ligand", "ligands"),
            ("Every chain", "chains"),
            ("Every selection", "selections"),
        ):
            self.tour.menu().addAction(label, lambda w=what: self._tour(w))
        self.up = button(
            "Up", "Move the shot earlier (Alt+Up)", lambda: self.move_shot(-1)
        )
        self.down = button(
            "Down", "Move the shot later (Alt+Down)", lambda: self.move_shot(1)
        )
        self.remove = button("Delete", "Delete the shot (Delete)", self.delete)
        self.clear = button("Clear", "Remove the whole movie", self.clear_movie)
        bar.addStretch(1)
        self.info = QtWidgets.QLabel()
        bar.addWidget(self.info)
        self.play = button("Play", "Play or stop (Space)", lambda: cmd.mtoggle())
        self.export = button("Export", "Render the movie to a file", menu=True)
        menu = self.export.menu()
        self.ray = menu.addAction("Ray traced")
        self.ray.setCheckable(True)
        menu.addSeparator()
        for preset in EXPORTS:
            menu.addAction(preset[0], lambda p=preset: self._export(*p[1:]))
        menu.addSeparator()
        menu.addAction("More formats...", self._export_dialog)
        menu.addAction("Copy as script", self._copy)

        self.strip = Strip(self)
        layout.addWidget(self.strip)
        self.table = table = QtWidgets.QTableWidget(0, len(COLUMNS))
        table.setHorizontalHeaderLabels(COLUMNS)
        table.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows
        )
        table.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.SingleSelection
        )
        table.verticalHeader().hide()
        table.horizontalHeader().setStretchLastSection(True)
        table.itemChanged.connect(self._edited)
        table.currentCellChanged.connect(lambda *_: self.strip.update())
        layout.addWidget(table)
        self.setWidget(widget)

        children = Qt.ShortcutContext.WidgetWithChildrenShortcut
        for keys, run in (
            ("Alt+Up", lambda: self.move_shot(-1)),
            ("Alt+Down", lambda: self.move_shot(1)),
            ("Delete", self.delete),
        ):
            QtGui.QShortcut(QtGui.QKeySequence(keys), table, run, context=children)
        QtGui.QShortcut(
            QtGui.QKeySequence("Space"),
            self.strip,
            lambda: cmd.mtoggle(),
            context=children,
        )
        self.strip.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self._timer = QtCore.QTimer(self)
        self._timer.setInterval(250)
        self._timer.timeout.connect(self._watch_view)
        # one timeline at a time: the core's keyframe strip under the
        # viewport is off while this panel is open
        self.visibilityChanged.connect(lambda on: cmd.set("movie_panel", int(not on)))
        self.refresh()

    # --- what the strip draws -------------------------------------------

    def total_frames(self):
        return self.cmd.get_movie_length()

    def blocks(self):
        """(first frame, frames, text, pixmap or None) per shot."""
        ends = self.starts[1:] + [self._built + 1]
        result = []
        for item, first, end in zip(self.shots, self.starts, ends):
            text = item["kind"]
            if item.get("target"):
                text = "%s %s" % (item["kind"], item["target"])
            pixmap = self._thumb(item["target"]) if item["kind"] == "scene" else None
            result.append((first, end - first, text, pixmap))
        return result

    def _thumb(self, name):
        png = self.cmd.get_scene_thumbnail(name)
        if not png:
            return None
        if self._thumbs.get(name, (None,))[0] != png:
            pixmap = QtGui.QPixmap()
            pixmap.loadFromData(png)
            self._thumbs[name] = (png, pixmap)
        return self._thumbs[name][1]

    def poll(self):
        """From the window's timer: follow the playhead and notice a movie
        that was replaced from outside (commands, a session). The panel
        opens by itself when a movie appears; closed again, it stays closed
        until the next new movie."""
        has_movie = self.total_frames() > 0
        if has_movie and not self._had_movie:
            self.show()
        self._had_movie = has_movie
        if not self.isVisible():
            return
        if self.shots and self.total_frames() != self._built:
            self.shots, self.starts = [], []
            self._fill()
        frame = self.cmd.get_frame()
        if frame != self.strip.frame:
            self.strip.frame = frame
            self.strip.update()
        self._show_info()

    def seek(self, frame):
        self.cmd.frame(frame)
        self.strip.frame = frame
        rows = [row for row, first in enumerate(self.starts) if first <= frame]
        if self.shots and rows and self.table.currentRow() != rows[-1]:
            self.table.selectRow(rows[-1])
        self.strip.update()

    # --- the list ---------------------------------------------------------

    def refresh(self):
        self._fill()
        self._show_info()

    def _show_info(self):
        cmd = self.cmd
        frames = self.total_frames()
        fps = cmd.get_setting_float("movie_fps") or 30
        if not frames:
            text = ""
        elif self.shots:
            text = "%d shots, %s, %d frames" % (
                len(self.shots),
                _duration(frames / fps),
                frames,
            )
        else:
            text = (
                "Made with commands: %s, %d frames. It plays; Add starts a new one."
                % (
                    _duration(frames / fps),
                    frames,
                )
            )
        self.info.setText(text)

    def _fill(self):
        table = self.table
        row = table.currentRow()
        with QtCore.QSignalBlocker(table):
            table.setRowCount(len(self.shots))
            for r, item in enumerate(self.shots):
                kind = QtWidgets.QTableWidgetItem(item["kind"])
                kind.setFlags(kind.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(r, KIND, kind)
                target = QtWidgets.QTableWidgetItem(item.get("target", ""))
                if item["kind"] not in ("scene", "zoom"):
                    target.setFlags(target.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(r, TARGET, target)
                table.setItem(
                    r, SECONDS, QtWidgets.QTableWidgetItem("%g" % item["seconds"])
                )
                for column, key, values in (
                    (START, "start", shots.STARTS),
                    (EFFECT, "effect", ("", *shots.EFFECTS)),
                ):
                    box = QtWidgets.QComboBox()
                    box.addItems(values)
                    box.setCurrentText(item.get(key, ""))
                    box.currentTextChanged.connect(
                        lambda text, i=item, k=key: self._set(i, k, text)
                    )
                    table.setCellWidget(r, column, box)
            if self.shots:
                table.selectRow(min(max(row, 0), len(self.shots) - 1))
        self.strip.update()

    def _set(self, item, key, value):
        item[key] = value
        self.rebuild()

    def _edited(self, cell):
        item = self.shots[cell.row()]
        if cell.column() == TARGET:
            item["target"] = cell.text().strip()
        elif cell.column() == SECONDS:
            try:
                item["seconds"] = max(0.1, float(cell.text()))
            except ValueError:
                pass
            with QtCore.QSignalBlocker(self.table):
                cell.setText("%g" % item["seconds"])
        self.rebuild()

    def rebuild(self):
        """Make the movie of the core from the list; the view of now is
        where a movie that does not start with a scene begins."""
        cmd = self.cmd
        view = cmd.get_view()
        try:
            self.starts = shots.build(self.shots, _self=cmd)
        except Exception as error:  # a scene or selection that is gone
            self.starts = [1] * len(self.shots)
            print(" Timeline: %s" % error)
        cmd.set_view(view)
        self._built = self.total_frames()
        self.strip.frame = 1
        self.strip.update()
        self._show_info()

    def insert(self, new):
        """Add shots after the selected one and rebuild."""
        if not self.shots and self.total_frames() and not self._replace_ok():
            return
        row = self.table.currentRow() + 1 if self.shots else 0
        self.shots[row:row] = new
        self.rebuild()
        self._fill()
        if new:
            self.table.selectRow(row + len(new) - 1)

    def _replace_ok(self):
        """A movie that was not made here would be lost: ask first."""
        box = QtWidgets.QMessageBox
        return (
            box.question(
                self,
                "Timeline",
                "This movie was made with commands or comes from a session.\n"
                "A shot list replaces it. Replace the movie?",
            )
            == box.StandardButton.Yes
        )

    def append(self, kind, target="", **more):
        self.insert([shots.shot(kind, target, _self=self.cmd, **more)])

    def move_shot(self, step):
        row = self.table.currentRow()
        other = row + step
        if row < 0 or not 0 <= other < len(self.shots):
            return
        self.shots[row], self.shots[other] = self.shots[other], self.shots[row]
        self.rebuild()
        self._fill()
        self.table.selectRow(other)

    def delete(self):
        row = self.table.currentRow()
        if 0 <= row < len(self.shots):
            del self.shots[row]
            self.rebuild()
            self._fill()

    def clear_movie(self):
        self.shots = []
        self.rebuild()
        self._fill()

    # --- menus ------------------------------------------------------------

    def _fill_add(self):
        menu = self.add.menu()
        menu.clear()
        cmd = self.cmd
        scenes = menu.addMenu("Scene")
        for name in cmd.get_scene_list():
            scenes.addAction(name, lambda n=name: self.append("scene", n))
        scenes.setEnabled(bool(cmd.get_scene_list()))
        zoom = menu.addMenu("Zoom to")
        for name in ["all", "organic", *cmd.get_names("public_selections")]:
            zoom.addAction(name, lambda n=name: self.append("zoom", n))
        menu.addAction("View of now", lambda: self.append("view"))
        menu.addSeparator()
        menu.addAction("Turn 360\N{DEGREE SIGN}", lambda: self.append("turn"))
        menu.addAction("Rock", lambda: self.append("rock"))
        menu.addAction("Nutate", lambda: self.append("nutate"))
        states = menu.addAction("Play the states", lambda: self.append("states"))
        states.setEnabled(cmd.count_states() > 1)
        menu.addAction("Hold", lambda: self.append("hold"))

    def _tour(self, what):
        new = shots.tour(what, _self=self.cmd)
        if new:
            self.insert(new)
        else:
            QtWidgets.QMessageBox.information(
                self, "Tour", "Nothing to visit: no %s." % what
            )

    def _record(self, on):
        self._rest = self.cmd.get_view() if on else None
        self._moving = False
        (self._timer.start if on else self._timer.stop)()

    def _watch_view(self):
        """While recording: a view that changed and then stayed for one
        tick becomes a shot."""
        view = self.cmd.get_view()
        if view != self._rest:
            self._rest = view
            self._moving = True
        elif self._moving:
            self._moving = False
            self.append("view", seconds=2)

    def _copy(self):
        QtWidgets.QApplication.clipboard().setText(shots.describe(self.shots))

    def _export_dialog(self):
        self.parentWidget().file_save_mpeg()

    def _export(self, width, height, filter):
        cmd = self.cmd
        ray = self.ray.isChecked()
        frames, seconds, size = shots.estimate(width, height, ray, _self=cmd)
        if not frames or self.total_frames() == 0:
            QtWidgets.QMessageBox.information(self, "Export", "There is no movie yet.")
            return
        text = "%d frames at %d x %d" % (frames, width, height)
        if seconds is not None:
            text += ", about %s to render, about %.0f MB of frames on the way" % (
                _duration(seconds),
                size / 1e6,
            )
        ask = QtWidgets.QMessageBox.question(self, "Export", text + ". Render it now?")
        if ask != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        name = QtWidgets.QFileDialog.getSaveFileName(self, "Export movie", "", filter)[
            0
        ]
        if name:
            cmd.movie.produce(
                name, mode="ray" if ray else "draw", width=width, height=height, quiet=0
            )
