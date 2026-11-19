'''
new feature: cartoon_gap_cutoff

Not very sophisticated test, just check if images with and without
setting differ.
'''

from pymol import cmd, CmdException, testing, stored


def test():
    cmd.set('cartoon_gap_cutoff', 0) # default varies by version

    testing.ambient_only()

    cmd.viewport(150, 150)
    cmd.load(testing.datafile('1oky-frag.pdb'))
    cmd.cartoon('dash')
    cmd.show_as('cartoon')
    cmd.orient()

    # no gaps
    img_nogaps = testing.get_imagearray()

    # gap of length 0
    cmd.unbond('96/C', '97/N')
    img_gap = testing.get_imagearray()
    assert not (img_gap == img_nogaps).all()

    # close gap with setting, should match first image (special case)
    cmd.set('cartoon_gap_cutoff', 1) # exact cutoff
    img_gap = testing.get_imagearray()
    assert (img_gap == img_nogaps).all()

    # gap of length 1
    cmd.remove('92/')
    img_gap = testing.get_imagearray()
    cmd.set('cartoon_gap_cutoff', 2) # exact cutoff
    img_nogaps = testing.get_imagearray()
    assert not (img_gap == img_nogaps).all()

    # gap of length 3
    cmd.remove('102-104/')
    cmd.cartoon('auto') # default
    img_gap = testing.get_imagearray()
    cmd.set('cartoon_gap_cutoff', 10) # arbitrary larger cutoff
    img_nogaps = testing.get_imagearray()
    assert not (img_gap == img_nogaps).all()
