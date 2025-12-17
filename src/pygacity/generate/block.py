# Author: Cameron F. Abrams, <cfa22@drexel.edu>
import logging
import re

from importlib.resources import files
from pathlib import Path

logger = logging.getLogger(__name__)

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
        self.rawcontents: str = ''
        self.processedcontents: str = ''
        self.points: int = block_specs.get('points', 0)

    def path_resolver(self):
        if not self.filename:
            raise ValueError("Name of the LaTeX input file is not specified.")
        # check local directory first
        local_path = Path(self.filename)
        if local_path.exists():
            self.path = local_path
        # check templates directory next
        template_path = self.templates_dir / self.filename
        if template_path.exists():
            self.path = template_path
        else:
            raise FileNotFoundError(f'Could not locate source file {self.filename} in either CWD or {self.templates_dir}.')

    def load(self):
        self.path_resolver()
        if not self.path:
            raise ValueError("Name of the LaTeX input file is not specified.")
        if not self.path.exists():
            raise FileNotFoundError(f'LaTeX input file {self.path} does not exist.')
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
        return self

    def substitute(self, super_substitutions: dict = {}, match_all: bool = True):
        substitutions = self.substitution_map.copy()
        substitutions.update(super_substitutions)
        for key, value in substitutions.items():
            if key in self.substitution_map:
                self.substitution_map[key] = value
        # apply substitutions to the contents
        self.processedcontents = self.rawcontents[:]
        for key, value in self.substitution_map.items():
            if value is not None:
                self.processedcontents = self.processedcontents.replace(f'{self.substitution_delimiters[0]}{key}{self.substitution_delimiters[1]}', str(value))
            elif match_all:
                raise KeyError(f'Substitution key {key} has no associated value for input file {self.path.name}')

    def __str__(self):
        return self.processedcontents

class LatexListBlock:
    def __init__(self, block_specs: dict = {}):
        self.item_specs = block_specs.get('items', [])
        self.list_type = block_specs.get('type', 'enumerate')
        self.items: list[LatexSimpleBlock] = []

    def load(self):
        for item_spec in self.item_specs:
            item_type = list(item_spec.keys())[0]
            item = LatexSimpleBlock(block_specs=item_spec[item_type]).load()
            self.items.append(item)
        return self

    def substitute(self, super_substitutions: dict = {}):
        for idx, item in enumerate(self.items):
            if not 'qno' in item.substitution_map:
                item.substitution_map['qno'] = idx + 1
            item.substitute(super_substitutions=super_substitutions)

    def __str__(self):
        lines = [rf'\begin{{{self.list_type}}}']
        for item in self.items:
            lines.append(r'\item ' + str(item))
        lines.append(rf'\end{{{self.list_type}}}')
        return '\n'.join(lines)