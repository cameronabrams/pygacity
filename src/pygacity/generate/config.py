# Author: Cameron F. Abrams, <cfa22@drexel.edu>
import logging
import os
import random
import stat
import sys
import yaml


from argparse import Namespace
from copy import deepcopy
from importlib.resources import files
from pathlib import Path
from shutil import which, rmtree

from ..util.stringthings import chmod_recursive

logger = logging.getLogger(__name__)

def is_executable(cmd: str) -> bool:
    return which(cmd) is not None

class Config:
    """ 
    Configuration class for pygacity
    """
    resource_root = files('pygacity') / 'resources'
    def __init__(self, args: Namespace = None):

        if hasattr(args, 'f') and args.f:
            logger.debug(f'Reading {args.f}...')
            assert os.path.exists(args.f), f'Config file {args.f} not found'
            with open(args.f, 'r', encoding='utf-8') as f:
                self.specs = yaml.safe_load(f)
            assert 'document' in self.specs, f'Your config file does not specify a document structure'
            assert 'build' in self.specs, f'Your config file does not specify document build parameters'
        elif hasattr(args, 'texfile') and args.texfile:
            # singlet problem build
            self.specs['document'], self.specs['build'] = self._config_singlet(args)
        else:
            self.specs['document'] = {}
            self.specs['build'] = {}

        # shortcuts    
        self.document_specs = self.specs['document']
        self.build_specs = self.specs['build']

        logger.debug(f'Build specs: {self.build_specs}')

        self.autoprob_package_root = self.resource_root / 'autoprob-package'
        self.autoprob_package_dir = self.autoprob_package_root / 'tex' / 'latex'
        logger.debug(f'autoprob_package_root {self.autoprob_package_root}')
        
        self.progress = self.build_specs.get('progress', False)
        self.templates_root = self.resource_root / 'templates'
        assert os.path.exists(self.templates_root)

        self.platform = sys.platform
        self.home = Path.home()

        self._set_defaults()

        # shortcuts
        self.build_path = Path(self.build_specs['paths']['build-dir'])
        self.cache_path = self.build_path / self.build_specs['paths']['cache-dir']

        logger.debug(f'Build path: {str(self.build_path)}')
        logger.debug(f'Cache path: {str(self.cache_path)}')

        self._setup_paths(args)

        if 'seed' in self.build_specs:
            random.seed(self.build_specs['seed'])
            logger.info(f'Setting random seed to {self.build_specs["seed"]}.')

        self.solutions = False
        if hasattr(args, 'solutions') and args.solutions:
            self.solutions = True
            self.solution_build_specs = deepcopy(self.build_specs)
            self.solution_build_specs['job-name'] = self.build_specs.get('job-name', 'document') + '_soln'
            self.solution_document_specs = deepcopy(self.document_specs)
            self.solution_document_specs['class']['options'].append('solutions')

    def _config_singlet(self, args):
        """
        Builds a solution document for a single input tex file, no input config needed
        """
        tex_sourcefile = args.texfile
        docspecs = {
            'class': {
                'classname': 'autoprob',
                'options': [
                    '11pt',
                    'solutions'
                ]
            },
            'preamble': r"""
\usepackage[T1]{fontenc}
\usepackage{tgheros}
\renewcommand{\sfdefault}{qhv}
\renewcommand{\familydefault}{\sfdefault}""",
            'structure': [
                {'text': r'\begin{document}'},
                {'pythontex': [
                    'setup',
                    'matplotlib',
                    'sandlersteam',
                    'chemeq'
                ]},
                {'enumerate':[
                    {'source': tex_sourcefile,
                    'points': 100,
                    'group': 1}
                ]},
                {'pythontex': [
                    'showsteamtables',
                    'teardown'
                ]},
                {'text': r'\end{document}'}
            ]
        }
        buildspecs = {
            'copies': 1,
            'job-name': Path(tex_sourcefile).stem + '-singlet',
            'paths': {
                'build-dir': './build_singlet',
                'pdflatex': 'pdflatex',
                'pythontex': 'pythontex'
            }
        }

        return docspecs, buildspecs

    def retrieve_serials(self):
        if self.build_specs.get('copies', 1) > 1:
            if self.build_specs.get('serials', None):
                # check for explict serials
                serials = [int(x) for x in self.build_specs['serials']]
            elif self.build_specs.get('serial-range', None):
                # check for a serial range
                serials = list(range(self.build_specs['serial-range'][0],
                                    self.build_specs['serial-range'][1] + 1))
            elif self.build_specs.get('serial-file', None):
                # check for a file containing serials, one integer per line
                with open(self.build_specs['serial-file'], 'r') as f:
                    serials = [int(line.strip()) for line in f if line.strip()]
            else:
                serial_digits = self.build_specs.get('serial-digits', len(str(self.build_specs['copies'])))
                # generate 'copies' random serial numbers
                serials = set()
                while len(serials) < self.build_specs['copies']:
                    serial = random.randint(10**(serial_digits-1), 10**serial_digits - 1)
                    serials.add(serial)
                serials = list(serials)
                serials.sort()
        else:
            if self.build_specs.get('serials', None):
                # check for explict serials
                serials = [int(x) for x in self.build_specs['serials']]
            else:
                serials = [0]
        return serials

    def _set_defaults(self):
        if 'class' not in self.document_specs:
            self.document_specs['class'] = {
                'classname': 'autoprob',
                'options': ['11pt']
            }
        if 'structure' not in self.document_specs:
            self.document_specs['structure'] = []
        if 'substitutions' not in self.document_specs:
            self.document_specs['substitutions'] = {}
        if 'paths' not in self.build_specs:
            self.build_specs['paths'] = {}
        for cmd in ['pdflatex', 'pythontex']:
            if cmd not in self.build_specs['paths']:
                self.build_specs['paths'][cmd] = cmd
                logger.debug(f'Setting default path for {cmd} to "{cmd}"')
                if not is_executable(cmd):
                    if self.platform == 'win32':
                        # default: C:\Users\cfa22\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe
                        self.build_specs['paths'][cmd] = self.home / 'AppData' / 'Local' / 'Programs' / 'MiKTeX' / 'miktex' / 'bin' / 'x64' / f'{cmd}.exe'
                        cmd = str(self.build_specs['paths'][cmd])
                        if not is_executable(cmd):
                            raise ValueError(f'{cmd} executable not found in PATH; please specify its location in the config file')
                    else:
                        raise ValueError(f'{cmd} executable not found in PATH; please specify its location in the config file')
                else:
                    logger.debug(f'Found {cmd} executable in PATH')
        if 'build-dir' not in self.build_specs['paths']:
            self.build_specs['paths']['build-dir'] = 'build'
        if 'cache-dir' not in self.build_specs['paths']:
            self.build_specs['paths']['cache-dir'] = '.cache'
        if 'job-name' not in self.build_specs:
            self.build_specs['job-name'] = 'pygacity_document'
        if 'overwrite' not in self.build_specs:
            self.build_specs['overwrite'] = False
        if 'solutions' not in self.build_specs:
            self.build_specs['solutions'] = True
        if 'copies' not in self.build_specs:
            self.build_specs['copies'] = 1
        if 'serial-digits' not in self.build_specs:
            self.build_specs['serial-digits'] = 8
        if 'answer-set' not in self.build_specs:
            self.build_specs['answer-set'] = 'all'

    def _setup_paths(self, args: Namespace = None):
        
        build_path: Path = self.build_path
        if not build_path.exists():
            build_path.mkdir(parents=True, exist_ok=True)
        else:
            if hasattr(args, 'overwrite') and args.overwrite:
                permissions = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
                chmod_recursive(build_path, permissions)
                rmtree(build_path)
                build_path.mkdir(parents=True, exist_ok=True)
            else:
                raise Exception(f'Build directory "{build_path.as_posix()}" already exists and "--overwrite" was not specified.')

        cache_path: Path = self.cache_path
        if not cache_path.exists():
            cache_path.mkdir(parents=True, exist_ok=True)
