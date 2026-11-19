'''
bg_image_filename in session files
'''

import shutil
import os
from pymol import cmd, testing

pytestmark = testing.requires('incentive', 'gui')


def test():
    cmd.set('opaque_background')
    with testing.mktemp('tmp.pse') as session_filename:
        with testing.mktemp('bg.png') as bg_image_filename:
            cmd.bg_color('red')
            cmd.png(bg_image_filename)
            cmd.bg_color('blue')
            cmd.set('bg_image_filename', bg_image_filename)
            cmd.save(session_filename)

        cmd.load(session_filename)
    x = cmd.get('bg_image_filename')
    assert x.startswith('data:')
    testing.assert_image_has_color('red', delta=4,
            msg='bg_image_filename=data: not rendered')

