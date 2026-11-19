'''
some elements assigned wrong from SDF and XYZ files
'''

import pytest
import os
from pymol import cmd, CmdException, testing, stored


@pytest.mark.parametrize("ext", ['mol', 'xyz'])
def test(ext):
    cmd.load(testing.datafile('elements.' + ext))
    for elem in 'Ne Si Cd Sn Ce Nd Sm Dy Ho Hf Hg Np Cm Cf No Db Sg Hs Ds Cn'.split():
        assert cmd.count_atoms('elem ' + elem) == 1, elem
