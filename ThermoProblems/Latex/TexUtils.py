import pandas as pd
import fractions as fr
from math import fabs
import numpy as np
''' 
    TexUtils for ThermoProblems 
    Cameron F. Abrams cfa22@drexel.edu

    These functions are used to produce LaTeX-syntax strings relevant
    for preparing documents containing homework and exam problems for
    thermodynamics (and beyond).

'''
def table_as_tex(tabledict,float_format='{:.4f}'.format,drop_zeros=None,total_row=[]):
    ''' A wrapper to Dataframe.to_latex() that takes a dictionary of heading:column
        items and generates a table '''
    df=pd.DataFrame(tabledict)
    if drop_zeros:
        for k,d in zip(tabledict.keys(),drop_zeros):
            if d:
                df=df[df[k]!=0.]
    tablestring=df.to_latex(escape=False,index=False,float_format=float_format)
    if len(total_row)>0:
        i=tablestring.find(r'\bottomrule')
        tmpstr=tablestring[:i-1]+r'\hline'+'\n'+'&'.join(total_row)+r'\\'+'\n'+tablestring[i:]
        tablestring=tmpstr
    return tablestring

def sci_notation_as_tex(x,**kwargs):
    ''' Writes a floating point in LaTeX format scientific notation '''
    maglimit=1000 if 'maglimit' not in kwargs else kwargs['maglimit']
    fmt='{:.4f}' if 'fmt' not in kwargs else kwargs['fmt']
    mantissa_fmt='{:.6e}' if 'mantissa_fmt' not in kwargs else kwargs['mantissa_fmt']
    mathmode=False if 'mathmode' not in kwargs else kwargs['mathmode']
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
        return mantissa+r'$\times10^{'+exponent+r'}$'
    else:
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