
import pytest
from pymol import cmd, testing, stored


def test_indices():
    # setting indices must not change, since they are used in session files
    assert 787 == cmd.pymol.setting._get_index('isosurface_algorithm')


def testGet():
    name_bool = 'cartoon_fancy_helices'
    name_obj = 'ala'
    cmd.fragment('ala', name_obj)
    cmd.set(name_bool, 1, name_obj)
    assert 'off' == cmd.get(name_bool)
    assert 'on' == cmd.get(name_bool, name_obj)
    cmd.unset(name_bool, '*')
    cmd.set(name_bool)
    assert 'on' == cmd.get(name_bool)
    assert 'on' == cmd.get(name_bool, name_obj)
    cmd.set(name_bool, 0, name_obj)
    assert 'on' == cmd.get(name_bool)
    assert 'off' == cmd.get(name_bool, name_obj)


def testGetBond():
    # see testSetBond
    pass


def testGetSettingBoolean():
    for v_ref in (0, 1):
        cmd.set('orthoscopic', v_ref)
        v = cmd.get_setting_boolean('orthoscopic')
        assert isinstance(v, int)
        assert v == v_ref


def testGetSettingFloat():
    for v_ref in (0.0, 1.0):
        # bool as float
        cmd.set('orthoscopic', v_ref)
        v = cmd.get_setting_float('orthoscopic')
        assert isinstance(v, float)
        assert v == v_ref

    # float with 6 significant digits
    cmd.set('sphere_scale', 1.234565)
    v = cmd.get_setting_float('sphere_scale')
    assert int(v * 1e5) == 123456


def testGetSettingFloatExact():
    # PyMOL 2.4 uses pymol::pretty_f2d which rounds 7 significant digits
    for v_ref in (1.234567, 1234567.e6, 9999999.0):
        cmd.set('sphere_scale', v_ref)
        v = cmd.get_setting_float('sphere_scale')
        assert v == v_ref


def testGetSettingInt():
    cmd.set('light_count', 4)
    v = cmd.get_setting_int('light_count')
    assert isinstance(v, int)
    assert v == 4

    # float as int gets floored
    cmd.set('sphere_scale', 3.7)
    v = cmd.get_setting_int('sphere_scale')
    assert isinstance(v, int)
    assert v == 3


def testGetSettingText():
    # int
    cmd.set('light_count', 4)
    v = cmd.get_setting_text('light_count')
    assert isinstance(v, str)
    assert v == '4'

    # bool
    cmd.set('orthoscopic', 0)
    v = cmd.get_setting_text('orthoscopic')
    assert v == 'off'

    # float gets rounded to 5 digits
    cmd.set('sphere_scale', 3.7)
    v = cmd.get_setting_text('sphere_scale')
    assert v == '3.70000'

    # float3 gets nicely formatted
    cmd.set('label_position', (0.100009, 2.3, 4.56789))
    v = cmd.get_setting_text('label_position')
    assert v == '[ 0.10001, 2.30000, 4.56789 ]'

    # string
    cmd.set('pdb_echo_tags', 'Hello World')
    v = cmd.get_setting_text('pdb_echo_tags')
    assert v == 'Hello World'


def testGetSettingTuple():
    cmd.set('label_position', (1, 2, 4))
    v = cmd.get_setting_tuple('label_position')
    assert v == (4, (1.0, 2.0, 4.0))


def testGetSettingUpdates():
    v = cmd.get_setting_updates() # consume whatever
    cmd.set('orthoscopic', 1)
    v = cmd.get_setting_updates()
    assert v == [23]


def _testGetSettingUpdates_reinitialize(store):
    SEQ_VIEW_INDEX = 353

    cmd.reinitialize("purge_defaults")
    cmd.reinitialize("original_settings")

    if store:
        cmd.reinitialize("store")

    cmd.get_setting_updates() # consume whatever
    assert SEQ_VIEW_INDEX not in cmd.get_setting_updates()

    cmd.set("seq_view")
    assert SEQ_VIEW_INDEX in cmd.get_setting_updates()
    assert SEQ_VIEW_INDEX not in cmd.get_setting_updates()

    cmd.reinitialize()
    assert SEQ_VIEW_INDEX in cmd.get_setting_updates()
    assert SEQ_VIEW_INDEX not in cmd.get_setting_updates()

    cmd.set("seq_view")
    cmd.get_setting_updates() # consume whatever

    cmd.reinitialize("settings")
    assert SEQ_VIEW_INDEX in cmd.get_setting_updates()
    assert SEQ_VIEW_INDEX not in cmd.get_setting_updates()

    cmd.set("seq_view")
    cmd.get_setting_updates() # consume whatever

    cmd.reinitialize("original_settings")
    assert SEQ_VIEW_INDEX in cmd.get_setting_updates()
    assert SEQ_VIEW_INDEX not in cmd.get_setting_updates()


def testGetSettingUpdates_reinitialize():
    _testGetSettingUpdates_reinitialize(False)
    _testGetSettingUpdates_reinitialize(True)


@pytest.mark.parametrize("sele", ('', 'ala', '(elem O)'))
@pytest.mark.parametrize("name", ('sphere_scale',))
@pytest.mark.parametrize("value", (2.3,))
@pytest.mark.parametrize("defaultvalue", (1.0,))
def testSet(sele, name, value, defaultvalue):
    cmd.fragment('ala')
    cmd.set(name, value, sele)
    n = cmd.iterate('first (%s)' % (sele or 'all'), 'stored.v = s.' + name)
    assert n == 1
    assert stored.v == pytest.approx(value, abs=5e-8)

    if sele:
        cmd.unset(name, sele)
        n = cmd.iterate('first (%s)' % (sele or 'all'), 'stored.v = s.' + name)
        assert n == 1
        assert stored.v == defaultvalue


def testSetBond():
    value = 2.3
    cmd.fragment('ala')
    cmd.set_bond('stick_radius', value, '*', '*')
    v_list = cmd.get_bond('stick_radius', 'first *', '*')
    assert v_list[0][1][0][2] == pytest.approx(value, abs=5e-8)

    # unset
    # before 1.8.4, get_bond reported [0,0,0] after unset_bond
    cmd.unset_bond('stick_radius', '*', '*')
    v_list = cmd.get_bond('stick_radius', 'first *', '*')
    assert v_list[0][1][0][2] == None


def testUnset():
    # unset with selection: see testSet

    # unset global settings since PyMOL 2.5:
    for name, value in [
        ('light_count', 5),  # int, non-zero-default
        ('sphere_scale', 2.0),  # float, non-zero default
        ('ray_shadow', 'off'),  # bool, non-zero-default
        ('orthoscopic', 'on'),  # bool, zero-default
        ('cartoon_highlight_color', 'blue'),  # color
        ('fetch_path', '/some/path'),  # string
    ]:
        old_value = cmd.get(name)
        cmd.set(name, value)
        assert old_value != cmd.get(name)
        cmd.unset(name)
        assert old_value == cmd.get(name)


def testUnsetBond():
    # see testSetBond
    pass


def testUnsetDeep():
    cmd.fragment('ala')
    cmd.fragment('gly')
    cmd.fragment('his')

    # global
    sphere_scale_global = 0.8
    cmd.set('sphere_scale', sphere_scale_global)
    cmd.set('stick_color', 'blue')

    # object-level
    cmd.set('sphere_scale', .5, 'ala')
    cmd.set('stick_radius', .4, 'gly')

    # atom-level
    cmd.set('sphere_scale', .3, 'index 1-3')
    cmd.set('sphere_color', 'yellow', 'index 2-4')

    # bond-level
    cmd.set('stick_radius', .6, 'elem C')
    cmd.set('stick_color', 'red', 'index 1-5')

    cmd.unset_deep()
    names = cmd.get_object_list()

    for oname in names:
        # object-level check
        for sname in ['sphere_scale', 'sphere_color']:
            assert cmd.get(sname) == cmd.get(sname, oname)

        # atom-level check (1)
        # type float
        sname = 'sphere_scale'
        a_level_values = set()
        cmd.iterate(oname, 'a_level_values.add(s.' + sname + ')', space=locals())
        assert len(a_level_values) == 1
        assert sphere_scale_global == pytest.approx(list(a_level_values)[0], abs=1e-4)

        # atom-level check (2)
        # type color ('default' -> None)
        sname = 'sphere_color'
        a_level_values = set()
        cmd.iterate(oname, 'a_level_values.add(s.' + sname + ')', space=locals())
        assert len(a_level_values) == 1
        assert None == list(a_level_values)[0]

    # bond-level check (None for unset settings)
    for sname in ['stick_radius', 'stick_color']:
        b_level_values = cmd.get_bond(sname, '*')
        for o_set in b_level_values:
            for b_set in o_set[1]:
                assert None == b_set[2], sname + ' ' + o_set[0] + ' ' + str(b_set)
