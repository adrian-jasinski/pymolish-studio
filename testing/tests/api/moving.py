
import pytest
from pymol import cmd, testing, stored


def prep_movie():
    cmd.mset("1x60")


def testAccept():
    cmd.accept
    pytest.skip("TODO")


def testBackward():
    prep_movie()
    cmd.middle()
    cmd.backward()
    assert cmd.get_frame() == 30

    cmd.frame(1)
    cmd.backward()
    assert cmd.get_frame() == 1
    


def testDecline():
    cmd.decline
    pytest.skip("TODO")


def testEnding():
    prep_movie()
    cmd.ending()
    assert cmd.get_frame() == 60


def testForward():
    prep_movie()
    cmd.forward()
    assert cmd.get_frame() == 2
    cmd.forward()
    assert cmd.get_frame() == 3
    cmd.frame(30)
    assert cmd.get_frame() == 30
    cmd.frame(60)
    cmd.forward()
    assert cmd.get_frame() == 60

    cmd.frame(60)
    cmd.forward()
    assert cmd.get_frame() == 60


def testFrame():
    prep_movie()
    cmd.frame(30)
    assert cmd.get_frame() == 30

    cmd.frame(60)
    assert cmd.get_frame() == 60

    cmd.frame(65)
    assert cmd.get_frame() == 60

    cmd.frame(-5)
    assert cmd.get_frame() == 1

    cmd.frame(10)
    cmd.frame(1)
    assert cmd.get_frame() == 1


def testGetFrame():
    prep_movie()
    cmd.frame(30)
    assert cmd.get_frame() == 30

    cmd.frame(60)
    assert cmd.get_frame() == 60

    cmd.frame(65)
    assert cmd.get_frame() == 60

    cmd.frame(-5)
    assert cmd.get_frame() == 1

    cmd.frame(10)
    cmd.frame(1)
    assert cmd.get_frame() == 1


def testGetMoviePlaying():
    prep_movie()
    cmd.mplay()
    assert cmd.get_movie_playing() == 1

    cmd.mstop()
    assert cmd.get_movie_playing() == 0
    


def testGetState():
    cmd.get_state
    pytest.skip("TODO")


def testMadd():
    # test clearing
    prep_movie()
    assert cmd.count_frames() == 60

    # test states and frame mapping
    cmd.madd("1x10 1 -10 10 -1")
    assert cmd.count_frames() == 90
    
    cmd.frame(1)
    assert cmd.get_frame() == 1
    assert cmd.get("state") == "1"
    cmd.frame(10)
    assert cmd.get_frame() == 10
    assert cmd.get("state") == "1"
    cmd.frame(72)
    assert cmd.get_frame() == 72
    assert cmd.get("state") == "2"
    cmd.frame(82)
    assert cmd.get_frame() == 82
    assert cmd.get("state") == "9"
    cmd.frame(90)
    assert cmd.get_frame() == 90
    assert cmd.get("state") == "1"


def testMappend():
    prep_movie()
    cmd.fragment("ala")
    cmd.mappend(5,"delete *")
    cmd.mappend(5,"frame 1")
    cmd.frame(5)
    assert len(cmd.get_names()) == 0
    assert cmd.get_frame() == 1

    


def testMclear():
    cmd.mclear
    pytest.skip("TODO")


def testMcopy():
    cmd.mcopy
    pytest.skip("TODO")


def testMdelete():
    cmd.mset("1x10 1 -10 10 -1")

    # 1-10 = state 1
    # 11-20 = states 1..10
    # 21-30 = states 10..1

    cmd.mdelete(count=10, frame=11)
    # simple delete
    assert cmd.count_frames() == 20

    # test state mapping
    cmd.frame(1)
    assert cmd.get("state") == "1"
    cmd.frame(11)
    assert cmd.get("state") == "10"
    cmd.frame(20)
    assert cmd.get("state") == "1"


def testMdo():
    prep_movie()
    cmd.fragment("ala")
    cmd.mdo(5,"delete *")
    cmd.frame(5)
    assert len(cmd.get_names()) == 0


def testMdump():
    cmd.mdump
    pytest.skip("TODO: This prints to console, not sure how to test.")


def testMiddle():
    prep_movie()
    cmd.middle()
    assert cmd.get_frame() == 31


def testMinsert():
    prep_movie()
    cmd.minsert(20)
    assert cmd.count_frames() == 80

    # need a more sophisticated test for this
    


def testMmatrix():
    cmd.mmatrix
    pytest.skip("TODO")


def testMmove():
    cmd.mmove
    pytest.skip("TODO")


def testMplay():
    prep_movie()
    cmd.mplay()
    assert cmd.get_movie_playing() == 1
    cmd.mstop()


@pytest.mark.parametrize("modal", [0, 1])
def testMpng(modal):
    import glob, os

    shape2 = (100, 100)
    cmd.mset("1x4")
    cmd.mdo(1, 'bg_color red')
    cmd.mdo(3, 'bg_color blue')

    with testing.mkdtemp() as dirname:
        cmd.mpng(os.path.join(dirname, 'image'), width=shape2[0],
                 height=shape2[1], modal=modal, mode=2)

        if modal:
            # modal export renders one frame per draw cycle (GitHub #519)
            for _ in range(100):
                if not cmd.get_modal_draw():
                    break
                cmd._cmd._draw(cmd._COb)
            assert not cmd.get_modal_draw()

        filenames = glob.glob(os.path.join(dirname, 'image*.png'))
        filenames.sort()

        assert 4 == len(filenames)

        img = testing.get_imagearray(filenames[0])
        assert img.shape[:2] == shape2
        testing.assert_image_has_color('red', img)

        img = testing.get_imagearray(filenames[-1])
        assert img.shape[:2] == shape2
        testing.assert_image_has_color('blue', img)


def testMset():
    # basic tet
    prep_movie()
    assert cmd.count_frames() == 60

    # test clearing
    cmd.mset()
    assert cmd.count_frames() == 0

    # test states and frame mapping
    cmd.mset("1x10 1 -10 10 -1")
    cmd.frame(1)
    assert cmd.get_frame() == 1
    assert cmd.get("state") == "1"
    cmd.frame(10)
    assert cmd.get_frame() == 10
    assert cmd.get("state") == "1"
    cmd.frame(12)
    assert cmd.get_frame() == 12
    assert cmd.get("state") == "2"
    cmd.frame(22)
    assert cmd.get_frame() == 22
    assert cmd.get("state") == "9"
    cmd.frame(30)
    assert cmd.get_frame() == 30
    assert cmd.get("state") == "1"


def testMstop():
    prep_movie()
    cmd.mplay()
    cmd.mstop()
    assert cmd.get_movie_playing() == 0


def testMtoggle():
    prep_movie()
    cmd.mstop()
    
    # toggle on
    cmd.mtoggle()
    assert cmd.get_movie_playing() == 1
    # toggle off
    cmd.mtoggle()
    assert cmd.get_movie_playing() == 0


def testMview():
    cmd.mview
    pytest.skip("TODO")


def testMviewSmooth():
    cmd.pseudoatom('m1')
    cmd.mset("1x30")
    cmd.mview('store', 1)
    cmd.turn('y', 90)
    cmd.mview('store', 15)
    cmd.turn('x', 90)
    cmd.mview('store', 30)
    cmd.mview('reinterpolate')
    cmd.frame(15)
    before = cmd.get_view()
    cmd.mview('smooth', window=7)
    cmd.frame(15)
    after = cmd.get_view()
    # the corner at the middle key frame is rounded off, nothing blows up
    assert before != pytest.approx(after, abs=1e-4)
    assert all(abs(x) < 1e3 for x in after)


def testRewind():
    prep_movie()
    cmd.frame(30)
    assert cmd.get_frame() == 30

    cmd.rewind()
    assert cmd.get_frame() == 1

    


def testSetFrame():

    prep_movie()

    # within
    cmd.set_frame(30)
    assert cmd.get_frame() == 30

    # extent < 
    cmd.set_frame(-1)
    assert cmd.get_frame() == 1

    # extent > 
    cmd.set_frame(300)
    assert cmd.get_frame() == 60

    
