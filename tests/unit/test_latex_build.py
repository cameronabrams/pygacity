from argparse import Namespace
from pathlib import Path

import pygacity.generate.build as build_module
from pygacity.generate.latexcompiler import LatexCompiler


class DummyDocument:
    def __init__(self, has_pycode: bool = False, serial: int = 0):
        self.has_pycode = has_pycode
        self.substitutions = {
            'serial': serial,
            'serialstr': str(serial),
            'solutions': False,
        }
        self.blocks = []

    def write_source(self, local_output_name=None):
        return None


class FakeCommand:
    created = []
    executed = []

    def __init__(self, command, ignore_codes=None, timeout=120, **options):
        self.command = command
        self.ignore_codes = ignore_codes or []
        self.timeout = timeout
        self.options = options
        self.c = command
        FakeCommand.created.append(self)

    def run(self):
        FakeCommand.executed.append(self.c)
        return '', ''


def _reset_fake_command_state():
    FakeCommand.created.clear()
    FakeCommand.executed.clear()


def test_latexcompiler_build_commands_without_pycode():
    compiler = LatexCompiler(
        {
            'job-name': 'doc',
            'paths': {
                'latexmk': 'latexmk',
                'latexmkrc': '/tmp/pygacity/resources/latexmkrc',
                'pythontex': 'pythontex',
                'build-dir': '.',
                'cache-dir': '.cache',
            },
            'pythontex-workflow': 'explicit',
        },
        searchdirs=['/tmp/incdir'],
    )
    cmds = compiler.build_commands(DummyDocument(has_pycode=False))
    assert len(cmds) == 1
    assert '-xelatex' in cmds[0].c
    assert '/tmp/pygacity/resources/latexmkrc' in cmds[0].c
    assert '-latexoption="-include-directory=/tmp/incdir"' in cmds[0].c
    assert 'pythontex' not in cmds[0].c


def test_latexcompiler_build_commands_with_pycode():
    compiler = LatexCompiler(
        {
            'job-name': 'doc',
            'paths': {
                'latexmk': 'latexmk',
                'latexmkrc': '/tmp/pygacity/resources/latexmkrc',
                'pythontex': 'pythontex',
                'build-dir': '.',
                'cache-dir': '.cache',
            },
            'pythontex-workflow': 'explicit',
        },
        searchdirs=['/tmp/incdir'],
    )
    cmds = compiler.build_commands(DummyDocument(has_pycode=True, serial=7))
    assert len(cmds) == 3
    assert cmds[0].c == cmds[2].c
    assert '-xelatex' in cmds[0].c
    assert '/tmp/pygacity/resources/latexmkrc' in cmds[0].c
    assert cmds[1].c.strip() == 'pythontex ./doc-7'


def test_latexcompiler_build_commands_with_pycode_latexmkrc_mode():
    compiler = LatexCompiler(
        {
            'job-name': 'doc',
            'paths': {
                'latexmk': 'latexmk',
                'latexmkrc': '/tmp/pygacity/resources/latexmkrc',
                'pythontex': 'pythontex',
                'build-dir': '.',
                'cache-dir': '.cache',
            },
            'pythontex-workflow': 'latexmkrc',
        },
        searchdirs=['/tmp/incdir'],
    )
    cmds = compiler.build_commands(DummyDocument(has_pycode=True, serial=7))
    assert len(cmds) == 1
    assert 'latexmk -r' in cmds[0].c
    assert ' pythontex ' not in cmds[0].c


def test_latexcompiler_build_commands_explicit_mode_without_rc():
    compiler = LatexCompiler(
        {
            'job-name': 'doc',
            'paths': {
                'latexmk': 'latexmk',
                'latexmkrc': '',
                'pythontex': 'pythontex',
                'build-dir': '.',
                'cache-dir': '.cache',
            },
            'pythontex-workflow': 'explicit',
        },
        searchdirs=['/tmp/incdir'],
    )
    cmds = compiler.build_commands(DummyDocument(has_pycode=True, serial=7))
    assert len(cmds) == 3
    assert ' -r ' not in cmds[0].c
    assert cmds[1].c.strip() == 'pythontex ./doc-7'


def test_latex_subcommand_without_pycode_runs_requested_count(monkeypatch, tmp_path):
    _reset_fake_command_state()
    tex = tmp_path / 'plain.tex'
    tex.write_text('\\documentclass{article}\\begin{document}Hi\\end{document}', encoding='utf-8')

    monkeypatch.setattr(build_module, '_resolve_executable', lambda name: name)
    monkeypatch.setattr(build_module, 'Command', FakeCommand)

    args = Namespace(texfile=str(tex), output_dir='.', runs=3)
    build_module.latex_subcommand(args)

    assert len(FakeCommand.created) == 1
    assert len(FakeCommand.executed) == 3
    cmd = FakeCommand.created[0].c
    assert 'latexmk -r' in cmd
    assert '-xelatex' in cmd
    assert '/resources/latexmkrc' in cmd
    assert '-latexoption="-include-directory=' in cmd
    assert '/resources/autoprob-package/tex/latex"' in cmd
    assert '"' + str(tex) + '"' in cmd


def test_latex_subcommand_with_pycode_runs_pythontex_between_latexmk(monkeypatch, tmp_path):
    _reset_fake_command_state()
    tex = tmp_path / 'pycode.tex'
    tex.write_text(
        '\\begin{pycode}\\nprint(1)\\n\\end{pycode}',
        encoding='utf-8',
    )

    monkeypatch.setattr(build_module, '_resolve_executable', lambda name: name)
    monkeypatch.setattr(build_module, 'Command', FakeCommand)

    args = Namespace(texfile=str(tex), output_dir='outdir', runs=99)
    build_module.latex_subcommand(args)

    assert len(FakeCommand.executed) == 3
    assert 'latexmk -r' in FakeCommand.executed[0]
    assert '-xelatex' in FakeCommand.executed[0]
    assert '/resources/latexmkrc' in FakeCommand.executed[0]
    assert FakeCommand.executed[1] == 'pythontex outdir/pycode'
    assert 'latexmk -r' in FakeCommand.executed[2]
    assert '-xelatex' in FakeCommand.executed[2]
    assert '-outdir=outdir' in FakeCommand.executed[0]
    assert '-outdir=outdir' in FakeCommand.executed[2]
    assert '/resources/autoprob-package/tex/latex"' in FakeCommand.executed[0]
