PyMOL Testing Framework
=======================

The tests are pytest functions, run inside pymolish.

How to Run Tests
----------------

From the repository root:

    pymolish -ckqy testing/testing.py --run all
    pymolish -ckqy testing/testing.py --run testing/tests/api/<file>.py

The exit code is the one of pytest (0: all passed). Extra pytest options go
into the environment variable `PYTEST_ADDOPTS`, for example
`PYTEST_ADDOPTS="--durations=20"`.

From the pymol command line:

    PyMOL> run /path/to/pymol-testing/testing.py
    PyMOL> run_testfiles path/to/*.py

How to write Tests
------------------

A test is a function whose name starts with "test", in a file under
`tests/`, for example in "api/" or "performance/". The fixture
`clean_session` in `conftest.py` makes every test start

*   with a clean PyMOL session (does reinitialize)
*   from the directory of its file (does os.chdir)

State that several tests of a file share goes into a pytest fixture. A
fixture that needs the clean session takes `clean_session` as an argument.

Decorators
----------

*   `@testing.requires(keyword)`: Takes one or more keywords and skips the
    test, if the requirement is not met. Valid keywords include: gui,
    network, `no_run_all`, multicore, `multi_undo`. For every test of a file:
    `pytestmark = testing.requires(keyword)`.
*   `@pytest.mark.parametrize("a,b", [(1, 2), (3, 4)])`: runs a test once
    per set of arguments.

Helpers
-------

*    `testing.timing(max=sec)`: Context manager, makes the test fail if the
     block takes longer than `max` seconds.
*    `testing.mktemp(suffix)`: Context manager, generates a temporary file
     name and deletes the file at context exit.
*    `testing.datafile(name)`: Path of a file in the current directory or in
     `testing/data`.

Assertion Functions
-------------------

Use plain `assert`, `pytest.raises` and `pytest.approx`. In addition:

*   `testing.assert_image_equal(img1, img2=None, delta=0)`: Takes two images
    (as filenames, PIL objects or numpy arrays). If only one image is given,
    grab the current PyMOL scene as second image
*   `testing.assert_image_has_color(color, img=None, delta=0)`: Takes a color
    name, RGB or RGBA color tuple and an image (or grab the current scene)
    and check if it contains the given color
*   `testing.assert_image_has_not_color`
*   `testing.assert_image_has_transparency`
*   `testing.assert_image_has_no_transparency`
*   `testing.assert_color_equal`
*   `testing.assert_array_equal`
*   `testing.assert_array_not_equal`

Code Example
------------

    from pymol import cmd, testing

    def test_foo():
        cmd.fragment('ala')
        cmd.show_as('sticks')
        cmd.orient()
        testing.assert_image_equal('ref-foo.png')

    @testing.requires('gui')
    def test_bar():
        cmd.some_opengl_feature()
