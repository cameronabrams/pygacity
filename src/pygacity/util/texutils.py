# Author: Cameron F. Abrams, <cfa22@drexel.edu>
import os
import fractions as fr
import numpy as np
import pandas as pd
import logging
from .command import Command
from .stringthings import FileCollector
from ..generate.document import Document
logger = logging.getLogger(__name__)

class LatexBuilder:
    def __init__(self, build_specs: dict, searchdirs: list = []):
        self.specs = build_specs
        self.pdflatex = self.specs['paths']['pdflatex']
        self.pythontex = self.specs['paths']['pythontex']
        assert os.access(self.pdflatex, os.X_OK)
        assert os.access(self.pythontex, os.X_OK)
        self.searchdirs = searchdirs
        self.output_dir = self.specs.get('output-dir', '.')
        self.output_name_stem = self.specs.get('output-name', 'document')
        self.FC = FileCollector()
        # logger.debug(f'localdirs {self.localdirs}')

    def build_commands(self, document: Document = None, serial=0, make_solutions=False):
        commands = []
        document.write_source(local_output_name=self.output_name_stem)
        includedirs = ''
        for d in self.searchdirs:
            includedirs = includedirs + ' -include-directory=' + str(d)
        logger.debug(f'includedirs {includedirs}')
        has_pycode = document.has_pycode
        output_option = ''
        if self.output_dir != '.':
            output_option = f'-output-directory={self.output_dir}'
        job_name = self.specs.get('job-name', self.output_name_stem)
        if serial > 0:
           job_name = f'{job_name}-{serial}'

        repeated_command = (f'{self.pdflatex} -interaction=nonstopmode '
                                f'-jobname={job_name} {includedirs} '
                                f'{output_option} {self.output_name_stem}')
        commands.append(Command(repeated_command, ignore_codes=[1]))

        self.FC.append(f'{self.output_dir}/{job_name}.aux')
        self.FC.append(f'{self.output_dir}/{job_name}.log')
        if has_pycode:
            self.FC.append(f'{self.output_dir}/{job_name}.pytxcode')
            self.FC.append(f'{self.output_dir}/pythontex-files-{job_name}')
            # don't know if this will work
            commands.append(Command(f'{self.pythontex} {self.output_dir}/{job_name}'))

        commands.append(Command(repeated_command, ignore_codes=[1]))
        return commands

    def build_document(self, document=None, serial=0, make_solutions=False, cleanup=True):
        commands = self.build_commands(document, serial=serial, make_solutions=make_solutions)
        for c in commands:
            logger.debug(f'Running command: {c.c}')
            out, err = c.run()
            logger.debug(f'Command output:\n{out}\n\n')
            logger.debug(f'Command error:\n{err}\n\n')
        if cleanup:
            self.FC.flush()
            
def table_as_tex(table,float_format='{:.4f}'.format,drop_zeros=None,total_row=[]):
    ''' A wrapper to Dataframe.to_latex() that takes a dictionary of heading:column
        items and generates a table '''
    df=pd.DataFrame(table)
    if drop_zeros:
        for k,d in zip(table.keys(),drop_zeros):
            if d:
                df=df[df[k]!=0.]
    tablestring=df.style.to_latex(float_format=float_format)
    if len(total_row)>0:
        i=tablestring.find(r'\bottomrule')
        tmpstr=tablestring[:i-1]+r'\hline'+'\n'+'&'.join(total_row)+r'\\'+'\n'+tablestring[i:]
        tablestring=tmpstr
    return tablestring

def Cp_as_tex(Cp,letters=True,decoration='*'):
    idx=[0,1,2,3]
    if letters:
        idx='abcd'
    sgns=[]
    for i in range(4):
        sgns.append('-' if Cp[idx[i]]<0 else '+')
    retstr=r'$C_p^'+f'{decoration}'+r'$ = '+f'{Cp[idx[0]]:.3f} {sgns[1]} '
    retstr+=sci_notation_as_tex(np.abs(Cp[idx[1]]),mantissa_fmt='{:.4e}')+r' $T$ '+f'{sgns[2]} '
    retstr+=sci_notation_as_tex(np.abs(Cp[idx[2]]),mantissa_fmt='{:.4e}')+r' $T^2$ '+f'{sgns[3]} '
    retstr+=sci_notation_as_tex(np.abs(Cp[idx[3]]),mantissa_fmt='{:.4e}')+r' $T^3$'
    return(retstr)

def sci_notation_as_tex(x,**kwargs):
    ''' Writes a floating point in LaTeX format scientific notation '''
    maglimit=kwargs.get('maglimit',1000)
    fmt=kwargs.get('fmt','{:.4f}')
    mantissa_fmt=kwargs.get('mantissa_fmt','{:.6e}')
    mathmode=kwargs.get('mathmode',False)
    if 1/maglimit<np.abs(x)<maglimit:
        return str(fmt.format(x))
    xstr=mantissa_fmt.format(x)
    mantissa,exponent=xstr.split('e')
    if exponent[0]=='+':
        exponent=exponent[1:]
        if exponent[0]=='0':
            exponent=exponent[1:]
            if exponent[0]=='0':
                return mantissa
    elif exponent[0]=='-' and exponent[1]=='0':
        exponent='-'+exponent[2:]
    if not mathmode:
        if float(mantissa)==1.0: return r'$10^{'+exponent+r'}$'
        return mantissa+r'$\times10^{'+exponent+r'}$'
    else:
        if float(mantissa)==1.0: return r'10^{'+exponent+r'}'
        return mantissa+r'\times10^{'+exponent+r'}'

def file_listing(filename,style='mypython'):
    ''' Generates a program listing using the listings package '''
    return r'\lstinputlisting[style='+style+r']{'+filename+r'}'

def StoProd_as_tex(bases,nu,parens=False):
    ''' Generates a LaTeX formatted stoichiometric ratio 
        Parameters:
            bases -- list of strings, e.g., ['x_1', 'x_2', ] 
            nu -- list of stoichiometric coefficients, parallel to bases
        Returns:
            a \frac{}{}
    '''
    reactants,products,nureactants,nuproducts=split_reactants_products(bases,nu)
    expreactants=['' if n==1 else r'^{'+n+r'}' for n in nureactants]
    expproducts=['' if n==1 else r'^{'+n+r'}' for n in nuproducts]
    if parens:
        numerator=''.join([r'('+c+r')'+e for c,e in zip(products,expproducts)])
        denominator=''.join([r'('+c+r')'+e for c,e in zip(reactants,expreactants)])
    else:
        numerator=''.join([c+e for c,e in zip(products,expproducts)])
        denominator=''.join([c+e for c,e in zip(reactants,expreactants)])
    return r'\frac{'+numerator+r'}{'+denominator+r'}'

def split_reactants_products(emps,nu):
    reactants=[]
    products=[]
    nureactants=[]
    nuproducts=[]
    for e,n in zip(emps,nu):
        if n<0:
            reactants.append(e)
            f=fr.Fraction(-n)
            nureactants.append(frac_or_int_as_tex(f))
        elif n>0:
            products.append(e)
            f=fr.Fraction(n)
            nuproducts.append(frac_or_int_as_tex(f))
    return (reactants,products,nureactants,nuproducts)

def frac_or_int_as_tex(f):
    if f.denominator>1:
        return r'\frac{'+'{:d}'.format(f.numerator)+r'}{'+'{:d}'.format(f.denominator)+r'}'
    else:
        if f.numerator==1:
            return ''
        else:
            return '{:d}'.format(f.numerator)
        
def polynomial_as_tex(p,x='x',coeff_round=0):
    coeff=p.coef
    if coeff_round==0:
        coeff=coeff.astype(int)
    term_strings=[]
    for i,c in enumerate(coeff):
        sgn='+' if c>=0 else '-'
        if i==0 and sgn=='+': sgn=''
        power=len(coeff)-1-i
        cstr=str(np.abs(c))
        if coeff_round!=0:
            cstr=str(np.round(np.abs(c),coeff_round))
        if power>0:
            pstr='' if power==1 else r'^{'+f'{power}'+r'}'
            cst='' if np.abs(c)==1 else cstr
            xstr=x
        else:
            pstr=''
            xstr=''
            cst=cstr
        if c!=0:
            term_strings.append(f'{sgn}{cst}{xstr}{pstr}')
    polystr=''.join(term_strings)
    return polystr