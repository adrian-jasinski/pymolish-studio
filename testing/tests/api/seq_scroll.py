"""
The scroll state of the sequence viewer that the window's scroll bar reads
and sets (pmg_qt/pymol_gl_widget.py). Without a window there are no rows on
screen: the query answers None and setting an offset does nothing.
"""

from pymol import cmd, testing


class TestSeqScroll(testing.PyMOLTestCase):
    def test_headless(self):
        cmd.fab("A" * 300, "m")
        cmd.set("seq_view", 1)
        self.assertIsNone(cmd._cmd.seq_scroll(cmd._COb, -1))
        self.assertIsNone(cmd._cmd.seq_scroll(cmd._COb, 50))
        self.assertRaises(TypeError, cmd._cmd.seq_scroll, cmd._COb)
