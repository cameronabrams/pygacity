# Author: Cameron F. Abrams, <cfa22@drexel.edu>
import numpy as np

class Picker:
    def __init__(self,serial=0):
        self.rng=np.random.default_rng(serial)
    def pick_state(self,specs):
        _pick_recursive(specs,self.rng)
        return specs
    

def _pick_recursive(specs,rng):
    if not type(specs)==dict:
        return 
    for k,v in specs.items():
        if type(v)==dict and 'pick' in v:
            pickrule=v['pick']
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
        

