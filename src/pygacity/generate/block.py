# Author: Cameron F. Abrams, <cfa22@drexel.edu>
import logging
import os
import re

from importlib.resources import files
from pathlib import Path
from shutil import copy2

logger = logging.getLogger(__name__)

def path_resolver(filename: str, search_paths: list[Path] = [], ext: str ='') -> Path:
    local_filename = filename if filename.endswith(ext) else filename + ext
    # check local directory first
    local_path = Path(local_filename)
    if local_path.exists():
        return local_path
    # check search path next
    else:
        for search_path in search_paths:
            template_path = search_path / local_filename
            if template_path.exists():
                return template_path
        spm = ':'.join([str(sp) for sp in search_paths])
        raise FileNotFoundError((f'Could not locate source file {local_filename} in cwd ({os.getcwd()}) '
                                 f'or search path {spm}.'))

class LatexSimpleBlock:
    resources_root: Path = files('pygacity') / 'resources'
    templates_dir: Path = resources_root / 'templates'
    substitution_delimiters: tuple = (r'<<<', r'>>>')

    def __init__(self, block_specs: dict):
        self.block_specs = block_specs
        self.filename: str = block_specs.get('source', None)
        self.path = Path(self.filename) if self.filename else None
        self.substitution_map: dict = block_specs.get('substitutions', {})
        self.has_pycode: bool = False
        self.embedded_graphics: list[str | Path] = []
        self.rawcontents: str = block_specs.get('content', '')
        self.processedcontents: str = ''
        self.points: int = block_specs.get('points', 0)
        self.config_filename: str = block_specs.get('config', None)
        self.config_path = Path(self.config_filename) if self.config_filename else None

    def load(self):
        if self.rawcontents == '':
            self.path = path_resolver(self.filename, search_paths=[self.templates_dir])
            with open(self.path, 'r') as f:
                self.rawcontents = f.read()
        self.has_pycode = r'\begin{pycode}' in self.rawcontents
        # check contents for substitution keys and embedded graphics files
        KEY_RE = re.compile(rf'{self.substitution_delimiters[0]}\s*([A-Za-z0-9_-]+)\s*{self.substitution_delimiters[1]}')
        for line in self.rawcontents.split('\n'):
            keys = set(KEY_RE.findall(line))
            for key in keys:
                if not key in self.substitution_map:
                    self.substitution_map[key] = None
            # check for embedded graphics
            GRAPHICS_RE = re.compile(r'\\includegraphics(?:\[[^\]]*\])?\{([^\}]+)\}')
            graphics_files = GRAPHICS_RE.findall(line)
            for gf in graphics_files:
                if gf not in self.embedded_graphics:
                    self.embedded_graphics.append(gf)
        self.processedcontents = self.rawcontents[:]
        if self.config_path:
            if not self.config_path.exists():
                raise FileNotFoundError(f'Configuration file {self.config_path} does not exist.')
            self.substitution_map['config'] = self.config_path.name
        return self

    def substitute(self, super_substitutions: dict = {}, match_all: bool = True):
        substitutions = self.substitution_map.copy()
        substitutions.update(super_substitutions)
        for key, value in substitutions.items():
            if key in self.substitution_map:
                self.substitution_map[key] = value
        logger.debug(f'LatexSimpleBlock.substitute with substitutions: {self.substitution_map}')
        # apply substitutions to the contents
        for key, value in self.substitution_map.items():
            if value is not None:
                self.processedcontents = self.processedcontents.replace(f'{self.substitution_delimiters[0]}{key}{self.substitution_delimiters[1]}', str(value))
            elif match_all:
                raise KeyError(f'Substitution key {key} has no associated value for input file {self.path.name}')

    def copy_referenced_configs(self, output_dir: str):
        if self.config_path and self.config_path.exists():
            dest_path = Path(output_dir) / self.config_path.name
            if not dest_path.exists():
                copy2(self.config_path, dest_path)
                logger.debug(f'Copied config file {self.config_path} to {dest_path}')

    def __str__(self):
        return self.processedcontents

class LatexListBlock:
    def __init__(self, block_specs: dict = {}):
        self.item_specs = block_specs.get('items', [])
        self.list_type = block_specs.get('type', 'enumerate')
        self.items: list[LatexSimpleBlock] = []
        self.has_pycode: bool = False
        self.embedded_graphics: list[str | Path] = []

    def load(self):
        for item_spec in self.item_specs:
            item_type = list(item_spec.keys())[0]
            item = LatexSimpleBlock(block_specs=item_spec[item_type]).load()
            self.items.append(item)
            if item.has_pycode:
                self.has_pycode = True
            self.embedded_graphics.extend(item.embedded_graphics)
        return self

    def substitute(self, super_substitutions: dict = {}):
        for idx, item in enumerate(self.items):
            if not 'qno' in item.substitution_map or not item.substitution_map['qno']:
                item.substitution_map['qno'] = idx + 1
            logger.debug(f'LatexListBlock.substitute item {idx} with substitutions: {item.substitution_map}')
            item.substitute(super_substitutions=super_substitutions)

    def copy_referenced_configs(self, output_dir: str):
        for item in self.items:
            item.copy_referenced_configs(output_dir)

    def __str__(self):
        lines = [rf'\begin{{{self.list_type}}}']
        for item in self.items:
            lines.append(r'\item ' + str(item))
        lines.append(rf'\end{{{self.list_type}}}')
        return '\n'.join(lines)

class PythontexPycodeBlock(LatexSimpleBlock):
    pythontex_dir = files('pygacity') / 'resources' / 'pythontex'

    def __init__(self, block_specs: dict):
        self.block_specs = block_specs
        super().__init__(block_specs)
        self.imports: list[str] = block_specs.get('imports', [])
        self.load_raw()

    def load_raw(self):
        if len(self.imports) > 0:
            self.rawcontents = r'\begin{pycode}' + '\n'
        for imp in self.imports:
            self.path = path_resolver(imp, search_paths=[PythontexPycodeBlock.pythontex_dir], ext='.pycode')
            with open(self.path, 'r') as f:
                self.rawcontents += f.read() + '\n\n'
        if len(self.imports) > 0:
            self.rawcontents += r'\end{pycode}' + '\n'