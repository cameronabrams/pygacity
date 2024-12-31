import unittest
import os
from thermoproblems.template import Template, _template_dir_

class TemplateTest(unittest.TestCase):
    def test_template_instance(self):
        T=Template({'source':'blank_template.tex'})
        self.assertEqual(T.filepath,os.path.join(_template_dir_,'blank_template.tex'))
        self.assertEqual(str(T),r'\input{blank_template.tex}')
        self.assertTrue('key1' in T.keys)
        self.assertTrue('key2' in T.keys)
        submap={'serial':12345678,'key1':'value1','key2':'value2'}
        if os.path.exists('blank_template-12345678.tex'):
            os.remove('blank_template-12345678.tex')
        T.resolve(submap)
        T.write_local()
        self.assertTrue(os.path.exists('blank_template-12345678.tex'))
        self.assertEqual(str(T),r'\input{blank_template-12345678.tex}')

    def test_template_local(self):
        T=Template({'source':'local_template.tex'})
        self.assertEqual(T.filepath,os.path.realpath('local_template.tex'))
        self.assertTrue('localkey1' in T.keys)
        self.assertTrue('localkey2' in T.keys)
