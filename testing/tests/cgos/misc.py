from pymol import cmd, testing, cgo


def test_pse():
    testing.ambient_only()

    viewport = (50, 50)
    cmd.viewport(*viewport)

    objname = 'simpletri'
    obj = []
    obj.extend([
        cgo.BEGIN, cgo.TRIANGLES,
        cgo.COLOR, 1.0, 0., 0.,
        cgo.VERTEX, 0.0, 0.0, 1.0,
        cgo.VERTEX, 1.0, 0.0, 0.0,
        cgo.VERTEX, 0.0, 1.0, 0.0,
        cgo.END
        ])
    cmd.load_cgo(obj, objname, 1)

    s = cmd.get_session()
    cmd.set_session(s)

    assert [objname] == cmd.get_names()
    testing.assert_image_has_color('red')
