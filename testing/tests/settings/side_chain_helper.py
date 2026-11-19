'''
test side chain helper settings

cartoon_side_chain_helper
cartoon_nucleic_acid_mode
ribbon_side_chain_helper
ribbon_nucleic_acid_mode
'''

import pytest
from pymol import cmd, testing


@pytest.mark.parametrize("bb_rep", ['cartoon', 'ribbon'])                 # X_nucleic_acid_mode
@pytest.mark.parametrize("sc_rep", ['sticks', 'lines'])                 # X_nucleic_acid_mode
@pytest.mark.parametrize("bb_set", ['cartoon', 'ribbon'])                 # X_nucleic_acid_mode
@pytest.mark.parametrize("n_a_m", [0, 1])                 # X_nucleic_acid_mode
def test(bb_rep, sc_rep, bb_set, n_a_m):
    cmd.viewport(100, 100)

    # color classes
    color = {'cartoon': 'blue', 'ribbon': 'red'}
    sc_color = 'white'
    op_color = 'green'
    p_color = 'yellow'

    # lighting setup for color testing
    testing.ambient_only()
    cmd.set('dynamic_width', 0)
    cmd.set('line_width', 4)
    cmd.set('ribbon_width', 4)

    # settings setup
    cmd.set(bb_set + '_side_chain_helper')
    cmd.set(bb_set + '_nucleic_acid_mode', n_a_m)
    cmd.set('ribbon_color', color['ribbon'])
    cmd.set('cartoon_color', color['cartoon'])

    # data
    cmd.load(testing.datafile('1ehz-5.pdb'))
    cmd.orient()

    # atom colors
    cmd.color(sc_color)
    cmd.color(op_color, "name OP1+OP2")         # not visible with SCH
    cmd.color(p_color, "name P+O3'+C5'+O5'")    # not visible with SCH and NAM=1

    # need to check for OP1 and O1P naming scheme, so alter some atoms
    cmd.alter('name OP1 & resi 1-2', 'name="O1P"')
    cmd.alter('name OP2 & resi 1-2', 'name="O2P"')

    # reps
    cmd.show_as(bb_rep)
    cmd.show(sc_rep)

    # test
    img = testing.get_imagearray()
    testing.assert_image_has_color(sc_color, img) # always visible
    for bb_test in ['cartoon', 'ribbon']:
        testing._assert_image_has_color(bb_rep == bb_test, color[bb_test], img, 0, bb_test + ' wrong')
    testing._assert_image_has_color(not (bb_rep == bb_set), op_color, img, 0, 'OP wrong')
    testing._assert_image_has_color(not (bb_rep == bb_set and n_a_m == 1), p_color, img, 0, 'NAM=1 wrong')
