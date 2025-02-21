# Author: Cameron F. Abrams, <cfa22@drexel.edu>
import logging
import os
import random
import shutil
from .template import Template
from . import resources
from .stringthings import FileCollector

logger=logging.getLogger(__name__)

_template_dir_=os.path.join(os.path.split(resources.__file__)[0],'templates')
assert os.path.isdir(_template_dir_)

class Input:
    def __init__(self,specs={}):
        self.filename=specs['include']
        self.has_pycode=False
        self.filepath=''
        self.contents=None
        tmp=os.path.join(_template_dir_,self.filename)
        if os.path.exists(tmp):
            self.filepath=tmp
            shutil.copy(self.filepath,self.filename) # make a local copy
        else:
            if os.path.exists(self.filename):
                self.filepath=os.path.realpath(self.filename)
            else:
                logger.warning(f'Could not locate input file {self.filename} in {os.getcwd()}')
        if self.filepath:
            with open(self.filepath,'r') as f:
                self.contents=f.read()
            self.has_pycode=r'\begin{pycode}' in self.contents
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
    
_classmap={'template':Template,'include':Input}

class Document:
    def __init__(self,docspecs={},buildspecs={}):
        self.FC=FileCollector()
        self.structure=[]
        self.specs=docspecs
        self.buildspecs=buildspecs
        self.has_pycode=False
        for s in docspecs['structure']:
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

            metadata=self.specs.get('metadata',{})
            if self.specs['class']['classname']=='autoprob':
                for mdelem in ['Universityname','Departmentname','Coursename','Termname','Termcode','Instructorname','Instructoremail','Subjectname']:
                    if mdelem in metadata:
                        f.write(r'\renewcommand{'+'\\'+mdelem+r'}{'+str(metadata[mdelem])+r'}'+'\n')

            f.write(r'\ifthenelse{\equal{\detokenize{'+local_output_name+'_soln'+r'}}{\jobname}}{\showsolutionstrue}{}'+'\n')
            f.write(r'\begin{document}'+'\n')
            doctype=self.specs.get('type',None)
            if doctype=='exam':
                f.write('\n'+r'\examheader{'+metadata['description']+r'}{'+metadata['date']+r'}'+'\n\n')
            elif doctype=='assignment':
                msg=metadata.get('message','')
                f.write('\n'+r'\asnheader{'+metadata['assignment_number']+r'}{'+metadata['date']+r'}{'+msg+r'}'+'\n\n')
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
