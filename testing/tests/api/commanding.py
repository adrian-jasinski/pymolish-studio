from __future__ import print_function

import os
import subprocess
import sys
import pytest

import pymol
import __main__
from pymol import cmd, testing, stored


def testAlias():
    stored.v = None
    cmd.alias('foo', '/stored.v = 123')
    cmd.do('_ foo', echo=0)
    assert stored.v == 123


@testing.requires('gui', 'no_run_all')
def testCls():
    cmd.set('internal_prompt', 0)
    cmd.set('text', 1)
    cmd.cls()

    # check on black screen
    img = testing.get_imagearray()
    assert not img[...,:3].any()


def testDelete():
    cmd.pseudoatom('m1')
    cmd.pseudoatom('m2')
    cmd.pseudoatom('m3')
    cmd.delete('m1 m2')
    assert cmd.get_names() == ['m3']


def testDeleteStates():
    cmd.pseudoatom('m1', state=10)
    assert cmd.count_states('m1') == 10
    cmd.delete_states('m1', '4-8')
    assert cmd.count_states('m1') == 5


def testDo():
    # tested with other methods
    pass


def testExtend():
    def check(v):
        stored.v = None
        cmd.do('foo', echo=0)
        assert stored.v == v

    cmd.extend('foo', lambda: setattr(stored, 'v', 123))
    check(123)

    @cmd.extend
    def foo():
        stored.v = 456
    check(456)


def testLog():
    with testing.mktemp('.pml') as logfile:
        cmd.log_open(logfile)
        cmd.do('_ color blue')
        cmd.log('hello world')
        cmd.log_close()
        lines = [_f for _f in map(str.strip, open(logfile)) if _f]
        assert lines == ['color blue', 'hello world']


def testLog2():
    """
        Tests robustness of different logging methods:
        1) Python implementation (cmd.log) vs. C implementation (PLog, via cmd.do)
        2) pml vs. py syntax
        3) handling of quoted input (''' broken in 1.8.2)
        """
    testing.ambient_only()
    cmd.viewport(100, 100)
    cmd.fragment('gly')
    cmd.orient()
    cmd.show_as('spheres')

    for ext in ['.pml', '.py']:
        with testing.mktemp(ext) as logfile:
            cmd.log_open(logfile)
            cmd.do('_ color blue')
            cmd.do('/cmd.color("yellow", "elem O")')
            cmd.do('cmd.color("""green""",' " '''elem N''')")
            cmd.log('bg red\n')
            cmd.log('', 'cmd.color(\'magenta\', "hydro")\n')
            cmd.log_close()

            cmd.color('white')
            cmd.bg_color('white')

            if ext == '.pml':
                cmd.do('@' + logfile)
            else:
                cmd.do('run ' + logfile)

            img = testing.get_imagearray()
            testing.assert_image_has_color('blue', img)
            testing.assert_image_has_color('yellow', img)
            testing.assert_image_has_color('green', img)
            testing.assert_image_has_color('red', img)
            testing.assert_image_has_color('magenta', img)
            testing.assert_image_has_not_color('white', img)


def testLogClose():
    # see testLog
    pass


def testLogOpen():
    # see testLog
    pass


def testQuit():
    # a headless script with a Qt application and a live widget: the
    # exit code of quit arrives
    with testing.mktemp('.py') as filename:
        with open(filename, 'w') as handle:
            handle.write(
                'from pymol.Qt import QtWidgets\n'
                'app = QtWidgets.QApplication([])\n'
                'panel = QtWidgets.QDockWidget()\n'
                'cmd.quit(3)\n'
            )
        code = subprocess.call(
            [sys.executable, '-m', 'pymol', '-ckq', filename],
            env=dict(os.environ, QT_QPA_PLATFORM='offscreen'),
        )
    assert code == 3


def testReinitialize():
    def check(v, names):
        assert v == cmd.get('pdb_conect_all')
        assert cmd.get_names() == names

    cmd.pseudoatom('m1')
    v = cmd.set('pdb_conect_all')
    cmd.reinitialize('store_defaults')

    cmd.reinitialize('original_settings')
    check('off', ['m1'])

    cmd.reinitialize('settings')
    check('on', ['m1'])

    cmd.reinitialize('purge_defaults')
    cmd.reinitialize('settings')
    check('off', ['m1'])

    cmd.reinitialize('everything')
    check('off', [])


def testResume():
    with testing.mktemp('.pml') as logfile:
        with open(logfile, 'w') as f:
            print('bg yellow', file=f)
        cmd.resume(logfile)
        assert 'yellow' == cmd.get('bg_rgb')
        cmd.log('hello world')
        cmd.log_close()
        lines = [_f for _f in map(str.strip, open(logfile)) if _f]
        assert lines == ['bg yellow', 'hello world']


def testSplash():
    cmd.feedback('disable', 'all', 'output')
    cmd.splash()


def testSync():
    cmd.sync()


@pytest.mark.parametrize("namespace,mod,rw", [
    ('local', 'pymol', False),
    ('global', 'pymol', True),
    ('module', '', False),
    ('main', '__main__', True),
    ('private', '__main__', False),
])
def testRun(namespace, mod, rw):
    stored.tmp = False
    with testing.mktemp('.py') as filename:
        varname = '_tmp_' + namespace
        with open(filename, 'w') as handle:
            print('from pymol import stored', file=handle)
            if mod:
                print('stored.tmp = (__name__ == "%s")' % (mod), file=handle)
            else:
                print('stored.tmp = True', file=handle)
            print(varname + ' = True', file=handle)
        cmd.do('run %s, %s' % (filename, namespace), 0, 0)
        assert stored.tmp
        if mod:
            assert rw == hasattr(sys.modules[mod], varname)
