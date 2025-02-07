import unittest
from pygacity.pick import Picker, Stepper
import numpy as np
from itertools import product
from argparse import Namespace

class PickTest(unittest.TestCase):
    def test_picker1(self):
        P=Picker(12345678)
        state=P.pick_state({'P1':   {'pick':{'between':[2.9,3.9],'round':1}},
                            'T1C':  {'pick':{'between':[340,360],'round':0}},
                            'Psat': {'pick':{'between':[2.7,2.9],'round':3}},
                            'TLC':  {'pick':{'between':[45,55],'round':0}},
                            'mdot': {'pick':{'between':[10,50],'round':0}}})
        self.assertTrue(state.P1>=2.9)
        self.assertTrue(state.P1<=3.9)
    def test_picker2(self):
        P=Picker(12345678)
        state=P.pick_state({'P1':   {'pick':{'pickfrom':[2.9,3.1,3.3,3.5,3.7,3.9]}},
                            'T1C':  {'pick':{'between':[340,360],'round':0}},
                            'Psat': {'pick':{'between':[2.7,2.9],'round':3}},
                            'TLC':  {'pick':{'between':[45,55],'round':0}},
                            'mdot': {'pick':{'between':[10,50],'round':0}}})
        self.assertTrue(state.P1 in [2.9,3.1,3.3,3.5,3.7,3.9])
    def test_picker_defaults(self):
        P=Picker(0)
        state=P.pick_state(dict(P={'default':10.0,'pick':{'between':[9,11],'round':2}}))
        self.assertEqual(state.P,10.0)
    def test_stepper0(self):
        S=Stepper({'P1':   {'pick':{'between':[2.9,3.9],'round':1}},
                            'T1C':  {'pick':{'between':[340,360],'round':0,'intervals':11}},
                            'Psat': {'pick':{'between':[2.7,2.9],'round':3}},
                            'TLC':  {'pick':{'between':[45,55],'round':0}},
                            'mdot': {'pick':{'between':[10,50],'round':0}}})
        self.assertEqual(len(S.space.P1),10)
        self.assertTrue(np.all(S.space.P1==np.linspace(2.9,3.9,10)))
        allv=[k for k in vars(S.space).values()]
        self.assertTrue(np.all(allv[1]==np.linspace(340,360,11)))
        T=product(*allv)
        TT=list(T)
        self.assertEqual(len(TT),10*11*10*10*10)
        T=product(*allv)
        t=next(T)
        resdict={k:v for k,v in zip(vars(S.space).keys(),t)}
        X=Namespace(**resdict)
        
        self.assertEqual(X.P1,2.9)
        self.assertEqual(X.T1C,340)
        self.assertEqual(X.Psat,2.7)
        self.assertEqual(X.TLC,45)
        self.assertEqual(X.mdot,10)
        self.assertEqual(len(t),5)
    def test_stepper1(self):
        S=Stepper({'P1':   {'pick':{'between':[2.9,3.9],'round':1}},
                            'T1C':  {'pick':{'between':[340,360],'round':0,'intervals':11}},
                            'Psat': {'pick':{'between':[2.7,2.9],'round':3}},
                            'TLC':  {'pick':{'between':[45,55],'round':0}},
                            'mdot': {'pick':{'between':[10,50],'round':0}}})
        xx=np.linspace(10,50,10)
        for i,N in enumerate(S):
            if i>9: break
            self.assertEqual(N.P1,2.9)
            self.assertEqual(N.TLC,45)
            self.assertEqual(N.mdot,xx[i])
    def test_stepper2(self):
        S=Stepper({'P1':   {'pick':{'between':[2.9,3.9],'round':1}},
                            'T1C':  {'pick':{'between':[340,360],'round':0,'intervals':11}},
                            'Psat': {'pick':{'between':[2.7,2.9],'round':3}},
                            'TLC':  {'pick':{'between':[45,55],'round':0}},
                            'mdot': 100.0})
        xx=np.linspace(10,50,10)
        for i,N in enumerate(S):
            # if i>9: break
            # self.assertEqual(N.P1,2.9)
            self.assertEqual(N.mdot,100.0)