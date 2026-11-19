import pytest
import os
import pymol
from pymol import cmd, testing, stored

pytestmark = testing.requires("no_run_all", "gui")


def _setup_movie(rep):
    cmd.load(testing.datafile('1aon.pdb.gz'))
    cmd.show_as(rep)
    cmd.orient()
    cmd.mset('1x100')
    pymol.movie.roll(1, cmd.count_frames(), 0, 'y')


@pytest.mark.parametrize("use_shaders,cgo_shader_ub,rep", [
        (0, 0, "cartoon"),
        (0, 0, "surface"),
        (1, 0, "cartoon"),
        (1, 0, "surface"),
        (1, 1, "cartoon"),
        ])
def test(use_shaders, cgo_shader_ub, rep):
    _setup_movie(rep)

    cmd.set("use_shaders", use_shaders)
    cmd.set("cgo_shader_ub_color", cgo_shader_ub)
    cmd.set("cgo_shader_ub_flags", cgo_shader_ub)
    cmd.set("cgo_shader_ub_normal", cgo_shader_ub)

    with testing.mkdtemp() as tempdir, testing.timing():
        cmd.mpng(os.path.join(tempdir, "f"))
