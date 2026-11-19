'''
cmd.create(copy_properties=True) copies object and atom properties
'''

from pymol import cmd


def testCopyObjectProperties():
    cmd.load('CID_6830.sdf', 'test', object_props='*')
    cmd.create('test_copy', 'test', copy_properties=True)
    props = cmd.get_property_list('test')
    assert props
    assert set(props) == set(cmd.get_property_list('test_copy'))
    for prop in props:
        assert cmd.get_property(prop, 'test') == cmd.get_property(prop, 'test_copy')


def testCopyAtomProperties():
    cmd.load('CID_6830.sdf', 'test')
    cmd.alter('test', 'p.foo = index')
    cmd.create('test_copy', 'test', copy_properties=True)
    props = {}
    cmd.iterate('test test_copy', 'props.setdefault(model, {})[index] = p.all',
                space={'props': props})
    assert props['test'][1] == {'foo': 1}
    assert props['test'] == props['test_copy']
