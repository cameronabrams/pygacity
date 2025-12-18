import unittest
import pytest
from pygacity.generate.config import Config

class ConfigTest(unittest.TestCase):

    def test_config_init_empty(self):
        c = Config()
        self.assertTrue('document' in c.specs)
        self.assertTrue('build' in c.specs)
        docspecs = c.document_specs
        self.assertTrue(type(docspecs['structure']) == list)
        self.assertEqual(len(docspecs['structure']), 0)
        
        buildspecs = c.build_specs
        self.assertEqual(buildspecs['output-name'], 'tpdoc')
        self.assertEqual(len(buildspecs['paths']), 3)
        self.assertTrue(buildspecs['solutions'])

    def test_config_user1(self):
        c = Config('exam_description1.yaml')
        self.assertTrue('document' in c.specs)
        self.assertTrue('build' in c.specs)
        docspecs = c.document_specs
        self.assertTrue(type(docspecs['structure']) == list)
        self.assertEqual(len(docspecs['structure']), 3)
        
        block1 = docspecs['structure'][0]
        self.assertEqual(list(block1.keys())[0], 'unstructured')
        block2 = docspecs['structure'][1]
        self.assertEqual(list(block2.keys())[0], 'list')
        block2_items = block2['list']['items']
        self.assertEqual(len(block2_items), 4)
        block2_item1 = block2_items[0]['item']
        self.assertEqual(block2_item1['source'], 'true_false.tex')
        self.assertEqual(block2_item1['config'], 'true_false.yaml')
        self.assertEqual(block2_item1['points'], 15)
        self.assertEqual(block2_item1['type'], 'question')

        block3 = docspecs['structure'][2]
        self.assertEqual(list(block3.keys())[0], 'unstructured')
        buildspecs = c.build_specs
        self.assertEqual(buildspecs['output-name'], 'exam')
        self.assertEqual(buildspecs['copies'], 25)
        self.assertEqual(buildspecs['output-dir'], 'output')
        self.assertEqual(buildspecs['serial-file'], 'exam-serials.dat')
    