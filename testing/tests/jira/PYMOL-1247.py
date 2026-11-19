'''
PYMOL-1247 commands with LITERAL parsing mode and leading whitespace fail
'''

import pytest
from pymol import cmd, testing, stored, parsing

def myfunc(a='adefault', b='bdefault'):
    stored.v = (a, b)


@pytest.mark.parametrize("mode", ['STRICT', 'LITERAL2'])
def testLeadingSpace(mode):
    cmd.keyword['myfunc'] = [myfunc, 0, 0, '', getattr(parsing, mode)]
    cmd.do(' myfunc x', 0, 0, 1)
    assert stored.v == ('x', 'bdefault')
