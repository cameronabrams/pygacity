# Author: Cameron F. Abrams, <cfa22@drexel.edu>

"""
LaTeX compound block class for pygacity
"""

from __future__ import annotations
import logging
import os
import re

from copy import deepcopy
from importlib.resources import files
from pathlib import Path
from shutil import copy2

logger = logging.getLogger(__name__)

def path_resolver(filename: str, search_paths: list[Path] = [], ext: str ='') -> Path:
    """
    Resolves a filename to a **Path** object, checking the local directory first,
    then searching the provided search paths. If the file is not found, raises
    a **FileNotFoundError**.
    
    Parameters
    ----------
    filename : str
        the name of the file to locate
    search_paths : list of **Path**, optional
        list of directories to search if the file is not found locally
    ext : str, optional
        file extension to append if not already present
    
    Returns
    -------
    Path
        the resolved **Path** object for the file
    """
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

class LatexBlock:
    """
    A LaTeX block with support for external source files, substitutions, and embedded pythontex code.
    """
    resources_root: Path = files('pygacity') / 'resources'
    """ The root path for pygacity resources """
    templates_dir: Path = resources_root / 'templates'
    """ The directory containing LaTeX template files """
    # pythontex_dir = resources_root / 'pythontex'
    """ The directory containing pythontex source files """
    substitution_delimiters: tuple = (r'<<<', r'>>>')
    """ The delimiters for substitution keys in LaTeX text """

    @classmethod
    def from_specs(cls, block_specs: dict) -> list[LatexBlock]:
        """
        Factory that returns a list of LatexBlocks. Handles the old-style
        'enumerate' shorthand: if block_specs has an 'enumerate' key whose value
        is a list, each item is treated as a question block with question_number
        assigned sequentially starting from 1.
        """
        if 'enumerate' in block_specs and isinstance(block_specs['enumerate'], list):
            blocks = []
            for q_num, item_specs in enumerate(block_specs['enumerate'], start=1):
                specs = deepcopy(item_specs)
                specs.setdefault('question_number', q_num)
                blocks.append(cls(block_specs=specs).load())
            return blocks
        return [cls(block_specs=block_specs).load()]

    def __init__(self, block_specs: dict):
        self.block_specs = block_specs
        self.textcontents: str = block_specs.get('text', '')

        self.sourcename: str = block_specs.get('source', None)
        self.question_number: int = block_specs.get('question_number', None)
        raw_substitutions = block_specs.get('substitutions', {})
        if isinstance(raw_substitutions, list):
            self.substitution_map: dict = {item['search']: item['replace'] for item in raw_substitutions}
        else:
            self.substitution_map: dict = raw_substitutions

        self.points: int = block_specs.get('points', 0)
        self.config_filename: str = block_specs.get('config', None)
        self.group: int = block_specs.get('group', 0)
        self.toplevel: bool = block_specs.get('toplevel', False)

        self.pythontex: list[str] = block_specs.get('pythontex', [])

        self.sourcepath = None
        self.config_path = Path(self.config_filename) if self.config_filename else None
        self.processedcontents: str = ''
        self.has_pycode: bool = False
        self.embedded_graphics: list[str | Path] = []

        self._check_schema()

        logger.debug(f'LatexBlock.__init__ substitution_map: {self.substitution_map}')

    def _check_schema(self):
        # cannot specify both text content and a source file
        if self.textcontents != '' and self.sourcename is not None:
            raise ValueError('Block cannot specify both "text" content and a "source" file.')
        # if list of pythontext files is non-empty, cannot specify text or source
        if len(self.pythontex) > 0:
            if self.textcontents != '' or self.sourcename is not None:
                raise ValueError('Block cannot specify "pythontex" files along with "text" content or a "source" file.')

    def load(self) -> LatexBlock:
        """
        Loads the block's text contents from source files if specified,
        processes substitutions to identify keys, and recursively loads
        child blocks.
        
        Returns
        -------
        LatexCompoundBlock
            the loaded block instance
        """
        if self.sourcename:
            self.sourcepath = path_resolver(self.sourcename, search_paths=[self.templates_dir])
            logger.debug(f'Block resolved source file {self.sourcename} to {self.sourcepath}')
            with open(self.sourcepath, 'r', encoding='utf-8') as f:
                self.textcontents = f.read()
            header_contents = r'\begin{pycode}' + '\n'
            header_contents += '### BLOCK GLOBALS BEGIN ####\n'
            if self.question_number is not None:
                header_contents += f'points = {self.points}\n'
                header_contents += f'group = {self.group}\n'
                header_contents += f'qno = {self.question_number}\n'
                if self.points > 0:
                    header_contents += f'print(f"({self.points} pts.)")\n'
            if self.config_path:
                header_contents += f'configfilename = r"""{self.config_path.as_posix()}"""\n'
            if self.toplevel:
                header_contents += 'first_ordinal = 1\n'
            header_contents += '### BLOCK GLOBALS END ####\n'
            header_contents += r'\end{pycode}' + '\n'
            self.textcontents = header_contents + self.textcontents
        elif len(self.pythontex) > 0:
            self.textcontents = r'\begin{pycode}' + '\n'
            for ptfile in self.pythontex:
                if ptfile == 'setup':
                    ## document-specific substitutions; manager does this via string replacement later
                    self.textcontents += '### DOCUMENT GLOBALS BEGIN ####\n'
                    self.textcontents += '### These should be resolved by subsitution prior to execution ###\n'
                    self.textcontents += 'serial = <<<serial>>>\n'
                    self.textcontents += 'serialstr = "<<<serialstr>>>"\n'
                    self.textcontents += '_build_dir = "<<<build_dir>>>"\n'
                    self.textcontents += '_cache_dir = "<<<cache_dir>>>"\n'
                    self.textcontents += 'solutions = <<<solutions>>>\n'
                    ## block-specific substitutions; can do these now
                    self.textcontents += '### These are block-specific ###\n'
                    self.textcontents += '### DOCUMENT GLOBALS END ####\n'
                self.textcontents += f'from pygacity.pythontex.{ptfile} import *\n'
            self.textcontents += r'\end{pycode}' + '\n'
        self.has_pycode = r'\begin{pycode}' in self.textcontents or self.has_pycode
        # check contents for substitution keys and embedded graphics files
        KEY_RE = re.compile(rf'{self.substitution_delimiters[0]}\s*([A-Za-z0-9_-]+)\s*{self.substitution_delimiters[1]}')
        for line in self.textcontents.split('\n'):
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
        self.processedcontents = self.textcontents[:]
        if self.config_path:
            if not self.config_path.exists():
                raise FileNotFoundError(f'Configuration file {self.config_path.as_posix()} does not exist.')
            self.substitution_map['config'] = self.config_path.as_posix()
        if self.question_number is not None:
            self.substitution_map['qno'] = self.question_number
        if self.points:
            self.substitution_map['points'] = self.points
        if self.group:
            self.substitution_map['group'] = self.group

        logger.debug(f'LatexBlock.load completed with substitutions: {self.substitution_map}')
        return self

    def substitute(self, super_substitutions: dict = {}, match_all: bool = True):
        """
        Applies substitutions to the block's text contents and recursively to its children.
        
        Parameters
        ----------
        super_substitutions : dict, optional
            substitutions from parent blocks
        match_all : bool, optional
            if True, raises KeyError if any substitution key has no associated value    
        """
        self.processedcontents = self.textcontents[:]
        substitutions = deepcopy(super_substitutions)
        logger.debug(f'block incoming substitutions: {substitutions}')
        logger.debug(f'block own substitution_map: {self.substitution_map}')
        substitutions.update({k: v for k, v in self.substitution_map.items() if v is not None})
        logger.debug(f'block substitutions: {substitutions}')
        # apply substitutions to the contents
        for key, value in substitutions.items():
            if value is not None:
                self.processedcontents = self.processedcontents.replace(f'{self.substitution_delimiters[0]}{key}{self.substitution_delimiters[1]}', str(value))
            elif match_all:
                raise KeyError(f'Substitution key {key} has no associated value for text {self.textcontents[:30]}...')

    def copy_referenced_configs(self, output_dir: str):
        """
        Copies any referenced configuration files to the specified output directory.
        
        Parameters
        ----------
        output_dir : str
            the directory to copy configuration files to
        
        Returns
        -------
        list of str
            list of paths to the copied configuration files
        """
        config_paths = []
        if self.config_path and self.config_path.exists():
            dest_path = Path(output_dir) / self.config_path.name
            if not dest_path.exists():
                copy2(self.config_path, dest_path)
                logger.debug(f'Copied config file {self.config_path} to {dest_path}')
            config_paths.append(str(dest_path))
        return config_paths

    def __str__(self):
        """
        Returns the processed contents of the block as a string.
        
        Returns
        -------
        str
            the processed LaTeX contents of the block
        """
        contents = self.processedcontents
        return contents