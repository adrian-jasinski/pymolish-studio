"""Sequence alignment, stable residue mapping, fitting and the Qt window."""

import copy
import os
import shutil
import subprocess
import sys
import threading
import time

import numpy as np
import pytest
from pymol import CmdException, cmd, sequence, session_extra, snapshots, testing


def test_fasta_and_statistics():
    rows = sequence.read_fasta(
        ">reference\na-cx?*\n>second\nAT-T?*\n>unknown\nXXX???\n"
    )
    assert sequence.read_fasta(sequence.fasta(rows)) == rows
    consensus, conservation, identity = sequence.statistics(rows)
    assert consensus == "ATCT--"
    assert conservation == [1, 1, 1, 1, 0, 0]
    assert identity == [1, 1, None]
    for text in ("", "ACGT", ">\nACGT", ">empty", ">bad\nAC1", ">gaps\n---"):
        with pytest.raises(CmdException):
            sequence.read_fasta(text)
    bad = copy.deepcopy(rows)
    bad[0]["source"] = ["m", "", "A", 1]
    with pytest.raises(ValueError):
        sequence.validate_rows(bad)


def test_mapping_and_deleted_objects():
    cmd.fab("AGST", "m_first")
    cmd.alter("m_first and resi 2", "resi='2A'")
    cmd.alter("m_first", "chain='A'; segi='S'")
    cmd.create("second", "m_first")
    cmd.create("states", "m_first", 1, 1)
    cmd.create("states", "m_first", 1, 2)
    cmd.translate([0, 5, 0], "states", state=2)
    rows = sequence.structure_rows("m_first or second")
    assert len(rows) == 2
    row = rows[0]
    row["sequence"] = "A-GST"
    sequence.validate_rows(rows)
    assert sequence.aligned_residues(row)[1] is None
    assert row["residues"][1][0] == "2A"
    sequence.select_residues([(row, [row["residues"][1]])])
    assert cmd.count_atoms("sele") == cmd.count_atoms("m_first and resi 2A")
    assert not cmd.count_atoms("sele and second")
    # Remove an earlier residue: saved atom indices would now be wrong.
    cmd.remove("m_first and resi 1")
    sequence.select_residues([(row, [row["residues"][1]])])
    assert cmd.count_atoms("sele and resi 2A") == cmd.count_atoms("sele") > 0
    assert sequence.structure_rows("states", 2)[0]["source"][3] == 2
    cmd.delete("m_first")
    assert sequence.atom_indices(row, row["residues"]) == []
    sequence.select_residues([(row, row["residues"])])
    assert cmd.count_atoms("?sele") == 0


def test_structure_fitting_and_undo():
    cmd.fab("ACDEFGHIKLMNPQRSTVWY", "reference")
    cmd.create("mobile", "reference")
    cmd.rotate("z", 35, "mobile")
    cmd.translate([3, -2, 7], "mobile")
    fixed = cmd.get_coords("reference").copy()
    before = cmd.get_coords("mobile").copy()
    rows = sequence.structure_rows("reference or mobile")
    reference = next(i for i, row in enumerate(rows) if row["source"][0] == "reference")
    snapshots._undo.clear()
    results = sequence.fit_rows(rows, reference)
    assert len(results) == 1 and results[0]["rmsd"] < 1e-3
    assert results[0]["atoms"] > 15
    np.testing.assert_allclose(cmd.get_coords("reference"), fixed)
    np.testing.assert_allclose(cmd.get_coords("mobile"), fixed, atol=1e-4)
    assert len(snapshots._undo) == 1
    snapshots.step(True, cmd)
    np.testing.assert_allclose(cmd.get_coords("mobile"), before, atol=1e-4)
    with pytest.raises(CmdException, match="one chain/state"):
        sequence.fit_rows([rows[0], rows[0]])
    with pytest.raises(CmdException, match="structure rows"):
        sequence.fit_rows(rows + sequence.read_fasta(">FASTA\nACD"))


def test_real_mafft(tmp_path):
    executable = os.environ.get("PYMOLISH_TEST_MAFFT") or shutil.which("mafft")
    if not executable:
        pytest.skip(
            "MAFFT is optional; set PYMOLISH_TEST_MAFFT to test a local installation"
        )
    cmd.fab("ACDEFGHIKLMNPQRSTVWY", "protein")
    coordinates = cmd.get_coords().copy()
    rows = sequence.structure_rows("protein") + sequence.read_fasta(
        ">deletion\nACDEFGHIKMNPQRSTVWY\n>substitution\nACDEFGHIKLMNPQKSTVWY\n"
    )
    aligned = sequence.align_sequences(rows, executable)
    # MAFFT --auto fixture: the missing L belongs after K, before M.
    assert aligned == [
        "ACDEFGHIKLMNPQRSTVWY",
        "ACDEFGHIK-MNPQRSTVWY",
        "ACDEFGHIKLMNPQKSTVWY",
    ]
    np.testing.assert_array_equal(cmd.get_coords(), coordinates)
    source, target = tmp_path / "sequences.fasta", tmp_path / "aligned.fasta"
    source.write_text(sequence.fasta(rows))
    result = cmd.sequence_align(str(source), str(target), executable)
    assert target.read_text() == result
    assert [r["sequence"] for r in sequence.read_fasta(result)] == aligned


def test_backend_failure_cancel_and_invalid_output(tmp_path, monkeypatch):
    program = tmp_path / "backend.py"
    original = subprocess.Popen
    monkeypatch.setattr(
        sequence.subprocess,
        "Popen",
        lambda args, **kw: original(
            [sys.executable, str(program), *args[1:]]
            if args[0] == "test-backend"
            else args,
            **kw,
        ),
    )
    rows = sequence.read_fasta(">a\nACDE\n>b\nACDF")
    program.write_text(
        "import sys\nprint('backend failed', file=sys.stderr)\nsys.exit(2)\n"
    )
    with pytest.raises(CmdException, match="backend failed"):
        sequence.align_sequences(rows, "test-backend")
    program.write_text("print('>row0\\nACDE\\n>row1\\nAAAA')\n")
    with pytest.raises(CmdException, match="changed the input"):
        sequence.align_sequences(rows, "test-backend")
    program.write_text("import time\ntime.sleep(60)\n")
    cancel = threading.Event()
    timer = threading.Timer(0.3, cancel.set)
    timer.start()
    started = time.monotonic()
    try:
        with pytest.raises(CmdException, match="cancelled"):
            sequence.align_sequences(rows, "test-backend", cancel)
    finally:
        timer.cancel()
    assert time.monotonic() - started < 5


@pytest.fixture
def panel():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from pmg_qt.sequence_panel import SequencePanel
    from pymol.Qt import QtWidgets

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    window = SequencePanel(cmd)
    window.open()
    yield app, window
    window.stop()
    if window.worker:
        window.worker.wait(5000)
    window.close()
    app.processEvents()


def test_window_selection_restore_and_resize(panel):
    from pymol.Qt import QtCore

    app, window = panel
    cmd.fab("AGST", "peptide")
    window.add_chains()
    window.model.rows += sequence.read_fasta(">FASTA\nA-ST")
    window.refresh()
    window.form.view.selectionModel().select(
        window.model.index(0, 1),
        QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect,
    )
    assert cmd.count_atoms("sele and resi 2") == cmd.count_atoms("sele") > 0
    window.poll()
    assert (
        window.model.data(
            window.model.index(0, 1), QtCore.Qt.ItemDataRole.BackgroundRole
        )
        is not None
    )
    assert window.model.data(window.model.index(1, 1)) == "-"
    saved = cmd.get_session()
    window.model.rows.clear()
    window.refresh()
    cmd.set_session(saved)
    window.poll()
    assert len(window.model.rows) == 2
    assert window.model.rows[1]["source"] is None
    cmd.delete("peptide")
    window.poll()
    assert "unmapped" in window.model.headerData(0, QtCore.Qt.Orientation.Vertical)
    for width, height in ((800, 450), (1200, 700)):
        window.resize(width, height)
        app.processEvents()
        assert window.form.view.viewport().width() > 0
    window.close()
    window.open()
    assert len(window.model.rows) == 2
    session_extra.entries["alignment"] = {"rows": [{"sequence": "BAD"}]}
    window.poll()
    assert not window.model.rows


def test_late_worker_result_is_discarded(panel):
    from PySide6.QtTest import QTest

    app, window = panel
    window.model.rows = sequence.read_fasta(">a\nACD\n>b\nACD")
    window.refresh()
    accepted = []
    window.run(lambda: (time.sleep(0.1), "result")[1], accepted.append)
    session_extra.entries["alignment"] = {"rows": [], "reference": 0}
    window.poll()
    while window.worker.isRunning():
        QTest.qWait(20)
    app.processEvents()
    assert not accepted and not window.model.rows
    # A non-native job must not leave the core's asynchronous interrupt set.
    cmd.load(testing.datafile("1oky-frag.pdb"), "after_cancel")
    assert cmd.count_atoms("after_cancel") > 0


def test_ss_track_and_colors(panel):
    from pmg_qt import sequence_panel as sp
    from pymol.Qt import QtCore

    # the consensus track: most rows' H/S per column, numbered elements
    H, S, L = (("1", "A", c) for c in "HSL")
    mapping = [[H, H, None, S, S, L], [H, L, L, S, S, None], [L, H, L, S, L, L]]
    track = sp.ss_track(mapping)
    assert track == "HH SS "
    elements = sp.ss_elements(track)
    assert elements[1] == ("H", 0, 1, 1) and elements[4] == ("S", 3, 4, 2)
    assert elements[2] == (" ", 2, 2, 0)

    _, window = panel
    Role = QtCore.Qt.ItemDataRole
    window.model.rows = sequence.read_fasta(">a\nAKD\n>b\nAKE")
    window.refresh()
    # FASTA rows have no structure: no track
    assert window.model.rowCount() == 3 and window.model.track_row == -1
    window.model.mapping = [[H, H, S]] * 2
    window.model.elements = sp.ss_elements(sp.ss_track(window.model.mapping))
    window.model.track_row = 3
    assert window.model.headerData(3, QtCore.Qt.Orientation.Vertical) == (
        "Secondary structure"
    )
    assert window.model.data(window.model.index(3, 2), sp.SS_ROLE)[0] == "S"
    assert "Helix 1" in window.model.data(window.model.index(3, 0), Role.ToolTipRole)

    # colors: none by default, Zappo, hydrophobicity, identity to consensus
    def background(row, column):
        value = window.model.data(window.model.index(row, column), Role.BackgroundRole)
        return value and value.name()

    window.form.coloring.setCurrentIndex(0)
    assert background(0, 0) is None
    window.form.coloring.setCurrentIndex(1)
    assert background(0, 1) == "#6464ff" and background(0, 2) == "#ff0000"
    window.form.coloring.setCurrentIndex(2)
    assert background(0, 0) != background(0, 1)  # A hydrophobic, K not
    window.form.coloring.setCurrentIndex(3)
    assert background(0, 0) == "#6464ff"  # A in both rows
    # D and E half each: D is the consensus, at 50 %; E does not match it
    assert background(0, 2) == "#ccccff" and background(1, 2) is None
    window.form.coloring.setCurrentIndex(0)
