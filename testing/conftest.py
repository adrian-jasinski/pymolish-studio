import os

import pytest

import pymol

pymol.__path__.append(".")
pymol.__path__.append("tests/helpers")

from pymol import cmd, testing

collect_ignore = [
    "tests/helpers",
]


@pytest.fixture(autouse=True)
def clean_session(request):
    """Every test starts with a clean session, in the directory of its file."""
    oldcwd = os.getcwd()
    cmd.reinitialize()
    cmd.viewport(640, 480)
    if testing.cliargs.no_undo:
        cmd.set("suspend_undo", updates=0)
    os.chdir(request.path.parent)
    cmd.feedback("push")
    cmd.feedback("disable", "all", "details actions")
    yield
    cmd.feedback("pop")
    os.chdir(oldcwd)
