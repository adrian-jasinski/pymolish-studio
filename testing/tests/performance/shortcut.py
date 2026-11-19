import pymol
from pymol import cmd, testing, stored


@testing.requires('no_run_all')
def testShortcutTiming():
    names = pymol.setting.get_name_list()
    colors = [c[0] for c in cmd.get_color_indices(0)]

    with testing.timing():
        sc = cmd.Shortcut(names)
        sc = cmd.Shortcut(cmd.kw_list)
        sc = cmd.Shortcut(colors)
