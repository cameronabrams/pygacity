# Author: Cameron F. Abrams, <cfa22@drexel.edu>
from dataclasses import dataclass
import logging
import os
import shutil

from importlib.resources import files
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class LatexInput:
    resources_dir: Path = files('pygacity') / 'resources'
    template_dir: Path = resources_dir / 'templates'
    metadata: dict = {}

@dataclass
class Header(LatexInput):
    default: Path = LatexInput.template_dir / 'header.tex'

@dataclass
class Footer(LatexInput):
    default: Path = LatexInput.template_dir / 'footer.tex'

@dataclass
class LatexRawInput:
    def __init__(self, specs={}):
        self.resources_dir = files('pygacity') / 'resources'
        self.template_dir = self.resources_dir / 'templates'
        self.filename = specs['include']
        self.has_pycode = False
        self.filepath = ''
        self.contents = None
        tmp = os.path.join(self.template_dir, self.filename)
        if os.path.exists(tmp):
            self.filepath = tmp
            shutil.copy(self.filepath, self.filename) # make a local copy
        else:
            if os.path.exists(self.filename):
                self.filepath = os.path.realpath(self.filename)
            else:
                raise FileNotFoundError(f'Could not locate input file {self.filename} in {os.getcwd()}')
        if self.filepath:
            with open(self.filepath, 'r') as f:
                self.contents = f.read()
            self.has_pycode = r'\begin{pycode}' in self.contents
    def resolve(self,serial=0):
        pass
    def write_local(self,FC=None):
        if not os.path.exists(self.filename) and self.contents!=None:
            with open(self.filename,'w') as f:
                f.write(self.contents)
            if FC!=None:
                FC.append(self.filename)
                
    def resgister_files(self,FC):
        FC.append(self.filename)

    def __str__(self):
        return r'\input{'+self.filename+r'}'

class Template:
    def __init__(self, specs={}, keydelim=(r'<<<',r'>>>'), **kwargs):
        templates_dir = files("pygacity") / "resources" / "templates"
        assert len(specs) == 1, f'Bad template specs: {specs}'
        self.specs = specs['template']
        self.has_pycode = False
        self.template = None
        self.inst_map = {}
        self.local_serial = 0
        self.templatefile = self.specs.get('source', None)
        self.modulefile = self.specs.get('module', None)
        if 'config' in self.specs:
            self.inst_map['config'] = self.specs['config']
        self.local_file = self.templatefile
        self.filepath = None
        self.keys = []
        
        if os.path.exists(self.local_file):
            self.filepath = os.path.realpath(self.local_file)
        else:
            # search installed templates
            tmp = os.path.join(templates_dir, self.templatefile)
            if os.path.exists(tmp):
                self.filepath = tmp
        if not self.filepath:
            raise FileNotFoundError(f'No template file found for {self.templatefile}')
        else:
            with open(self.filepath,'r') as f:
                self.template = f.read()
            self.has_pycode = r'\begin{pycode}' in self.template
            ldelim_idx = []
            rdelim_idx = []
            self.ldelim,self.rdelim = keydelim
            for i,c in enumerate(self.template):
                if self.template[i:i+len(self.ldelim)] == self.ldelim:
                    ldelim_idx.append(i)
                if self.template[i:i+len(self.rdelim)] == self.rdelim:
                    rdelim_idx.append(i)
            keys = []
            for l,r in zip(ldelim_idx, rdelim_idx):
                key = self.template[l+len(self.ldelim):r]
                if not key in keys:
                    keys.append(key)
            # print(self.filepath,keys)
            self.keys = keys
            images = []
            for line in self.template.split('\n'):
                if r'\includegraphics' in line:
                    images.append(line.split('{')[1].split('}')[0])
            self.embedded_images = images
            assert all([os.path.exists(x) for x in self.embedded_images]), f'Not all embedded images exist ({self.embedded_images})'

    def register_files(self, FC):
        FC.append(self.local_file)

    def resolve(self, map):
        local_map = map.copy()
        local_map.update(self.inst_map)
        assert all([x in local_map for x in self.keys]), f'Not all keys in template ({self.keys}) are in the applied map ({local_map})'
        self.local_serial = local_map.get('serial', 0)
        self.resolved_template = self.template[:] # copy!
        for k in self.keys:
            tmp = self.resolved_template.replace(self.ldelim + k + self.rdelim, str(local_map[k]))
            self.resolved_template = tmp

    def write_local(self, FC=None):
        # TODO: module file handling
        tf, ext = os.path.splitext(self.templatefile)
        self.local_file = tf + f'-{self.local_serial}' + ext
        if os.path.exists(self.local_file):
            logger.warning(f'Overwriting {self.local_file}')
        with open(self.local_file, 'w') as f:
            f.write(self.resolved_template)
        if FC != None:
            FC.append(self.local_file)

    def __str__(self):
        ptstr = ''
        if 'points' in self.specs:
            ess = 's' if self.specs['points'] > 1 or self.specs['points'] == 0 else ''
            ptstr = f'({self.specs["points"]} pt{ess}) '
        return ptstr + r'\input{' + self.local_file + r'}'