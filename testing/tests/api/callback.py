from pymol import cmd, testing, stored, callback


def testPseSupport():
    cmd.load_callback(callback.Callback(), 'c1')
    with testing.mktemp('tmp.pse') as session_filename:
        cmd.save(session_filename)
        cmd.delete('*')
        cmd.load(session_filename)
        assert 'c1' in cmd.get_names()
