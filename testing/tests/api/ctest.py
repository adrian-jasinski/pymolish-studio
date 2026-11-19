import pytest
import pymol
from pymol import cmd, testing


def test2():
    parser = cmd._parser
    try:
        status = pymol._cmd.test2()
    except NotImplementedError:
        pytest.skip("not compiled with --testing")
    assert status in (0, None)
    # the C++ test instances call PInit on this same cmd
    assert cmd._parser is parser
