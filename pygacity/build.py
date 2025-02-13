# Author: Cameron F. Abrams, <cfa22@drexel.edu>
from shutil import rmtree
import os
from .config import Config
import logging
import stat
from .stringthings import chmod_recursive, FileCollector
from .answerset import AnswerSuperSet
from .pdfutils import combine_pdfs

logger=logging.getLogger(__name__)

logging.getLogger("ycleptic").setLevel(logging.WARNING)
logging.getLogger("matplotlib").setLevel(logging.WARNING)

def build(args):
    FC=FileCollector()
    print(f'Building exams as specified in {args.f}...')
    c=Config(args.f,overwrite=args.overwrite)
    savedir=c.build.get('output-dir','.')
    if os.path.exists(savedir):
        if args.overwrite:
            permissions = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
            chmod_recursive(savedir,permissions)
            rmtree(savedir)
        else:
            raise Exception(f'Directory "{savedir}" already exists and "--overwrite" was not specified.')
    os.mkdir(savedir)
    basedir=os.getcwd()
    os.chdir(savedir)
    for i,serial in enumerate(c.serials):
        keymap=dict(serial=serial)
        c.document.resolve_instance(keymap)
        c.LB.build_document(c.document,make_solutions=args.solutions)
        FC.append(f'{c.document.output_name}.pdf')
        print(f'serial # {serial} ({i+1}/{len(c.serials)}) => {c.document.output_name}.pdf')
    if len(c.serials)>1:
        AS=AnswerSuperSet([f'answers-{serial}.yaml' for serial in c.serials])
        AS.to_pdf(c)

    if 'combine' in c.build:
        outname=c.build['combine'].get('name',None)
        if outname:
            args.i=FC.data
            if c.build['combine']['sort']:
                args.i.sort()
            args.o=outname
            combine_pdfs(args)

    if savedir!='.':
        os.chdir(basedir)

