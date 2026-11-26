"""A separate sequence window; molecular state stays in cmd, alignments in the session."""

import copy
import csv
import itertools
import os
import threading
from collections import Counter
from pathlib import Path

from pymol import CmdException, sequence, session_extra
from pymol.Qt import QtCore, QtGui, QtWidgets
from pymol.Qt.utils import AsyncFunc, getMonospaceFont, loadUi

Qt = QtCore.Qt
SS_ROLE = Qt.ItemDataRole.UserRole  # track row: (code, first, last, number)
HELIX, STRAND, COIL = (
    QtGui.QColor("#e0413a"),
    QtGui.QColor("#2fa84f"),
    QtGui.QColor(128, 128, 128),
)
SS_NAMES = {"H": "Helix", "S": "Strand"}
# Jalview's colour schemes: Zappo by residue kind, Kyte-Doolittle hydropathy
ZAPPO = {
    **dict.fromkeys("ILVAM", "#ffafaf"),
    **dict.fromkeys("FWY", "#ffc800"),
    **dict.fromkeys("KRH", "#6464ff"),
    **dict.fromkeys("DE", "#ff0000"),
    **dict.fromkeys("STNQ", "#00ff00"),
    **dict.fromkeys("PG", "#ff00ff"),
    "C": "#ffff00",
}
KYTE_DOOLITTLE = dict(
    I=4.5, V=4.2, L=3.8, F=2.8, C=2.5, M=1.9, A=1.8, G=-0.4, T=-0.7, S=-0.8,
    W=-0.9, Y=-1.3, P=-1.6, H=-3.2, E=-3.5, Q=-3.5, D=-3.5, N=-3.5, K=-3.9, R=-4.5,
)  # fmt: skip
# percent identity: residues equal to the consensus, by how many share it
IDENTITY = ((0.8, "#6464ff"), (0.6, "#9999ff"), (0.4, "#ccccff"))
COLORINGS = ("No color", "Residue type", "Hydrophobicity", "Percent identity")


def ss_track(mapping):
    """Consensus secondary structure per column: "H" or "S" where that is
    the most common assignment of the structure rows, else " "."""
    track = []
    for column in itertools.zip_longest(*mapping):
        best = Counter(r[2] for r in column if r and r[2] in "HSL").most_common(1)
        track.append(best[0][0] if best and best[0][0] in "HS" else " ")
    return "".join(track)


def ss_elements(track):
    """Per column (code, first column, last column, number) of the helix
    or strand it is in, numbered from 1; coil is (" ", column, column, 0)."""
    elements, number = [], 0
    for code, run in itertools.groupby(track):
        n = len(list(run))
        first = len(elements)
        if code != " ":
            number += 1
        elements += [(code, first, first + n - 1, number if code != " " else 0)] * n
    return elements


def residue_color(scheme, letter, consensus="", conservation=0.0):
    """Background of one residue under a COLORINGS index, or None."""
    letter = letter.upper()
    if scheme == 1:
        return ZAPPO.get(letter)
    if scheme == 2 and letter in KYTE_DOOLITTLE:
        t = (KYTE_DOOLITTLE[letter] + 4.5) / 9  # blue hydrophilic, red hydrophobic
        return QtGui.QColor.fromRgbF(0.5 + 0.5 * t, 0.5, 1 - 0.5 * t).name()
    if scheme == 3 and letter == consensus and letter not in "-X?*":
        return next((c for limit, c in IDENTITY if conservation > limit), None)
    return None


class TrackDelegate(QtWidgets.QStyledItemDelegate):
    """Draws the secondary structure track: helices as cylinders, strands
    as arrows, coil as a line, each element numbered at its start."""

    def sizeHint(self, option, index):
        size = super().sizeHint(option, index)
        if index.data(SS_ROLE) is not None:
            size.setHeight(34)
        return size

    def paint(self, painter, option, index):
        element = index.data(SS_ROLE)
        if element is None:
            return super().paint(painter, option, index)
        code, first, last, number = element
        column, rect = index.column(), QtCore.QRectF(option.rect)
        mid = rect.center().y() + 5
        painter.save()
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setClipRect(rect)
        painter.setPen(Qt.PenStyle.NoPen)
        if code == "H":
            body = QtCore.QRectF(rect.left(), mid - 6, rect.width(), 12)
            # a run continues past the cell edges, so only its ends are round
            body.adjust(-8 if column > first else 2, 0, 8 if column < last else -2, 0)
            painter.setBrush(HELIX)
            painter.drawRoundedRect(body, 6, 6)
        elif code == "S":
            painter.setBrush(STRAND)
            left = rect.left() + (2 if column == first else 0)
            if column < last:
                painter.drawRect(QtCore.QRectF(left, mid - 4, rect.right() - left, 8))
            else:
                x = rect.center().x()
                points = ((left, -4), (x, -4), (x, -8), (rect.right() - 2, 0),
                          (x, 8), (x, 4), (left, 4))  # fmt: skip
                painter.drawPolygon(
                    QtGui.QPolygonF([QtCore.QPointF(px, mid + dy) for px, dy in points])
                )
        else:
            painter.setPen(QtGui.QPen(COIL, 1.5))
            painter.drawLine(
                QtCore.QPointF(rect.left(), mid), QtCore.QPointF(rect.right(), mid)
            )
        if number and column == first:
            painter.setPen(option.palette.text().color())
            font = QtGui.QFont(option.font)
            font.setPointSizeF(font.pointSizeF() * 0.8)
            painter.setFont(font)
            top = QtCore.QRectF(
                rect.left() + 2, rect.top(), rect.width(), mid - 7 - rect.top()
            )
            painter.drawText(
                top,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom,
                str(number),
            )
        painter.restore()


class AlignmentModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rows = []
        self.secondary = True
        self.reference = 0
        self.coloring = 0  # index into COLORINGS
        self.picked = set()
        self.missing = set()
        self.update()

    def update(self):
        self.beginResetModel()
        self.mapping = [sequence.aligned_residues(r) for r in self.rows]
        self.consensus, self.conservation, self.identities = sequence.statistics(
            self.rows, self.reference
        )
        track = ss_track(self.mapping) if self.secondary else ""
        self.elements = ss_elements(track) if track.strip() else []
        # under the sequences: the consensus, then the secondary structure
        self.track_row = len(self.rows) + bool(self.consensus) if self.elements else -1
        self.endResetModel()

    def rowCount(self, parent=None):
        return (
            0
            if parent is not None and parent.isValid()
            else len(self.rows) + bool(self.consensus) + bool(self.elements)
        )

    def columnCount(self, parent=None):
        return (
            0
            if parent is not None and parent.isValid()
            else max((len(r["sequence"]) for r in self.rows), default=0)
        )

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal:
            return str(section + 1)
        if section == self.track_row:
            return "Secondary structure"
        if section == len(self.rows):
            return "Consensus"
        identity = self.identities[section] if self.identities else None
        return (
            self.rows[section]["label"]
            + (" (unmapped)" if section in self.missing else "")
            + (f" · {identity:.0%}" if identity is not None else "")
        )

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        row, column = index.row(), index.column()
        if row == self.track_row:
            element = self.elements[column] if column < len(self.elements) else None
            if role == SS_ROLE:
                return element or (" ", column, column, 0)
            if role == Qt.ItemDataRole.ToolTipRole and element and element[3]:
                code, first, last, number = element
                return f"{SS_NAMES[code]} {number}, columns {first + 1}–{last + 1} (most rows)"
            return None
        if row == len(self.rows):
            if role == Qt.ItemDataRole.DisplayRole:
                return self.consensus[column]
            if role == Qt.ItemDataRole.ToolTipRole:
                return f"Conservation: {self.conservation[column]:.0%}; gaps and X/?/* excluded"
            return None
        record = self.rows[row]
        if column >= len(record["sequence"]):
            return None
        residue = self.mapping[row][column]
        if role == Qt.ItemDataRole.DisplayRole:
            letter = record["sequence"][column]
            if not self.secondary:
                return letter
            symbol = (
                {"H": "∿", "S": "→", "L": "─", "?": "?"}.get(residue[2], "?")
                if residue
                else "·"
            )
            return symbol + "\n" + letter
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter
        if role == Qt.ItemDataRole.ToolTipRole:
            if residue:
                return (
                    f"{record['label']} · {residue[1]} {residue[0]} · "
                    + {"H": "helix", "S": "sheet", "L": "coil", "?": "unassigned"}[
                        residue[2]
                    ]
                )
            return (
                "Alignment gap"
                if record["sequence"][column] == "-"
                else "No coordinates"
            )
        if role in (Qt.ItemDataRole.BackgroundRole, Qt.ItemDataRole.ForegroundRole):
            picked = (
                record["source"]
                and residue
                and tuple(record["source"][:3]) + tuple(residue[:2]) in self.picked
            )
            palette = QtWidgets.QApplication.palette()
            color = self.color(row, column)
            if role == Qt.ItemDataRole.BackgroundRole:
                return palette.highlight() if picked else color and QtGui.QColor(color)
            if picked:
                return palette.highlightedText()
            return QtGui.QColor("black") if color else None  # the colors are light
        return None

    def color(self, row, column):
        consensus = self.consensus[column] if self.consensus else ""
        return residue_color(
            self.coloring,
            self.rows[row]["sequence"][column],
            consensus,
            self.conservation[column] if consensus else 0.0,
        )


class SequencePanel(QtWidgets.QDockWidget):
    def __init__(self, cmd, parent=None):
        super().__init__("Sequence alignment", parent)
        self.setObjectName("dock_sequences")
        self.setAllowedAreas(Qt.DockWidgetArea.NoDockWidgetArea)
        self.cmd = cmd
        self.cancel = threading.Event()
        self.worker = None
        self._saved = None
        self.settings = QtCore.QSettings("pymolish", "pymolish-studio")
        self.form = form = loadUi(
            os.path.join(os.path.dirname(__file__), "forms", "sequence.ui"),
            QtWidgets.QWidget(),
        )
        self.setWidget(form)
        self.setFloating(True)
        self.resize(1000, 520)
        geometry = self.settings.value("sequence/geometry")
        if geometry:
            self.restoreGeometry(geometry)
        room = self.screen().availableGeometry()
        self.resize(self.size().boundedTo(room.size()))
        if not room.intersects(self.frameGeometry()):
            self.move(room.topLeft())
        self.model = AlignmentModel(self)
        form.view.setModel(self.model)
        form.view.setFont(getMonospaceFont())
        form.view.setItemDelegate(TrackDelegate(form.view))
        form.coloring.addItems(COLORINGS)
        form.coloring.setCurrentIndex(int(self.settings.value("sequence/coloring", 0)))
        self.model.coloring = form.coloring.currentIndex()
        form.coloring.currentIndexChanged.connect(self.coloring_changed)
        form.view.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Fixed
        )
        form.view.horizontalHeader().setDefaultSectionSize(28)
        form.view.verticalHeader().setDefaultSectionSize(42)
        form.view.selectionModel().selectionChanged.connect(self.select)
        form.view.verticalHeader().sectionClicked.connect(
            lambda row: form.view.selectRow(row)
        )
        form.method.addItems(["align", "super", "cealign"])
        form.addChains.clicked.connect(self.add_dialog)
        form.importFasta.clicked.connect(self.import_dialog)
        form.exportFasta.clicked.connect(self.export_dialog)
        form.removeRows.clicked.connect(self.remove)
        form.alignSequences.clicked.connect(self.align)
        form.fitStructures.clicked.connect(self.fit)
        form.stop.clicked.connect(self.stop)
        form.stop.setEnabled(False)
        form.undo.clicked.connect(lambda: self.cmd.undo())
        form.reference.currentIndexChanged.connect(self.reference_changed)
        form.secondary.toggled.connect(self.secondary_changed)
        form.onlySelected.toggled.connect(self.filter_rows)
        form.copy.clicked.connect(self.copy)
        form.zoom.clicked.connect(self.zoom)
        form.search.returnPressed.connect(self.search)
        form.mafft.clicked.connect(self.choose_mafft)
        form.assignSS.clicked.connect(self.assign_ss)
        QtGui.QShortcut(
            QtGui.QKeySequence.StandardKey.Copy, form.view, activated=self.copy
        )
        QtGui.QShortcut(QtGui.QKeySequence("Return"), form.view, activated=self.select)
        self.hide()

    def selected_rows(self):
        return sorted(
            {
                i.row()
                for i in self.form.view.selectionModel().selectedIndexes()
                if i.row() < len(self.model.rows)
            }
        )

    def save(self):
        self._saved = {
            "rows": copy.deepcopy(self.model.rows),
            "reference": self.model.reference,
        }
        session_extra.entries["alignment"] = self._saved

    def refresh(self):
        self.model.reference = min(
            self.model.reference, max(len(self.model.rows) - 1, 0)
        )
        self.model.update()
        combo = self.form.reference
        combo.blockSignals(True)
        combo.clear()
        combo.addItems([r["label"] for r in self.model.rows])
        combo.setCurrentIndex(self.model.reference)
        combo.blockSignals(False)
        self.form.view.resizeRowsToContents()
        self.save()

    def poll(self):
        if not self.isVisible():
            return
        data = session_extra.entries.get("alignment")
        if data is not self._saved:
            self.stop()
            rows = data.get("rows", []) if isinstance(data, dict) else []
            try:
                sequence.validate_rows(rows)
                self.model.rows = copy.deepcopy(rows)
                self.model.reference = (
                    max(0, int(data.get("reference", 0))) if data else 0
                )
            except (KeyError, ValueError, TypeError):
                self.model.rows = []
                self.form.status.setText("The saved alignment is invalid.")
            self.refresh()
        objects = set(self.cmd.get_object_list())
        missing = {
            i
            for i, row in enumerate(self.model.rows)
            if row["source"] and row["source"][0] not in objects
        }
        if missing != self.model.missing:
            self.model.missing = missing
            self.model.headerDataChanged.emit(
                Qt.Orientation.Vertical, 0, len(self.model.rows)
            )
        picked = set()
        if "sele" in self.cmd.get_names("selections"):
            self.cmd.iterate(
                "sele",
                "picked.add((model, segi, chain, resi, resn))",
                space={"picked": picked},
            )
        if picked != self.model.picked:
            self.model.picked = picked
            self.form.view.viewport().update()

    def open(self):
        self.show()
        self.raise_()
        self.poll()

    def add_chains(self, selection="enabled", state=0):
        existing = [r["source"] for r in self.model.rows if r["source"]]
        self.model.rows.extend(
            r
            for r in sequence.structure_rows(selection, state, _self=self.cmd)
            if r["source"] not in existing
        )
        self.refresh()

    def add_dialog(self):
        selection, ok = QtWidgets.QInputDialog.getText(
            self, "Add structure chains", "Selection:", text="enabled"
        )
        if ok:
            self.action(lambda: self.add_chains(selection, self.form.state.value()))

    def import_dialog(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Import FASTA",
            filter="FASTA (*.fa *.fasta *.faa *.fna *.aln);;All files (*)",
        )
        if filename:

            def load():
                self.model.rows.extend(
                    sequence.read_fasta(Path(filename).read_text(encoding="utf-8-sig"))
                )
                self.refresh()

            self.action(load)

    def export_dialog(self):
        filename, kind = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Export alignment",
            filter="Aligned FASTA (*.fasta);;Statistics (*.csv)",
        )
        if filename:

            def save():
                if "csv" in kind:
                    if not self.model.identities:
                        raise CmdException(
                            "Align the sequences before exporting statistics"
                        )
                    with open(filename, "w", newline="", encoding="utf-8") as handle:
                        writer = csv.writer(handle)
                        writer.writerow(
                            ["sequence", "identity_to_reference", "reference"]
                        )
                        for row, identity in zip(
                            self.model.rows, self.model.identities
                        ):
                            writer.writerow(
                                [
                                    row["label"],
                                    identity,
                                    self.model.rows[self.model.reference]["label"],
                                ]
                            )
                else:
                    Path(filename).write_text(
                        sequence.fasta(self.model.rows), encoding="utf-8"
                    )

            self.action(save)

    def remove(self):
        chosen = set(self.selected_rows())
        reference = self.model.reference
        self.model.rows = [r for i, r in enumerate(self.model.rows) if i not in chosen]
        self.model.reference = (
            0 if reference in chosen else reference - sum(i < reference for i in chosen)
        )
        self.refresh()

    def select(self, *_):
        picks = {}
        for index in self.form.view.selectionModel().selectedIndexes():
            row, col = index.row(), index.column()
            if row < len(self.model.rows) and col < len(self.model.mapping[row]):
                residue = self.model.mapping[row][col]
                if residue:
                    picks.setdefault(row, []).append(residue)
        if picks:
            add = bool(
                QtWidgets.QApplication.keyboardModifiers()
                & Qt.KeyboardModifier.ControlModifier
            )
            sequence.select_residues(
                [(self.model.rows[i], residues) for i, residues in picks.items()],
                add,
                _self=self.cmd,
            )

    def zoom(self):
        self.select()
        if self.cmd.count_atoms("?sele"):
            self.cmd.zoom("sele", 4)

    def copy(self):
        selected = self.form.view.selectionModel().selectedIndexes()
        rows = {}
        for index in selected:
            i, j = index.row(), index.column()
            if i < len(self.model.rows) and j < len(self.model.rows[i]["sequence"]):
                rows.setdefault(i, []).append(j)
        text = "\n".join(
            "".join(self.model.rows[i]["sequence"][j] for j in sorted(cols))
            for i, cols in sorted(rows.items())
        )
        QtWidgets.QApplication.clipboard().setText(
            text or sequence.fasta(self.model.rows)
        )

    def search(self):
        text = self.form.search.text().upper().strip()
        if not text:
            return
        selection = QtCore.QItemSelection()
        for i, row in enumerate(self.model.rows):
            start = row["sequence"].find(text)
            if start >= 0:
                selection.select(
                    self.model.index(i, start),
                    self.model.index(i, start + len(text) - 1),
                )
            for j, residue in enumerate(self.model.mapping[i]):
                if residue and residue[0].upper() == text:
                    selection.select(self.model.index(i, j), self.model.index(i, j))
        self.form.view.selectionModel().select(
            selection, QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect
        )
        if selection.indexes():
            self.form.view.scrollTo(selection.indexes()[0])

    def filter_rows(self, checked):
        chosen = self.selected_rows()
        for row in range(len(self.model.rows)):
            self.form.view.setRowHidden(row, checked and row not in chosen)

    def reference_changed(self, index):
        if index >= 0:
            self.model.reference = index
            self.model.update()
            self.save()

    def coloring_changed(self, index):
        self.model.coloring = index
        self.settings.setValue("sequence/coloring", index)
        self.form.view.viewport().update()

    def secondary_changed(self, checked):
        self.model.secondary = checked
        self.model.update()
        self.form.view.resizeRowsToContents()

    def choose_mafft(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Choose MAFFT executable (mafft or mafft.bat)"
        )
        if filename:
            self.settings.setValue("sequence/mafft", filename)

    def action(self, function):
        try:
            function()
        except (CmdException, OSError, ValueError) as exc:
            self.form.status.setText(str(exc))

    def busy(self, yes):
        for name in (
            "addChains",
            "importFasta",
            "removeRows",
            "alignSequences",
            "fitStructures",
            "reference",
            "assignSS",
            "undo",
        ):
            getattr(self.form, name).setEnabled(not yes)
        self.form.stop.setEnabled(yes)

    def run(self, function, accept):
        if self.worker and self.worker.isRunning():
            return
        self.cancel.clear()
        saved = self._saved
        self.busy(True)
        self.form.status.setText("Working…")

        def finished(result):
            self.busy(False)
            value, error = result
            if (
                self.cancel.is_set()
                or session_extra.entries.get("alignment") is not saved
            ):
                self.form.status.setText(
                    "Stopped; pending results were discarded. Completed structure changes can be undone."
                )
            elif error:
                self.form.status.setText(str(error))
            else:
                accept(value)
                self.form.status.setText(
                    "Done. Identity excludes gaps and unknown residues (X/?/*)."
                )

        self.worker = AsyncFunc(function, finishslot=finished)
        self.worker()

    def align(self):
        indices = self.selected_rows() or list(range(len(self.model.rows)))
        rows = copy.deepcopy([self.model.rows[i] for i in indices])
        executable = self.settings.value("sequence/mafft", "")

        def accept(aligned):
            for i, letters in zip(indices, aligned):
                self.model.rows[i]["sequence"] = letters
            self.refresh()

        self.run(
            lambda: sequence.align_sequences(rows, executable, self.cancel), accept
        )

    def fit(self):
        if not self.model.rows:
            self.form.status.setText("Add at least two structure rows first.")
            return
        indices = sorted(
            set(self.selected_rows() or range(len(self.model.rows)))
            | {self.model.reference}
        )
        rows = copy.deepcopy([self.model.rows[i] for i in indices])
        reference = indices.index(self.model.reference) if indices else 0
        method = self.form.method.currentText()

        def accept(results):
            self.form.results.setPlainText(
                "\n".join(
                    r["label"]
                    + ": "
                    + (
                        r["error"]
                        if "error" in r
                        else f"RMSD {r['rmsd']:.3f} Å, {r['atoms']} aligned atoms"
                    )
                    for r in results
                )
            )

        self.run(
            lambda: sequence.fit_rows(
                rows, reference, method, self.cancel, _self=self.cmd
            ),
            accept,
        )

    def assign_ss(self):
        indices = self.selected_rows() or list(range(len(self.model.rows)))
        rows = copy.deepcopy([self.model.rows[i] for i in indices])

        def accept(updated):
            for i, row in zip(indices, updated):
                self.model.rows[i] = row
            self.refresh()

        self.run(
            lambda: sequence.assign_secondary(rows, self.cancel, _self=self.cmd), accept
        )

    def stop(self):
        self.cancel.set()

    def closeEvent(self, event):
        self.stop()
        self.settings.setValue("sequence/geometry", self.saveGeometry())
        super().closeEvent(event)
