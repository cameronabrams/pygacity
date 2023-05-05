import pandas as pd
from shutil import move, rmtree
import os
import numpy as np
import argparse as ap
from ThermoProblems.command import Command
import json

def get_keys(template,ldelim='<%',rdelim='%>'):
    ldelim_idx=[]
    rdelim_idx=[]
    for i,c in enumerate(template):
        if template[i:i+2]==ldelim:
            ldelim_idx.append(i)
        if template[i:i+2]==rdelim:
            rdelim_idx.append(i)
    keys=[]
    for l,r in zip(ldelim_idx,rdelim_idx):
        keys.append(template[l+2:r])
    keys=list(set(keys))
    return keys

def key_match(sourcedict,row,ldelim='<%',rdelim='%>'):
    template=sourcedict['template'][:] # copy!
    for k in sourcedict['keys']:
        tmp=template.replace(ldelim+k+rdelim,str(row[k]))
        template=tmp
    return template

def make_all(sources,count=1,**kwargs):
    if 'explicit_tags' in kwargs:
        test_tags=kwargs['explicit_tags']
    else:
        test_tags=np.random.randint(10000000,99999999,count)
    for s in sources:
        with open(s['source'],'r') as f:
            s['template']=f.read()
            if s['customize']:
                s['keys']=get_keys(s['template'])

    for tag in test_tags:
        print(f'Compiling exam for tag {tag}...',end='',flush=True)
        master_source=f'{tag}'
        with open(master_source+'.tex','w') as f:
            for s in sources:
                if s['customize']:
                    source=key_match(s,{'tag':tag})
                else:
                    source=s['template']
                if 'points' in s:
                    pts=s['points']
                    source=r'\item ('+f'{pts}'+r' pts)'+'\n'+source
                f.write(source)
        print('...1',end='',flush=True)
        Command(f'pdflatex --interaction=nonstopmode {master_source}').run(ignore_codes=[1])
        print('...2',end='',flush=True)
        Command(f'pythontex {master_source}').run()
        print('...3',end='',flush=True)
        Command(f'pdflatex {master_source}').run()
        print('...4',end='',flush=True)
        Command(f'pdflatex -jobname={master_source}_soln {master_source}').run()
        print('...5',end='',flush=True)
        Command(f'pythontex {master_source}_soln').run()
        print('...6',end='',flush=True)
        Command(f'pdflatex -jobname={master_source}_soln {master_source}.tex').run()
        print('...moving',end='',flush=True)
        # clean up
        rmtree(f'pythontex-files-{master_source.lower()}')
        rmtree(f'pythontex-files-{master_source.lower()}_soln')
        for suf in ['.tex','.pdf','_soln.pdf']:
            if os.path.exists(os.path.join(savedir,f'{master_source}{suf}')):
                os.remove(os.path.join(savedir,f'{master_source}{suf}'))
            move(f'{master_source}{suf}',savedir)
        for typ in ['.aux','.log','.pytxcode','_soln.aux','_soln.log','_soln.pytxcode']:
            os.remove(f'{master_source}{typ}')
        print('...done.',flush=True)

if __name__=='__main__':
    parser=ap.ArgumentParser()
    parser.add_argument('-n',help='number of unique exams',default=1)
    parser.add_argument('--overwrite',action=ap.BooleanOptionalAction)
    parser.add_argument('--explicit-tags',nargs='+',default=[],help='one or more explicit tags')
    parser.add_argument('-d',help='directory to put exam pdfs in',default='specific')
    parser.add_argument('f',help='mandatory JSON input file')
    args=parser.parse_args()
    savedir=args.d
    if os.path.exists(savedir):
        if args.overwrite:
            rmtree(savedir)
        else:
            raise Exception(f'Directory "{savedir}" already exists and "--overwrite" was not specified.')
    os.mkdir(savedir)
    with open(args.f,'r') as f:
        sources=json.load(f)
    if len(args.explicit_tags)>0:
        make_all(sources,num=args.n,explicit_tags=args.explicit_tags)
    else:
        make_all(sources,num=args.n)