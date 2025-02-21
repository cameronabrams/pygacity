# Author: Cameron F. Abrams, <cfa22@drexel.edu>
import os
import logging
from . import resources
logger=logging.getLogger(__name__)
_template_dir_=os.path.join(os.path.split(resources.__file__)[0],'templates')
assert os.path.isdir(_template_dir_)

class Template:
    def __init__(self,specs={},keydelim=(r'<%',r'%>'),**kwargs):
        # TODO: module file handling
        assert len(specs)==1,f'Bad template specs: {specs}'
        self.specs=specs['template']
        self.has_pycode=False
        self.template=None
        self.inst_map={}
        self.local_serial=0
        self.templatefile=self.specs.get('source',None)
        self.modulefile=self.specs.get('module',None)
        if 'config' in self.specs:
            self.inst_map['config']=self.specs['config']
        self.local_file=self.templatefile
        self.filepath=None
        self.keys=[]
        # search local directory for template first
        if os.path.exists(self.local_file):
            self.filepath=os.path.realpath(self.local_file)
        else:
            # search installed templates
            tmp=os.path.join(_template_dir_,self.templatefile)
            if os.path.exists(tmp):
                self.filepath=tmp
        if not self.filepath:
            logger.warning(f'No template file found for {self.templatefile}')
        else:
            with open(self.filepath,'r') as f:
                self.template=f.read()
            self.has_pycode=r'\begin{pycode}' in self.template
            ldelim_idx=[]
            rdelim_idx=[]
            self.ldelim,self.rdelim=keydelim
            for i,c in enumerate(self.template):
                if self.template[i:i+2]==self.ldelim:
                    ldelim_idx.append(i)
                if self.template[i:i+2]==self.rdelim:
                    rdelim_idx.append(i)
            keys=[]
            for l,r in zip(ldelim_idx,rdelim_idx):
                key=self.template[l+2:r]
                if not key in keys:
                    keys.append(key)
            # print(self.filepath,keys)
            self.keys=keys

    def register_files(self,FC):
        FC.append(self.local_file)

    def resolve(self,map):
        local_map=map.copy()
        local_map.update(self.inst_map)
        assert all([x in local_map for x in self.keys]),f'Not all keys in template ({self.keys}) are in the applied map ({local_map})'
        self.local_serial=local_map.get('serial',0)
        self.resolved_template=self.template[:] # copy!
        for k in self.keys:
            tmp=self.resolved_template.replace(self.ldelim+k+self.rdelim,str(local_map[k]))
            self.resolved_template=tmp

    def write_local(self,FC=None):
        # TODO: module file handling
        tf,ext=os.path.splitext(self.templatefile)
        self.local_file=tf+f'-{self.local_serial}'+ext
        if os.path.exists(self.local_file):
            logger.warning(f'Overwriting {self.local_file}')
        with open(self.local_file,'w') as f:
            f.write(self.resolved_template)
        if FC!=None:
            FC.append(self.local_file)

    def __str__(self):
        ptstr=''
        if 'points' in self.specs:
            ess='s' if self.specs['points']>1 or self.specs['pts']==0 else ''
            ptstr=f'({self.specs["points"]} pt{ess}) '
        return ptstr+r'\input{'+self.local_file+r'}'
