import unittest
import os
from pygacity.generate.document import Document
import yaml

class DocumentTest(unittest.TestCase):
    def test_document_structure1(self):
        with open('document1.yaml','r') as f:
            specs=yaml.safe_load(f)
        D=Document(specs,buildspecs={'output-name':'local_result1'})
        self.assertEqual(D.specs['type'],'exam')
        self.assertTrue(type(D.structure)==list)
        self.assertEqual(len(D.structure),2)
        self.assertEqual(str(D.structure[0]),r'\input{head.tex}')
        self.assertEqual(str(D.structure[1]),r'\input{tail.tex}')
        self.assertTrue('class' in D.specs)
        if os.path.exists('local_result1.tex'):
            os.remove('local_result1.tex')
        D.write_tex()
        self.assertTrue(os.path.exists('local_result1.tex'))

    def test_document_structure2(self):
        with open('document2.yaml','r') as f:
            specs=yaml.safe_load(f)
        D=Document(specs,buildspecs={'output-name':'local_result2'})
        self.assertEqual(D.specs['type'],'exam')
        self.assertTrue(type(D.structure)==list)
        self.assertEqual(len(D.structure),3)
        self.assertEqual(str(D.structure[0]),r'\input{head.tex}')
        self.assertEqual(str(D.structure[2]),r'\input{tail.tex}')
        self.assertTrue('class' in D.specs)
        if os.path.exists('local_result2.tex'):
            os.remove('local_result2.tex')
        D.write_tex()
        self.assertTrue(os.path.exists('local_result2.tex'))
