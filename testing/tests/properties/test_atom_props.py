
'''
Testing atom properties for simple getting/setting and loading from sdf files
'''

from pymol import cmd, testing, stored


def testSetNoAtomProperty():
    try:
        cmd.set_atom_property('test_prop', 1, "index 1")
    except:
        assert False == True
        pass


def testDel():
    cmd.pseudoatom('m1')

    stored.keys = []
    cmd.alter('all', 'p.foo = 123')
    cmd.alter('all', 'p.bar = "Hello World"')
    cmd.iterate('all', 'stored.keys = list(sorted(p.all))')
    assert stored.keys == ['bar', 'foo']

    stored.keys = []
    cmd.alter('all', "del p['foo']")
    cmd.iterate('all', 'stored.keys = list(sorted(p.all))')
    assert stored.keys == ['bar']

    stored.keys = []
    cmd.alter('all', "p.bar = None")
    cmd.iterate('all', 'stored.keys = list(sorted(p.all))')
    assert stored.keys == []

    # object-level
    cmd.set_property('bla', 456, 'm1')
    stored.keys = cmd.get_property_list('m1')
    assert stored.keys == ['bla']
    cmd.set_property('bla', None, 'm1')
    stored.keys = cmd.get_property_list('m1')
    assert stored.keys == []


def testNonAsciiSessionRoundTrip():
    # property names/values were truncated: buffers were sized by
    # code points instead of UTF-8 bytes (github #517)
    name = "名前"
    value = "测试消息" * 4
    cmd.pseudoatom('m1')
    cmd.alter('m1', 'p[%r] = %r' % (name, value))
    with testing.mktemp('.pse') as psefilename:
        cmd.save(psefilename)
        cmd.delete('all')
        cmd.load(psefilename)
    stored.val = None
    cmd.iterate('m1', 'stored.val = p[%r]' % name)
    assert stored.val == value
