import unittest
import yaml

from pygacity.generate.document import Document

class DocumentTest(unittest.TestCase):

    def test_document_structure1(self):
        with open('document1.yaml', 'r') as f:
            specs = yaml.safe_load(f)
        D = Document(specs)
        self.assertIsInstance(D.blocks, list)
        self.assertEqual(len(D.blocks), 2)
        self.assertIsNone(D.blocks[0].question_number)
        self.assertIsNone(D.blocks[1].question_number)
        # problem_abc.tex contains <<<config>>> so it lands in substitution_map
        self.assertIn('config', D.blocks[0].substitution_map)
        self.assertIn('class', D.specs)

    def test_document_structure2(self):
        with open('document2.yaml', 'r') as f:
            specs = yaml.safe_load(f)
        D = Document(specs)
        self.assertIsInstance(D.blocks, list)
        # 1 unstructured + 2 question blocks (from enumerate) + 1 unstructured = 4
        self.assertEqual(len(D.blocks), 4)
        self.assertIsNone(D.blocks[0].question_number)
        self.assertEqual(D.blocks[1].question_number, 1)
        self.assertEqual(D.blocks[2].question_number, 2)
        self.assertIsNone(D.blocks[3].question_number)
        self.assertEqual(D.blocks[1].points, 50)
        self.assertEqual(D.blocks[2].points, 50)
