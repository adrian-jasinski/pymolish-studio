'''
Plugin contract without a GUI: discovery in a startup directory, import as
pymol.plugins.startup.<name>, __init_plugin__(None) (menu calls do nothing),
and cmd.extend registration tracking. With a window: rows and submenus of
the one Plugin menu.
'''

import pytest
import os
import shutil
import tempfile

from pymol import cmd, plugins, testing

PLUGIN = '''
from pymol import cmd, plugins

def __init_plugin__(app=None):
    plugins.addmenuitem('Test Plugin|Hello', lambda: None)
    cmd.extend('_pymolish_testplugin_hello', lambda: 'hello')
'''


def test_headless_plugin_load():
    tmp = tempfile.mkdtemp()
    orig = plugins.get_startup_path(True)
    try:
        with open(os.path.join(tmp, 'pymolish_testplugin.py'), 'w') as f:
            f.write(PLUGIN)
        plugins.set_startup_path([tmp], autosave=False)

        found = plugins.findPlugins([tmp])
        assert 'pymolish_testplugin' in found

        info = plugins.PluginInfo('pymolish_testplugin',
                                  found['pymolish_testplugin'],
                                  'pymol.plugins.startup.pymolish_testplugin')
        assert info.load()
        assert info.loaded
        assert '_pymolish_testplugin_hello' in info.commands
        assert cmd.keyword['_pymolish_testplugin_hello'][0]() == 'hello'
    finally:
        plugins.set_startup_path(orig, autosave=False)
        shutil.rmtree(tmp)


def test_addmenuitem(request):
    from unittest import mock

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import shiboken6
    from pymol.Qt import QtWidgets

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    pytest.raises(plugins.QtNotAvailableError, plugins.addmenuitemqt, 'x')
    menu = QtWidgets.QMenu()
    request.addfinalizer(lambda: shiboken6.delete(menu))
    window = mock.Mock(menudict={'Plugin': menu})
    hits = []
    with mock.patch.object(plugins, 'HAVE_QT', True), \
                mock.patch('pymol.gui.get_qtwindow', return_value=window):
        plugins.addmenuitemqt('Test|One', lambda: hits.append(1))
        # the menu name of the time when legacy plugins had their own
        plugins.addmenuitem('Test|Two', lambda: hits.append(2), 'PluginQt')
        plugins.addmenuitem('-')
        plugins.addmenuitem('Flat', lambda: hits.append(3))
    assert [a.text() for a in menu.actions()] == ['Test', '', 'Flat']
    sub = menu.actions()[0].menu()  # one submenu, not one per row
    assert [a.text() for a in sub.actions()] == ['One', 'Two']
    sub.actions()[1].trigger()
    menu.actions()[2].trigger()
    assert hits == [2, 3]
    # no Tk stand-ins are left
    assert not hasattr(plugins, 'get_pmgapp')
    import importlib.util
    assert importlib.util.find_spec('pmg_qt.mimic_tk') is None
