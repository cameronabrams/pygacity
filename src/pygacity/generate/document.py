# Author: Cameron F. Abrams, <cfa22@drexel.edu>
"""
Document build functions for pygacity
"""

import logging
import re

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
        preamble_text = self._resolve_preamble(self.specs.get('preamble', None))
        self.preamble = LatexBlock(block_specs={'text': preamble_text}).load()
        self.substitutions = self.specs.get('substitutions', {})
        logger.debug(f'Document.__init__ with specs: {self.specs}')
        for idx, block_specs in enumerate(self.specs['structure']):
            assert type(block_specs) == dict
            self.blocks.extend(LatexBlock.from_specs(block_specs))
            logger.debug(f'Added block {idx}: {block_specs}')
        self.has_pycode = any(block.has_pycode for block in self.blocks)
        self.embedded_graphics = []
        for block in self.blocks:
            self.embedded_graphics.extend(block.embedded_graphics)
            
    def _get_autoprob_commands(self) -> set:
        """Return the set of zero-argument ``\\newcommand`` names defined in autoprob.cls."""
        cls_path = self.resources_root / 'autoprob-package' / 'tex' / 'latex' / 'autoprob.cls'
        text = cls_path.read_text(encoding='utf-8')
        # match \newcommand{\Name}{...} but NOT \newcommand{\Name}[n] (which have arguments)
        return {
            m.group(1)
            for m in re.finditer(r'\\newcommand\{\\([A-Za-z]+)\}(?!\[)', text)
        }

    def _resolve_preamble_attr(self, attr: str, val) -> str:
        """Resolve one preamble sub-key (*font*, *pagestyle*, or *commands*) to LaTeX text."""
        preambles_dir = self.resources_root / 'preambles'
        KEYWORDS = {'default', 'example'}

        if isinstance(val, str):
            if val in KEYWORDS:
                fname = f'{val}_{attr}.tex'
                fpath = preambles_dir / fname
                if not fpath.is_file():
                    raise FileNotFoundError(
                        f'Preamble resource file not found: {fname}. '
                        f'Expected it at {fpath}'
                    )
                return fpath.read_text(encoding='utf-8')
            else:
                # literal LaTeX string
                return val

        elif isinstance(val, dict):
            if attr in ('font', 'pagestyle'):
                if 'input' not in val:
                    raise ValueError(
                        f'preamble.{attr} dict must contain an "input" key '
                        f'naming a local file to read'
                    )
                local_file = Path(val['input'])
                if not local_file.is_file():
                    raise FileNotFoundError(
                        f'Local preamble file not found: {local_file}'
                    )
                return local_file.read_text(encoding='utf-8')

            elif attr == 'commands':
                valid_cmds = self._get_autoprob_commands()
                lines = []
                for cmd, value in val.items():
                    if cmd not in valid_cmds:
                        raise ValueError(
                            f'Unknown command "{cmd}" in preamble.commands. '
                            f'Valid commands: {sorted(valid_cmds)}'
                        )
                    lines.append(rf'\renewcommand{{\{cmd}}}{{{value}}}')
                return '\n'.join(lines)

            else:
                raise ValueError(
                    f'preamble.{attr}: dict value is not supported for this attribute. '
                    f'Use a keyword string ("default"/"example"), a literal LaTeX string, '
                    f'or — for font/pagestyle — a dict with an "input" key.'
                )

        else:
            raise ValueError(
                f'preamble.{attr} must be a string or dict, got {type(val).__name__}'
            )

    def _resolve_preamble(self, preamble_specs) -> str:
        """
        Resolve ``document.preamble`` specs to a LaTeX string.

        Accepts three forms:

        * **None** (or absent from config) — defaults are applied: *font* and
          *pagestyle* both fall back to ``"default"``.
        * **str** — used as-is (backward-compatible literal LaTeX); no
          defaults are injected.
        * **dict** — structured form with optional sub-keys *font*,
          *pagestyle*, and *commands*, each resolved independently and
          concatenated in that order.  *font* and *pagestyle* default to
          ``"default"`` when absent; set either to ``null`` (``~``) in YAML
          to suppress its default entirely.
        """
        if isinstance(preamble_specs, str):
            return preamble_specs
        if preamble_specs is None:
            preamble_specs = {}
        if isinstance(preamble_specs, dict):
            parts = []
            for attr in ('font', 'pagestyle', 'commands'):
                val = preamble_specs.get(attr, 'default' if attr in ('font', 'pagestyle') else None)
                if val is None:
                    continue
                parts.append(self._resolve_preamble_attr(attr, val))
            # any remaining unknown keys are treated as literal LaTeX strings
            for attr, val in preamble_specs.items():
                if attr not in ('font', 'pagestyle', 'commands'):
                    logger.warning(f'Unknown preamble attribute "{attr}"; treating value as literal LaTeX')
                    parts.append(str(val))
            return '\n'.join(parts)
        raise ValueError(
            f'document.preamble must be a string or dict, got {type(preamble_specs).__name__}'
        )

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


   