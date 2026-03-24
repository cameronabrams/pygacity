# Author: Cameron F. Abrams, <cfa22@drexel.edu>
"""
Configuration class for pygacity
"""
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

from ..util.stringthings import chmod_recursive_dirs_files

logger = logging.getLogger(__name__)

def _user_cache_base() -> Path:
    """
    Return the platform-appropriate user-level cache root for pygacity.

    * Windows  — ``%LOCALAPPDATA%\\pygacity``
    * macOS    — ``~/Library/Caches/pygacity``
    * Linux    — ``$XDG_CACHE_HOME/pygacity`` (default ``~/.cache/pygacity``)
    """
    if sys.platform == 'win32':
        base = Path(os.environ.get('LOCALAPPDATA', Path.home() / 'AppData' / 'Local'))
    elif sys.platform == 'darwin':
        base = Path.home() / 'Library' / 'Caches'
    else:
        base = Path(os.environ.get('XDG_CACHE_HOME', Path.home() / '.cache'))
    return base / 'pygacity'

def is_executable(cmd: str) -> bool:
    """
    Checks if cmd is an executable in PATH
    
    Parameters
    ----------
    cmd : str
       command name
       
    Returns
    -------
    bool
       True if cmd is found in PATH, False otherwise
    """
    return which(cmd) is not None

class Config:
    """ 
    Configuration class for pygacity
    """
    resource_root = files('pygacity') / 'resources'
    """ Path to pygacity resources directory """

    def __init__(self, args: Namespace = None):
        """
        Initializes the Config instance by loading configuration from a YAML file
        or setting up a singlet build from command-line arguments.
        
        Parameters
        ----------
        args : **argparse.Namespace**, optional
           command-line arguments
        """
        if hasattr(args, 'f') and args.f:
            logger.debug(f'Reading {args.f}...')
            assert os.path.exists(args.f), f'Config file {args.f} not found'
            with open(args.f, 'r', encoding='utf-8') as f:
                self.specs = yaml.safe_load(f)
            assert 'document' in self.specs, f'Your config file does not specify a document structure'
            assert 'build' in self.specs, f'Your config file does not specify document build parameters'
        elif hasattr(args, 'texfile'):
            # singlet problem build
            self.specs = {}
            self.specs['document'], self.specs['build'] = self._config_singlet(args)
        else:
            self.specs = {}
            self.specs['document'] = {}
            self.specs['build'] = {}

        # shortcuts    
        self.document_specs = self.specs['document']
        self.build_specs = self.specs['build']

        logger.debug(f'Build specs: {self.build_specs}')

        self.autoprob_package_root = self.resource_root / 'autoprob-package'
        self.autoprob_package_dir = self.autoprob_package_root / 'tex' / 'latex'
        self.latexmkrc_file = self.resource_root / 'latexmkrc'
        logger.debug(f'autoprob_package_root {self.autoprob_package_root}')
        
        self.progress = self.build_specs.get('progress', False)
        self.templates_root = self.resource_root / 'templates'
        assert os.path.exists(self.templates_root)

        self.platform = sys.platform
        self.home = Path.home()

        self._set_defaults()

        # shortcuts
        self.build_path = Path(self.build_specs['paths']['build-dir'])
        _cache_spec = Path(self.build_specs['paths']['cache-dir'])
        self.cache_path = _cache_spec if _cache_spec.is_absolute() else self.build_path / _cache_spec

        logger.debug(f'Build path: {str(self.build_path)}')
        logger.debug(f'Cache path: {str(self.cache_path)}')

        self._setup_paths(args)

        if 'seed' in self.build_specs:
            random.seed(self.build_specs['seed'])
            logger.info(f'Setting random seed to {self.build_specs["seed"]}.')

        self.solutions = self.build_specs.get('solutions', True)
        self.solution_build_specs = deepcopy(self.build_specs)
        self.solution_build_specs['job-name'] = self.build_specs.get('job-name', 'document') + '_soln'
        self.solution_document_specs = deepcopy(self.document_specs)
        self.solution_document_specs['class']['options'].append('solutions')

    def _config_singlet(self, args: Namespace) -> tuple[dict, dict]:
        """
        Builds a solution document for a single input tex file, no input config needed

        Parameters
        ----------
        args : **argparse.Namespace**
            command-line arguments

        Returns
        -------
        tuple[dict, dict]
            document specs and build specs dictionaries
        """
        tex_sourcefile = args.texfile
        docspecs = {
            'class': {
                'classname': 'autoprob',
                'options': [
                    '11pt'
                ]
            },
            'preamble': {
                'pagestyle': 'single',
            },
            'structure': [
                {'pythontex': [
                    'setup',
                    'matplotlib',
                    'sandler'
                ]},
                {
                    'source': tex_sourcefile,
                    'points': 100,
                    'group': 1
                },
                {'pythontex': [
                    'showsteamtables',
                    'teardown'
                ]},
            ]
        }
        buildspecs = {
            'copies': 1,
            'job-name': Path(tex_sourcefile).stem + '-singlet',
            'paths': {
                'build-dir': './build_singlet',
                'latexmk': 'latexmk',
                'pythontex': 'pythontex'
            }
        }

        return docspecs, buildspecs

    def retrieve_serials(self):
        """
        Retrieves or generates serial numbers for multiple copies
        
        Returns
        -------
        list of int
            list of serial numbers for document copies
        """
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
                # generate 'copies' random serial numbers
                if self.build_specs.get('serial-hex', False):
                    hex_digits = self.build_specs.get('serial-hex-digits', 8)
                    lo, hi = 16 ** (hex_digits - 1), 16 ** hex_digits - 1
                else:
                    serial_digits = self.build_specs.get('serial-digits', len(str(self.build_specs['copies'])))
                    lo, hi = 10 ** (serial_digits - 1), 10 ** serial_digits - 1
                serials = set()
                while len(serials) < self.build_specs['copies']:
                    serials.add(random.randint(lo, hi))
                serials = sorted(serials)
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
        # Backward compatibility: accept legacy pdflatex key but prefer latexmk.
        if 'latexmk' not in self.build_specs['paths'] and 'pdflatex' in self.build_specs['paths']:
            logger.warning('build.paths.pdflatex is deprecated; using default "latexmk" for build.paths.latexmk')
            self.build_specs['paths']['latexmk'] = 'latexmk'

        for cmd in ['latexmk', 'pythontex']:
            if cmd not in self.build_specs['paths']:
                self.build_specs['paths'][cmd] = cmd
                logger.debug(f'Setting default path for {cmd} to "{cmd}"')
                if not is_executable(cmd):
                    if self.platform == 'win32':
                        # default: C:\Users\cfa22\AppData\Local\Programs\MiKTeX\miktex\bin\x64\latexmk.exe
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
        if 'latexmkrc-profile' not in self.build_specs:
            self.build_specs['latexmkrc-profile'] = 'pythontex'
        if self.build_specs['latexmkrc-profile'] not in ['minimal', 'pythontex']:
            raise ValueError(
                f'Unknown build.latexmkrc-profile "{self.build_specs["latexmkrc-profile"]}"; '
                'expected "minimal" or "pythontex"'
            )
        if 'latexmkrc' not in self.build_specs['paths']:
            if self.build_specs['latexmkrc-profile'] == 'pythontex':
                self.build_specs['paths']['latexmkrc'] = str(self.resource_root / 'latexmkrc-pythontex')
            else:
                self.build_specs['paths']['latexmkrc'] = str(self.latexmkrc_file)
        if 'job-name' not in self.build_specs:
            self.build_specs['job-name'] = 'pygacity_document'
        if 'cache-dir' not in self.build_specs['paths']:
            self.build_specs['paths']['cache-dir'] = str(
                _user_cache_base() / self.build_specs['job-name']
            )
        if 'pythontex-workflow' not in self.build_specs:
            self.build_specs['pythontex-workflow'] = 'latexmkrc'
        if 'overwrite' not in self.build_specs:
            self.build_specs['overwrite'] = False
        if 'solutions' not in self.build_specs:
            self.build_specs['solutions'] = True
        if 'copies' not in self.build_specs:
            self.build_specs['copies'] = 1
        if 'serial-digits' not in self.build_specs:
            self.build_specs['serial-digits'] = 8
        if 'serial-hex' not in self.build_specs:
            self.build_specs['serial-hex'] = False
        if 'serial-hex-digits' not in self.build_specs:
            self.build_specs['serial-hex-digits'] = 8
        if 'bundle-size' not in self.build_specs:
            self.build_specs['bundle-size'] = 0
        if 'two-sided' not in self.build_specs:
            self.build_specs['two-sided'] = False
        if 'answer-set' not in self.build_specs:
            self.build_specs['answer-set'] = 'all'

    def format_serial(self, serial: int) -> str:
        """
        Formats a serial number as a string for display and filenames.

        Parameters
        ----------
        serial : int
            the integer serial number

        Returns
        -------
        str
            zero-padded hexadecimal string of width ``build.serial-hex-digits``
            if ``build.serial-hex`` is ``true``, otherwise the plain decimal string
        """
        if self.build_specs.get('serial-hex', False):
            digits = self.build_specs.get('serial-hex-digits', 8)
            return f'{serial:0{digits}x}'
        return str(serial)

    def _setup_paths(self, args: Namespace = None):
        
        build_path: Path = self.build_path
        if not build_path.exists():
            build_path.mkdir(parents=True, exist_ok=True)
        else:
            if hasattr(args, 'overwrite') and args.overwrite:
                permissions = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
                chmod_recursive_dirs_files(build_path)
                rmtree(build_path)
                build_path.mkdir(parents=True, exist_ok=True)
            else:
                raise Exception(f'Build directory "{build_path.as_posix()}" already exists and "--overwrite" was not specified.')

        cache_path: Path = self.cache_path
        if cache_path.exists():
            rmtree(cache_path)
        cache_path.mkdir(parents=True, exist_ok=True)
