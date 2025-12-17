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
    LB = LatexBuilder(config.build_specs, 
                      searchdirs = [config.autoprob_package_dir])

    if os.path.exists(output_dir):
        if args.overwrite:
            permissions = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
            chmod_recursive(output_dir, permissions)
            rmtree(output_dir)
        else:
            raise Exception(f'Directory "{output_dir}" already exists and "--overwrite" was not specified.')

    document = Document(config.document_specs)

    if config.build_specs.get('ncopies', 1) > 1:
        serials = list(range(1, config.build_specs['ncopies'] + 1))
    else:
        serials = []

    if not serials:
        document.make_substitutions()
        LB.build_document(document, make_solutions=args.solutions)
        FC.append(f'{output_dir}/{LB.output_name_stem}.pdf')
        print(f' => {output_dir}/{LB.output_name_stem}.pdf')
    else:
        for i, serial in enumerate(serials):
            outer_substitutions = dict(serial=serial)
            document.make_substitutions(outer_substitutions)
            LB.build_document(document, make_solutions=args.solutions)
            FC.append(f'{output_dir}/{LB.output_name_stem}.pdf')
            print(f'serial # {serial} ({i+1}/{len(serials)}) => {output_dir}/{LB.output_name_stem}.pdf')
    #     if len(serials) > 1:
    #         AS = AnswerSuperSet([f'answers-{serial}.yaml' for serial in serials])
    #         AS.to_pdf(c)

    # if 'combine' in c.build:
    #     outname = c.build['combine'].get('name', None)
    #     if outname:
    #         args.i = FC.data
    #         if c.build['combine']['sort']:
    #             args.i.sort()
    #         args.o = outname
    #         combine_pdfs(args)


