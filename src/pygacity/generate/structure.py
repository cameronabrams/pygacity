# Author: Cameron F. Abrams, <cfa22@drexel.edu>
from dataclasses import dataclass, field
import logging
import re

from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class LatexInputFile:
    path: Path = None
    substitution_map: dict = field(default_factory=dict)
    substitution_delimiters: tuple = (r'<<<', r'>>>')
    has_pycode: bool = False
    embedded_graphics: list[str | Path] = field(default_factory=list)
    rawcontents: str = None
    points: int = 0
    local_build_file: Path = None

    def load(self):
        if not self.path:
            raise ValueError("Name of the LaTeX input file is not specified.")
        if not self.path.exists():
            raise FileNotFoundError(f'LaTeX input file {self.path} does not exist.')
        with open(self.path, 'r') as f:
            self.rawcontents = f.read()
        self.has_pycode = r'\begin{pycode}' in self.contents
        # check contents for substitution keys and embedded graphics files
        KEY_RE = re.compile(r'<<<\s*([A-Za-z0-9_-]+)\s*>>>')
        for line in self.contents.split('\n'):
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

    def save_instance(self, serial_no: int = 0, substitutions: dict = {}, destination_dir: Path = Path('build')):
        for key, value in substitutions.items():
            if key in self.substitution_map:
                self.substitution_map[key] = value
        # apply substitutions to the contents
        contents = self.rawcontents[:]
        for key, value in self.substitution_map.items():
            if value is not None:
                contents = contents.replace(f'{self.substitution_delimiters[0]}{key}{self.substitution_delimiters[1]}', str(value))
            else:
                raise KeyError(f'Substitution key {key} has no associated value for input file {self.name}')
        # write the resolved file to the current working directory
        if serial_no == 0:
            self.local_build_file = destination_dir / self.path.name
        else:
            if 'SERIAL' in self.path.name:
                local_name = self.path.name.replace('SERIAL', str(serial_no))
            else:
                local_name = self.path.stem + f'_SERIAL{serial_no}' + self.path.suffix
        self.local_build_file = destination_dir / Path(local_name)
        with open(self.local_build_file, 'w') as f:
            f.write(contents)
        logger.debug(f'Fetched and wrote input file {self.path.name} to {self.local_build_file.name}')
        # fetch embedded graphics files
        for gf in self.embedded_graphics:
            # assume graphics files are relative to the input file's directory
            gf_path = self.path.parent / gf
            if not gf_path.exists():
                raise FileNotFoundError(f'Embedded graphics file {gf} not found relative to {self.path}')
            dest_path = destination_dir / gf_path.name
            logger.debug(f'Copying embedded graphics file {gf_path} to {dest_path}')
            with open(gf_path, 'rb') as src_f:
                with open(dest_path, 'wb') as dest_f:
                    dest_f.write(src_f.read())

    def __str__(self):
        ptstr = ''
        if self.points:
            ess = 's' if self.points > 1 else ''
            ptstr = f'({self.points} pt{ess}) '
        return ptstr + r'\input{' + self.local_build_file.name + r'}'

