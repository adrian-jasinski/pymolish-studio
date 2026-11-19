'''
Tests for periodic boundary condition tools
'''

import pytest
from pymol import cmd, testing

stem = "desmond/Bace_mapper_20143_3a51a59_e85111a_solvent_11_replica0"
ligsele = "segi C2"


def _load_traj():
    cmd.load(testing.datafile(stem + "-out.cif"), "m1")
    cmd.load_traj(testing.datafile(stem + "_trj/clickme.dtr"), "m1", state=1)
    assert cmd.count_states() == 209


def _get_mean(sele, state):
    return cmd.get_coords(sele, state).mean(0)


def assertMeanEqual(sele, state, expected, delta=1e-4):
    testing.assert_array_equal(_get_mean(sele, state),
                          expected,
                          delta=delta)


def assertMeanEqualAllStates(sele, expected, delta=1e-4):
    for state in range(1, cmd.count_states(sele) + 1):
        assertMeanEqual(sele, state, expected, delta=delta)


def test_pbc_wrap():
    _load_traj()
    assertMeanEqual("m1", 1, [0.1931318, 0.02557054, -0.19974825])
    assertMeanEqual("m1", 10, [-0.39728516, -0.15377004, 0.3353078])
    cmd.pbc_unwrap("m1", bymol=1)
    assertMeanEqual("m1", 1, [0.1931318, 0.02557054, -0.19974825])
    assertMeanEqual("m1", 10, [-13.647337, 17.052486, 20.949625])
    assertMeanEqual("m1", 100, [-99.25437, 112.844734, 146.75703])
    assertMeanEqual(ligsele, 100, [13.758579, 160.77652, 108.984375])
    cmd.pbc_wrap("m1")
    assertMeanEqual("m1", 1, [0.35491294, 0.06518874, -0.44330302])
    assertMeanEqual("m1", 10, [0.26413238, -0.11394002, -0.41091236])
    assertMeanEqual("m1", 100, [-0.21415119, 0.01216528, -0.23332132])
    assertMeanEqual(ligsele, 100, [-13.1273365, -3.823541, -6.660239])
    cmd.pbc_wrap("m1", center=[0, 0, 0])
    assertMeanEqualAllStates("m1", [0., 0., 0.], delta=0.5)
    cmd.pbc_wrap("m1", center=[10, 20, 30])
    assertMeanEqualAllStates("m1", [10., 20., 30.], delta=0.5)
    assertMeanEqual(ligsele, 100, [13.758579, 29.096472, 22.250914])


@pytest.mark.parametrize("state,mean,mix", [
    (100, [-13.1273365, -3.8235407, -6.660238], False),
    (200, [12.344244, 12.3195715, -1.104801], True),
])
def test_intra_fit(state, mean, mix):
    _load_traj()

    deltasolvent = 1.0
    assertMeanEqualAllStates("solvent", [0, 0, 0], delta=deltasolvent)

    cmd.intra_fit(ligsele, state, pbc=0, mix=mix)
    assertMeanEqualAllStates(ligsele, mean, delta=0.1)
    assertMeanEqual("solvent", state, [0, 0, 0], delta=deltasolvent)

    cmd.intra_fit(ligsele, state, pbc=1, mix=mix)
    assertMeanEqualAllStates(ligsele, mean, delta=0.1)
    assertMeanEqualAllStates("solvent", mean, delta=deltasolvent)


def test_smooth():
    _load_traj()

    cmd.smooth("m1", 10, pbc=1)
    testing.assert_array_equal(
        cmd.get_extent("m1", state=100),
        [[-14.278, -17.192, -15.273], [14.187, 17.142, 15.317]],
        delta=1.0)

    cmd.smooth("m1", 10, pbc=0)
    testing.assert_array_equal(
        cmd.get_extent("m1", state=100),
        [[-11.245, -13.397, -12.412], [10.829, 12.899, 12.103]],
        delta=0.5)
