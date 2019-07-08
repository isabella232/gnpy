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
import pytest
from copy import deepcopy
from json import loads
from math import ceil
from gnpy.core.equipment import load_equipment, automatic_nch
from gnpy.core.network import load_network, build_network
from gnpy.core.utils import lin2db
from gnpy.core.request import compute_path_dsjctn, find_reversed_path

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
    return network

def test_strings(setup):
    """ test that __str and __repr work
    """

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

