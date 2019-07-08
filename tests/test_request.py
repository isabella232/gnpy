#!/usr/bin/env python3
# TelecomInfraProject/gnpy/examples
# Module name : test_request.py
# Version :
# License : BSD 3-Clause Licence
# Copyright (c) 2018, Telecom Infra Project

"""
@author: esther.lerouzic

"""

from pathlib import Path
from json import loads
import pytest
from gnpy.core.equipment import load_equipment, automatic_nch
from gnpy.core.network import load_network, build_network
from gnpy.core.utils import lin2db
from gnpy.core.request import compute_path_dsjctn, Result_element
from gnpy.core.spectrum_assignment import build_oms_list, pth_assign_spectrum
from examples.path_requests_run import (requests_from_json, disjunctions_from_json, correct_disjn,
                                        compute_path_with_disjunction)

TEST_DIR = Path(__file__).parent
DATA_DIR = TEST_DIR / 'data'
EQPT_FILENAME = DATA_DIR / 'eqpt_config.json'
NETWORK_FILENAME = DATA_DIR / 'testTopology_auto_design_expected.json'
SERVICE_FILENAME = DATA_DIR / 'testTopology_services_expected.json'

@pytest.fixture()
def eqpt():
    """ common setup for tests: builds network, equipment and oms only once
    """
    equipment = load_equipment(EQPT_FILENAME)
    return equipment

@pytest.fixture()
def setup(eqpt):
    """ common setup for tests: builds network, equipment and oms only once
    """
    equipment = eqpt
    network = load_network(NETWORK_FILENAME, equipment)
    p_db = equipment['SI']['default'].power_dbm
    p_total_db = p_db + lin2db(automatic_nch(equipment['SI']['default'].f_min,\
        equipment['SI']['default'].f_max, equipment['SI']['default'].spacing))
    build_network(network, equipment, p_db, p_total_db)
    oms_list = build_oms_list(network, equipment)
    return network, oms_list

@pytest.fixture()
def data(eqpt):
    """ common setup for service list: builds service only once
    """
    with open(SERVICE_FILENAME, encoding='utf-8') as my_f:
        data = loads(my_f.read())
    return data

def test_strings(setup, data, eqpt):
    """ test that __str and __repr work
        if print fails it raises an error and test fails
    """
    equipment = eqpt
    rqs = requests_from_json(data, equipment)
    print(rqs[0])
    print(str(rqs[0]))
    dsjn = disjunctions_from_json(data)
    print(dsjn)
    print(str(dsjn[0]))
    dsjn = correct_disjn(dsjn)
    equipment = eqpt
    network, oms_list = setup
    pths = compute_path_dsjctn(network, equipment, rqs, dsjn)
    # print(pths)
    propagatedpths, reversed_pths, reversed_propagatedpths = \
        compute_path_with_disjunction(network, equipment, rqs, pths)
    pth_assign_spectrum(pths, rqs, oms_list, reversed_pths)
    for i, pth in enumerate(propagatedpths):
        print(Result_element(rqs[i], pth).json)
        print(str(Result_element(rqs[i], pth)))
        print('\n\n')

""" test that agregation groups only identical demands, that id is correct concatenation
"""

""" test that identical demands return true with compare request function
"""

""" test that a candidate is correctly removed
"""

""" test that reversed path is really reversed from path
"""

""" test that duplicated disjunction is correctly removed
"""

""" test case when no disjunction path is found
"""

""" tests that best mode is effectively chosen
"""

""" test that path_result is consistant with yang
"""
