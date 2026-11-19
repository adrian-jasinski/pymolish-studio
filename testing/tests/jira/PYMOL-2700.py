'''
mol2 partial charge export
'''

from pymol import cmd, CmdException, testing, stored


def testMol2PartialChargeExport():
    cmd.fragment('gly')

    charges_pre = []
    cmd.iterate('*', 'charges_pre.append(partial_charge)', space=locals())

    # fragment library has charges, but better check...
    assert sum(abs(c) for c in charges_pre) > 0.0

    with testing.mktemp('.mol2') as filename:
        cmd.save(filename)
        cmd.delete('*')
        cmd.load(filename)

    charges_post = []
    cmd.iterate('*', 'charges_post.append(partial_charge)', space=locals())

    testing.assert_array_equal(charges_pre, charges_post, delta=1e-2)
