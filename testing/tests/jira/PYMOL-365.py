'''
ray+png in batch mode did ray trace twice
'''

from pymol import cmd, testing, stored


def test():
    cmd.fragment('ala')
    cmd.ray(100, 100)
    img = testing.get_imagearray() # cmd.png without optional arguments

    # bug was: ray tracing twice, second time would not be 100x100
    assert img.shape[:2] == (100,100)
