'''
Python installation tests
'''

from __future__ import absolute_import

import pytest
import sys
from pymol import testing

required_modules = [
    'Image',
    'numpy',
]

# when building on OSX with system python, some modules are not
# available by default. Only test for them if we build with our
# own python distribution which should ship all these modules.
if (not sys.executable.startswith('/System/Library/Frameworks/Python.framework/Versions/2.7')
        and not testing.PYMOL_EDU
        ):
    required_modules += [
#        'OpenGL', # we don't have it on Windows for PyMOL > 1.7.6
#        'matplotlib',
    ]


def testHasModules():
    failed = []
    for name in required_modules:
        try:
            __import__(name, level=0)
        except ImportError:
            failed.append(name)
    assert failed == []


def testNoCmd():
    # https://github.com/schrodinger/pymol-open-source/issues/18
    pytest.skip("made non-fatal in 2.3.0")

    import pymol
    with pytest.raises(pymol.CmdException):
        import cmd
