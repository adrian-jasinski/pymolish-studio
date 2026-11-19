'''
Regression test for PYMOL-772
partial load of PSE file duplicates groups with identical name 
'''

import pytest
from pymol import cmd, testing


v_ref = ['m1', 'm2', 'g1']


def _load_session_twice():
    cmd.load('PYMOL-772-example.pse.gz', partial=1)
    cmd.load('PYMOL-772-example.pse.gz', partial=1)


def testDoNotDuplicateGroup():
    cmd.pseudoatom('m3')
    cmd.group('g1', 'm3')
    cmd.load('PYMOL-772-example.pse.gz', partial=1)

    v = cmd.get_names()
    assert v == ['m3', 'g1', 'm1', 'm2']


@pytest.mark.skip(reason="alter not implemented yet")
def testAppend():
    cmd.set('auto_rename_duplicate_objects', 0)

    _load_session_twice()

    v = cmd.get_names()
    assert v == v_ref


def testRename():
    cmd.set('auto_rename_duplicate_objects', 1)

    _load_session_twice()

    v = cmd.get_names()
    expected = v_ref + [n + '_2' for n in v_ref
            if not n.startswith('g')]
    assert v == expected

# vi:nowrap
