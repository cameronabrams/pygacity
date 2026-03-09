# Author: Cameron F. Abrams, <cfa22@drexel.edu>

"""
Picker and Stepper classes for parameter selection
"""

import numpy as np
from argparse import Namespace
from itertools import product

class Picker:
    """
    Picker class for randomly selecting parameter values.
    """
    def __init__(self, serial=0):
        self.rng = np.random.default_rng(serial) if serial != 0 else None

    def pick_state(self, specs: dict) -> Namespace:
        """
        Picks parameter values based on the provided specifications.
        
        Parameters
        ----------
        specs : dict
            parameter specifications with picking rules
            
        Returns
        -------
        Namespace
            namespace containing picked parameter values
        """
        _pick_recursive(specs, self.rng)
        return Namespace(**specs)

class Stepper:
    """
    Stepper class for iterating over parameter spaces.
    """
    def __init__(self, specs: dict):
        _space_recursive(specs)
        self.space = Namespace(**specs)
        allv = []
        for k in vars(self.space).values():
            if not hasattr(k, '__len__'):
                allv.append([k])
            else:
                allv.append(k)
        self.T = product(*allv)

    def __iter__(self):
        return self

    def __next__(self):
        try:
            t = next(self.T)
            resdict = {k: v for k, v in zip(vars(self.space).keys(), t)}
            return Namespace(**resdict)
        except:
            raise StopIteration
        
def _pick_recursive(specs: dict, rng: np.random.Generator | None):
    """
    Recursively picks values in specs according to pick rules.

    - **between**: picks a random value between two limits
    - **pickfrom**/**from**: picks a random value from a given list
    """
    if not type(specs) == dict:
        return
    for k, v in specs.items():        
        if type(v) == dict and 'pick' in v:
            pickrule = v['pick']
            if rng == None:
                assert 'default' in v, f'Error: serial is 0 but no default for {k} is given'
                specs[k] = v['default']
            else:
                if 'between' in pickrule:
                    lims = pickrule['between']
                    r = rng.random()
                    specs[k] = lims[0] + r * (lims[1] - lims[0])
                    if 'round' in pickrule:
                        specs[k] = np.round(specs[k], pickrule['round'])
                elif 'pickfrom' in pickrule or 'from' in pickrule:
                    domain = pickrule.get('pickfrom', pickrule.get('from', None))
                    if domain is None:
                        raise ValueError('Pickrule expecting from or pickfrom')
                    specs[k] = rng.choice(domain)
                    if 'round' in pickrule:
                        specs[k] = np.round(specs[k], pickrule['round'])
                else:
                    raise Exception('Missing picking rule')
            if 'units' in v:
                specs[k] *= v['units']
        else:
            _pick_recursive(v,rng)
        
def _space_recursive(specs):
    if not type(specs) == dict:
        return 
    for k, v in specs.items():        
        if type(v) == dict and 'pick' in v:
            pickrule = v['pick']
            if 'between' in pickrule:
                lims = pickrule['between']
                intervals = pickrule.get('intervals', 10)
                specs[k] = np.linspace(lims[0], lims[1], intervals)
            elif 'pickfrom' in pickrule:
                domain = pickrule['pickfrom']
                specs[k] = np.array(domain)
            else:
                raise Exception('Missing picking rule')
            if 'units' in v:
                specs[k] *= v['units']
        else:
            _space_recursive(v)

