# Author: Cameron F. Abrams, <cfa22@drexel.edu>
import os
import logging
import numpy as np
from collections import UserDict
from importlib.metadata import version
from ycleptic.yclept import Yclept
from . import resources
from .stringthings import my_logger
from .document import Document
from .texutils import LatexBuilder

logger=logging.getLogger(__name__)

class ResourceManager(UserDict):
    excludes=['__pycache__'] # exclude from top-level resources
    def __init__(self):
        data={}
        data['root']=os.path.dirname(resources.__file__)
        roottk=data['root'].split(os.sep)
        rootdepth=len(roottk)
        for root,dirs,files in os.walk(data['root']):
            tk=root.split(os.sep)
            absdepth=len(tk)
            if rootdepth<absdepth<rootdepth+3:
                rn=tk[rootdepth:absdepth]
                bn=tk[-1]
                if not bn in ResourceManager.excludes:
                    myset(data,rn,root)
        super().__init__(data)

def myset(a_dict,keylist,val):
    if len(keylist)==1:
        a_dict[keylist[0]]=val
    else:
        key=keylist.pop(0)
        if not key in a_dict or type(a_dict[key])==type(val):
            a_dict[key]={}
        myset(a_dict[key],keylist,val) 

class Config(Yclept):
    def __init__(self,userfile='',**kwargs):
        vrep=f"""ycleptic v. {version("ycleptic")}"""
        quiet=kwargs.get('quiet',False)
        if not quiet:
            my_logger(vrep,logger.info,just='<',frame='*',fill='',no_indent=True)
        r=ResourceManager()
        logger.debug(f'Resources:')
        for k,v in r.items():
            if type(v)!=dict:
                logger.debug(f'  {k}: {v}')
            else:
                logger.debug(f'  {k}:')
                for kk,vv in v.items():
                    logger.debug(f'      {kk}: {vv}')
        # resolve full pathname of YCleptic base config for this application
        basefile=os.path.join(r['config'],'base.yaml')
        assert os.path.exists(basefile)
        super().__init__(basefile,userfile=userfile)
        self['Resources']=r
        self.resource_root=self['Resources']['root']
        self._set_internal_shortcuts(**kwargs)
        self._set_external_apps(verify_access=(userfile!=''))

    def _set_external_apps(self,verify_access=True):
        user=self['user']
        paths=user['paths']
        self.autoprob_package_root=os.path.join(self.resource_root,'autoprob-package')
        logger.debug(f'autoprob_package_root {self.autoprob_package_root}')
        self.LB=LatexBuilder(paths,localdirs=[os.path.join(self.autoprob_package_root,'tex','latex')])
        if verify_access:
            self.LB.verify_access()
        self.pdflatex=paths['pdflatex']
        self.pythontex=paths['pythontex']

    def _set_internal_shortcuts(self,**kwargs):
        self.progress=kwargs.get('progress',False)
        self.templates_root=os.path.join(self.resource_root,'templates')
        assert os.path.exists(self.templates_root)
        self.data_root=os.path.join(self.resource_root,'data')
        
        user=self['user']
        assert 'document' in user,f'Your config file does not specify a document structure'
        assert 'build' in user,f'Your config file does not specify document build parameters'
        self.build=user['build']
        self.document=Document(user['document'],buildspecs=self.build)
        self.ncopies=self.build['copies']
        # print(f'seed {self.build.get('seed','whoops')}')
        np.random.seed(self.build.get('seed',10214596))
        serial_file=self.build.get('serial-file',None)
        if len(self.build['serials'])==0:
            if not kwargs.get('overwrite',False) and serial_file and os.path.exists(serial_file):
                with open(serial_file,'r') as f:
                    serial_str=f.read()
                self.build['serials']=list(map(int,serial_str.split()))
                if len(self.build['serials'])!=self.ncopies:
                    if len(self.build['serials'])>self.ncopies:
                        self.build['serials']=self.build['serials'][:self.ncopies]
                    else:
                        self.ncopies=len(self.build['serials'])
                # print(f'reading serials from {serial_file}')
                # print(f'-> {self.build["serials"]}')
                logger.info(f'{len(self.build["serials"])} serials read in from {serial_file}')
            else:
                # print(f'new serials {self.build["serials"]}')
                self.build['serials']=np.random.randint(10000000,99999999,self.ncopies)
                while len(self.build['serials'])>len(set(self.build['serials'])):
                    self.build['serials']=np.random.randint(10000000,99999999,self.ncopies)
                if serial_file:
                    with open(serial_file,'w') as f:
                        for s in self.build['serials']:
                            f.write(f'{s}\n')
        else:
            if serial_file and not os.path.exists(serial_file):
                with open(serial_file,'w') as f:
                    for s in self.build['serials']:
                        f.write(f'{s}\n')    
        self.serials=self.build['serials']
        assert self.ncopies==len(self.build['serials']),f'Expected {self.ncopies} unique serial numbers'
        assert len(self.build['serials'])==len(set(self.build['serials'])),f'Expected {self.ncopies} unique serial numbers'