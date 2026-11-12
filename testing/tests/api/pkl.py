"""
Session unpickling: the C fast path returns what the Python unpickler does,
and Python 2 era strings still take the slow path (ASCII -> str, else bytes).
"""

import pickle

from chempy.pkl import cPickle
from pymol import cmd, testing


class TestPkl(testing.PyMOLTestCase):
    def test_loads(self):
        obj = {"name": "abc", "blob": b"\x01\x00\xff", "xs": [1, 2.5, None, "\xe5"]}
        for protocol in (1, 2, 4):
            data = pickle.dumps(obj, protocol)
            self.assertEqual(cPickle.loads(data), obj)
            self.assertEqual(cPickle.loads(data), pickle._loads(data))

        # written the Python 2 way (chempy.pkl patches the Python pickler)
        py2 = pickle._dumps(["abc", b"\x01\x00\xff", b"\x01\x00\x00\x00"], 1)
        self.assertIn(pickle.SHORT_BINSTRING, py2)
        self.assertEqual(
            cPickle.loads(py2), ["abc", b"\x01\x00\xff", b"\x01\x00\x00\x00"]
        )

    def test_legacy_pse_roundtrip(self):
        cmd.fragment("ala")
        with testing.mktemp(".pse") as filename:
            cmd.set("pse_export_version", 1.8)  # Python 2 pickle
            cmd.save(filename)
            cmd.reinitialize()
            cmd.load(filename)
        self.assertEqual(cmd.count_atoms(), 10)
