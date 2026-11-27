'''
Infrastructure for PyMOL testing

Usage:
    pymolish testing.py --run all             Run all tests
    pymolish testing.py --run some/file.py    Run tests from given files

Tests are pytest functions. Every test starts with a clean PyMOL session
and in the directory of its file (the fixture in conftest.py); the helpers
below are used as testing.<name>.
'''

from __future__ import print_function

import os
import sys
import pymol
import collections
import platform
import inspect
import pathlib

try:
    WindowsError
except NameError:
    WindowsError = None

try:
    basestring
except NameError:
    basestring = (str, bytes)

def compareListFunction(x, y):
    return collections.Counter(x) == collections.Counter(y)


def import_from_file(filename: str, name: str = None):
    import importlib
    if name is None:
        try:
            name = os.path.relpath(filename).replace('.', '_')
        except ValueError:
            name = os.path.basename(filename).replace('.', '_')
    for suffix in importlib.machinery.all_suffixes():
        if filename.endswith(suffix):
            break
    else:
        raise ValueError(f"invalid extension: {filename}")
    loader = importlib.machinery.SourceFileLoader(name, filename)
    return loader.load_module()


if __name__ != 'pymol.testing':
    # pymol foo.py    -> __name__ == 'pymol'
    # pymol -r foo.py -> __name__ == '__main__'

    # absolute: the tests change the working directory
    this_path = pathlib.Path(inspect.currentframe().f_code.co_filename).resolve()
    test_utils = this_path.parent.joinpath('tests', 'helpers', 'test_utils.py')
    pymol.testing = import_from_file(str(this_path), 'pymol.testing')
    pymol.test_utils = import_from_file(str(test_utils), 'pymol.test_utils')
    pymol.testing.cli()

else:
    import time
    import tempfile
    import argparse
    import pytest

    try:
        import Image
    except ImportError:
        from PIL import Image
        sys.modules['Image'] = Image

    from pymol import cmd
    from pymol.invocation import options

    get_capabilities = getattr(pymol, 'get_capabilities', lambda: ())

    def tupleize_version(strversion):
        r = []
        for x in strversion.split('.'):
            try:
                r.append(int(x))
            except ValueError:
                break
        return tuple(r)

    PYMOL_VERSION = cmd.get_version()
    PYMOL_VERSION_TUPLE = tupleize_version(PYMOL_VERSION[0])
    PYMOL_EDU = 'Edu' in PYMOL_VERSION[0]
    is_win64bit = "Windows" in platform.system() and sys.maxsize > 2**32

    usage = 'pymolish [pymol options] %s [test options]' % (os.path.basename(__file__))
    parser = argparse.ArgumentParser("pymolish", usage=usage)
    parser.add_argument('filenames', nargs='*', default=[])
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--no-undo', action='store_true', default=True)
    parser.add_argument('--with-undo', action='store_false', dest='no_undo')

    have_dash_dash = __file__.startswith(sys.argv[0]) or '--run' in sys.argv
    cliargs = parser.parse_known_args(None if have_dash_dash else [])[0]

    run_all = False
    max_threads = int(cmd.get('max_threads'))

    cmd.set('use_shaders')
    use_shaders = cmd.get_setting_boolean('use_shaders')

    pymol_test_dir = os.path.abspath(os.path.dirname(__file__))

    deferred_unlink = []
    deferred_rmtree = []

    def requires(*flags):
        """
        Mark that skips a test unless every named condition holds.

            >>> @testing.requires('gui')
            >>> def test_something():

        For every test of a file: `pytestmark = testing.requires('gui')`.
        """
        unmet = {
            'shaders': not use_shaders,
            'gui': options.no_gui,
            'no_edu': PYMOL_EDU,
            'network': cliargs.offline,
            'no_run_all': run_all,
            'multicore': max_threads <= 1,
            'no_win64bit': is_win64bit,
            'multi_undo': 'multi_undo' not in get_capabilities(),
        }
        unknown = sorted(set(flags) - set(unmet))
        if unknown:
            raise ValueError('unknown flags: ' + ', '.join(unknown)
                    + '; choices: ' + ', '.join(sorted(unmet)))
        missing = [flag for flag in flags if unmet[flag]]
        return pytest.mark.skipif(bool(missing),
                reason='requires ' + ', '.join(missing))

    class mktemp(object):
        '''
        Context manager which returns a temporary filename and
        deletes the file in the end, if it exists.
        '''
        def __init__(self, suffix=''):
            self.filename = tempfile.mktemp(suffix)
        def __enter__(self):
            return self.filename
        def __exit__(self, exc_type, exc_value, traceback):
            if os.path.exists(self.filename):
                try:
                    os.remove(self.filename)
                except WindowsError:
                    deferred_unlink.append(self.filename)

    class mkdtemp(object):
        '''
        Context manager for temporary directory
        '''
        def __init__(self):
            self.name = tempfile.mkdtemp()
        def __enter__(self):
            return self.name
        def __exit__(self, exc_type, exc_value, traceback):
            import shutil
            if os.path.exists(self.name):
                try:
                    shutil.rmtree(self.name)
                except WindowsError:
                    deferred_rmtree.append(self.name)

    class timing(object):
        """
        Context manager: the test fails if the block takes longer than
        `max` seconds.

            >>> with testing.timing(max=3.0):
            >>>     do_something()
        """
        def __init__(self, msg=None, max=None):
            self.msg = msg
            self.max = max
        def __enter__(self):
            self.start = time.time()
        def __exit__(self, exc_type, exc_value, traceback):
            if exc_type:
                return
            delta = time.time() - self.start
            if self.max and delta > self.max:
                msg = 'slow: %fs > %fs' % (delta, self.max)
                if self.msg:
                    msg = self.msg + ', ' + msg
                raise AssertionError(msg)

    def _color_tuple(color):
        if isinstance(color, (tuple, list)):
            return tuple(color)
        return cmd.get_color_tuple(color)

    def assert_color_equal(color1, color2):
        assert _color_tuple(color1) == _color_tuple(color2)

    def assert_image_equal(img1, img2=None, delta=0, count=0, msg='images not equal'):
        """
        Test if two images are the same.

        img1, img2 can be either filenames, Image (PIL) objects
        or numpy arrays.

        delta > 0 is for inexact match (image data is 0..255 int)

        count is the number of allowed pixel mismatches.
        """
        import numpy

        if isinstance(img1, basestring) and not \
                os.path.exists(img1):
            print(' Generating reference img:', img1)
            png(img1)
            return

        data1 = get_imagearray(img1)
        data2 = get_imagearray(img2)

        assert data1.shape == data2.shape, 'image shapes not equal '

        diff = abs(data1 - data2)

        noff = numpy.sum(diff > delta)
        if noff > count * data1.shape[-1]:
            filename = tempfile.mktemp('diff.png')

            diffimg = Image.fromarray((255 - diff.reshape(data1.shape)).astype(numpy.uint8))
            diffimg.save(filename)

            raise AssertionError(msg + ' (%d) %s' % (noff, filename))

    def assert_image_not_equal(img1, img2=None, delta=0, count=0, msg='images equal'):
        import numpy
        data1 = get_imagearray(img1)
        data2 = get_imagearray(img2)
        diff = abs(data1 - data2)
        noff = numpy.sum(diff > delta)
        assert noff > count * data1.shape[-1], msg

    def image_count_colors(img, ignorealpha=False):
        dim = img.shape[-1]
        if dim == 4 and ignorealpha:
            dim = 3
            img = img[...,:dim]
        colors = set(tuple(row) for row in img.reshape((-1, dim)).tolist())
        return len(colors)

    def _image_has_color(color, img, delta=0):
        if isinstance(color, str):
            color = [int(v*255) for v in cmd.get_color_tuple(color)]
        else:
            color = list(color)
        dim = img.shape[-1]
        if dim == len(color) + 1:
            dim -= 1
            img = img[...,:dim]
        diff = abs(img.reshape((-1, dim)) - color)
        return (diff - delta <= 0).prod(1).sum()

    def save_imagearray(img, filename=None):
        if not filename:
            filename = tempfile.mktemp('.png')

        img = Image.fromarray(img)
        img.save(filename)

        return filename

    def _assert_image_has_color(test, color, img, delta, msg):
        img = get_imagearray(img)
        has_color = _image_has_color(color, img, delta)

        if bool(has_color) != test:
            raise AssertionError(msg + ', ' + save_imagearray(img))

    def assert_image_has_color(color, img=None, delta=0, msg=''):
        if not msg:
            msg = 'no such color: ' + str(color)
        _assert_image_has_color(True, color, img, delta, msg)

    def assert_image_has_not_color(color, img=None, delta=0, msg=''):
        if not msg:
            msg = 'color found: ' + str(color)
        _assert_image_has_color(False, color, img, delta, msg)

    def assert_image_has_transparency(img=None):
        img = get_imagearray(img)
        assert (img[:,:,3] < 255).any()

    def assert_image_has_no_transparency(img=None):
        img = get_imagearray(img)
        if img.shape[-1] == 4:
            assert (img[:,:,3] == 255).all()

    def assert_array_equal(a1, a2, delta=0, msg='arrays not equal', _not=False):
        """
        Test if two (multi-)dimensional numeric arrays are (almost) equal.
        """
        import numpy

        a1 = numpy.asarray(a1)
        a2 = numpy.asarray(a2)

        assert a1.shape == a2.shape, msg + ' (shape)'
        assert (not _not) == numpy.allclose(a1, a2, 0, delta), msg

    def assert_array_not_equal(a1, a2, delta=0, msg='arrays equal'):
        assert_array_equal(a1, a2, delta, msg, True)

    def datafile(filename):
        """
        Return path to filename, the current directory and the data
        directory are searched for filename.
        """
        if os.path.exists(filename):
            return filename
        return os.path.join(pymol_test_dir, 'data', filename)

    def get_imagearray(img=None, **kwargs):
        """
        Get bitmap data as a numpy array.

        img can be either a filename or a Image (PIL) object.
        """
        if PYMOL_EDU and (options.no_gui or 'ray' in kwargs):
            pytest.skip("edu no-ray")

        import numpy

        if img is None:
            with mktemp('.png') as filename:
                png(filename, **kwargs)
                return get_imagearray(filename)

        if isinstance(img, numpy.ndarray):
            return img

        if isinstance(img, basestring):
            img = Image.open(img)

        if not isinstance(img, Image.Image):
            raise TypeError('img must be filename or Image instance')

        return numpy.array(img.getdata(),
                           numpy.uint8).reshape((img.size[1], img.size[0], -1))

    def png(filename, *args, **kwargs):
        """
        Save image to filename, with antialias=0.
        """
        if 'multi_undo' in get_capabilities():
            with cmd.UndoPauseCM():
                cmd.set('antialias', 0)
        else:
            cmd.set('antialias', 0)
        cmd.png(filename, *args, **kwargs)
        cmd.draw()

    def ambient_only():
        cmd.set('ambient', 1)
        cmd.set('antialias', 0)
        cmd.set('light_count', 1)
        cmd.set('depth_cue', 0)

        # needed for open-source
        cmd.set('reflect', 0)
        cmd.set('direct', 0)

    def run_testfiles(filenames='all', **kwargs):
        '''
DESCRIPTION

    Run one or more test files or directories with pytest.

USAGE

    run_testfiles file1 file2 ...
        '''
        if filenames in ('all', ['all']):
            global run_all
            run_all = True
            filenames = [os.path.join(pymol_test_dir, 'tests')]

        nfail = int(pytest.main(['-v', *map(str, filenames)]))

        while deferred_unlink:
            os.unlink(deferred_unlink.pop())

        while deferred_rmtree:
            import subprocess
            subprocess.call(['rd', '/s', '/q', deferred_rmtree.pop()], shell=True)

        return nfail

    def cli():
        '''
        Test suite client application.
        '''
        if not cliargs.filenames:
            # silently do nothing
            return
        nfail = run_testfiles(**vars(cliargs))
        cmd.quit(nfail)

    cmd.extend('run_testfiles', run_testfiles)

