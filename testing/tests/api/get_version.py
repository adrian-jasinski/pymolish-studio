'''
Testing template for PyMOL testing
'''

from pymol import cmd, testing


def _get_num(x):
    retlist = []
    for ele in x:
        if ele.isdigit() or ele == '.':
            retlist.append(ele)
        else:
            break
    return ''.join(retlist)


def test_version():
    v = cmd.get_version()[:3]
    # check types
    assert isinstance(v[0], str)
    assert isinstance(v[1], float)
    assert isinstance(v[2], int)
    # check that major of str and float match
    assert int(v[0].split('.')[0]) == int(v[1])
