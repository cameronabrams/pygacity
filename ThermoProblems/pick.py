# Author: Cameron F. Abrams, <cfa22@drexel.edu>
import numpy as np

def pick_recursive(specs,rng):
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
            pick_recursive(v,rng)
        
def pick_state(specs):
    num=specs['tag']
    rng=np.random.default_rng(num)
    pick_recursive(specs,rng)
    return specs
