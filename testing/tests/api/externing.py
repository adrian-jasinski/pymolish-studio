import pytest
import os
import sys
from pymol import cmd, testing, stored

def touch(filename):
    open(filename, 'ab').close()


def testCdLsPwd():
    with testing.mkdtemp() as path:
        cmd.cd(path)
        if sys.platform == 'win32':
            import ctypes
            def get_long_path_name(path):
                buf = ctypes.create_unicode_buffer(260)
                ctypes.windll.kernel32.GetLongPathNameW(path, buf, len(buf))
                return buf.value
            assert get_long_path_name(os.getcwd()) == get_long_path_name(os.path.realpath(path))
        else:
            assert os.getcwd() == os.path.realpath(path)

        touch('foo1.txt')
        touch('foo2.txt')
        touch('foo3.bin')

        cmd.feedback("disable", "python", "output")

        cmd.pwd()
        # no test of output possible

        cmd.ls('*.txt')
        # no test of output possible


def testPaste():
    cmd.paste
    # partly functional command (?)


def testSystem():
    cmd.system
    pytest.skip("TODO")

