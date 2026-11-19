'''
PYMOL-1232
Cannot load session file after "wizard message"
'''

from pymol import cmd, CmdException, testing, stored


def test1232():
    with testing.mktemp('.pse') as filename:
        cmd.save(filename)
        cmd.wizard('message', 'foo')
        cmd.load(filename)
