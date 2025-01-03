import unittest
import os
from thermoproblems.config import Config

class BuildTests(unittest.TestCase):
    def test_build1(self):
        c=Config('exam_description5.yaml')
        p1keys=c.document.structure[1][0].keys
        self.assertEqual(set(p1keys),set(['serial', 'qno']))
        keymap={'serial':12345678}
        c.document.resolve_instance(keymap)
        self.assertTrue(os.path.exists('exam-12345678.tex'))
        c.LB.build_document(c.document,make_solutions=True)