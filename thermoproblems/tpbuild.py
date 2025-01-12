# Author: Cameron F. Abrams, <cfa22@drexel.edu>
from shutil import rmtree
import os
import argparse as ap
from .config import Config
import logging

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
    savedir=args.d
    if os.path.exists(savedir):
        if args.overwrite:
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
    if savedir!='.':
        os.chdir(basedir)

if __name__=='__main__':
    cli()
