# Author: Cameron F. Abrams, <cfa22@drexel.edu>
import logging

from importlib.resources import files
from pathlib import Path

from .block import LatexSimpleBlock, LatexListBlock

logger = logging.getLogger(__name__)

class Document:
    resources_root: Path = files('pygacity') / 'resources'
    templates_dir: Path = resources_root / 'templates'
    def __init__(self, document_specs: dict):
        self.blocks: list[LatexSimpleBlock | LatexListBlock] = []
        self.specs = document_specs
        self.name = self.specs.get('name', 'document')
        self.type = self.specs.get('type', None)
        self.substitutions = self.specs.get('substitutions', {})
        for section in self.specs['structure']:
            assert type(section) == dict
            assert len(section) == 1
            section_type = list(section.keys())[0]
            if section_type == 'block':
                block_specs = section['block']
                self._add_block_to_structure(block_specs)
            else:
                raise ValueError(f'Unrecognized section type "{section_type}" in document structure.')
        self.has_pycode = any(block.has_pycode for block in self.blocks)
        self.embedded_graphics = []
        for block in self.blocks:
            self.embedded_graphics.extend(block.embedded_graphics)
            
    def _add_block_to_structure(self, block_specs: dict):
            block_name = block_specs.get('name', None)
            if block_name is None:
                raise ValueError('Block section must have a "name" field.')
            block_type = block_specs.get('type', None)
            if block_type is None:
                raise ValueError('Block section must have a "type" field.') 
            match block_type:
                case 'paragraph':
                    self.blocks.append(LatexSimpleBlock(block_specs=block_specs).load())
                case 'enumerate' | 'itemize':
                    self.blocks.append(LatexListBlock(block_specs=block_specs).load())
            
    def make_substitutions(self, outer_substitutions: dict = {}):
        substitutions = outer_substitutions.copy()
        substitutions.update(self.substitutions.copy())
        for block in self.blocks:
            # if this is the opening block, append the autoprob header line
            if block == self.blocks[0]:
                match self.type:
                    case 'assignment':
                        block.rawcontents += rf'\asnheader{{<<<Description>>>}}{{<<<Duedate>>>}}{{}}' + '\n'
                    case 'exam':
                        block.rawcontents += rf'\examheader{{<<<Description>>>}}{{<<<Duedate>>>}}{{}}' + '\n'
                    case 'plain':
                        block.rawcontents += rf'\plainheader{{<<<Description>>>}}' + '\n'
            block.substitute(substitutions)

    def write_source(self, local_output_name='local_document', serial=None):
        with open(local_output_name + '.tex', 'w') as f:
            for block in self.blocks:
                f.write(str(block) + '\n')


   