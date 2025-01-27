# Author: Cameron F. Abrams, <cfa22@drexel.edu>
from shutil import rmtree
import os
import argparse as ap
from .config import Config
import logging
import stat
from .stringthings import chmod_recursive
from .answerset import AnswerSuperSet

logger=logging.getLogger(__name__)

logging.getLogger("ycleptic").setLevel(logging.WARNING)
logging.getLogger("matplotlib").setLevel(logging.WARNING)

def cli():
    parser=ap.ArgumentParser()
    parser.add_argument('--overwrite',default=False,action=ap.BooleanOptionalAction,help='completely remove old save dir and build new exams')
    parser.add_argument('--solutions',default=True,action=ap.BooleanOptionalAction,help='build solutions')
    parser.add_argument('f',help='mandatory YAML input file')
    args=parser.parse_args()
    c=Config(args.f)
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
    for serial in c.serials:
        keymap=dict(serial=serial)
        c.document.resolve_instance(keymap)
        c.LB.build_document(c.document,make_solutions=args.solutions)
        print(f'{serial}')
    if len(c.serials)>1:
        AS=AnswerSuperSet([f'answers-{serial}.yaml' for serial in c.serials])
        AS.to_pdf(c)

    if savedir!='.':
        os.chdir(basedir)

if __name__=='__main__':
    cli()
