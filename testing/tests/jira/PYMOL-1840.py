from pymol import cmd, testing, stored


def testSdfV3000():
    cmd.load(testing.datafile('1rx1.pdb'))
    with testing.mktemp('.sdf') as filename:
        cmd.save(filename)
        cmd.delete('*')
        cmd.load(filename)
    assert cmd.count_atoms() == 1435

    # check for capitalized element symbols
    cmd.set('ignore_case', 0)
    assert cmd.count_atoms('elem Ca') == 1
