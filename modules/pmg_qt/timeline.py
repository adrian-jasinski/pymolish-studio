"""
Timeline panel: the movie as a list of shots. A strip shows the shots as
blocks as wide as they last, with the playhead; the table under it edits
them. Every edit rebuilds the movie of the core (pymol.shots.build), so the
movie that plays, exports and is saved in a session is an ordinary one.

The list is kept in the session under the key "pymolish"
(pymol.session_extra, entry "timeline"), with the length of the movie it
built: a session whose movie still has that length brings its list back. A
movie made with commands has no list: it plays and scrubs here, and "Add"
starts a new one (docs/plans/19-movie-timeline.md).
"""

import copy

from pymol import session_extra, shots
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


RULER = 14  # height of the band of seconds above the blocks
EDGE = 5  # this close to the end of a block, a drag makes it longer
SLOP = 4  # a press that moves less is a click


class Strip(QtWidgets.QWidget):
    """The shots as blocks on a time axis under a ruler of seconds. A click,
    or a drag on the ruler, moves the playhead; a drag moves a block to
    another place, and a drag of its right end makes it longer or shorter."""

    def __init__(self, panel):
        super().__init__(panel)
        self.panel = panel
        self.frame = 1
        self._drag = None  # (mode, row, x at press), mode: seek, move, stretch
        self._x = 0  # where the drag is now
        self.setMinimumHeight(56 + RULER)
        self.setMouseTracking(True)
        self.setToolTip(
            "Click, or drag on the ruler: go to that moment.\n"
            "Drag a shot to move it, its right end to change its length."
        )
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
        # the ruler: a tick each second, or each ten when they get crowded
        fps = panel.cmd.get_setting_float("movie_fps") or 30
        step = fps * (10 if width * fps / total < 6 else 1)
        painter.setPen(palette.mid().color())
        for tick in range(int(total / step) + 1):
            x = int(tick * step * width / total)
            painter.drawLine(x, RULER - (7 if tick % 5 == 0 else 3), x, RULER)
        for row, (first, count, text, pixmap) in enumerate(blocks):
            x0 = int((first - 1) * width / total)
            x1 = int((first - 1 + count) * width / total)
            box = QtCore.QRect(x0, RULER, max(2, x1 - x0 - 1), height - RULER - 1)
            selected = row == current and panel.shots
            painter.fillRect(box, palette.highlight() if selected else palette.button())
            painter.setPen(palette.mid().color())
            painter.drawRect(box)
            left = box.left() + 4
            if pixmap is not None and box.width() > 60:
                thumb = pixmap.scaledToHeight(
                    box.height() - 8, Qt.TransformationMode.SmoothTransformation
                )
                painter.drawPixmap(left, RULER + 4, thumb)
                left += thumb.width() + 4
            role = palette.highlightedText() if selected else palette.buttonText()
            painter.setPen(role.color())
            painter.drawText(
                QtCore.QRect(left, RULER, box.right() - left - 2, box.height()),
                Qt.AlignmentFlag.AlignVCenter | Qt.TextFlag.TextSingleLine,
                painter.fontMetrics().elidedText(
                    text, Qt.TextElideMode.ElideRight, max(0, box.right() - left - 2)
                ),
            )
        x = int((self.frame - 0.5) * width / total)
        painter.setPen(QtGui.QPen(palette.text().color(), 2))
        painter.drawLine(x, 0, x, height)
        if self._drag and self._drag[0] != "seek":  # where the drag would end
            painter.setPen(QtGui.QPen(palette.link().color(), 2))
            painter.drawLine(self._x, RULER, self._x, height)

    def _seek(self, x):
        total = self.panel.total_frames()
        if total:
            frame = 1 + int(max(0, min(self.width() - 1, x)) * total / self.width())
            self.panel.seek(frame)

    def hit(self, x, y):
        """What a press at (x, y) starts: ("seek" | "move" | "stretch", row)."""
        total = self.panel.total_frames()
        if y < RULER or not total or not self.panel.shots:
            return "seek", -1
        for row, (first, count, _, _) in enumerate(self.panel.blocks()):
            end = (first - 1 + count) * self.width() / total
            if x <= end:
                return ("stretch" if end - x <= EDGE else "move"), row
        return "seek", -1

    def mousePressEvent(self, event):
        x, y = int(event.position().x()), int(event.position().y())
        self._drag = (*self.hit(x, y), x)
        self._x = x
        if self._drag[0] == "seek":
            self._seek(x)

    def mouseMoveEvent(self, event):
        x, y = int(event.position().x()), int(event.position().y())
        if not self._drag:  # no button: show what a drag here would do
            mode = self.hit(x, y)[0]
            self.setCursor(
                Qt.CursorShape.SizeHorCursor
                if mode == "stretch"
                else Qt.CursorShape.ArrowCursor
            )
            return
        self._x = x
        if self._drag[0] == "seek":
            self._seek(x)
        self.update()

    def mouseReleaseEvent(self, event):
        drag, self._drag = self._drag, None
        if not drag:
            return
        mode, row, start = drag
        panel, x = self.panel, int(event.position().x())
        total = panel.total_frames()
        if mode == "seek":
            pass
        elif abs(x - start) < SLOP:  # a click on a block
            self._seek(x)
        elif mode == "move":
            panel.move_shot_to(row, self.hit(min(x, self.width() - 1), RULER)[1])
        else:
            first = panel.starts[row]
            frames = x * total / self.width() - (first - 1)
            fps = panel.cmd.get_setting_float("movie_fps") or 30
            panel.set_seconds(row, round(frames / fps, 1))
        self.update()


class TimelinePanel(QtWidgets.QDockWidget):
    def __init__(self, cmd, parent=None):
        super().__init__("Timeline", parent)
        self.setObjectName("dock_timeline")
        self.cmd = cmd
        self.shots = []
        self.starts = []
        self._built = 0  # movie length after our last build
        self._thumbs = {}  # scene name -> (png bytes, pixmap)
        self._kept = None  # our entry in the session, as last written or read
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
        kept = session_extra.entries.get("timeline")
        if kept is not self._kept:  # a session was loaded
            self._kept = kept
            self._adopt(kept)
        if not self.isVisible():
            return
        if self.shots and self.total_frames() != self._built:
            self.shots, self.starts = [], []
            self._forget()
            self._fill()
        frame = self.cmd.get_frame()
        if frame != self.strip.frame:
            self.strip.frame = frame
            self.strip.update()
        self._show_info()

    def _forget(self):
        session_extra.entries.pop("timeline", None)
        self._kept = None

    def _adopt(self, kept):
        """Take the list a session brought, if its movie is still the one
        the list built; else there is no list."""
        try:
            listed = copy.deepcopy(kept["shots"])
            starts = [int(first) for first in kept["starts"]]
            ok = (
                kept["frames"] == self.total_frames()
                and len(starts) == len(listed)
                and all(item["kind"] in shots.KINDS for item in listed)
                and all(float(item["seconds"]) > 0 for item in listed)
            )
        except (KeyError, TypeError, ValueError):
            ok = False
        self.shots, self.starts = (listed, starts) if ok else ([], [])
        self._built = self.total_frames() if ok else 0
        self._fill()

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
        if self.shots:  # into the session, with the movie it belongs to
            self._kept = session_extra.entries["timeline"] = {
                "shots": copy.deepcopy(self.shots),
                "starts": list(self.starts),
                "frames": self._built,
            }
        else:
            self._forget()
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
        self.move_shot_to(row, row + step)

    def move_shot_to(self, row, other):
        """Put shot `row` where shot `other` is (the strip drags to here)."""
        count = len(self.shots)
        if row == other or not (0 <= row < count and 0 <= other < count):
            return
        self.shots.insert(other, self.shots.pop(row))
        self.rebuild()
        self._fill()
        self.table.selectRow(other)

    def set_seconds(self, row, seconds):
        """The length of shot `row`, as typed into the table."""
        self.table.item(row, SECONDS).setText("%g" % seconds)

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
