from pygacity.topics.thermo.corrsts import CorrespondingStates
import unittest

class TestCoorsts(unittest.TestCase):

    def test_coorsts(self):
        CS=CorrespondingStates()
        H=CS.readHdep(1.1,1.5)
        self.assertAlmostEqual(H,4.1,places=1)
        S=CS.readSdep(0.6,2.0)
        self.assertAlmostEqual(S,13.0,places=1)
        S=CS.readSdep(0.7,3.0)
        self.assertAlmostEqual(S,10.8,places=1)
        Hbad=CS.readHdep(0.5,1.0)
        self.assertEqual(Hbad,None)
