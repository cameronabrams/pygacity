import unittest
import yaml

from importlib.resources import files

from pygacity.generate.document import Document

class DocumentTest(unittest.TestCase):

    def setUp(self):
        self.default_header_tex = files('pygacity') / 'resources' / 'templates' / 'header.tex'
        self.default_header_contents = self.default_header_tex.read_text()
        self.default_footer_tex = files('pygacity') / 'resources' / 'templates' / 'footer.tex'
        self.default_footer_contents = self.default_footer_tex.read_text()

    def test_document_structure1(self):
        with open('document1.yaml', 'r') as f:
            specs = yaml.safe_load(f)
        D = Document(specs)
        self.assertTrue(type(D.blocks) == list)
        self.assertEqual(len(D.blocks), 2)
        self.assertEqual(str(D.blocks[0]), self.default_header_contents)
        self.assertEqual(len(D.blocks[0].substitution_map), 7)
        self.assertTrue('Departmentname' in D.blocks[0].substitution_map)
        self.assertTrue('Coursename' in D.blocks[0].substitution_map)
        self.assertTrue('Documentname' in D.blocks[0].substitution_map)
        self.assertTrue('Instructorname' in D.blocks[0].substitution_map)
        self.assertTrue('Instructoremail' in D.blocks[0].substitution_map)
        self.assertTrue('Termname' in D.blocks[0].substitution_map)
        self.assertTrue('Termcode' in D.blocks[0].substitution_map)
        self.assertEqual(str(D.blocks[1]), self.default_footer_contents)
        self.assertTrue('class' in D.specs)

    def test_document_structure2(self):
        with open('document2.yaml', 'r') as f:
            specs = yaml.safe_load(f)
        D = Document(specs)
        
