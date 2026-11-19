'''
Crash with names selection of length >= 1024
'''

from pymol import cmd, util, testing, stored


def test():
    for i in range(100):
        cmd.pseudoatom('xxxxxxxxxx%04d' % i)

    setting = 'sphere_color'
    color = 'blue'
    name = 'xxxxxxxxxx0005'
    cmd.set(setting, color, name)
    assert cmd.get(setting, name) == color

    # crashes in 1.7.6.0 to 1.7.6.6
    util.color_deep('red', 'all')

    assert cmd.get(setting, name) == 'default'
