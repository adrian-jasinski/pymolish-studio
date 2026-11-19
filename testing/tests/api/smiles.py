"""
load_smiles (modules/pymol/smiles.py) and Build > From SMILES. Skipped
without rdkit, except the message that names the extra.
"""

import pytest
import os
import sys
import tempfile
from unittest import mock

from pymol import CmdException, cmd, smiles, testing

try:
    import rdkit  # noqa: F401
except ImportError:
    rdkit = None

needs_rdkit = pytest.mark.skipif(not rdkit, reason="rdkit not installed")


def test_without_rdkit():
    with mock.patch.dict(sys.modules, {"rdkit": None}):
        with pytest.raises(CmdException, match=r"pymolish\[chem\]"):
            cmd.load_smiles("CCO")
    assert "load_smiles" in cmd.keyword


@needs_rdkit
def test_one():
    assert cmd.load_smiles('"CC(=O)O"', "acid") == ["acid"]
    assert cmd.count_atoms("acid") == 8  # with hydrogens
    assert cmd.count_atoms("acid and elem H") == 4
    extent = cmd.get_extent("acid")
    assert extent[1][2] - extent[0][2] > 0.5  # 3D, not flat
    # the same input gives the same coordinates; a used name gets a number
    assert cmd.load_smiles("CC(=O)O", "acid") == ["acid01"]
    assert cmd.rms_cur("acid", "acid01") == pytest.approx(0, abs=5e-4)
    assert cmd.load_smiles("C#N") == ["mol01"]
    pytest.raises(CmdException, cmd.load_smiles, "not a smiles")
    assert len(cmd.get_names()) == 3


@needs_rdkit
def test_conformers():
    cmd.load_smiles("CCCCCCO", "hexanol", 8, "g")
    assert cmd.count_states("hexanol") > 1
    assert cmd.count_states("hexanol") <= 8
    assert cmd.count_atoms("hexanol") == 21  # states, not copies
    assert cmd.get_object_list("g") == ["hexanol"]


@needs_rdkit
def test_file():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "ligands.csv")
        with open(path, "w") as handle:
            handle.write(
                "smiles,name\n# comment\nCCO,ethanol\n\n"
                '"c1ccccc1";"benzene"\nXYZ,bad\nCO\nN\tb\n'
            )
        names = cmd.load_smiles(path, "lig", group="ligands")
    # "b" is a reserved word: PyMOL names the object "b_"
    assert names == ["ethanol", "benzene", "lig", "b_"]
    assert cmd.get_object_list("ligands") == names
    assert cmd.count_atoms("benzene") == 12


@needs_rdkit
def test_menu():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from pymol.Qt import QtWidgets

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    from pmg_qt import file_dialogs

    app.clipboard().setText(" C=O ")
    window = mock.Mock(cmd=cmd)
    asked = {}

    def get_text(parent, title, label, text=""):
        asked["text"] = text
        return "C=C", True

    with mock.patch.object(QtWidgets.QInputDialog, "getText", get_text):
        file_dialogs.build_from_smiles(window)
    assert asked["text"] == "C=O"  # from the clipboard
    assert cmd.count_atoms("mol01") == 6  # ethene, typed
    app.clipboard().setText("two words")
    with mock.patch.object(QtWidgets.QInputDialog, "getText", get_text):
        file_dialogs.build_from_smiles(window)
    assert asked["text"] == ""
