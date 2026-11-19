'''
Test that all reps are present.

PYMOL-2222
'''

import os
from pymol import cmd, testing, stored

REPS = [
    'sticks',
    'labels',
    'surface',
    'ribbon',
    # 'cartoon',
    # 'ellipsoids',     # PYMOL-1356
    'dots',
    'nonbonded',
    'nb_spheres',
    'mesh',
    'lines',
    'spheres',

    'dashes',
    'angles',
    'dihedrals',

    # 'cell',
    # 'extent',

    # 'slice',
    # 'callback',
    # 'cgo',
    # 'volume',
]

CARTOONS = [
    'putty',
    'rectangle',
    'arrow',
    'oval',
    # 'skip',
    'tube',
    'dumbbell',
    # 'automatic',
    'loop',
]


def testRepsExist():
    cmd.viewport(200, 150)
    cmd.load(testing.datafile('1oky-frag.pdb'), 'm1')

    # make some nonbonded
    cmd.unbond('resi 115-', 'resi 115-')

    # labels
    cmd.label('all', 'name')

    # measurements
    cmd.distance('measure1', 'index 1', 'index 10')
    cmd.angle('measure1', 'index 1', 'index 10', 'index 20')
    cmd.dihedral('measure1', 'index 1', 'index 10', 'index 20', 'index 30')

    # color test setup
    cmd.color('white', '*')
    cmd.set('ambient', 1)
    cmd.set('depth_cue', 0)
    cmd.set('antialias', 0)
    cmd.set('line_smooth', 0)
    cmd.orient()

    # test most reps
    for rep in REPS:
        cmd.show_as(rep)
        testing.assert_image_has_color('white', msg='rep missing: ' + rep)

    # test cartoon
    cmd.show_as('cartoon')
    for cart in CARTOONS:
        cmd.cartoon(cart)
        testing.assert_image_has_color('white', msg='cartoon missing: ' + cart)


@testing.requires('incentive')
def test_sphere_mode_10_11():
    cmd.viewport(200, 100)
    cmd.set('orthoscopic')
    cmd.set('opaque_background')
    cmd.pseudoatom('m1', pos=(1, 2, 3), vdw=1.3, color='blue')
    cmd.pseudoatom('m1', pos=(5, 2, 3), vdw=2.5, color='red')
    cmd.zoom()
    cmd.turn('x', 45)
    testing.ambient_only()
    cmd.show_as('spheres')
    cmd.set('sphere_mode', 10)  # cubes
    testing.assert_image_equal('ref/sphere_mode_10.png')
    cmd.set('sphere_mode', 11)  # tetrahedra
    testing.assert_image_equal('ref/sphere_mode_11.png')
