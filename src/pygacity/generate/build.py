# Author: Cameron F. Abrams, <cfa22@drexel.edu>
from copy import deepcopy
import logging
import os
import pickle
from pathlib import Path
from .answerset import AnswerSet, AnswerSuperSet
from .config import Config
from .document import Document
from ..util.collectors import FileCollector
from .latexcompiler import LatexCompiler
from pathlib import Path

logger = logging.getLogger(__name__)

logging.getLogger("ycleptic").setLevel(logging.WARNING)
logging.getLogger("matplotlib").setLevel(logging.WARNING)

def build(args):
    FC = FileCollector()
    config = Config(args)

    build_path: Path = config.build_path
    build_dir = build_path.as_posix()
    cache_path: Path = config.cache_path
    cache_dir = cache_path.relative_to(build_path.parent).as_posix()

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
        outer_substitutions = dict(serial=serial, build_dir=build_dir, cache_dir=cache_dir)
        base_doc.make_substitutions(outer_substitutions)
        base_builder.build_document(base_doc)
        FC.append(f'{base_builder.working_job_name}.tex')
        logger.info(f'serial # {serial} ({i+1}/{len(serials)}) => {build_path.absolute().relative_to(Path.cwd()).as_posix()}/{base_builder.working_job_name}.pdf')
        if config.solutions:
            solution_doc.make_substitutions(outer_substitutions)
            soln_builder.build_document(solution_doc)
            FC.append(f'{soln_builder.working_job_name}.tex')
            logger.info(f'serial # {serial} ({i+1}/{len(serials)}) => {build_path.absolute().relative_to(Path.cwd()).as_posix()}/{soln_builder.working_job_name}.pdf')

    answerset_tex = answerset(config)
    if answerset_tex:
        FC.append(answerset_tex)

    tex_archive = FC.archive(build_path / 'tex_artifacts', delete=True)
    logger.info(f'Archived TeX artifacts to {tex_archive.absolute().relative_to(Path.cwd()).as_posix()}')
    buildfiles_archive = base_builder.FC.archive(build_path / 'buildfiles', delete=True)
    logger.info(f'Archived build files to {buildfiles_archive.absolute().relative_to(Path.cwd()).as_posix()}')

    pythontex_usergenerated = cache_path.glob('pythontex-usergenerated*.pkl')
    if len(pythontex_usergenerated) > 0:
        UG_FC = FileCollector()
        for f in pythontex_usergenerated:
            with open(f, 'rb') as f:
                obj = pickle.load(f)
            UG_FC.extend([build_path / x for x in obj.data])
        usergen_archive = UG_FC.archive(build_path / 'usergenerated', delete=True)
        logger.info(f'Archived user-generated files to {usergen_archive.absolute().relative_to(Path.cwd()).as_posix()}')

    if config.solutions:
        solnbuildfiles_archive = soln_builder.FC.archive(build_path / 'solnbuildfiles', delete=True)
        logger.info(f'Archived solution build files to {solnbuildfiles_archive.absolute().relative_to(Path.cwd()).as_posix()}')

def answerset(config: Config = None) -> str:
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
    AnswerSetDoc.make_substitutions(dict(serial='Answer Set'))
    AnswerSetBuilder.build_document(AnswerSetDoc)
    logger.info(f'Combined answer set => {build_path.absolute().relative_to(Path.cwd()).as_posix()}/{AnswerSetBuilder.working_job_name}.pdf')
    answerset_archive = AnswerSetBuilder.FC.archive(build_path / 'answerset_buildfiles', delete=True)
    logger.info(f'Archived answer set build files to {answerset_archive.absolute().relative_to(Path.cwd()).as_posix()}')
    return Path.cwd() / f'{AnswerSetBuilder.working_job_name}.tex'

def answerset_subcommand(args):
    logger.info(f'Generating answer set document from previous build specified in {args.f}...')
    config = Config(args.f)
    tex_file = answerset(config)
    # remove the tex source
    os.remove(tex_file)

    