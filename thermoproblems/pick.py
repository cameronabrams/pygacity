# Author: Cameron F. Abrams, <cfa22@drexel.edu>
import numpy as np
from argparse import Namespace

class Picker:
    def __init__(self,serial=0):
        self.rng=np.random.default_rng(serial) if serial!=0 else None
    def pick_state(self,specs):
        _pick_recursive(specs,self.rng)
        return Namespace(**specs)
    
def _pick_recursive(specs,rng):
    if not type(specs)==dict:
        return 
    for k,v in specs.items():        
        if type(v)==dict and 'pick' in v:
            pickrule=v['pick']
            if rng==None:
                assert 'default' in v,f'Error: serial is 0 but no default for {k} is given'
                specs[k]=v['default']
            else:
                if 'between' in pickrule:
                    lims=pickrule['between']
                    r=rng.random()
                    specs[k]=lims[0]+r*(lims[1]-lims[0])
                    if 'round' in pickrule:
                        specs[k]=np.round(specs[k],pickrule['round'])
                elif 'pickfrom' in pickrule:
                    domain=pickrule['pickfrom']
                    specs[k]=rng.choice(domain)
                    if 'round' in pickrule:
                        specs[k]=np.round(specs[k],pickrule['round'])
                else:
                    raise Exception('Missing picking rule')
        else:
            _pick_recursive(v,rng)
        

