import sys
from io import StringIO
from unittest.mock import patch
from pymol import cmd, testing, stored


def func_with_indented_help():
    '''
    USAGE

        foo

    SEE ALSO

        https://github.com/schrodinger/pymol-open-source/issues/116
    '''


cmd.extend('func_with_indented_help', func_with_indented_help)


def testApi():
    with patch('sys.stdout', new=StringIO()) as out:
        cmd.api("color")
        assert 'API: pymol.viewing.color' in out.getvalue()


def testHelp():
    with patch('sys.stdout', new=StringIO()) as out:
        cmd.help('color')
        assert 'USAGE\n\n    color color' in out.getvalue()


def testHelp_dedent():
    with patch('sys.stdout', new=StringIO()) as out:
        cmd.help('func_with_indented_help')
        assert 'USAGE\n\n    foo\n\nSEE' in out.getvalue()
