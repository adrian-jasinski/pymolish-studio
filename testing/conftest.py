import os

import pytest

import pymol

pymol.__path__.append(".")
pymol.__path__.append("tests/helpers")

from pymol import cmd, testing

collect_ignore = [
    "tests/helpers",
]


@pytest.fixture(autouse=True, scope="session")
def own_settings(tmp_path_factory):
    """What the window remembers (QSettings: palettes of the user, sizes) is
    read from an empty folder, not from the person who runs the tests: a
    palette saved in the window made palettes.py::test_data fail. Qt moves
    the native settings like this where they are files (Linux); on Windows
    and macOS the call does nothing."""
    from pymol.Qt import QtCore

    Settings = QtCore.QSettings
    Settings.setPath(
        Settings.Format.NativeFormat,
        Settings.Scope.UserScope,
        str(tmp_path_factory.mktemp("settings")),
    )


@pytest.fixture(autouse=True)
def clean_session(request, monkeypatch):
    """Every test starts with a clean session, in the directory of its file,
    outside the undo step of the line that runs the tests."""
    from pymol import snapshots

    monkeypatch.setattr(snapshots, "_step", None)
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
