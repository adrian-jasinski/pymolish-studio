'''
MAE export chain=" "
'''

from pymol import cmd, testing

pytestmark = testing.requires('incentive')


def _test(literal):
    cmd.fragment('ala')
    cmd.alter('all', 'chain=" "') # space
    cmd.alter('index 1', 'chain=""') # empty
    cmd.alter('index 2', "chain='\"'") # quote
    cmd.alter('elem O', "name='O\"'") # quote
    with testing.mktemp('.mae') as filename:
        cmd.save(filename)
        cmd.delete('*')

        if literal:
            cmd.set('pdb_literal_names')
            strip = lambda s: s
        else:
            strip = str.strip

        cmd.load(filename)
        assert 10 == cmd.count_atoms()

        atomnames = []
        cmd.iterate('all', 'atomnames.append(name)', space=locals())
        assert strip(' O" ') in atomnames
        assert strip(' N  ') in atomnames
        assert strip('1HB ') in atomnames


def test():
    _test(False)


def test_literal():
    _test(True)
