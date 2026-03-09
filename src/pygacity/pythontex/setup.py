import yaml
import random
import numpy as np
import fractions as fr
import logging
import pickle
import os
import sys

from argparse import Namespace
from pathlib import Path

import pygacity.pythontex.texutils as tu
from pygacity.generate.answerset import AnswerSet
from pygacity.generate.pick import Picker
from pygacity.util.collectors import FileCollector

# pythontex_module is the __main__ module where pythontex code is executed
# during document compilation
pythontex_module = sys.modules['__main__']
serial: int = getattr(pythontex_module, 'serial', 0)
serialstr: str = getattr(pythontex_module, 'serialstr', str(serial))
build_dir: str = getattr(pythontex_module, '_build_dir', '.')
cache_dir: str = getattr(pythontex_module, '_cache_dir', '.cache')
is_solutions: bool = getattr(pythontex_module, 'solutions', False)
log_level: str = getattr(pythontex_module, 'log_level', 'DEBUG')

_loglevel_numeric = getattr(logging, log_level.upper())
_pythontex_logfile = f'pythontex-{serial}.log'
if is_solutions:
    _pythontex_logfile = f'pythontex-solutions-{serial}.log'
logging.basicConfig(filename=_pythontex_logfile,
                    filemode='w',
                    format='%(asctime)s %(name)s %(message)s',
                    level=_loglevel_numeric)
logger = logging.getLogger(__name__)
logger.debug(f'Pygacity pythontex module begins')
logger.debug(f'Pythontex serial:    {serial}')
logger.debug(f'Pythontex solutions: {is_solutions}')
logger.debug(f'Pythontex build_dir: {build_dir} (pythontex runs with this as CWD)')
logger.debug(f'Pythontex cache_dir: {cache_dir}')
logger.debug(f'Pythontex logfile:   {_pythontex_logfile}')

# Pythontex runs in the directory that contains the pytxcode file(s), which
# may be different than the CWD of the manager if the user specified a 
# build directory relative to that CWD
manager_pickle_cache = Path(cache_dir)
manager_build_path = Path(build_dir)
pythontex_pickle_cache = manager_pickle_cache.relative_to(manager_build_path)
logger.debug(f'Pickling to {pythontex_pickle_cache.as_posix()}')

last_qno = 0

rng = np.random.default_rng(seed=serial)
Pick = Picker(serial=serial)
AnsSet = AnswerSet(serial=serial, serialstr=serialstr)
pythontexFC = FileCollector()
logger.debug(f'rng at {id(rng)}')
logger.debug(f'Pick at {id(Pick)}')
logger.debug(f'AnsSet at {id(AnsSet)}')
logger.debug(f'pythontexFC at {id(pythontexFC)}')
logger.debug(f'Pygacity pythontex module setup complete')