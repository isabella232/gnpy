#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: Esther Le Rouzic
# @Date:   2019-06-07
"""
@author: esther.lerouzic
checks that json created with yang modules are consistant with gnpy example topologies

"""

from os import system, unlink, mkdir, path, remove
from pathlib import Path
from pprint import PrettyPrinter
from shutil import rmtree
import pyangbind
# from importlib import import_module
import pyangbind.lib.pybindJSON as pbJ
import pytest
import git


TEST_DIR = Path(__file__).parent
YANG_DIR = Path(__file__).parent.parent / 'yangModels'
DATA_DIR = TEST_DIR / 'data'
EQPT_LIBRARY_NAME = TEST_DIR / 'data/eqpt_config.json'
NETWORK_FILE_NAME = TEST_DIR / 'data/testTopology_expected.json'
TEMP_DIR = TEST_DIR / 'ietf_library'
try:
    rmtree(TEMP_DIR)
except FileNotFoundError:
    pass
try:
    mkdir(TEMP_DIR)
except OSError:
    print(f'Creation of the {TEMP_DIR} directory failed.')
print(f'Creation of the {TEMP_DIR} directory')
# retrieve ietf models from official github repo
git.Repo.clone_from('https://github.com/YangModels/yang.git',\
                    TEMP_DIR, branch='master', depth=1)

EXPORT_string = path.dirname(pyangbind.__file__)

system(f'export PYBINDPLUGIN=`/usr/bin/env python -c {EXPORT_string}`')

@pytest.mark.parametrize('yang_input', [
    YANG_DIR / 'gnpy-network-topology@2019-02-19.yang',
    YANG_DIR / 'gnpy-path-computation-simplified@2019-05-07.yang'])
def test_compile(yang_input):
    """ test that yang is correct by generating the tree
        if the generation fails then the test fails
    """
    tree_file = TEST_DIR /'test.tree'
    print(tree_file)

    my_cmd = f'pyang -f tree -p {TEMP_DIR} {yang_input} -o {tree_file}'
    system(my_cmd)
    try:
        with open(tree_file) as expected:
            expected_tree = expected.read()
        print(f'expected : \n{expected_tree}')
    except FileNotFoundError:
        raise AssertionError()
    unlink(tree_file)

@pytest.mark.parametrize('json_file, yang_model', \
    {
        TEST_DIR / 'LinkforTest.json':\
        YANG_DIR / 'gnpy-network-topology@2019-02-19.yang'
        # this file does not work because yang has not been updated with 
        # restrictions
        # DATA_DIR / 'testTopology_expected.json':\
        # YANG_DIR / 'gnpy-network-topology@2019-02-19.yang'
        # pyangbind does not support bits type yet so we can not
        # test path_computation module yet
        # to uncomment when this will be solved
        # DATA_DIR / 'testTopology_service_expected.json':\
        #     YANG_DIR / 'gnpy-path-computation-simplified@2019-01-07.yang'
    }.items())
def test_yang_against_json(json_file, yang_model):
    """ test that current json example comply to the yang
    """
    model_name = str(yang_model.stem).split('@')[0]
    print('model_name', model_name)
    binding_py = model_name.replace('-', '_') + '.py'
    print('binding_py', binding_py)
    binding_py_absolute_path = TEST_DIR / binding_py
    # remove previous binder version
    try:
        remove(binding_py_absolute_path)
    except FileNotFoundError:
        pass
    system(f'pyang --plugindir $PYBINDPLUGIN -f pybind -p {TEMP_DIR} \
             -o {binding_py_absolute_path} {yang_model}')
    print(EXPORT_string)

    # binding module must be gnpy_network_topology or gnpy_eqpt_config
    # or gnpy_path_computation_simplified but
    # module = import_module(<variable>, package=None)
    # does not work so I have hardcoded the modules name
    my_pp = PrettyPrinter(indent=2)
    if 'gnpy-network-topology' in str(yang_model):
        import gnpy_network_topology
        loaded_ietf_obj = pbJ.load_ietf(json_file, gnpy_network_topology, model_name)
    if 'gnpy-path-computation-simplified' in str(yang_model):
        import gnpy_path_computation_simplified
        loaded_ietf_obj = pbJ.load_ietf(json_file, gnpy_path_computation_simplified, model_name)
    my_pp.pprint(loaded_ietf_obj.get(filter=True))

