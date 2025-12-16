# Author: Cameron F. Abrams, <cfa22@drexel.edu>
import logging
import os
import shutil

from importlib.resources import files
from pathlib import Path

from .structure import LatexInputFile
from ..util.stringthings import FileCollector

logger = logging.getLogger(__name__)


class Document:
    resources_root: Path = files('pygacity') / 'resources'
    templates_dir: Path = resources_root / 'templates'
    def __init__(self, sources_root: Path = Path('.'), build_root: Path = Path('build')):
        self.local_sources_root = sources_root
        self.build_root = build_root
        assert self.local_sources_root != self.build_root
        if not self.local_sources_root.exists():
            raise FileNotFoundError(f'Sources root directory {self.local_sources_root} does not exist.')
        self.build_root.mkdir(parents=True, exist_ok=True)
        self.structure: list[LatexInputFile] = []
        self.FC = FileCollector()

    def source_resolver(self, source_name: str) -> Path:
        # check local sources root first
        local_path = self.local_sources_root / source_name
        if local_path.exists():
            return local_path
        # check templates directory next
        template_path = self.templates_dir / source_name
        if template_path.exists():
            return template_path
        raise FileNotFoundError(f'Could not locate source file {source_name} in either {self.local_sources_root} or {self.templates_dir}.')

    def generate_source(self, docspecs: dict):
        logger.debug('Generating document source from specs')
        self.specs = docspecs
        self.name = docspecs.get('name', 'document')
        self.type = docspecs.get('type', None)

        for section in docspecs['structure']:
            assert type(section) == dict
            assert len(section) == 1
            section_type = list(section.keys())[0]
            if section_type == 'header':
                self.structure.append(LatexInputFile(path=self.source_resolver(section['header'].get('source', 'header.tex'))).load())
            elif section_type == 'footer':
                self.structure.append(LatexInputFile(path=self.source_resolver(section['footer'].get('source', 'footer.tex'))).load())
            elif section_type == 'block':
                block_specs = section['block']
                block_name = block_specs.get('name', None)
                if block_name is None:
                    raise ValueError('Block section must have a "name" field.')
                block_type = block_specs.get('type', None)
                if block_type is None:
                    raise ValueError('Block section must have a "type" field.') 

                pass
            else:
                raise ValueError(f'Unrecognized section type "{section_type}" in document structure.')
            label=list(s.keys())[0]
            if label=='items':
                itemlist=[]
                qno=1
                for item in s['items']:
                    itemlabel=list(item.keys())[0]
                    this_item=_classmap[itemlabel](item)
                    itemlist.append(this_item)
                    itemlist[-1].inst_map['qno']=qno
                    if hasattr(itemlist[-1],'has_pycode') and itemlist[-1].has_pycode:
                        self.has_pycode=True
                    qno+=1
                self.structure.append(itemlist)
            else:
                cls=_classmap[label]
                self.structure.append(cls(s))

    def resolve_instance(self,keymap={}):
        logger.debug('resolving document')
        _resolve_recursive(self.structure,keymap=keymap,depth=0,FC=self.FC)
        self.write_tex(serial=keymap.get('serial',None))
        
    def write_tex(self,local_output_name='local_document',serial=None):
        if self.buildspecs and 'output-name' in self.buildspecs:
            if serial!=None:
                local_output_name=self.buildspecs['output-name']+f'-{serial}'
            else:
                local_output_name=self.buildspecs['output-name']
        self.output_name=local_output_name
        local_output_file=local_output_name+'.tex'
        self.sourcefile=local_output_file
        with open(local_output_file,'w') as f:
            if not 'options' in self.specs['class'] or len(self.specs['class']['options'])==0:
                f.write(r'\documentclass{'+self.specs['class']['classname']+r'}'+'\n')
            else:
                f.write(r'\documentclass['+','.join(self.specs['class']['options'])+r']{'+self.specs['class']['classname']+r'}'+'\n')
            if 'packages' in self.specs and len(self.specs['packages'])>0:
                for p in self.specs['packages']:
                    if not 'options' in p or len(p['options'])==0:
                        f.write(r'\usepackage{'+p['package_name']+r'}'+'\n')
                    else:
                        f.write(r'\usepackage['+','.join(p['options'])+r']{'+p['package_name']+r'}'+'\n')
                    if 'affiliated_commands' in p:
                        for c in p['affiliated_commands']:
                            f.write(c+r'\n')
            if 'header_commands' in self.specs:
                for c in self.specs['header_commands']:
                    f.write(c+'\n')           
            metadata=self.specs.get('metadata',{})
            if self.specs['class']['classname']=='autoprob':
                for mdelem in ['Universityname',
                               'Departmentname',
                               'Coursename',
                               'Termname',
                               'Termcode',
                               'Instructorname',
                               'Instructoremail',
                               'Subjectname']:
                    if mdelem in metadata:
                        f.write(r'\renewcommand{'+'\\'+mdelem+r'}{'+str(metadata[mdelem])+r'}'+'\n')

            f.write(r'\ifthenelse{\equal{\detokenize{'+local_output_name+'_soln'+r'}}{\jobname}}{\showsolutionstrue}{}'+'\n')
            f.write(r'\begin{document}'+'\n')
            doctype=self.specs.get('type',None)
            if doctype=='exam':
                f.write('\n'+r'\examheader{'+metadata['description']+r'}{'+metadata['date']+r'}'+'\n\n')
            elif doctype=='assignment':
                msg=metadata.get('message','')
                f.write('\n'+r'\asnheader{'+str(metadata['assignment_number'])+r'}{'+metadata['date']+r'}{'+msg+r'}'+'\n\n')
            elif doctype=='plain':
                f.write('\n'+r'\plainheader{'+metadata['date']+r'}'+'\n\n')
            for element in self.structure:
                if type(element)==list:
                    f.write(r'\begin{enumerate}'+'\n')
                    for item in element:
                        f.write(r'    \item '+str(item)+'\n')
                    f.write(r'\end{enumerate}'+'\n')
                else:
                    f.write(str(element)+'\n')
            f.write(r'\end{document}'+'\n')
        logger.debug(f'Wrote {local_output_file}')

    def flush(self):
        self.FC.flush()

def _resolve_recursive(structure,keymap,depth=0,FC=None):
    if hasattr(structure,'resolve'):
        structure.resolve(keymap)
        structure.write_local(FC=FC)
    elif type(structure)==list:
        for ino,item in enumerate(structure):
            keymap['qno']=ino+1
            _resolve_recursive(item,keymap,depth=depth+1)
