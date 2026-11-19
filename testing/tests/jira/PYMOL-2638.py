'''
PYMOL-2638
Arbitrary identifier lengths
'''

from random import randint
from pymol import cmd, CmdException, testing, stored

def randhex(e=2):
    return '%x' % randint(1, 10**randint(e, 10))

def next_decorator(iterable):
    iterator = iter(iterable)
    try:
        return iterator.next
    except AttributeError:
        return iterator.__next__


def test2638():
    cmd.set('retain_order')
    cmd.fragment('ala', 'm1')
    n = cmd.count_atoms()

    ##
    ## Make long identifiers
    ##

    chain = [randhex()] * n
    resn = [randhex()] * n
    resv = [randint(10**4, 10**6 - 1)] * n
    names = [randhex(4) + str(i) for i in range(n)]

    identif_str = '(chain, resn, resv, name)'
    identifiers = list(zip(chain, resn, resv, names))
    afterload = []

    cmd.alter('m1', identif_str + ' = _next()',
            space={'_next': next_decorator(identifiers)})

    ##
    ## Test if cif in/out preserves identifiers
    ##

    with testing.mktemp('.cif') as filename:
        cmd.save(filename, 'm1')
        cmd.load(filename, 'm2')

    cmd.iterate('m2', '_afterload.append(' + identif_str + ')',
            space={'_afterload': afterload})

    assert identifiers == afterload

    ##
    ## Test if various formats preserve coordinates
    ##

    coords = cmd.get_coordset('m1')

    for ext in ['.pdb', '.xyz', '.mol2', '.sdf']:
        cmd.delete('m2')

        with testing.mktemp(ext) as filename:
            cmd.save(filename, 'm1')
            cmd.load(filename, 'm2')

        testing.assert_array_equal(coords, cmd.get_coordset('m2'), delta=1e-3,
                msg='not preserving coordinates: ' + ext)
