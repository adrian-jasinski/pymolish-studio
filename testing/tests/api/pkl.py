"""
Session unpickling: the C fast path returns what the Python unpickler does,
and Python 2 era strings still take the slow path (ASCII -> str, else bytes).
"""

import pickle

from chempy.pkl import cPickle
from pymol import cmd, testing


def test_loads():
    obj = {"name": "abc", "blob": b"\x01\x00\xff", "xs": [1, 2.5, None, "\xe5"]}
    for protocol in (1, 2, 4):
        data = pickle.dumps(obj, protocol)
        assert cPickle.loads(data) == obj
        assert cPickle.loads(data) == pickle._loads(data)

    # written the Python 2 way (chempy.pkl patches the Python pickler)
    py2 = pickle._dumps(["abc", b"\x01\x00\xff", b"\x01\x00\x00\x00"], 1)
    assert pickle.SHORT_BINSTRING in py2
    assert cPickle.loads(py2) == ["abc", b"\x01\x00\xff", b"\x01\x00\x00\x00"]


def test_legacy_pse_roundtrip():
    cmd.fragment("ala")
    with testing.mktemp(".pse") as filename:
        cmd.set("pse_export_version", 1.8)  # Python 2 pickle
        cmd.save(filename)
        cmd.reinitialize()
        cmd.load(filename)
    assert cmd.count_atoms() == 10
