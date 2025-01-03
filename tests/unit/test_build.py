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
        self.assertTrue(os.path.exists('exam-12345678.pdf'))
        self.assertTrue(os.path.exists('exam-12345678_soln.pdf'))
    def test_build2(self):
        c=Config('exam_description5.yaml')
        self.assertEqual(len(c.serials),2)
        for serial in c.serials:
            keymap=dict(serial=serial)
            c.document.resolve_instance(keymap)
            c.LB.build_document(c.document,make_solutions=True)
            self.assertTrue(os.path.exists(f'exam-{serial}.pdf'))
            self.assertTrue(os.path.exists(f'exam-{serial}_soln.pdf'))
