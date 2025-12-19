# Author: Cameron F. Abrams, <cfa22@drexel.edu>
from copy import deepcopy
import logging
import os
import stat
import random
from shutil import rmtree
from pathlib import Path
from .answerset import AnswerSuperSet
from .config import Config
from .document import Document
from ..util.pdfutils import combine_pdfs
from ..util.stringthings import chmod_recursive, FileCollector
from ..util.texutils import LatexBuilder

logger = logging.getLogger(__name__)

logging.getLogger("ycleptic").setLevel(logging.WARNING)
logging.getLogger("matplotlib").setLevel(logging.WARNING)

def build(args):
    logger.info(f'Building document(s) as specified in {args.f}...')
    FC = FileCollector()
    config = Config(args.f)
    seed = config.build_specs.get('seed', None)
    if seed is not None:
        random.seed(seed)
        logger.info(f'Setting random seed to {seed}.')
    output_dir = config.build_specs.get('output-dir', '.')
    if os.path.exists(output_dir):
        if args.overwrite:
            permissions = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
            chmod_recursive(output_dir, permissions)
            rmtree(output_dir)
        else:
            raise Exception(f'Directory "{output_dir}" already exists and "--overwrite" was not specified.')
    os.makedirs(output_dir, exist_ok=True)

    base_builder = LatexBuilder(config.build_specs, 
                                 searchdirs = [config.autoprob_package_dir])
    base_doc = Document(config.document_specs)
    logger.debug(f'base_doc has {len(base_doc.blocks)} blocks')
    if args.solutions:
        solution_build_specs = deepcopy(config.build_specs)
        # solution_build_specs['output-name'] = config.build_specs.get('output-name', 'document') + '_soln'
        solution_build_specs['job-name'] = config.build_specs.get('job-name', 'document') + '_soln'
        soln_builder = LatexBuilder(solution_build_specs,
                                    searchdirs = [config.autoprob_package_dir])
        
        solution_document_specs = deepcopy(config.document_specs)
        solution_document_specs['class']['options'].append('solutions')
        solution_doc = Document(solution_document_specs)
        logger.debug(f'solution_doc has {len(solution_doc.blocks)} blocks')

    if output_dir != '.':
        # find any configs referenced in document blocks and copy them to output_dir
        for block in base_doc.blocks:
            block.copy_referenced_configs(output_dir)

    if config.build_specs.get('copies', 1) > 1:
        if config.build_specs.get('serials', None):
            # check for explict serials
            serials = [int(x) for x in config.build_specs['serials']]
        elif config.build_specs.get('serial-range', None):
            # check for a serial range
            serials = list(range(config.build_specs['serial-range'][0],
                                 config.build_specs['serial-range'][1] + 1))
        elif config.build_specs.get('serial-file', None):
            # check for a file containing serials, one integer per line
            with open(config.build_specs['serial-file'], 'r') as f:
                serials = [int(line.strip()) for line in f if line.strip()]
        else:
            serial_digits = config.build_specs.get('serial-digits', len(str(config.build_specs['copies'])))
            # generate 'copies' random serial numbers
            serials = set()
            while len(serials) < config.build_specs['copies']:
                serial = random.randint(10**(serial_digits-1), 10**serial_digits - 1)
                serials.add(serial)
            serials = list(serials)
            serials.sort()
    else:
        serials = [0]

    for i, serial in enumerate(serials):
        outer_substitutions = dict(serial=serial)
        base_doc.make_substitutions(outer_substitutions)
        base_builder.build_document(base_doc)
        FC.append(f'{base_builder.working_job_name}.tex')
        print(f'serial # {serial} ({i+1}/{len(serials)}) => {output_dir}/{base_builder.working_job_name}.pdf')
        if args.solutions:
            solution_doc.make_substitutions(outer_substitutions)
            soln_builder.build_document(solution_doc)
            FC.append(f'{soln_builder.working_job_name}.tex')
            print(f'serial # {serial} ({i+1}/{len(serials)}) => {output_dir}/{soln_builder.working_job_name}.pdf')
    for f in FC.data:
        logger.debug(f'Generated file: {f}')
    FC.archive(os.path.join(output_dir, 'tex_artifacts'))
    if len(serials) > 1:
        answerset(config)

def answerset(config: Config = None):
    output_dir = config.build_specs.get('output-dir', '.')
    apparent_answer_files = list(Path(output_dir).glob('answers-*.yaml'))
    if not apparent_answer_files:
        raise FileNotFoundError(f'No answer files found in {output_dir} matching pattern "answers-*.yaml"')
    filenames = [str(x) for x in apparent_answer_files]
    filenames.sort()
    AS = AnswerSuperSet(filenames)
    answer_buildspecs = {'output-dir': output_dir,
                            'job-name': config.build_specs.get('answer-name', 'answerset'),
                            'paths': config.build_specs['paths']}
    AnswerSetBuilder = LatexBuilder(answer_buildspecs,
                                    searchdirs = [config.autoprob_package_dir])
    
    answer_docspecs = deepcopy(config.document_specs) 
    answer_docspecs['structure'] = [] 
    answer_docspecs['structure'].append(deepcopy(config.document_specs['structure'][0]))
    answer_docspecs['structure'].append(
        {
            'unstructured': {
                'content': r'\begin{center}\rotatebox{-90}{' + AS.to_latex() + r'}\end{center}'
            }
        })
    answer_docspecs['structure'].append(deepcopy(config.document_specs['structure'][-1]))
    AnswerSetDoc = Document(answer_docspecs)
    AnswerSetDoc.make_substitutions(dict(serial='Answer Set'))
    AnswerSetBuilder.build_document(AnswerSetDoc)
    print(f'Combined answer set => {output_dir}/{AnswerSetBuilder.working_job_name}.pdf')

def answerset_subcommand(args):
    logger.info(f'Generating answer set document from previous build specified in {args.f}...')
    config = Config(args.f)
    answerset(config)
    # if 'combine' in c.build:
    #     outname = c.build['combine'].get('name', None)
    #     if outname:
    #         args.i = FC.data
    #         if c.build['combine']['sort']:
    #             args.i.sort()
    #         args.o = outname
    #         combine_pdfs(args)


