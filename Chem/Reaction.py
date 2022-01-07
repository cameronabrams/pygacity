import numpy as np
from scipy.linalg import null_space
class Reaction:
    ''' simple class for describing and balancing chemical reactions
    
        a Reaction() instance must be initialized with a list of reactant Compound()'s 
        and a list of product Compound()'s.  scipy.linalg.null_space is used on the
        matrix of elements by compounds (with negative counts for reactants) to determine
        the balancing list of stoichiometric coefficients, stored in nu.

        Cameron F. Abrams cfa22@drexel.edu
     '''
    def __init__(self,R=[],P=[]):
        self.R=R
        self.nReactants=len(self.R)
        self.P=P
        self.nProducts=len(self.P)
        self.nCompounds=len(self.R)+len(self.P)
        self.nu=[]
        self._balance()
    def __str__(self):
        ''' spoof nu if reaction is not yet balanced '''
        nuR=['*']*self.nReactants if len(self.nu)==0 else self.nu[:self.nReactants]
        nuP=['*']*self.nProducts  if len(self.nu)==0 else self.nu[self.nReactants:]
        return '  +  '.join([f'{n:.0f} {str(s)}' for n,s in zip(nuR,self.R)])+'   ->   '+'  +  '.join([f'{n:.0f} {str(s)}' for n,s in zip(nuP,self.P)])
    def _balance(self):
        ''' Uses nullspace of (element)x(count-in-molecule) matrix to balance reaction '''
        self.Ratoms=set()
        for r in self.R:
            self.Ratoms.update(r.atomset)
        self.Patoms=set()
        for p in self.P:
            self.Patoms.update(p.atomset)
        self.atomList=list(self.Ratoms)
        #print(self.atomList)
        self.nAtoms=len(self.atomList)
        #print(f'{self.nReactants} reactants and {self.nProducts} products')
        if len(self.Ratoms.symmetric_difference(self.Patoms))>0:
            print('Error: all atoms not represented on both sides of reaction')
            print('R:',self.Ratoms)
            print('P:',self.Patoms)
        else:
            # make element x count-in-compound matrix
            mat=np.zeros((self.nCompounds,self.nAtoms))
            for i in range(self.nCompounds):
                for j in range(self.nAtoms):
                    if i<self.nReactants:
                        mat[i][j]=-self.R[i].countAtoms(self.atomList[j])
                    else:
                        mat[i][j]=self.P[i-self.nReactants].countAtoms(self.atomList[j])
            # find its nullspace vector
            ns=null_space(mat.T)
            ns*=np.sign(ns[0,0])
            # set nu; scale so lowest value is 1 making all integers
            self.nu=[a[0] for a in ns/min(ns)]

if __name__=='__main__':
    from Compound import Compound
    rxn=Reaction(R=[Compound('AgNO3'),Compound('CoCl2')],P=[Compound('AgCl'),Compound('Co(NO3)2')])
    print(str(rxn))
    rxn=Reaction(R=[Compound('AgCl'),Compound('NH3')],P=[Compound('Ag(NH3)2^{+1}'),Compound('Cl^{-1}')])
    print(str(rxn))
    rxn=Reaction(R=[Compound('AgCl'),Compound('Na3AsO4')],P=[Compound('Ag3AsO4'),Compound('NaCl')])
    print(str(rxn))
    rxn=Reaction(R=[Compound('H2'),Compound('O2')],P=[Compound('H2O')])
    print(str(rxn))
    rxn=Reaction(R=[Compound('H2'),Compound('N2')],P=[Compound('NH3')])
    print(str(rxn))
    rxn=Reaction(R=[Compound('H2'),Compound('N2'),Compound('O2')],P=[Compound('HNO3')])
    print(str(rxn))
    rxn=Reaction(R=[Compound('Ca^{+2}'),Compound('H2PO4^{-1}'),Compound('H2O')],P=[Compound('Ca3(PO4)2'),Compound('H3O^{+1}')])
    print(rxn)
    rxn=Reaction(R=[Compound('Ca(HCO3)2'),Compound('Ca(OH)2')],P=[Compound('CaCO3'),Compound('H2O')])
    print(rxn)

