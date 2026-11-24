"""
21f: a session carries its background picture, not only the name of the
file. testing/tests/jira/PYMOL-1571.py checks the drawing in a real window.
"""

from pymol import cmd


def test_picture_travels_with_the_session(tmp_path):
    picture = tmp_path / "bg.png"
    session = str(tmp_path / "with_picture.pse")
    cmd.bg_color("red")
    cmd.png(str(picture), 40, 30, ray=1)
    cmd.bg_color("black")
    cmd.set("bg_image_filename", str(picture))
    cmd.save(session)
    assert cmd.get("bg_image_filename") == str(picture)  # saving changes nothing here
    picture.unlink()
    cmd.reinitialize()
    cmd.load(session)
    text = cmd.get("bg_image_filename")
    assert text.startswith("data:image/png;base64,iVBOR")
    cmd.save(session)  # saved again, it stays what it is
    cmd.reinitialize()
    cmd.load(session)
    assert cmd.get("bg_image_filename") == text
    # a name without a file is kept as a name
    cmd.set("bg_image_filename", str(picture))
    cmd.save(session)
    cmd.load(session)
    assert cmd.get("bg_image_filename") == str(picture)

