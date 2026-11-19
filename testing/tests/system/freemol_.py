'''
FreeMOL tests
'''

from pymol import testing

pytestmark = testing.requires('freemol')


def testValidate():
    import freemol.apbs
    import freemol.mengine
    import freemol.mpeg_encode

    # psize.py not used with PyMOL 2.0
    freemol.apbs._psize_py = '<ignore>'

    assert freemol.apbs.validate()
    assert freemol.mengine.validate()
    assert freemol.mpeg_encode.validate()
