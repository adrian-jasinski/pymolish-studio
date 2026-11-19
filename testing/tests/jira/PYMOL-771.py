'''
Regression test for PYMOL-771
group_auto_mode setting is not applied when loading a maestro structure file
'''

from pymol import cmd, testing

pytestmark = testing.requires('incentive')


def testMAEName():
    import gzip
    from epymol import mae

    name = 'a.b.c'
    filename = 'PYMOL-771-example.mae.gz'
    contents = gzip.open(filename).read()

    mae.read_maestr(contents, name)

    v = cmd.get_object_list()
    assert v == [name]
