# Author: Cameron F. Abrams, <cfa22@drexel.edu>
from __future__ import annotations
import fractions as fr
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def table_as_tex(table, float_format='\({:.4f}\)'.format, drop_zeros=None, total_row=[], index=False):
    ''' A wrapper to Dataframe.to_latex() that takes a dictionary of heading:column
        items and generates a table '''
    df = pd.DataFrame(table)
    if drop_zeros:
        for k, d in zip(table.keys(), drop_zeros):
            if d:
                df = df[df[k] != 0.]
    tablestring = df.to_latex(float_format=float_format, index=index, header=True)
    logger.debug(f'Generated table string:\n{tablestring}\n')
    if len(total_row) > 0:
        i = tablestring.find(r'\bottomrule')
        tmpstr = tablestring[:i-1] + r'\hline' + '\n' + '&'.join(total_row) + r'\\' + '\n' + tablestring[i:]
        tablestring = tmpstr
    return tablestring

def Cp_as_tex(Cp_coeff: dict | list, decoration='*', sig: int = 5) -> str:
    idx=[0,1,2,3]
    if type(Cp_coeff)==dict:
        idx='abcd'
    sgns=[]
    for i in range(4):
        sgns.append('-' if Cp_coeff[idx[i]]<0 else '+')
    retstr=r'$C_p^'+f'{decoration}'+r'$ = '+f'{Cp_coeff[idx[0]]:.3f} {sgns[1]} '
    retstr+=format_sig(np.abs(Cp_coeff[idx[1]]),sig=sig)+r' $T$ '+f'{sgns[2]} '
    retstr+=format_sig(np.abs(Cp_coeff[idx[2]]),sig=sig)+r' $T^2$ '+f'{sgns[3]} '
    retstr+=format_sig(np.abs(Cp_coeff[idx[3]]),sig=sig)+r' $T^3$'
    return(retstr)

def format_sig(x: float, sig: int = 5, use_tex: bool = True) -> str:
    s = format(x, f",.{sig}g")
    if "e" in s:
        mantissa, exponent = s.split("e")
        if use_tex:
            exponent = int(exponent)      # removes + and leading zeros
            return rf"{mantissa}\times 10^{{{exponent}}}"
    return s

def sci_notation_as_tex(x, **kwargs):
    ''' Writes a floating point in LaTeX format scientific notation '''
    maglimit = kwargs.get('maglimit',1000)
    fmt = kwargs.get('fmt','{:.4f}')
    mantissa_fmt = kwargs.get('mantissa_fmt','{:.6e}')
    mathmode = kwargs.get('mathmode',False)
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
    for e,nn in zip(emps,nu):
        n = float(np.round(nn,5))
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