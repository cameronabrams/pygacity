# Author: Cameron F. Abrams, <cfa22@drexel.edu>
from shutil import move, rmtree
import os
import numpy as np
import argparse as ap
from .command import Command
import json
import glob
from .config import Config
from .template import Template
import logging

logger=logging.getLogger(__name__)

logging.getLogger("ycleptic").setLevel(logging.WARNING)
logging.getLogger("matplotlib").setLevel(logging.WARNING)

def make_one(master_source,make_solutions=True):
    print('...1',end='',flush=True)
    Command(f'pdflatex --interaction=nonstopmode {master_source}').run(ignore_codes=[1])
    print('...2',end='',flush=True)
    Command(f'pythontex {master_source}').run()
    print('...3',end='',flush=True)
    Command(f'pdflatex {master_source}').run()
    if make_solutions:
        print('...4',end='',flush=True)
        Command(f'pdflatex -jobname={master_source}_soln {master_source}').run()
        print('...5',end='',flush=True)
        Command(f'pythontex {master_source}_soln').run()
        print('...6',end='',flush=True)
        Command(f'pdflatex -jobname={master_source}_soln {master_source}.tex').run()

def make_all(sources,count=1,**kwargs):
    savedir=kwargs.get('savedir','.')
    test_tags=kwargs.get('explicit_tags',np.random.randint(10000000,99999999,count))
    for s in sources:
        with open(s['source'],'r') as f:
            s['template']=f.read()
            if s['customize']:
                s['keys']=get_keys(s['template'])

    for tag in test_tags:
        print(f'Compiling exam for tag {tag}...',end='',flush=True)
        master_source=f'{tag}'
        make_solutions=kwargs.get('solutions',True)
        questions=[]
        with open(master_source+'.tex','w') as f:
            for s in sources:
                if s['source'].startswith('Q_'):
                    d,fn=os.path.split(s['source'])
                    questions.append(d[2:])
                if s['customize']:
                    source=key_match(s,{'tag':tag})
                else:
                    source=s['template']
                if 'points' in s:
                    pts=s['points']
                    source=r'\item ('+f'{pts}'+r' pts)'+'\n'+source
                f.write(source)
        # print(questions)
        make_one(master_source,make_solutions=make_solutions)
        print(f'...moving to {savedir}',end='',flush=True)
        # clean up
        for d in [f'pythontex-files-{master_source.lower()}',f'pythontex-files-{master_source.lower()}_soln']:
            if os.path.exists(d):
                rmtree(d)
        # print(['.tex','.pdf','_soln.pdf']+[f'{q}_soln.json' for q in questions])
        for suf in ['.tex','.pdf','_soln.pdf']+[f'_{q}_soln.json' for q in questions]:
            if os.path.exists(os.path.join(savedir,f'{master_source}{suf}')):
                os.remove(os.path.join(savedir,f'{master_source}{suf}'))
            if os.path.exists(f'{master_source}{suf}'):
                move(f'{master_source}{suf}',savedir)
            else:
                print(f'warning: could not find {master_source}{suf}')
        for typ in ['.aux','.log','.pytxcode','_soln.aux','_soln.log','_soln.pytxcode']:
            if os.path.exists(f'{master_source}{typ}'):
                os.remove(f'{master_source}{typ}')
        print('...done.',flush=True)

def cli():
    parser=ap.ArgumentParser()
    # parser.add_argument('-n',help='number of unique copies',default=1,type=int)
    # parser.add_argument('--overwrite',default=False,action=ap.BooleanOptionalAction,help='completely remove old save dir and build new exams')
    # parser.add_argument('--solutions',default=True,action=ap.BooleanOptionalAction,help='build solutions')
    # parser.add_argument('--rebuild',default=False,action=ap.BooleanOptionalAction,help='Rebuild all exams found in a previous save directory')
    # parser.add_argument('--explicit-tags',nargs='+',default=[],help='one or more explicit tags')
    # parser.add_argument('--explicit-tags-file',type=str,default='tags.in',help='file containing one or more explicit tags')
    # parser.add_argument('-d',help='directory to save exam pdfs and solution YAML files in',default='specific')
    parser.add_argument('f',help='mandatory YAML input file')
    args=parser.parse_args()
    c=Config(args.f)

    savedir=args.d
    if os.path.exists(savedir):
        if args.overwrite:
            rmtree(savedir)
        elif not args.rebuild:
            raise Exception(f'Directory "{savedir}" already exists and "--overwrite" or "--rebuild" was not specified.')
    if not args.rebuild:
        os.mkdir(savedir)
    with open(args.f,'r') as f:
        sources=json.load(f)
    if len(args.explicit_tags)>0:
        make_all(sources,count=args.n,explicit_tags=args.explicit_tags,solutions=args.solutions,savedir=savedir)
    elif args.rebuild:
        taglist=[x.split('\\')[1].split('_')[0] for x in glob.glob(f'{savedir}/*_soln.pdf')]
        rmtree(savedir)
        os.mkdir(savedir)
        make_all(sources,count=len(taglist),explicit_tags=taglist,solutions=args.solutions,savedir=savedir)
    elif os.path.exists(args.explicit_tags_file):
        with open(args.explicit_tags_file,'r') as f:
            explicit_tags=list(map(int,f.read().split('\n')))
        make_all(sources,count=len(explicit_tags),explicit_tags=explicit_tags,solutions=args.solutions,savedir=savedir)
    else:
        make_all(sources,count=args.n,solutions=args.solutions,savedir=savedir)

if __name__=='__main__':
    cli()
