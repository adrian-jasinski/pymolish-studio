from __future__ import absolute_import

from pymol import testing, invocation


def testDo():
    import pymol
    import pymol2
    p3 = pymol # singleton
    with pymol2.PyMOL() as p1:
        p3.cmd.do("viewport 100, 200")
        p1.cmd.do("viewport 300, 400")
        assert p3.cmd.get_viewport() == (100, 200)  # singleton
        assert p1.cmd.get_viewport() == (300, 400)


def testMultiInstance():
    import pymol
    import pymol2

    p1 = pymol2.PyMOL()
    p2 = pymol2.PyMOL()
    p3 = pymol # singleton

    p1.start()
    p2.start()

    p1.cmd.fragment('ala')
    p2.cmd.fragment('trp')
    p3.cmd.fragment('ile') # singleton

    assert p1.cmd.count_atoms() == 10
    assert p2.cmd.count_atoms() == 24
    assert p3.cmd.count_atoms() == 19 # singleton

    p1.stop()
    p2.stop()


def testDel():
    import pymol2
    import weakref

    p1 = pymol2.PyMOL()
    p1.start()
    p1.cmd.fragment('ala')

    # involve pymol._colortype (holds a bound method)
    _test_colortype(p1.cmd)

    p1.stop()

    weak_p = weakref.ref(p1)
    weak_c = weakref.ref(p1.cmd)

    del p1

    assert None == weak_p()
    assert None == weak_c()


def _test_colortype(_self):
    colorset = set()
    _self.set('sphere_color', 'blue', '(*)')
    _self.iterate('*', 'colorset.add(('
            'tuple(s.sphere_color),'
            'int(s.sphere_color)))',
            space={'colorset': colorset, 'tuple': tuple, 'int': int})
    assert list(colorset) == [((0., 0., 1.), 2)]
