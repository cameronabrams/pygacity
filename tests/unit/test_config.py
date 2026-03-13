import unittest
import pytest
import shutil
import os
from argparse import Namespace
from pathlib import Path

from pygacity.generate.config import Config
import pygacity.generate.config as config_module

class ConfigTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        if os.path.isdir('build'):
            shutil.rmtree('build')

    def tearDown(self):
        if os.path.isdir('build'):
            shutil.rmtree('build')

    def test_config_init_empty(self):
        c = Config()
        self.assertTrue('document' in c.specs)
        self.assertTrue('build' in c.specs)
        docspecs = c.document_specs
        self.assertTrue(type(docspecs['structure']) == list)
        self.assertEqual(len(docspecs['structure']), 0)
        
        buildspecs = c.build_specs
        self.assertEqual(buildspecs['job-name'], 'pygacity_document')
        self.assertEqual(len(buildspecs['paths']), 5)
        self.assertTrue('latexmkrc' in buildspecs['paths'])
        self.assertTrue(buildspecs['solutions'])

    def test_config_user1(self):
        c = Config(Namespace(f='exam_description1.yaml'))
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


def _write_minimal_config(path: Path, build_paths_block: str):
    path.write_text(
        f"""document:
  class:
    classname: autoprob
    options: [11pt]
  structure: []
build:
  paths:
{build_paths_block}
""",
        encoding='utf-8',
    )


def _write_config_with_build(path: Path, build_block: str):
        path.write_text(
                f"""document:
    class:
        classname: autoprob
        options: [11pt]
    structure: []
build:
{build_block}
""",
                encoding='utf-8',
        )


def test_config_defaults_include_latexmk(monkeypatch, tmp_path):
    monkeypatch.setattr(config_module, 'is_executable', lambda _cmd: True)
    cfg = tmp_path / 'config.yaml'
    _write_minimal_config(
        cfg,
        f"    build-dir: {tmp_path.as_posix()}/build\n",
    )
    c = Config(Namespace(f=str(cfg)))
    assert c.build_specs['paths']['latexmk'] == 'latexmk'
    assert c.build_specs['paths']['pythontex'] == 'pythontex'
    assert c.build_specs['paths']['latexmkrc'].replace('\\', '/').endswith('resources/latexmkrc-pythontex')


def test_config_accepts_legacy_pdflatex_key(monkeypatch, tmp_path):
    monkeypatch.setattr(config_module, 'is_executable', lambda _cmd: True)
    cfg = tmp_path / 'config-legacy.yaml'
    _write_minimal_config(
        cfg,
        (
            f"    build-dir: {tmp_path.as_posix()}/build-legacy\n"
            "    pdflatex: pdflatex\n"
        ),
    )
    c = Config(Namespace(f=str(cfg)))
    assert c.build_specs['paths']['latexmk'] == 'latexmk'
    assert c.build_specs['paths']['pdflatex'] == 'pdflatex'


def test_config_latexmkrc_pythontex_profile(monkeypatch, tmp_path):
    monkeypatch.setattr(config_module, 'is_executable', lambda _cmd: True)
    cfg = tmp_path / 'config-pythontex-profile.yaml'
    _write_config_with_build(
        cfg,
        (
            f"  paths:\n"
            f"    build-dir: {tmp_path.as_posix()}/build\n"
            f"  latexmkrc-profile: pythontex\n"
        ),
    )
    c = Config(Namespace(f=str(cfg)))
    assert c.build_specs['paths']['latexmkrc'].replace('\\', '/').endswith('resources/latexmkrc-pythontex')


def test_config_latexmkrc_profile_validation(monkeypatch, tmp_path):
    monkeypatch.setattr(config_module, 'is_executable', lambda _cmd: True)
    cfg = tmp_path / 'config-bad-profile.yaml'
    _write_config_with_build(
        cfg,
        (
            f"  paths:\n"
            f"    build-dir: {tmp_path.as_posix()}/build\n"
            f"  latexmkrc-profile: unknown-profile\n"
        ),
    )
    with pytest.raises(ValueError, match='Unknown build.latexmkrc-profile'):
        Config(Namespace(f=str(cfg)))
    