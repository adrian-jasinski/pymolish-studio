'''
PYMOL-2668
crash with cylinder shader and dist dash < 1.0 Angstrom
'''

from pymol import cmd, CmdException, testing, stored


@testing.requires('gui')
def test2668():
    cmd.pseudoatom('m1', pos=(-.4, 0, 0))
    cmd.pseudoatom('m2', pos=( .4, 0, 0))
    cmd.distance('d0', 'm1', 'm2')
    cmd.draw()
