"""
load_files and export_objects (modules/pymol/batch.py) and their two File
dialogs, with real forms on an offscreen QApplication.
"""

import pytest
import os
import pathlib
import tempfile

from pymol import CmdException, cmd, testing


@pytest.fixture
def root(clean_session):
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        (root / "sub").mkdir()
        cmd.fragment("ala", "tmp")
        for name in ("b.pdb", "a.pdb", "sub/a.pdb", "other.sdf", "UP.PDB"):
            cmd.save(str(root / name), "tmp")
        cmd.delete("tmp")
        (root / "junk.pdb").write_text("not a structure\n")
        yield root


def test_load_files(root):
    assert "load_files" in cmd.keyword
    assert "export_objects" in cmd.keyword
    names = cmd.load_files(str(root))
    # sorted, junk.pdb skipped; "b" is a reserved word and gets "_"
    assert names == ["UP", "a", "b_"]
    assert cmd.get_names() == names
    # a name in use gets a number, nothing is replaced or appended to
    assert cmd.load_files(str(root), pattern="a") == ["a01"]
    assert cmd.count_states("a") == 1
    cmd.delete("*")
    names = cmd.load_files(str(root), "pdb", "g", "[ab]", 1, "x_")
    assert names == ["x_a", "x_b", "x_sub_a"]
    assert cmd.get_object_list("g") == names
    assert cmd.load_files(str(root), ".SDF") == ["other"]
    pytest.raises(CmdException, cmd.load_files, str(root), "cif")
    pytest.raises(CmdException, cmd.load_files, str(root / "no"))


def test_export_objects(root):
    cmd.load_files(str(root), group="g")
    out = root / "out" / "deep"
    written = cmd.export_objects("g", str(out), "pdb")
    assert sorted(os.listdir(out)) == ["UP.pdb", "a.pdb", "b_.pdb"]
    assert len(written) == 3
    # files that exist are kept unless overwrite=1
    (out / "a.pdb").write_text("mine")
    assert len(cmd.export_objects("g", str(out), "pdb")) == 0
    assert (out / "a.pdb").read_text() == "mine"
    cmd.export_objects("a", str(out), "pdb", overwrite=1)
    assert "ATOM" in (out / "a.pdb").read_text()
    # of each object only the selected atoms; any format "save" knows
    cmd.export_objects("(a or b_) and name CA", str(out), "xyz")
    assert (out / "b_.xyz").read_text().split()[0] == "1"
    assert not (out / "UP.xyz").exists()
    pytest.raises(CmdException, cmd.export_objects, "none", str(out))


def test_dialogs(root):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from pymol.Qt import QtWidgets

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    from pmg_qt import file_dialogs
    from pmg_qt.pymol_qt_gui import PyMOLQtGUI

    class Window(QtWidgets.QWidget):
        load_form = PyMOLQtGUI.load_form
        initialdir = str(root / "sub")

    window = Window()
    window.cmd = cmd
    ok = QtWidgets.QDialogButtonBox.StandardButton.Ok

    form = file_dialogs.file_open_folder(window)
    assert form.output_count.text() == "1 files match"
    form.input_dir.setText(str(root / "missing"))
    assert form.output_count.text() == "Not a folder"
    assert not form.buttons.button(ok).isEnabled()
    form.input_dir.setText(str(root))
    form.input_recursive.setChecked(True)
    form.input_filter.setText("a")
    form.input_group.setText("g")
    assert form.output_count.text() == "2 files match"
    assert form.output_command.text() == "load_files %s, pdb, g, pattern=a, recursive=1" % root
    form.buttons.button(ok).click()
    assert cmd.get_object_list("g") == ["a", "sub_a"]
    assert window.initialdir == str(root)

    form = file_dialogs.file_export_objects(window)
    assert form.input_selection.currentText() == "g"
    assert form.output_count.text() == "2 objects"
    form.input_selection.setEditText("no such thing")
    assert not form.buttons.button(ok).isEnabled()
    form.input_selection.setEditText("sub_*")
    form.input_dir.setText(str(root / "out"))
    form.input_format.setEditText("pdb")
    assert form.output_command.text() == "export_objects sub_*, %s, pdb" % (root / "out")
    form.buttons.button(ok).click()
    assert os.listdir(root / "out") == ["sub_a.pdb"]
    del app
