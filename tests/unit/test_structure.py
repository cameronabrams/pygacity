import unittest
import os
from pygacity.generate.structure import LatexInputFile, Header, Footer

class TemplateTest(unittest.TestCase):

    def test_LatexInputFile_fetch(self):
        L=LatexInputFile()
        self.assertTrue(L.resources_dir.exists())
        self.assertTrue(L.template_dir.exists())