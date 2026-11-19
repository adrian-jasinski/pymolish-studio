'''
Testing selection by properties
'''

from pymol import cmd, testing


def testNumeric():
    cmd.fragment('ala')
    cmd.alter_state(1, 'all', 'p.x, p.y, p.index = x, y, index')
    cmd.select('sele_p_x', 'p.x < 0')
    cmd.select('sele_p_y', 'p.y > 0')
    cmd.select('sele_p_i', 'p.index = 3')
    cmd.select('sele_x', 'x < 0.0')
    cmd.select('sele_y', 'y > 0.0')
    cmd.select('sele_i', 'index 3')
    counts = [
        cmd.count_atoms('sele_p_x'),
        cmd.count_atoms('sele_x'),
        cmd.count_atoms('sele_x & sele_p_x'),
    ]
    assert counts[0] == 8
    assert counts[0] == counts[1]
    assert counts[0] == counts[2]
    counts = [
        cmd.count_atoms('sele_p_y'),
        cmd.count_atoms('sele_y'),
        cmd.count_atoms('sele_y & sele_p_y'),
    ]
    assert counts[0] == 6
    assert counts[0] == counts[1]
    assert counts[0] == counts[2]
    counts = [
        cmd.count_atoms('sele_i'),
        cmd.count_atoms('sele_p_i'),
        cmd.count_atoms('sele_i & sele_p_i'),
    ]
    assert counts[0] == 1
    assert counts[0] == counts[1]
    assert counts[0] == counts[2]


def testString():
    cmd.fragment('ala')
    cmd.alter('all', 'p.name = name')
    cmd.select('sele_p_x', 'p.name in C+N+O')
    cmd.select('sele_x', 'name C+N+O')
    counts = [
        cmd.count_atoms('sele_p_x'),
        cmd.count_atoms('sele_x'),
        cmd.count_atoms('sele_x & sele_p_x'),
    ]
    assert counts[0] == 3
    assert counts[0] == counts[1]
    assert counts[0] == counts[2]


def testCast():
    cmd.fragment('ala')
    cmd.alter('all', 'p.s, p.index = "10e0", index')
    cmd.alter('index 2+3', 'p.s = "30e0"')
    cmd.select('sele_p_s', 'p.s > 20')
    cmd.select('sele_p_i', 'p.index in 2+3')
    counts = [
        cmd.count_atoms('sele_p_s'),
        cmd.count_atoms('sele_p_i'),
    ]
    assert counts[0] == 2
    assert counts[1] == 2
