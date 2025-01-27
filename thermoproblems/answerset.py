# Author: Cameron F. Abrams, <cfa22@drexel.edu>
import yaml
import os
from collections import UserList
import pandas as pd
import logging
logger=logging.getLogger(__name__)

class AnswerSet:
    def __init__(self,serial=0):
        self.serial=serial
        self.dumpname=f'solutions-{serial:08d}.yaml'
        self.D={}

    @classmethod
    def from_yaml(cls,filename):
        root,ext=os.path.splitext(filename)
        assert ext in ['.yaml','.yml'],f'{filename} does not end in .yaml or .yml'
        tokens=root.split('-')
        assert len(tokens)==2,f'{filename} should be of the format "solutions-<serial#>.yaml"'
        serial=int(tokens[1])
        R=cls(serial)
        with open(filename,'r') as f:
            R.D=yaml.safe_load(f)
        return R
    
    def register(self,index,label=None,value=None,units=None,formatter=None):
        if not index in self.D:
            self.D[index]=[]
        self.D[index].append(dict(  label=label,
                                    value=value,
                                    units=units,
                                    formatter=formatter))
    def to_yaml(self):
        with open(self.dumpname,'w') as f:
            yaml.safe_dump(self.D,f)

class AnswerSuperSet(UserList):
    def __init__(self,files=[]):
        data=[]
        for f in files:
            data.append(AnswerSet.from_yaml(f))
        super().__init__(data)
        if not self._check_congruency():
            print(f'Error: There is a lack of congruency among {files}')
        self._make_df()

    def to_latex(self):
        return self.DF.to_latex(formatters=self.formatters,index=False,header=self.headings)

    def _check_congruency(self):
        if len(self)>0:
            indices=list(self.data[0].D.keys())
            for l in self.data[1:]:
                test_indices=list(l.D.keys())
                check=all([x==y for x,y in zip(indices,test_indices)])
                if not check:
                    return False
            for i in indices:
                ilen=len(self.data[0].D[i])
                for l in self.data[1:]:
                    test_ilen=len(l.D[i])
                    check=ilen==test_ilen
                    if not check:
                        return False
        return True
    
    def _make_df(self):
        serials=[x.serial for x in self.data]
        # logger.debug(serials)
        self.headings=['serials']
        keys=['serials']
        values={'serials':serials}
        pattern=self.data[0]
        self.formatters={}
        for index,AL in pattern.D.items():
            for a in AL:
                key=f'{index}-{a["label"]}'
                if not a['units']:
                    self.headings.append(f'{key}')
                else:
                    self.headings.append(f'{key} ({a["units"]})')
                keys.append(key)
                values[key]=[]
                if 'formatter' in a:
                    self.formatters[key]=a['formatter']
        # logger.debug(values)
        for inst in self.data:
            for index,AL in inst.D.items():
                for a in AL:
                    key=f'{index}-{a["label"]}'
                    # logger.debug(a['value'])
                    values[key].append(a['value'])
        # logger.debug(values)
        self.DF=pd.DataFrame(values)
        self.DF.sort_values(by='serials',inplace=True)


