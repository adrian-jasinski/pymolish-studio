import pytest
import os
from pymol import cmd, testing, stored, headering

mtzfiles = [
    '/schrodinger/mmshare/mmlibs/mmreflect/10_warpNtrace.mtz',
    '/schrodinger/tasks/other_maps/ec_1.1.mtz',
    '/schrodinger/tasks/other_maps/refine.mtz',
    '/schrodinger/tasks/other_maps/refine_without_eIF1A.mtz',
    '/schrodinger/tmp/1atx4.mtz',
]


def test():
    for filename in mtzfiles:
        if not os.path.exists(filename):
            continue
        header = headering.MTZHeader(filename)
        assert isinstance(header, headering.MTZHeader)
        assert header.datasets


def test2():
    filename = testing.datafile('4rwb.mtz')
    header = headering.MTZHeader(filename)

    assert isinstance(header, headering.MTZHeader)

    ds0 = header.datasets['0']
    assert ds0['name'] == 'HKL_base'
    assert ds0['project'] == 'HKL_base'
    assert float(ds0['alpha']) == pytest.approx(90.0, abs=5e-8)
    assert float(ds0['beta']) == pytest.approx(95.677, abs=5e-8)
    assert float(ds0['gamma']) == pytest.approx(90.0, abs=5e-8)

    ds1 = header.datasets['1']
    assert ds1['name'] == 'data_1'
    assert ds1['project'] == 'sf_convert'
    assert float(ds1['x']) == pytest.approx(40.93, abs=5e-8)
    assert float(ds1['y']) == pytest.approx(41.23, abs=5e-8)
    assert float(ds1['z']) == pytest.approx(27.93, abs=5e-8)

    assert sorted(header.getColumns()) == [
        'HKL_base/HKL_base/H', 'HKL_base/HKL_base/K',
        'HKL_base/HKL_base/L', 'cryst_1/data_1/FC', 'cryst_1/data_1/FOM',
        'cryst_1/data_1/FP', 'cryst_1/data_1/FREE', 'cryst_1/data_1/PHIC',
        'cryst_1/data_1/SIGFP'
    ]

    assert header.getColumnsOfType("W") == ['cryst_1/data_1/FOM']
