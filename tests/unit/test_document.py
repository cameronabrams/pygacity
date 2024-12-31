import unittest
import os
from thermoproblems.document import Input, Document
import yaml

class DocumentTest(unittest.TestCase):
    def test_input_instance(self):
        if os.path.exists('blank_template.tex'):
            os.remove('blank_template.tex')
        I=Input({'include':'blank_template.tex'})
        self.assertTrue(os.path.exists('blank_template.tex'))
        os.remove('blank_template.tex')
        self.assertEqual(I.filename,'blank_template.tex')
        self.assertEqual(str(I),r'\input{blank_template.tex}')
    def test_input_local(self):
        I=Input({'include':'local_input.tex'})
        self.assertEqual(I.filename,'local_input.tex')
        self.assertEqual(str(I),r'\input{local_input.tex}')
    def test_document_structure(self):
        with open('document1.yaml','r') as f:
            specs=yaml.safe_load(f)
        D=Document(specs)
        self.assertEqual(D.specs['type'],'exam')
        self.assertTrue(type(D.structure)==list)
        self.assertEqual(len(D.structure),2)
        self.assertEqual(str(D.structure[0]),r'\input{head.tex}')
        self.assertEqual(str(D.structure[1]),r'\input{tail.tex}')
        self.assertTrue('class' in D.specs)
        if os.path.exists('local_result.tex'):
            os.remove('local_result.tex')
        D.write_tex('local_result.tex')
        self.assertTrue(os.path.exists('local_result.tex'))
        # os.remove('local_result.tex')

