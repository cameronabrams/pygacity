# Author: Cameron F. Abrams, <cfa22@drexel.edu>
import os
import fractions as fr
import numpy as np
import pandas as pd
import logging
from .command import Command
from .stringthings import FileCollector
logger=logging.getLogger(__name__)

class LatexBuilder:
    def __init__(self,exepaths={},localdirs=[]):
        self.exepaths=exepaths
        self.localdirs=localdirs
        self.FC=FileCollector()
        logger.debug(f'localdirs {self.localdirs}')

    def verify_access(self):
        assert os.access(self.exepaths.get('pdflatex',None),os.X_OK)
        assert os.access(self.exepaths.get('pythontex',None),os.X_OK)

    def build_commands(self,document=None,make_solutions=False):
        commands=[]
        output_name=document.output_name
        if output_name:
            pdflatex_cmd=self.exepaths['pdflatex']
            pythontex_cmd=self.exepaths['pythontex']
            includedirs=''
            for d in self.localdirs:
                includedirs=includedirs+' --include-directory='+d
            logger.debug(f'includedirs {includedirs}')
            has_pycode=document.has_pycode
            commands.append(Command(f'{pdflatex_cmd} --interaction=nonstopmode {includedirs} {output_name}',ignore_codes=[1]))
            self.FC.append(f'{output_name}.aux')
            self.FC.append(f'{output_name}.log')
            if has_pycode:
                self.FC.append(f'{output_name}.pytxcode')
                self.FC.append(f'pythontex-files-{output_name}')
                commands.append(Command(f'{pythontex_cmd} {output_name}'))
            commands.append(Command(f'{pdflatex_cmd} {includedirs} {output_name}'))
            if make_solutions:
                commands.append(Command(f'{pdflatex_cmd} -jobname={output_name}_soln {includedirs} {output_name}'))
                self.FC.append(f'{output_name}_soln.aux')
                self.FC.append(f'{output_name}_soln.log')
                if has_pycode:
                    self.FC.append(f'{output_name}_soln.pytxcode')
                    self.FC.append(f'pythontex-files-{output_name}_soln')
                    commands.append(Command(f'{pythontex_cmd} {output_name}_soln'))
                commands.append(Command(f'{pdflatex_cmd} -jobname={output_name}_soln {includedirs} {output_name}'))
        return commands

    def build_document(self,document=None,make_solutions=False,cleanup=True):
        commands=self.build_commands(document,make_solutions=make_solutions)
        for c in commands:
            c.run()
        if cleanup:
            self.FC.flush()
            document.flush()
            
def table_as_tex(table,float_format='{:.4f}'.format,drop_zeros=None,total_row=[]):
    ''' A wrapper to Dataframe.to_latex() that takes a dictionary of heading:column
        items and generates a table '''
    df=pd.DataFrame(table)
    if drop_zeros:
        for k,d in zip(table.keys(),drop_zeros):
            if d:
                df=df[df[k]!=0.]
    tablestring=df.style.to_latex(escape=False,index=False,float_format=float_format)
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