import numpy as np
from ThermoProblems.Chem.Properties import PureProperties
from ThermoProblems.Chem.System import ChemEqSystem
from ThermoProblems.Chem.Reaction import Reaction
Prop=PureProperties()
my_compounds={
    'A':Prop.get_compound('hydrogen (equilib)'),
    'B':Prop.get_compound('nitrogen'),
    'C':Prop.get_compound('ammonia'),
}
N0={my_compounds['A']:3.,my_compounds['B']:1.,my_compounds['C']:0.}
T=500
P=8 # bar
Eq=ChemEqSystem(N0=N0,T=T,P=P)
Eq.solve_lagrange()
R=Reaction(R=[my_compounds['A'],my_compounds['B']],P=[my_compounds['C']])
mock=ChemEqSystem(N0=N0,T=T,P=P,Reactions=[R])

print('Test of ThermoProblems:  Ammonia Synthesis')
print('Compounds:')
for c in my_compounds.values():
    c.report(indent='    ')
print('Initial amounts:')
for c,n in N0.items():
    print(c.ef,n)
print('Results of Lagrange-method calculation:')
Eq.show()
print('Example reaction:')
rxnstr=R.as_tex()
print(rxnstr)
thermochemicaltable=mock.thermochemicaltable_as_tex()
print(thermochemicaltable)
print('End of test.')
