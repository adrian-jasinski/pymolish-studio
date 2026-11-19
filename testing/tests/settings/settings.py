'''
test various settings
'''

import pytest
import numpy
from pymol import cmd, testing


def assertNumColorsEqual(img, count, delta=0):
    assert len(numpy.unique(img[...,:3] // (delta + 1))) == count


@pytest.mark.parametrize("use_shader", [True, False])
def testStickBall(use_shader):
    '''
        Test some stick_ball* settings
        '''
    cmd.viewport(100, 100)

    cmd.set('use_shaders', use_shader)

    testing.ambient_only()

    cmd.set('stick_ball')
    cmd.set('stick_ball_ratio', 2.0)
    cmd.set('stick_ball_color', 'blue')
    cmd.set('stick_color', 'red')

    cmd.fragment('gly')
    cmd.orient()

    cmd.color('green')
    cmd.show_as('sticks')

    img = testing.get_imagearray()
    testing.assert_image_has_color('blue', img)
    testing.assert_image_has_color('red', img)
    testing.assert_image_has_not_color('green', img)


@testing.requires('no_edu')
@testing.requires('gui')
def testTransparencyMode3():
    '''
        Test if something gets rendered in transparency_mode=3
        '''
    cmd.viewport(100, 100)

    cmd.fragment('gly')
    cmd.zoom()

    cmd.set('transparency_mode', 3)
    cmd.set('transparency', 0.5)
    cmd.set('stick_transparency', 0.5)
    cmd.set('sphere_transparency', 0.5)
    cmd.set('cartoon_transparency', 0.5)

    for rep in ['sphere', 'stick', 'surface']:
        cmd.show_as(rep)

        # check on black screen to see if any shader failed
        img = testing.get_imagearray()
        assert img[...,:3].any()


@testing.requires('incentive')
@testing.requires('no_edu')
@testing.requires('gui')
def testAA():
    '''
        Make a black/white image and check if gray pixels are found with
        antialias_shader=1/2
        '''
    cmd.viewport(100, 100)

    cmd.set('use_shaders', True)

    testing.ambient_only()

    cmd.fragment('gly')
    cmd.show_as('spheres')
    cmd.color('white')
    cmd.zoom()

    # b/w image, we expect only two color values
    img = testing.get_imagearray()
    assertNumColorsEqual(img, 2)

    for aa in (1, 2):
        cmd.set('antialias_shader', aa)

        # smoothed edges, we expect more than two color values
        img = testing.get_imagearray()
        assert len(numpy.unique(img[...,:3])) > 2


@pytest.mark.parametrize("trilines", [0, 1])
@testing.requires('gui')
def testTrilines(trilines):
    cmd.viewport(100, 100)

    cmd.set('use_shaders', True)

    testing.ambient_only()

    cmd.set('dynamic_width', 0)
    cmd.set('line_width', 5)
    cmd.set('line_smooth', 0)

    cmd.fragment('ethylene')
    cmd.show_as('lines')
    cmd.color('white')
    cmd.orient()

    cmd.set('trilines', trilines)

    # check percentage of covered pixels
    img = testing.get_imagearray()
    npixels = img.shape[0] * img.shape[1]
    covered = numpy.count_nonzero(img[...,:3])
    ratio = covered / float(npixels)
    msg = "covered=%d npixels=%d ratio=%f" % (covered, npixels, ratio)
    assert 0.14 < ratio < 0.165, msg


@testing.requires('gui')
def testChromadepth():
    cmd.viewport(100, 100)

    testing.ambient_only()

    cmd.set('use_shaders')
    cmd.set('chromadepth')
    cmd.set('orthoscopic')

    cmd.pseudoatom(pos=(0, 0, -5))
    cmd.pseudoatom(pos=(0, 0, 5))
    cmd.color('gray')
    cmd.show_as('spheres')
    cmd.zoom()
    cmd.turn('y', 20)

    img = testing.get_imagearray()
    testing.assert_image_has_color('blue', img)
    testing.assert_image_has_color('red', img)


def testAtomCartoonTransparency():
    '''
        Test atom-level cartoon_transparency
        '''
    cmd.load(testing.datafile('1oky-frag.pdb'))
    cmd.select('sele', 'resi 106-111', 0)

    # hide blended parts between residues
    cmd.cartoon('skip', 'resi 105+112')

    return _testAtomCartoonTransparency()


def testAtomCartoonTransparencyCylHelices():
    '''
        Test atom-level cartoon_transparency with cylindrical helices
        '''
    cmd.load(testing.datafile('1oky-frag.pdb'))
    cmd.select('sele', 'resi 113-', 0)

    # hide blended parts between residues
    cmd.cartoon('skip', 'resi 112')

    cmd.set('cartoon_cylindrical_helices')

    return _testAtomCartoonTransparency()


def testAtomCartoonTransparencyNuc():
    '''
        Test atom-level cartoon_transparency with nucleic acid
        '''
    cmd.load(testing.datafile('1ehz-5.pdb'))
    cmd.select('sele', 'resi 4-', 0)

    # hide blended parts between residues
    cmd.cartoon('skip', 'resi 3')

    return _testAtomCartoonTransparency()


def _testAtomCartoonTransparency():
    testing.ambient_only()
    cmd.viewport(100, 100)
    cmd.set('opaque_background')
    cmd.set('ray_shadow', 0)

    cmd.orient()

    cmd.color('0xFF0000')
    cmd.color('0x0000FF', 'sele')

    # all opaque
    img = testing.get_imagearray()
    testing.assert_image_has_color('0xFF0000', img)
    testing.assert_image_has_color('0x0000FF', img)

    # object-level transparency
    cmd.set('cartoon_transparency', 0.4)
    img = testing.get_imagearray()
    testing.assert_image_has_color('0x990000', img) # 40%
    testing.assert_image_has_color('0x000099', img) # 40%
    testing.assert_image_has_not_color('0xFF0000', img)
    testing.assert_image_has_not_color('0x0000FF', img)

    # atom-level full-opaque
    cmd.set('cartoon_transparency', 0.0, 'sele')
    img = testing.get_imagearray()
    testing.assert_image_has_color('0x990000', img) # 40%
    testing.assert_image_has_color('0x0000FF', img) #  0%
    testing.assert_image_has_not_color('0xFF0000', img)
    testing.assert_image_has_not_color('0x000099', img)

    # atom-level semi-transparent
    cmd.set('cartoon_transparency', 0.6, 'sele')
    img = testing.get_imagearray()
    testing.assert_image_has_color('0x990000', img) # 40%
    testing.assert_image_has_color('0x000066', img, delta=1) # 60%
    testing.assert_image_has_not_color('0xFF0000', img)
    testing.assert_image_has_not_color('0x0000FF', img)
    testing.assert_image_has_not_color('0x000099', img)

    # atom-level full-transparent (expect only two color values)
    cmd.set('cartoon_transparency', 0.0)
    cmd.set('cartoon_transparency', 1.0, 'sele')
    img = testing.get_imagearray()
    testing.assert_image_has_color('0xFF0000', img)
    # need delta=1 with clang, but not with gcc
    assertNumColorsEqual(img, 2, delta=1)


def _testTransparency(rep, setting_name):
    cmd.fab('GGGG')
    cmd.remove('resi 2+3')
    cmd.select('sele', 'resi 4', 0)

    testing.ambient_only()
    cmd.viewport(100, 100)
    cmd.set('opaque_background')
    cmd.set('ray_shadow', 0)

    cmd.orient()

    cmd.color('0xFF0000')
    cmd.show_as(rep)

    # all opaque
    img = testing.get_imagearray()
    testing.assert_image_has_color('0xFF0000', img)

    # object-level transparency
    cmd.set(setting_name, 0.4)
    img = testing.get_imagearray()
    testing.assert_image_has_color('0x990000', img) # 40%
    testing.assert_image_has_not_color('0xFF0000', img)

    # atom-level full-opaque
    cmd.set(setting_name, 0.0, 'sele')
    img = testing.get_imagearray()
    testing.assert_image_has_color('0x990000', img) # 40%
    testing.assert_image_has_color('0xFF0000', img) #  0%

    # atom-level semi-transparent
    cmd.set(setting_name, 0.6, 'sele')
    img = testing.get_imagearray()
    testing.assert_image_has_color('0x990000', img) # 40%
    testing.assert_image_has_color('0x660000', img, delta=1) # 60%
    testing.assert_image_has_not_color('0xFF0000', img)

    # atom-level full-transparent (expect only two color values)
    cmd.set(setting_name, 0.0)
    cmd.set(setting_name, 1.0, 'sele')
    img = testing.get_imagearray()
    testing.assert_image_has_color('0xFF0000', img)
    # need delta=1 with clang, but not with gcc
    assertNumColorsEqual(img, 2, delta=1)


def testStickTransparency():
    _testTransparency('sticks', 'stick_transparency')


def testSphereTransparency():
    _testTransparency('spheres', 'sphere_transparency')


def testSurfaceTransparency():
    _testTransparency('surface', 'transparency')


def testIsomeshTransparency():
    testing.ambient_only()
    cmd.set('opaque_background')
    cmd.set('gaussian_b_floor', 30)
    cmd.set('mesh_width', 5)
    cmd.fragment('gly', 'm1')
    cmd.hide('everything')
    cmd.map_new('map1', 'gaussian', 0.5, 'm1')
    cmd.isomesh('mesh1', 'map1')

    # global
    cmd.set('transparency', 0.75)
    img = testing.get_imagearray(width=100, height=100)
    testing.assert_image_has_color('0x3F3F3F', img)
    testing.assert_image_has_not_color('0xFFFFFF', img)

    # object-level
    cmd.set('transparency', 0.25, 'mesh1')
    img = testing.get_imagearray(width=100, height=100)
    testing.assert_image_has_color('0xBFBFBF', img)
    testing.assert_image_has_not_color('0xFFFFFF', img)
