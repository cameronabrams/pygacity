# Author: Cameron F. Abrams, <cfa22@drexel.edu>
import os
import logging

from importlib.metadata import version
from importlib.resources import files
from ycleptic.yclept import Yclept

from ..util.stringthings import my_logger

logger = logging.getLogger(__name__)

class Config(Yclept):
    def __init__(self, userfile='' ,**kwargs):
        vrep = f"""ycleptic v. {version("ycleptic")}"""
        quiet = kwargs.get('quiet',False)
        if not quiet:
            my_logger(vrep,logger.info, just='<', frame='*', fill='', no_indent=True)
        self.resource_root = files('pygacity') / 'resources'
        config_dir = self.resource_root / 'config'
        base_yaml = config_dir / 'base.yaml'
        assert os.path.exists(base_yaml)
        super().__init__(base_yaml, userfile=userfile)

        self.specs = self['user']
        assert 'document' in self.specs, f'Your config file does not specify a document structure'
        assert 'build' in self.specs, f'Your config file does not specify document build parameters'
        self.document_specs = self.specs['document']
        self.build_specs = self.specs['build']
        
        self.autoprob_package_root = self.resource_root / 'autoprob-package'
        self.autoprob_package_dir = self.autoprob_package_root / 'tex' / 'latex'
        logger.debug(f'autoprob_package_root {self.autoprob_package_root}')
        
        self.progress = kwargs.get('progress', False)
        self.templates_root = self.resource_root / 'templates'
        assert os.path.exists(self.templates_root)
