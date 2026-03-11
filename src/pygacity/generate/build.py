# Author: Cameron F. Abrams, <cfa22@drexel.edu>
"""
Document build functions for pygacity
"""

from copy import deepcopy
import logging
import os
import pickle
import sys
from pathlib import Path
from .answerset import AnswerSet, AnswerSuperSet
from .config import Config, is_executable
from .document import Document
from ..util.collectors import FileCollector
from .latexcompiler import LatexCompiler
from ..util.command import Command

logger = logging.getLogger(__name__)

logging.getLogger("matplotlib").setLevel(logging.WARNING)

def build(args):
    """
    Main build function for pygacity.
    """
    FC = FileCollector()
    config = Config(args)

    build_path: Path = config.build_path
    build_dir = build_path.as_posix()
    cache_path: Path = config.cache_path
    cache_dir = (cache_path.as_posix() if cache_path.is_absolute()
                 else cache_path.relative_to(build_path.parent).as_posix())

    logger.debug(f'Building in {str(build_path)}')
    logger.debug(f'Caching data in {cache_dir}')

    base_builder = LatexCompiler(config.build_specs, 
                                 searchdirs = [config.autoprob_package_dir])
    base_doc = Document(config.document_specs)
    logger.debug(f'base_doc has {len(base_doc.blocks)} blocks')
    if config.solutions:
        soln_builder = LatexCompiler(config.solution_build_specs,
                                    searchdirs = [config.autoprob_package_dir])
        solution_doc = Document(config.solution_document_specs)
        logger.debug(f'solution_doc has {len(solution_doc.blocks)} blocks')

    serials = config.retrieve_serials()

    for i, serial in enumerate(serials):
        serialstr = config.format_serial(serial)
        outer_substitutions = dict(serial=serial, serialstr=serialstr, seriallabel='ser.', build_dir=build_dir, cache_dir=cache_dir, solutions=False)
        base_doc.make_substitutions(outer_substitutions)
        base_builder.build_document(base_doc)
        FC.append(f'{base_builder.working_job_name}.tex')
        logger.info(f'serial # {serialstr} ({i+1}/{len(serials)}) => {build_path.absolute().relative_to(Path.cwd()).as_posix()}/{base_builder.working_job_name}.pdf')
        if config.solutions:
            outer_substitutions['solutions'] = True
            solution_doc.make_substitutions(outer_substitutions)
            soln_builder.build_document(solution_doc)
            FC.append(f'{soln_builder.working_job_name}.tex')
            logger.info(f'serial # {serialstr} ({i+1}/{len(serials)}) => {build_path.absolute().relative_to(Path.cwd()).as_posix()}/{soln_builder.working_job_name}.pdf')

    answerset_tex = answerset(config)
    if answerset_tex:
        FC.append(answerset_tex)

    tex_archive = FC.archive(build_path / 'tex_artifacts', delete=True)
    logger.info(f'Archived TeX artifacts to {tex_archive.absolute().relative_to(Path.cwd()).as_posix()}')
    buildfiles_archive = base_builder.FC.archive(build_path / 'buildfiles', delete=True)
    logger.info(f'Archived build files to {buildfiles_archive.absolute().relative_to(Path.cwd()).as_posix()}')

    pythontex_usergenerated = list(cache_path.glob('pythontex-usergenerated-files-*.pkl'))
    if len(pythontex_usergenerated) > 0:
        UG_FC = FileCollector()
        for f in pythontex_usergenerated:
            with open(f, 'rb') as f:
                obj = pickle.load(f)
                assert isinstance(obj, FileCollector)
                logger.debug(f'Loaded pythontex usergenerated pickle file from {f} with {len(obj.data)} entries.')
            UG_FC.extend([build_path / x for x in obj.data])
            for f in pythontex_usergenerated:
                logger.debug(f'Removing temporary pythontex usergenerated pickle file {f}...')
        num_files = len(UG_FC.data)
        usergen_archive = UG_FC.archive(build_path / 'usergenerated', delete=True)
        logger.info(f'Archived {num_files} user-generated files to {usergen_archive.absolute().relative_to(Path.cwd()).as_posix()}')
    else:
        logger.debug('No user-generated files to archive.')

    if config.solutions:
        solnbuildfiles_archive = soln_builder.FC.archive(build_path / 'solnbuildfiles', delete=True)
        logger.info(f'Archived solution build files to {solnbuildfiles_archive.absolute().relative_to(Path.cwd()).as_posix()}')
        pythontex_usergenerated = list(cache_path.glob('pythontex-solutions-usergenerated-files-*.pkl'))
        if len(pythontex_usergenerated) > 0:
            UG_FC = FileCollector()
            for f in pythontex_usergenerated:
                with open(f, 'rb') as f:
                    obj = pickle.load(f)
                UG_FC.extend([build_path / x for x in obj.data])
                for f in pythontex_usergenerated:
                    logger.debug(f'Removing temporary pythontex usergenerated pickle file {f}...')
            num_files = len(UG_FC.data)
            usergen_archive = UG_FC.archive(build_path / 'solutions-usergenerated', delete=True)
            logger.info(f'Archived {num_files} user-generated files to {usergen_archive.absolute().relative_to(Path.cwd()).as_posix()}')
        else:
            logger.debug('No user-generated files to archive.')

def answerset(config: Config = None) -> str:
    """
    Generates an answer set document from cached answer sets in the build cache.
    """
    build_path: Path = config.build_path
    pickle_cache: Path = config.cache_path
    if not pickle_cache.exists():
        raise Exception(f'No cache found -- cannot build answer set')
    AnswerSets: list[AnswerSet] = []
    for pfile in pickle_cache.glob('answer*.pkl'):
        with pfile.open('rb') as f:
            obj = pickle.load(f)
        AnswerSets.append(obj)
    logger.debug(f'{len(AnswerSets)} answer sets found.')
    if len(AnswerSets) == 0:
        return None
    AS = AnswerSuperSet(initial=AnswerSets)

    answer_buildspecs = {'job-name': config.build_specs.get('answer-name', 'answerset'),
                         'paths': config.build_specs['paths']}
    AnswerSetBuilder = LatexCompiler(answer_buildspecs,
                                    searchdirs = [config.autoprob_package_dir])
    
    answer_docspecs = deepcopy(config.document_specs) 
    answer_docspecs['structure'] = [] 
    answer_docspecs['structure'].append(deepcopy(config.document_specs['structure'][0]))
    answer_docspecs['structure'].append({'text': AS.to_latex()})
    answer_docspecs['structure'].append(deepcopy(config.document_specs['structure'][-1]))
    AnswerSetDoc = Document(answer_docspecs)
    AnswerSetDoc.make_substitutions(dict(serial=0, serialstr='Answer Set', solutions=False, build_dir=build_path.as_posix(), cache_dir=pickle_cache.as_posix()))
    AnswerSetBuilder.build_document(AnswerSetDoc)
    logger.info(f'Combined answer set => {build_path.absolute().relative_to(Path.cwd()).as_posix()}/{AnswerSetBuilder.working_job_name}.pdf')
    answerset_archive = AnswerSetBuilder.FC.archive(build_path / 'answerset_buildfiles', delete=True)
    logger.info(f'Archived answer set build files to {answerset_archive.absolute().relative_to(Path.cwd()).as_posix()}')
    return Path.cwd() / f'{AnswerSetBuilder.working_job_name}.tex'

def answerset_subcommand(args):
    """
    CLI subcommand to build an answer set document from a previous build.
    """
    logger.info(f'Generating answer set document from previous build specified in {args.f}...')
    config = Config(args.f)
    tex_file = answerset(config)
    # remove the tex source
    os.remove(tex_file)

def _resolve_executable(name: str) -> str:
    """Return a usable path to *name*, checking the MiKTeX default on Windows."""
    if is_executable(name):
        return name
    if sys.platform == 'win32':
        candidate = str(Path.home() / 'AppData' / 'Local' / 'Programs' / 'MiKTeX'
                        / 'miktex' / 'bin' / 'x64' / f'{name}.exe')
        if is_executable(candidate):
            return candidate
    raise ValueError(f'"{name}" executable not found in PATH')

def latex_subcommand(args):
    """
    CLI subcommand to compile an arbitrary LaTeX source file with pygacity's
    autoprob package directory on the search path.

    If the source file contains ``\\begin{pycode}`` blocks, a pythontex pass
    is automatically inserted between the first and second pdflatex runs.
    """
    from importlib.resources import files

    tex_file = Path(args.texfile)
    if not tex_file.exists():
        raise FileNotFoundError(f'LaTeX source file not found: {tex_file}')

    # locate autoprob package directory
    autoprob_dir = files('pygacity') / 'resources' / 'autoprob-package' / 'tex' / 'latex'

    pdflatex = _resolve_executable('pdflatex')

    # detect pythontex requirement by scanning the source for pycode environments
    has_pycode = r'\begin{pycode}' in tex_file.read_text(encoding='utf-8', errors='replace')
    if has_pycode:
        pythontex = _resolve_executable('pythontex')
        logger.info(f'pycode blocks detected in {tex_file.name}; pythontex will be run')

    output_dir = args.output_dir or '.'
    output_option = f'-output-directory={output_dir}' if output_dir != '.' else ''
    stem = tex_file.stem
    pytxcode_target = f'{output_dir}/{stem}' if output_dir != '.' else stem

    pdflatex_cmd = Command(
        f'{pdflatex} -interaction=nonstopmode -file-line-error '
        f'-include-directory={autoprob_dir} '
        f'{output_option} {tex_file}',
        ignore_codes=[1],
    )

    def run_pdflatex(label):
        logger.info(f'pdflatex {label}: {tex_file.name}')
        out, err = pdflatex_cmd.run()
        logger.debug(f'pdflatex output:\n{out}')
        logger.debug(f'pdflatex stderr:\n{err}')

    if has_pycode:
        run_pdflatex('pass 1/2')
        logger.info(f'pythontex: {tex_file.name}')
        out, err = Command(f'{pythontex} {pytxcode_target}').run()
        logger.debug(f'pythontex output:\n{out}')
        logger.debug(f'pythontex stderr:\n{err}')
        run_pdflatex('pass 2/2')
    else:
        for i in range(args.runs):
            run_pdflatex(f'pass {i + 1}/{args.runs}')

    pdf = Path(output_dir) / f'{stem}.pdf'
    if pdf.exists():
        logger.info(f'Output: {pdf}')
    else:
        logger.warning(f'Expected output PDF not found: {pdf}')

    