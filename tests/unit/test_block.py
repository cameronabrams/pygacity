import unittest
import pytest
from pygacity.generate.block import LatexSimpleBlock, LatexListBlock

class SimpleBlockTest(unittest.TestCase):

    def test_LatexSimpleBlock_init(self):
        L = LatexSimpleBlock({})
        self.assertTrue(L.resources_root.exists())
        self.assertTrue(L.templates_dir.exists())

    def test_LatexSimpleBlock_fetch(self):
        L = LatexSimpleBlock({'source':'header.tex'})
        L.load()
        self.assertTrue(L.path.exists())
        self.assertTrue(len(L.rawcontents)>0)

    def test_LatexSimpleBlock_substitute(self):
        L = LatexSimpleBlock({'source':'header.tex', 'substitutions':{'Departmentname':'My Test Document'}})
        L.load()
        L.substitute(match_all=False)
        self.assertIn('My Test Document', L.processedcontents)

    def test_LatexSimpleBlock_substitute_match(self):
        L = LatexSimpleBlock({'source':'header.tex', 'substitutions':{'Departmentname':'My Test Document'}})
        L.load()
        with pytest.raises(KeyError):
            L.substitute(match_all=True)
        self.assertIn('My Test Document', L.processedcontents)

    def test_LatexSimpleBlock_load(self):
        L = LatexSimpleBlock({'source':'blank_template.tex'})
        L.load()
        self.assertTrue(L.has_pycode)
        self.assertEqual(len(L.embedded_graphics), 3)
        self.assertEqual(L.embedded_graphics[2], 'graphics3.pdf')

class ListBlockTest(unittest.TestCase):

    def test_LatexListBlock_init(self):
        L = LatexListBlock({})
        self.assertEqual(len(L.item_specs), 0)
        self.assertEqual(len(L.items), 0)
        self.assertEqual(L.list_type, 'enumerate')

    def test_LatexListBlock_load(self):
        item1 = {'question':{'source':'header.tex', 'substitutions':{'Departmentname':'List Item 1'}}}
        item2 = {'question':{'source':'header.tex', 'substitutions':{'Departmentname':'List Item 2'}}}
        L = LatexListBlock({'type':'itemize', 'items':[item1, item2]})
        L.load()
        self.assertEqual(L.list_type, 'itemize')
        self.assertEqual(len(L.items), 2)
        self.assertIsInstance(L.items[0], LatexSimpleBlock)
        self.assertIsInstance(L.items[1], LatexSimpleBlock)
        L.items[0].substitute(match_all=False)
        L.items[1].substitute(match_all=False)
        self.assertIn('List Item 1', L.items[0].processedcontents)
        self.assertIn('List Item 2', L.items[1].processedcontents)