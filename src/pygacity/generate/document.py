# Author: Cameron F. Abrams, <cfa22@drexel.edu>
"""
Document build functions for pygacity
"""

import logging

from copy import deepcopy
from importlib.resources import files
from pathlib import Path

from .block import LatexBlock

logger = logging.getLogger(__name__)

class Document:
    """
    Represents a LaTeX document composed of multiple blocks.

    Attributes
    ----------
    specs : dict
        document specifications
    blocks : list of LatexCompoundBlock
        list of blocks in the document
    preamble : list of str
        list of LaTeX preamble lines
    substitutions : dict
        dictionary of substitutions to apply in the document
    has_pycode : bool
        indicates if the document contains embedded Python code
    embedded_graphics : list of str
        list of embedded graphics file paths
    """
    resources_root: Path = files('pygacity') / 'resources'
    """ Root directory for resource files. """
    templates_dir: Path = resources_root / 'templates'
    """ Directory for template files. """
    def __init__(self, document_specs: dict):
        """
        Initializes the Document instance.
        
        Parameters
        ----------
        document_specs : dict
            document specifications
        """
        self.blocks: list[LatexBlock] = []
        self.specs = deepcopy(document_specs)
        preamble_text = self.specs.get('preamble', None)
        self.preable = None
        if preamble_text:
            self.preamble = LatexBlock(block_specs={'text': preamble_text}, idx=0).load()
        self.substitutions = self.specs.get('substitutions', {})
        logger.debug(f'Document.__init__ with specs: {self.specs}')
        for idx, block_specs in enumerate(self.specs['structure']):
            assert type(block_specs) == dict
            self.blocks.append(LatexBlock(block_specs=block_specs, idx=idx+1).load())
            logger.debug(f'Added block {idx}: {block_specs}')
        self.has_pycode = any(block.has_pycode for block in self.blocks)
        self.embedded_graphics = []
        for block in self.blocks:
            self.embedded_graphics.extend(block.embedded_graphics)
            
    def make_substitutions(self, outer_substitutions: dict = {}):
        """
        Applies substitutions to all blocks in the document.
        
        Parameters
        ----------
        outer_substitutions : dict, optional
            additional substitutions to apply (default is empty dict)
        """
        self.substitutions.update(deepcopy(outer_substitutions))
        logger.debug(f'Document.make_substitutions with substitutions: {self.substitutions}')
        self.preamble.substitute(super_substitutions=self.substitutions)
        for block in self.blocks:
            block.substitute(super_substitutions=self.substitutions)

    def write_source(self, local_output_name: str  = 'local_document'):
        """
        Writes the LaTeX source of the document to a .tex file.
        
        Parameters
        ----------
        local_output_name : str, optional
            base name for the output .tex file (default is 'local_document')
        """
        with open(local_output_name + '.tex', 'w', encoding='utf-8') as f:
            f.write('% Automatically generated LaTeX source file\n')
            class_specs = self.specs.get('class', {})
            logger.debug(f'Document.write_source with class_specs: {class_specs}')
            dcoptions = class_specs.get('options', [])
            classname = class_specs.get('classname', 'article')
            f.write(rf'\documentclass[{", ".join(dcoptions)}]{{{classname}}}' + '\n')
            f.write(str(self.preamble) + '\n')
            f.write(r'\begin{document}' + '\n')
            enumerating = False
            for block in self.blocks:
                if block.question_number is not None and not enumerating:
                    f.write(r'\begin{enumerate}' + '\n')
                    enumerating = True
                if block.question_number is None and enumerating:
                    enumerating = False
                if enumerating:
                    f.write(rf'\item[{block.question_number}.] ' + str(block) + '\n')
                else:
                    f.write(str(block) + '\n')
            if enumerating:
                f.write(r'\end{enumerate}' + '\n')
                enumerating = False
            f.write(r'\end{document}' + '\n')
            f.write('% End of automatically generated LaTeX source file\n')


   