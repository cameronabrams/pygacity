# Author: Cameron F. Abrams, <cfa22@drexel.edu>
"""
TeX utility functions for pygacity
"""

import fractions as fr
import numpy as np
import pandas as pd
import logging

from numpy.polynomial import Polynomial

logger = logging.getLogger(__name__)

def Cp_as_tex(Cp_coeff: dict | list, decoration='*', sig: int = 5) -> str:
    """
    Formats a heat capacity polynomial as a LaTeX string.
    
    Parameters
    ----------
    Cp_coeff : dict or list
        dictionary with keys 'a', 'b', 'c', 'd' or list of four coefficients
    decoration : str, optional
        decoration for Cp, e.g., '*' for Cp^*, default is '*'
    sig : int, optional
        number of significant figures for coefficients, default is 5

    Returns
    -------
    retstr : str
        LaTeX formatted heat capacity polynomial string
    """
    idx = [0, 1, 2, 3]
    if type(Cp_coeff) == dict:
        idx = 'abcd'
    sgns=[]
    for i in range(4):
        sgns.append('-' if Cp_coeff[idx[i]]<0 else '+')
    retstr = r'$C_p^' + f'{decoration}' + r'$ = ' + f'{Cp_coeff[idx[0]]:.3f} {sgns[1]} '
    retstr += format_sig(np.abs(Cp_coeff[idx[1]]),sig=sig)+r' $T$ '+f'{sgns[2]} '
    retstr += format_sig(np.abs(Cp_coeff[idx[2]]),sig=sig)+r' $T^2$ '+f'{sgns[3]} '
    retstr += format_sig(np.abs(Cp_coeff[idx[3]]),sig=sig)+r' $T^3$'
    return(retstr)

def table_as_tex(table: dict | pd.DataFrame, sig: int = 5, 
                 drop_zeros: list[bool] = None, total_row: list[str] = [],
                 index: bool = False, use_tex: bool = True) -> str:
    """
    A wrapper to Dataframe.to_latex() that takes a dictionary of heading: column
    items and generates a table 
    
    Parameters
    ----------
    table : dict or pd.DataFrame
        dictionary of column_name: list_of_column_values or a ready DataFrame
    sig: int, optional
        number of significant figures for floating point numbers; default is 5      
    drop_zeros : list of bool, optional
        list of booleans parallel to table keys indicating whether to drop rows with zero in that column; default is None
    total_row : list, optional
        list of strings representing a total row to be added at the bottom of the table; default is empty list
    index : bool, optional
        whether to include the DataFrame index in the LaTeX table; default is False
    use_tex : bool, optional
        whether to format numbers using \(...\) so they appear in math mode; default is True

    Returns
    -------
    tablestring : str
        LaTeX formatted table string
    """
    if isinstance(table, pd.DataFrame):
        df = table
    else:
        logger.debug(f'Creating DataFrame from table dict: {table}\n')
        df = pd.DataFrame(table)
        logger.debug(f'Created DataFrame:\n{df.to_string()}\n')
    if drop_zeros:
        for k, d in zip(table.keys(), drop_zeros):
            if d:
                df = df[df[k] != 0.]
    # determine datatype of each column
    column_formats = {}
    for col in df.columns:
        if pd.api.types.is_float_dtype(df[col]):
            if use_tex:
                column_formats[col] = lambda x: r'\(' + format_sig(x, sig=sig) + r'\)'
            else:
                column_formats[col] = lambda x: format_sig(x, sig=sig)
        elif pd.api.types.is_integer_dtype(df[col]):
            column_formats[col] = lambda x: f'{x:d}'
        else:
            column_formats[col] = lambda x: str(x)
    logger.debug(f'float formatter sig={sig}\n')
    float_format = lambda x: format_sig(x, sig=sig)
    tablestring = df.to_latex(formatters=column_formats, index=index, header=True)
    logger.debug(f'Generated table string:\n{tablestring}\n')
    if len(total_row) > 0:
        i = tablestring.find(r'\bottomrule')
        tmpstr = tablestring[:i-1] + r'\hline' + '\n' + '&'.join(total_row) + r'\\' + '\n' + tablestring[i:]
        tablestring = tmpstr
    return tablestring

def format_sig(x: float, sig: int = 5, use_tex: bool = True) -> str:
    """
    Formats a floating point number to a specified number of significant figures.
    
    Parameters
    ----------
    x : float
        the number to format
    sig : int, optional
        number of significant figures, default is 5
    use_tex : bool, optional
        whether to format in LaTeX scientific notation, default is True 

    Returns
    -------
    s : str
        formatted string
    """
    logger.debug(f'format_sig: x={x}, sig={sig}, use_tex={use_tex}\n')
    from math import log10, floor
    
    if x == 0:
        logger.debug('x is zero\n')
        return "0." + "0" * (sig - 1)
    
    # Determine the order of magnitude
    magnitude = floor(log10(abs(x)))
    
    # Calculate decimal places needed
    decimal_places = sig - magnitude - 1
    
    if decimal_places >= 0:
        # Use fixed-point notation
        result = f"{x:.{decimal_places}f}"    
    elif use_tex:
        s = format(x, f",.{sig}g")
        mantissa, exponent = s.split("e")
        if use_tex:
            exponent = int(exponent)
            result = rf"{mantissa}\times 10^{{{exponent}}}"
        else:
            result = format(x, f",.{sig-1}g")
    logger.debug(f'Formatted result: {result}\n')
    return result

def file_listing(filename: str, style: str = 'mypython') -> str:
    """
    Generates a LaTeX \lstinputlisting command string for including a file.
    
    Parameters
    ----------
    filename : str
        the name of the file to include
    style : str, optional
        the style to use for the listing, default is 'mypython'
        
    Returns
    -------
    str
        LaTeX \lstinputlisting command string
    """
    return r'\lstinputlisting[style='+style+r']{'+filename+r'}'

def frac_or_int_as_tex(f: fr.Fraction) -> str:
    """
    Formats a Fraction as a LaTeX string, using \\frac{}{} if necessary.
    
    Parameters
    ----------
    f : fr.Fraction
        the fraction to format
        
    Returns
    -------
    str
        LaTeX formatted string
    """
    if f.denominator > 1:
        return r'\frac{'+'{:d}'.format(f.numerator)+r'}{'+'{:d}'.format(f.denominator)+r'}'
    else:
        if f.numerator == 1:
            return ''
        else:
            return '{:d}'.format(f.numerator)
        
def polynomial_as_tex(p: Polynomial, x: str = 'x', coeff_round: int = 0):
    """
    Formats a numpy Polynomial as a LaTeX string.
    
    Parameters
    ----------
    p : Polynomial
        the polynomial to format
    x : str, optional
        multiplication symbol, default is 'x'
    coeff_round : int, optional
        number of decimal places to round coefficients, default is 0 (integer)

    Returns
    -------
    str
        LaTeX formatted polynomial string
    """
    coeff = p.coef
    if coeff_round == 0:
        coeff = coeff.astype(int)
    term_strings = []
    for i, c in enumerate(coeff):
        sgn = '+' if c >= 0 else '-'
        if i == 0 and sgn == '+': sgn = ''
        power = len(coeff) - 1 - i
        cstr = str(np.abs(c))
        if coeff_round != 0:
            cstr = str(np.round(np.abs(c), coeff_round))
        if power > 0:
            pstr = '' if power==1 else r'^{'+f'{power}'+r'}'
            cst = '' if np.abs(c) == 1 else cstr
            xstr = x
        else:
            pstr = ''
            xstr = ''
            cst = cstr
        if c != 0:
            term_strings.append(f'{sgn}{cst}{xstr}{pstr}')
    polystr = ''.join(term_strings)
    return polystr

def symneg(value: float, sig: int = 0) -> str:
    if value < 0:
        return f'{format_sig(abs(value), sig=sig)}'
    else:
        return f'-{format_sig(value, sig=sig)}'

def algebraify(expression: str, varvals: dict[str, any] | list[str], varsig: dict[str, int] = {}) -> str | tuple[str, str]:
    """
    Substitute variables into an algebraic expression with intelligent formatting.
    
    Parameters
    ----------
    expression : str
        Algebraic expression with variables in {varname} format
    varvals : dict[str, any] or list[str]
        If list: variable names to substitute symbolically
        If dict: variable names mapped to their values (str for symbols, float for numerics)
    varsig : dict[str, int], optional
        Variable names mapped to significant figures for numeric values
        
    Returns
    -------
    str or tuple[str, str]
        If varvals is a list: returns the symbolic expression
        If varvals is a dict: returns (symbolic_expression, numerical_expression)
    """
    import re
    
    # Convert list to dict for uniform processing
    if isinstance(varvals, list):
        varvals_dict = {name: name for name in varvals}
        return_both = False
    else:
        varvals_dict = varvals
        return_both = True
    
    # Find all variable placeholders in the expression
    var_pattern = r'(-?)\{(\w+)\}'
    
    def replace_var_symbolic(match):
        sign = match.group(1)
        varname = match.group(2)
        
        if varname not in varvals_dict:
            return match.group(0)
        
        value = varvals_dict[varname]
        
        # For symbolic, use the variable name or string value
        if isinstance(value, str):
            symbol = value
        else:
            symbol = varname
        
        # Handle sign cancellation
        if sign == '-' and symbol.startswith('-'):
            return symbol[1:]
        else:
            return sign + symbol
    
    def replace_var_numeric(match):
        sign = match.group(1)
        varname = match.group(2)
        
        if varname not in varvals_dict:
            return match.group(0)
        
        value = varvals_dict[varname]
        
        # Skip if value is symbolic (string)
        if isinstance(value, str):
            # Keep as variable name for symbolic expression
            return sign + varname
        
        # Apply significant figures if specified
        if varname in varsig:
            sigfigs = varsig[varname]
            formatted_value = f"{value:.{sigfigs}g}"
        else:
            formatted_value = str(value)
        
        # Handle sign cancellation for negative numbers
        if sign == '-' and value < 0:
            formatted_value = formatted_value.lstrip('-')
            sign = ''
        
        # Wrap numeric values in parentheses
        return f"{sign}({formatted_value})"
    
    symbolic_result = re.sub(var_pattern, replace_var_symbolic, expression)
    
    if return_both:
        numeric_result = re.sub(var_pattern, replace_var_numeric, expression)
        return symbolic_result, numeric_result
    else:
        return symbolic_result