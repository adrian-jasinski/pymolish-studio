from pymol import cmd, testing, stored


def test():
    with testing.timing(max=0.1):
        cmd.fab('AAAA')
