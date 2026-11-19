'''
selection macros
'''

import pytest
from pymol import cmd, CmdException, testing, stored


def testSeleMacro():
    cmd.fab('GGGGG',  'foo-bar-com')
    cmd.fragment('gly', 'foo-com-bar')

    assert cmd.count_atoms('/foo-bar-com')
    assert cmd.count_atoms('/foo-bar-com////c*')
    assert cmd.count_atoms('/foo-bar/')
    assert cmd.count_atoms('/foo-bar*/')
    assert cmd.count_atoms('/foo*/')
    assert cmd.count_atoms('/foo-bar-com///2:4/ca') == 3
    assert cmd.count_atoms('/foo-bar-com///2-4/ca') == 3
    assert cmd.count_atoms('foo-bar-com////')

    # test ambiguous prefix
    pytest.raises(CmdException, lambda: cmd.count_atoms('/foo/'))
