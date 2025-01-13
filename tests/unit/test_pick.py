import unittest
from thermoproblems.pick import Picker

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
