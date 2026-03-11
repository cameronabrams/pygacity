"""
Unit tests for pygacity.generate.block
"""
import pytest
from pathlib import Path
from pygacity.generate.block import LatexBlock, path_resolver


# ---------------------------------------------------------------------------
# path_resolver
# ---------------------------------------------------------------------------

class TestPathResolver:

    def test_finds_local_file(self, tmp_path):
        f = tmp_path / 'local.tex'
        f.write_text('hello')
        result = path_resolver(str(f))
        assert result == f

    def test_finds_file_in_search_path(self, tmp_path):
        f = tmp_path / 'remote.tex'
        f.write_text('hello')
        result = path_resolver('remote.tex', search_paths=[tmp_path])
        assert result == f

    def test_appends_extension(self, tmp_path):
        f = tmp_path / 'myfile.tex'
        f.write_text('hello')
        result = path_resolver('myfile', search_paths=[tmp_path], ext='.tex')
        assert result == f

    def test_raises_when_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            path_resolver('nonexistent.tex', search_paths=[tmp_path])


# ---------------------------------------------------------------------------
# LatexBlock.__init__
# ---------------------------------------------------------------------------

class TestLatexBlockInit:

    def test_text_block(self):
        b = LatexBlock({'text': r'\section{Hello}'})
        assert b.textcontents == r'\section{Hello}'
        assert b.sourcename is None
        assert b.question_number is None
        assert b.points == 0
        assert b.group == 0

    def test_empty_block(self):
        b = LatexBlock({})
        assert b.textcontents == ''
        assert not b.has_pycode

    def test_question_block_attrs(self):
        b = LatexBlock({'source': 'x.tex', 'question_number': 3, 'points': 25, 'group': 2})
        assert b.question_number == 3
        assert b.points == 25
        assert b.group == 2

    def test_substitutions_dict_form(self):
        b = LatexBlock({'text': 'hi', 'substitutions': {'FOO': 'bar'}})
        assert b.substitution_map == {'FOO': 'bar'}

    def test_substitutions_list_form(self):
        subs = [{'search': 'FOO', 'replace': 'bar'}, {'search': 'BAZ', 'replace': 'qux'}]
        b = LatexBlock({'text': 'hi', 'substitutions': subs})
        assert b.substitution_map == {'FOO': 'bar', 'BAZ': 'qux'}

    def test_schema_error_text_and_source(self):
        with pytest.raises(ValueError, match='both'):
            LatexBlock({'text': 'hi', 'source': 'foo.tex'})

    def test_schema_error_pythontex_and_source(self):
        with pytest.raises(ValueError):
            LatexBlock({'pythontex': ['setup'], 'source': 'foo.tex'})

    def test_schema_error_pythontex_and_text(self):
        with pytest.raises(ValueError):
            LatexBlock({'pythontex': ['setup'], 'text': 'hi'})

    def test_resources_exist(self):
        b = LatexBlock({})
        assert b.resources_root.exists()
        assert b.templates_dir.exists()


# ---------------------------------------------------------------------------
# LatexBlock.load() — text and pythontex blocks
# ---------------------------------------------------------------------------

class TestLatexBlockLoad:

    def test_text_block_load_is_noop(self):
        content = r'\section{Test} hello world'
        b = LatexBlock({'text': content}).load()
        assert b.textcontents == content
        assert b.processedcontents == content

    def test_text_block_no_pycode(self):
        b = LatexBlock({'text': r'\section{Test}'}).load()
        assert not b.has_pycode

    def test_text_block_detects_pycode(self):
        b = LatexBlock({'text': r'\begin{pycode}x=1\end{pycode}'}).load()
        assert b.has_pycode

    def test_substitution_keys_detected(self):
        b = LatexBlock({'text': r'Hello <<<NAME>>> and <<<PLACE>>>'}).load()
        assert 'NAME' in b.substitution_map
        assert 'PLACE' in b.substitution_map
        assert b.substitution_map['NAME'] is None
        assert b.substitution_map['PLACE'] is None

    def test_predefined_substitution_not_overwritten(self):
        b = LatexBlock({'text': r'<<<FOO>>>', 'substitutions': {'FOO': 'bar'}}).load()
        assert b.substitution_map['FOO'] == 'bar'

    def test_embedded_graphics_detected(self):
        tex = r'\includegraphics[width=0.5\textwidth]{myfig.pdf}'
        b = LatexBlock({'text': tex}).load()
        assert 'myfig.pdf' in b.embedded_graphics

    def test_embedded_graphics_no_duplicates(self):
        tex = (r'\includegraphics{fig.pdf}' + '\n') * 3
        b = LatexBlock({'text': tex}).load()
        assert b.embedded_graphics.count('fig.pdf') == 1

    def test_pythontex_setup_block(self):
        b = LatexBlock({'pythontex': ['setup']}).load()
        assert b.has_pycode
        assert 'serial' in b.textcontents
        assert 'from pygacity.pythontex.setup import *' in b.textcontents

    def test_pythontex_non_setup_block(self):
        b = LatexBlock({'pythontex': ['matplotlib']}).load()
        assert b.has_pycode
        assert 'from pygacity.pythontex.matplotlib import *' in b.textcontents
        # non-setup modules don't inject document globals
        assert 'serial' not in b.textcontents

    def test_source_block_load(self, tmp_path):
        f = tmp_path / 'prob.tex'
        f.write_text(r'\textbf{Problem content}')
        b = LatexBlock({'source': str(f)}).load()
        assert r'\textbf{Problem content}' in b.textcontents
        assert b.sourcepath == f

    def test_source_block_no_question_number_no_pycode_header(self, tmp_path):
        f = tmp_path / 'prob.tex'
        f.write_text('content')
        b = LatexBlock({'source': str(f)}).load()
        # no question_number → pycode header block is still present but empty
        assert b.textcontents.startswith(r'\begin{pycode}')
        assert 'qno' not in b.textcontents

    def test_source_block_with_question_number_injects_globals(self, tmp_path):
        f = tmp_path / 'q.tex'
        f.write_text('content')
        b = LatexBlock({'source': str(f), 'question_number': 2, 'points': 10, 'group': 1}).load()
        assert 'qno = 2' in b.textcontents
        assert 'points = 10' in b.textcontents
        assert 'group = 1' in b.textcontents

    def test_source_block_points_print_statement(self, tmp_path):
        f = tmp_path / 'q.tex'
        f.write_text('content')
        b = LatexBlock({'source': str(f), 'question_number': 1, 'points': 15}).load()
        assert 'print(f"(15 pts.)")' in b.textcontents

    def test_source_block_zero_points_no_print(self, tmp_path):
        f = tmp_path / 'q.tex'
        f.write_text('content')
        b = LatexBlock({'source': str(f), 'question_number': 1, 'points': 0}).load()
        assert 'print' not in b.textcontents

    def test_qno_in_substitution_map(self, tmp_path):
        f = tmp_path / 'q.tex'
        f.write_text('content')
        b = LatexBlock({'source': str(f), 'question_number': 4}).load()
        assert b.substitution_map.get('qno') == 4

    def test_points_in_substitution_map(self, tmp_path):
        f = tmp_path / 'q.tex'
        f.write_text('content')
        b = LatexBlock({'source': str(f), 'question_number': 1, 'points': 20}).load()
        assert b.substitution_map.get('points') == 20

    def test_group_in_substitution_map(self, tmp_path):
        f = tmp_path / 'q.tex'
        f.write_text('content')
        b = LatexBlock({'source': str(f), 'question_number': 1, 'group': 3}).load()
        assert b.substitution_map.get('group') == 3

    def test_missing_config_raises(self, tmp_path):
        f = tmp_path / 'q.tex'
        f.write_text('content')
        with pytest.raises(FileNotFoundError):
            LatexBlock({'source': str(f), 'config': 'nonexistent.yaml'}).load()


# ---------------------------------------------------------------------------
# LatexBlock.substitute()
# ---------------------------------------------------------------------------

class TestLatexBlockSubstitute:

    def test_basic_substitution(self):
        b = LatexBlock({'text': 'Hello <<<NAME>>>'}).load()
        b.substitute(super_substitutions={'NAME': 'World'})
        assert b.processedcontents == 'Hello World'

    def test_super_substitution_provides_value(self):
        b = LatexBlock({'text': '<<<A>>> <<<B>>>'}).load()
        b.substitute(super_substitutions={'A': 'foo', 'B': 'bar'})
        assert b.processedcontents == 'foo bar'

    def test_own_substitution_map_used(self):
        b = LatexBlock({'text': '<<<X>>>', 'substitutions': {'X': 'hello'}}).load()
        b.substitute()
        assert b.processedcontents == 'hello'

    def test_own_map_overrides_super(self):
        b = LatexBlock({'text': '<<<X>>>', 'substitutions': {'X': 'local'}}).load()
        b.substitute(super_substitutions={'X': 'super'})
        assert b.processedcontents == 'local'

    def test_match_all_raises_when_super_passes_none(self):
        # match_all=True raises only when super_substitutions contains a None value
        # (keys with None in substitution_map are filtered before the loop)
        b = LatexBlock({'text': '<<<KEY>>>'}).load()
        with pytest.raises(KeyError):
            b.substitute(super_substitutions={'KEY': None}, match_all=True)

    def test_unresolved_key_leaves_placeholder(self):
        # A key that is None in substitution_map and absent from super_substitutions
        # is simply left untouched regardless of match_all
        b = LatexBlock({'text': '<<<MISSING>>>'}).load()
        b.substitute(match_all=False)
        assert '<<<MISSING>>>' in b.processedcontents

    def test_unresolved_key_not_raised_by_default(self):
        # Confirm the filtering: None-valued keys in substitution_map never raise
        b = LatexBlock({'text': '<<<MISSING>>>'}).load()
        b.substitute(match_all=True)   # should NOT raise
        assert '<<<MISSING>>>' in b.processedcontents

    def test_substitute_resets_processedcontents(self):
        b = LatexBlock({'text': '<<<X>>>', 'substitutions': {'X': 'first'}}).load()
        b.substitute()
        assert b.processedcontents == 'first'
        b.substitution_map['X'] = 'second'
        b.substitute()
        assert b.processedcontents == 'second'

    def test_str_returns_processedcontents(self):
        b = LatexBlock({'text': '<<<X>>>', 'substitutions': {'X': 'result'}}).load()
        b.substitute()
        assert str(b) == 'result'


# ---------------------------------------------------------------------------
# LatexBlock.from_specs()
# ---------------------------------------------------------------------------

class TestFromSpecs:

    def test_plain_block_returns_single(self):
        blocks = LatexBlock.from_specs({'text': 'hello'})
        assert len(blocks) == 1
        assert isinstance(blocks[0], LatexBlock)

    def test_enumerate_expands_to_multiple(self, tmp_path):
        f1 = tmp_path / 'q1.tex'
        f2 = tmp_path / 'q2.tex'
        f1.write_text('Q1 content')
        f2.write_text('Q2 content')
        specs = {'enumerate': [
            {'source': str(f1)},
            {'source': str(f2)},
        ]}
        blocks = LatexBlock.from_specs(specs)
        assert len(blocks) == 2

    def test_enumerate_assigns_sequential_question_numbers(self, tmp_path):
        files = []
        for i in range(3):
            f = tmp_path / f'q{i}.tex'
            f.write_text(f'content {i}')
            files.append(f)
        specs = {'enumerate': [{'source': str(f)} for f in files]}
        blocks = LatexBlock.from_specs(specs)
        assert [b.question_number for b in blocks] == [1, 2, 3]

    def test_enumerate_respects_explicit_question_number(self, tmp_path):
        f = tmp_path / 'q.tex'
        f.write_text('content')
        specs = {'enumerate': [{'source': str(f), 'question_number': 7}]}
        blocks = LatexBlock.from_specs(specs)
        assert blocks[0].question_number == 7

    def test_enumerate_starts_at_one(self, tmp_path):
        f = tmp_path / 'q.tex'
        f.write_text('content')
        specs = {'enumerate': [{'source': str(f)}]}
        blocks = LatexBlock.from_specs(specs)
        assert blocks[0].question_number == 1

    def test_non_list_enumerate_treated_as_plain(self):
        # 'enumerate' key with non-list value → falls through to plain block
        blocks = LatexBlock.from_specs({'text': 'hello', 'enumerate': 'not a list'})
        assert len(blocks) == 1
