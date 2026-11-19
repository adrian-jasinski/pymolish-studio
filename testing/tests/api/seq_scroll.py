"""
The scroll state of the sequence viewer that the window's scroll bar reads
and sets (pmg_qt/pymol_gl_widget.py). Without a window there are no rows on
screen: the query answers None and setting an offset does nothing.
"""

import pytest
from pymol import cmd, testing


def test_headless():
    cmd.fab("A" * 300, "m")
    cmd.set("seq_view", 1)
    assert cmd._cmd.seq_scroll(cmd._COb, -1) is None
    assert cmd._cmd.seq_scroll(cmd._COb, 50) is None
    pytest.raises(TypeError, cmd._cmd.seq_scroll, cmd._COb)
