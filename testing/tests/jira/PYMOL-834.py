'''
PYMOL-834
Invalid list evaluation causes stack trace and function doesn't run

Solution: raise CmdException, which is handled quiet by PyMOL
'''

import pytest
import os
from pymol import cmd, CmdException, testing, stored


def _load_data():
    cmd.fragment('ala', 'm1')
    cmd.map_new('foo_map', 'gaussian', 1.0)


def _ramp_new():
    cmd.ramp_new('foo_ramp', 'foo_map', '[red, white, blue, green]')


def test834():
    '''
        Save a PNG image with width/height specified and
        check if the file exists.
        '''
    _load_data()
    pytest.raises(CmdException, _ramp_new)
