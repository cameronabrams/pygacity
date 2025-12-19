# Author: Cameron F. Abrams, <cfa22@drexel.edu>
import logging
import os
import stat

from shutil import rmtree

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
    config = Config(args.f, overwrite=args.overwrite)
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

    if config.build_specs.get('ncopies', 1) > 1:
        if config.build_specs.get('serials', None):
            serials = config.build_specs['serials']
        elif config.build_specs.get('serial-range', None):
            serials = list(range(config.build_specs['serial-range'][0],
                                 config.build_specs['serial-range'][1] + 1))
        elif config.build_specs.get('serials', None):
            serials = [int(x) for x in config.build_specs['serials']]
        elif config.build_specs.get('serial-file', None):
            with open(config.build_specs['serial-file'], 'r') as f:
                serials = [int(line.strip()) for line in f if line.strip()]
        else:  
            serials = list(range(1, config.build_specs['ncopies'] + 1))
    else:
        serials = [0]

    for i, serial in enumerate(serials):
        outer_substitutions = dict(serial=serial)
        base_doc.make_substitutions(outer_substitutions)
        base_builder.build_document(base_doc, serial=serial)
        FC.append(f'{output_dir}/{base_builder.output_name_stem}.pdf')
        print(f'serial # {serial} ({i+1}/{len(serials)}) => {output_dir}/{base_builder.output_name_stem}.pdf')

    if args.solutions:
        solution_build_specs = config.build_specs.copy()
        solution_build_specs['job-name'] = config.build_specs.get('job-name', 'document') + '_soln'
        soln_builder = LatexBuilder(solution_build_specs,
                                     searchdirs = [config.autoprob_package_dir])
        
        solution_document_specs = config.document_specs.copy()
        solution_document_specs['class']['options'].append('solutions')
        solution_doc = Document(solution_document_specs)
        for i, serial in enumerate(serials):
            outer_substitutions = dict(serial=serial)
            solution_doc.make_substitutions(outer_substitutions)
            soln_builder.build_document(solution_doc)
            FC.append(f'{output_dir}/{soln_builder.output_name_stem}.pdf')
            print(f'serial # {serial} ({i+1}/{len(serials)}) => {output_dir}/{soln_builder.output_name_stem}.pdf')

    # if len(serials) > 1:
    #     AS = AnswerSuperSet([f'answers-{serial}.yaml' for serial in serials])
    #     AS.to_pdf(c)

    # if 'combine' in c.build:
    #     outname = c.build['combine'].get('name', None)
    #     if outname:
    #         args.i = FC.data
    #         if c.build['combine']['sort']:
    #             args.i.sort()
    #         args.o = outname
    #         combine_pdfs(args)


