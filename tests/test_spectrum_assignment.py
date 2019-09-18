#!/usr/bin/env python3
# TelecomInfraProject/gnpy/examples
# Module name : test_spectrum_assignment.py
# Version :
# License : BSD 3-Clause Licence
# Copyright (c) 2018, Telecom Infra Project

"""
@author: esther.lerouzic

"""

from pathlib import Path
from copy import deepcopy
from json import loads
from math import ceil
import pytest
from gnpy.core.equipment import load_equipment, automatic_nch
from gnpy.core.network import load_network, build_network
from gnpy.core.utils import lin2db
from gnpy.core.elements import Roadm
from gnpy.core.spectrum_assignment import (build_oms_list, align_grids, nvalue_to_frequency,
                                           bitmap_sum, m_to_freq, slots_to_m, frequency_to_n,
                                           Bitmap)
from gnpy.core.exceptions import SpectrumError

TEST_DIR = Path(__file__).parent
DATA_DIR = TEST_DIR / 'data'
EQPT_FILENAME = DATA_DIR / 'eqpt_config.json'
NETWORK_FILENAME = DATA_DIR / 'testTopology_auto_design_expected.json'

@pytest.fixture()
def setup():
    """ common setup for tests: builds network, equipment and oms only once
    """
    equipment = load_equipment(EQPT_FILENAME)
    # fix band to be independant of changes in json file
    equipment['SI']['default'].f_min = 191300000000000.0
    equipment['SI']['default'].f_max = 196100000000000.0
    network = load_network(NETWORK_FILENAME, equipment)
    p_db = equipment['SI']['default'].power_dbm
    p_total_db = p_db + lin2db(automatic_nch(equipment['SI']['default'].f_min,\
        equipment['SI']['default'].f_max, equipment['SI']['default'].spacing))
    build_network(network, equipment, p_db, p_total_db)
    oms_list = build_oms_list(network, equipment)
    return network, oms_list

def test_oms(setup):
    """ tests that the oms is between two roadms, that there is no roadm or transceivers in the oms
        except end points, checks that the id of oms is present in the element and that the element
        oms id is consistant
    """
    network, oms_list = setup
    for oms in oms_list:
        if not isinstance(oms.el_list[0], Roadm) or not isinstance(oms.el_list[-1], Roadm):
            raise AssertionError()
        for i, elem in enumerate(oms.el_list[1:-2]):
            if isinstance(elem, Roadm):
                raise AssertionError()
            if elem not in network.nodes():
                raise AssertionError()
            if elem.oms.oms_id != oms.oms_id:
                raise AssertionError()
            if elem.uid != oms.el_id_list[i+1]:
                print(f'expected {elem.uid}, obtained {oms.el_id_list[i+1]}')
                raise AssertionError()

@pytest.mark.parametrize('nmin', [-288, -260, -300])
@pytest.mark.parametrize('nmax', [480, 320, 450])
def test_aligned(nmin, nmax, setup):
    """ checks that the oms grid is correctly aligned. Note that bitmap index uses guardband
        on both ends so that if nmin, nmax = -200, +200, min/max navalue in bitmap are
        -224, +223, which makes 223 -(-224) +1 frequencies
    """
    network, oms_list = setup
    # f_min = 193.1e12 - 280 * 0.00625e12
    # f_max = 193.1e12 + 320 * 0.00625e12
    # f_min = 1931.1 f_max = 195.1
    grid = 0.00625e12
    guardband = 0.15e12
    nguard = 24
    freq_min = 193.1e12 + nmin * 0.00625e12
    freq_max = 193.1e12 + nmax * 0.00625e12
    print('initial spectrum')
    print(nvalue_to_frequency(oms_list[10].spectrum_bitmap.freq_index_min)*1e-12,
          nvalue_to_frequency(oms_list[10].spectrum_bitmap.freq_index_max)*1e-12)
    # checks initial values consistancy
    ind_max = len(oms_list[10].spectrum_bitmap.bitmap) - 1
    print('with guardband', oms_list[10].spectrum_bitmap.getn(0),
          oms_list[10].spectrum_bitmap.getn(ind_max))
    print('without guardband', oms_list[10].spectrum_bitmap.freq_index_min,
          oms_list[10].spectrum_bitmap.freq_index_max)
    nvalmin = oms_list[10].spectrum_bitmap.getn(0) + nguard
    nvalmax = oms_list[10].spectrum_bitmap.getn(ind_max) - nguard + 1

    # min index in bitmap must be consistant with min freq attribute
    if nvalmin != oms_list[10].spectrum_bitmap.freq_index_min:
        print(f'test1 expected: {nvalmin}')
        print(f'freq_index_min : {oms_list[10].spectrum_bitmap.freq_index_min},')
        raise AssertionError('inconsistancy in Bitmap object')
    if nvalmax != oms_list[10].spectrum_bitmap.freq_index_max:
        print(f'test2 expected: {nvalmax}')
        print(f'freq_index_max: {oms_list[10].spectrum_bitmap.freq_index_max}')
        raise AssertionError('inconsistancy in Bitmap object')
    oms_list[10].update_spectrum(freq_min, freq_max, grid=grid, guardband=guardband)
    # checks that changes are applied on bitmap and freq attributes of Bitmap object
    if (nmin != oms_list[10].spectrum_bitmap.freq_index_min or
            nmax != oms_list[10].spectrum_bitmap.freq_index_max):
        print(f'expected: {nmin}, {nmax}')
        print(f'test3 obtained: {oms_list[10].spectrum_bitmap.freq_index_min},' +\
              f' {oms_list[10].spectrum_bitmap.freq_index_max}')
        raise AssertionError()

    print('novel spectrum')
    print(nvalue_to_frequency(oms_list[10].spectrum_bitmap.freq_index_min)*1e-12,
          nvalue_to_frequency(oms_list[10].spectrum_bitmap.freq_index_max)*1e-12)
    ind_max = len(oms_list[10].spectrum_bitmap.bitmap) - 1
    print('with guardband', oms_list[10].spectrum_bitmap.getn(0),
          oms_list[10].spectrum_bitmap.getn(ind_max))
    print('without guardband', oms_list[10].spectrum_bitmap.freq_index_min,
          oms_list[10].spectrum_bitmap.freq_index_max)
    nvalmin = oms_list[10].spectrum_bitmap.getn(0) + nguard
    nvalmax = oms_list[10].spectrum_bitmap.getn(ind_max) - nguard + 1
    # min index in bitmap must be consistant with min freq attribute
    if nvalmin != oms_list[10].spectrum_bitmap.freq_index_min:
        print(f'expected: {nvalmin}')
        print(f'freq_index_min : {oms_list[10].spectrum_bitmap.freq_index_min},')
        raise AssertionError('inconsistancy in Bitmap object')
    if nvalmax != oms_list[10].spectrum_bitmap.freq_index_max:
        print(f'expected: {nvalmax}')
        print(f'freq_index_max: {oms_list[10].spectrum_bitmap.freq_index_max}')
        raise AssertionError('inconsistancy in Bitmap object')
    oms_list = align_grids(oms_list)
    ind_max = len(oms_list[10].spectrum_bitmap.bitmap) - 1
    nvalmin = oms_list[10].spectrum_bitmap.getn(0)
    nvalmax = oms_list[10].spectrum_bitmap.getn(ind_max)
    print(f'expected: {min(nmin, nvalmin)}, {max(nmax, nvalmax)}')
    if nvalmin > nmin or nvalmax < nmax:
        print(f'expected: {nmin, nmax}')
        print(f'obtained after alignment: {nvalmin}, {nvalmax}')
        raise AssertionError()

@pytest.mark.parametrize('nval1', [0, 15, 24])
@pytest.mark.parametrize('nval2', [8, 12])
def test_assign_and_sum(nval1, nval2, setup):
    """ checks that bitmap sum gives correct result
    """
    network, oms_list = setup
    grid = 0.00625e12
    guardband = grid
    mval = 4 # slot in 12.5GHz
    freq_min = 193.1e12
    freq_max = 193.1e12 + 24 * 0.00625e12
    # arbitrary test on oms #10 and #11
    # first reduce the grid to 24 center frequencies to ease reading when test fails
    oms1 = oms_list[10]
    oms1.update_spectrum(freq_min, freq_max, grid=grid, guardband=guardband)
    oms2 = oms_list[11]
    oms2.update_spectrum(freq_min, freq_max, grid=grid, guardband=guardband)
    print('initial spectrum')
    print(nvalue_to_frequency(oms_list[10].spectrum_bitmap.freq_index_min)*1e-12,
          nvalue_to_frequency(oms_list[10].spectrum_bitmap.freq_index_max)*1e-12)
    # checks initial values consistancy
    ind_max = len(oms_list[10].spectrum_bitmap.bitmap) - 1
    print('with guardband', oms_list[10].spectrum_bitmap.getn(0),
          oms_list[10].spectrum_bitmap.getn(ind_max))
    print('without guardband', oms_list[10].spectrum_bitmap.freq_index_min,
          oms_list[10].spectrum_bitmap.freq_index_max)
    test1 = oms1.assign_spectrum(nval1, mval)
    print(oms1.spectrum_bitmap.bitmap)
    # if requested slots exceed grid spectrum should not be assigned and assignment
    # should return False
    if ((nval1 - mval) < oms1.spectrum_bitmap.getn(0) or
            (nval1 + mval-1) > oms1.spectrum_bitmap.getn(ind_max)):
        if test1:
            raise AssertionError('assignment on part of bitmap is not allowed')
        for elem in oms1.spectrum_bitmap.bitmap:
            if elem != 1:
                raise AssertionError
    else:
        oms2.assign_spectrum(nval2, mval)
        print(oms2.spectrum_bitmap.bitmap)
        test2 = bitmap_sum(oms1.spectrum_bitmap.bitmap, oms2.spectrum_bitmap.bitmap)
        print(test2)
        range1 = range(oms1.spectrum_bitmap.geti(nval1) - mval,
                       oms1.spectrum_bitmap.geti(nval1) + mval -1)
        range2 = range(oms2.spectrum_bitmap.geti(nval2) - mval,
                       oms2.spectrum_bitmap.geti(nval2) + mval -1)
        for elem in range1:
            if test2[elem] != 0:
                print(f'value should be zero at index {elem}')
                raise AssertionError
        for elem in range2:
            if test2[elem] != 0:
                print(f'value should be zero at index {elem}')
                raise AssertionError

def test_values(setup):
    """ checks that oms.assign_spectrum(13,7) is (193137500000000.0, 193225000000000.0)
        reference to Recommendation G.694.1 (02/12), Figure I.3
        https://www.itu.int/rec/T-REC-G.694.1-201202-I/en
    """
    network, oms_list = setup

    oms_list[5].assign_spectrum(13, 7)
    fstart, fstop = m_to_freq(13, 7)
    if fstart != 193.1375e12 or fstop != 193.225*1e12:
        print('expected: 193137500000000.0, 193225000000000.0')
        print(f'obtained: {fstart}, {fstop}')
        raise AssertionError()
    nstart = frequency_to_n(fstart)
    nstop = frequency_to_n(fstop)
    # nval, mval = slots_to_m(7, 20)
    nval, mval = slots_to_m(nstart, nstop)
    if nval != 13 or mval != 7:
        print('expected n, m: 13, 7')
        print(f'obtained: {nval}, {mval}')
        raise AssertionError()

""" checks spectrum selection function: if n is given, if n is empty
"""

""" checks that spectrum is correctly assigned
"""

