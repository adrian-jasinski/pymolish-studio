'''
Object visibility with hidden parent in scenes
'''

import os
from pymol import cmd, CmdException, testing, stored


def test():
    cmd.pseudoatom('m1')
    cmd.pseudoatom('m2')
    cmd.pseudoatom('m3')
    cmd.group('g1', 'm1')
    cmd.disable('g1')
    cmd.disable('m2')
    cmd.ray(1, 1)  # force scene update
    cmd.scene('s1', 'store')

    _test_recall()
    cmd.disable('*')
    _test_recall()
    cmd.enable('*')
    _test_recall()


def _test_recall():
    cmd.scene('s1', 'recall')
    cmd.ray(1, 1)  # force scene update
    assert ['m3'] == cmd.get_object_list('(visible)')
    assert ['m3'] == cmd.get_object_list('(enabled)')
    cmd.enable('g1')
    cmd.ray(1, 1)  # force scene update
    assert ['m1', 'm3'] == cmd.get_object_list('(visible)')
    assert ['m1', 'm3'] == cmd.get_object_list('(enabled)')
