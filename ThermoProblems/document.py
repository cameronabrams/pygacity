# Author: Cameron F. Abrams, <cfa22@drexel.edu>
import logging
import os
import shutil
from .template import Template
from . import resources

logger=logging.getLogger(__name__)

_template_dir_=os.path.join(os.path.split(resources.__file__)[0],'templates')
assert os.path.isdir(_template_dir_)

class Input:
    def __init__(self,specs={}):
        self.filename=specs['include']
        tmp=os.path.join(_template_dir_,self.filename)
        if os.path.exists(tmp):
            self.filepath=tmp
            shutil.copy(self.filepath,self.filename) # make a local copy
        else:
            if os.path.exists(self.filename):
                self.filepath=os.path.realpath(self.filename)
    def __str__(self):
        return r'\input{'+self.filename+r'}'
    
_classmap={'template':Template,'include':Input}

class Document:
    def __init__(self,docspecs={},buildspecs={}):
        self.structure=[]
        self.specs=docspecs
        self.buildspecs=buildspecs
        for s in docspecs['structure']:
            label=list(s.keys())[0]
            if label=='items':
                itemlist=[]
                qno=1
                for item in s['items']:
                    itemlabel=list(item.keys())[0]
                    cls=_classmap[itemlabel]
                    itemlist.append(cls(item[itemlabel]))
                    itemlist[-1].inst_map['qno']=qno
                    qno+=1
                self.structure.append(itemlist)
            else:
                cls=_classmap[label]
                self.structure.append(cls(s))

    def write_tex(self,outfile='local_document.tex'):
        if self.buildspecs and 'output-name' in self.buildspecs:
            outfile=self.buildspecs['output-name']+'.tex'
        with open(outfile,'w') as f:
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
            f.write(r'\begin{document}'+'\n')
            for element in self.structure:
                if type(element)==list:
                    f.write(r'\begin{enumerate}'+'\n')
                    for item in element:
                        f.write(r'    \item '+str(item)+'\n')
                    f.write(r'\end{enumerate}'+'\n')
                else:
                    f.write(str(element)+'\n')
            f.write(r'\end{document}'+'\n')
        logger.info(f'Wrote {outfile}')
