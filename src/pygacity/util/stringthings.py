# Author: Cameron F. Abrams, <cfa22@drexel.edu>
""" 
Utility string functions for pygacity
"""
import importlib.metadata
import logging
import pandas as pd
import shutil

from io import StringIO
from pathlib import Path

logger = logging.getLogger(__name__)

__pygacity_version__ = importlib.metadata.version("pygacity")

banner_message = f"""

░       ░░░  ░░░░  ░░░      ░░░░      ░░░░      ░░░        ░░        ░░  ░░░░  ░
▒  ▒▒▒▒  ▒▒▒  ▒▒  ▒▒▒  ▒▒▒▒▒▒▒▒  ▒▒▒▒  ▒▒  ▒▒▒▒  ▒▒▒▒▒  ▒▒▒▒▒▒▒▒  ▒▒▒▒▒▒  ▒▒  ▒▒
▓       ▓▓▓▓▓    ▓▓▓▓  ▓▓▓   ▓▓  ▓▓▓▓  ▓▓  ▓▓▓▓▓▓▓▓▓▓▓  ▓▓▓▓▓▓▓▓  ▓▓▓▓▓▓▓    ▓▓▓
█  ███████████  █████  ████  ██        ██  ████  █████  ████████  ████████  ████
█  ███████████  ██████      ███  ████  ███      ███        █████  {__pygacity_version__:█^8s}  ████
    (\"pie-GAS-ity\")
    (c) 2025 Cameron F. Abrams <cfa22@drexel.edu>
"""

def banner(logf: callable = print):
    """
    Logs the pygacity banner message using the provided logging function.
    
    Parameters
    ----------
    logf : function
       writer; e.g., print, f.write, etc.
    """
    my_logger(banner_message, logf, fill=' ', just='<')

def my_logger(msg: str | list | dict, logf: callable = print, width: int = None, 
              fill: str = '', just: str = '<', frame: str = '', 
              depth: int = 0, **kwargs):
    """
    A fancy logger with recursion for lists and dicts.
    
    Parameters
    ----------
    msg : str, list, or dict
       the message to be logged, either as a single string, list, or dict
    logf : function, optional
       writer; default is print; works with logger.info, f.write, etc.
    width : int, optional
       linelength in bytes; default is terminal width for print, 67 otherwise
    fill : str, optional
       single character used to fill blank spaces
    just : str, optional
       format character for justification: '<' (left), '>' (right), '^' (center). 
       default is '<' (left)
    frame : str, optional
       single character used to frame the message block
    depth : int, optional
       indentation depth for nested structures (default is 0)
    """
    if width is None:
        if logf is print:
            ts = shutil.get_terminal_size((80,20))
            width = ts.columns
        else:
            width = 67
    fmt = r'{' + r':' + fill + just + f'{width}' + r'}'
    ll = ' ' if just in '^>' else ''
    rr = ' ' if just in '^<' else ''
    if frame:
        ffmt = r'{' + r':' + frame + just + f'{width}' + r'}'
        logf(ffmt.format(frame))
    if type(msg) == list:
        for tok in msg:
            my_logger(tok, logf, width=width, fill=fill, just=just, frame=False, depth=depth, kwargs=kwargs)
    elif type(msg) == dict:
        for key,value in msg.items():
            if type(value) == str or not hasattr(value, "__len__"):
                my_logger(f'{key}: {value}', logf, width=width, fill=fill, just=just, frame=False, depth=depth, kwargs=kwargs)
            else:
                my_logger(f'{key}:', logf, width=width, fill=fill, just=just, frame=False, depth=depth, kwargs=kwargs)
                my_logger(value, logf, width=width, fill=fill, just=just, frame=False, depth=depth+1, kwargs=kwargs)
    elif type(msg) == pd.DataFrame:
        dfoutmode = kwargs.get('dfoutmode','value')
        if dfoutmode == 'value':
            my_logger([ll+x+rr for x in msg.to_string().split('\n')], logf, width=width, fill=fill, just=just, frame=False, depth=depth, kwargs=kwargs)
        elif dfoutmode == 'info':
            buf = StringIO()
            msg.info(buf=buf)
            my_logger([ll+x+rr for x in buf.getvalue().split('\n')], logf, width=width, fill=fill, just=just, frame=False, depth=depth, kwargs=kwargs)
        else:
            return
    else:
        indent = f'{" "*depth*2}' if just=='<' and not kwargs.get('no_indent',False) else ''
        if type(msg) == str:
            lns = msg.split('\n')
            if len(lns) > 1:
                my_logger(lns, logf, width=width, fill=fill, just=just, frame=False, depth=depth+1, kwargs=kwargs)
            else:
                outstr = indent + ll + f'{msg}' + rr
                logf(fmt.format(outstr))
        else:
            outstr = indent + ll + f'{msg}' + rr
            logf(fmt.format(outstr))
    if frame:
        logf(ffmt.format(frame))
            

def oxford(a_list: list[str], conjunction: str = 'or'):
    """ 
    Returns a comma-delimited string of items in a_list, 
    following the oxford comma rules including a 
    terminal conjuction (default is 'or')

    Parameters
    ----------
    a_list : list[str]
        list of strings to be joined
    conjunction : str, optional
        conjunction to use before last item (default is 'or')

    Returns
    -------
    str
        comma-delimited string of items in a_list with oxford comma usage
    """
    if not a_list: return ''
    if len(a_list) == 1:
        return a_list[0]
    elif len(a_list) == 2:
        return f'{a_list[0]} {conjunction} {a_list[1]}'
    else:
        return ", ".join(a_list[:-1]) + f', {conjunction} {a_list[-1]}'
    
def linesplit(line: str, cchar: str = '!'):
    """ 
    Splits the line into to substrings at first occurrence of 
    cchar and returns the two strings as a tuple.

    Parameters
    ----------
    line : str
        the string to be split
    cchar : str, optional
        the character at which to split the string (default is '!')

    Returns
    -------
    tuple[str, str]
        a tuple of two strings: the part before cchar and the part after cchar 
    """
    if not cchar in line:
        return line,''
    idx = line.index(cchar)
    if idx == 0:
        return '', line[1:]
    return line[:idx], line[idx+1:]

def striplist(L: list[str]) -> list[str]:
    """
    Removes all blank bytes from all members of list L and returns a new list. 
    
    Parameters
    ----------
    L : list[str]
        list of strings to be stripped of blank bytes

    Returns
    -------
    list[str]
        new list of strings with blank bytes removed
    """
    l = [x.strip() for x in L]
    while '' in l:
        l.remove('')
    return l

def chmod_recursive_dirs_files(path: Path, dmode=0o755, fmode=0o644):
    """
    Recursively changes permissions of a directory and its contents.
    
    Parameters
    ----------
    path : Path
        The root directory to change permissions for.
    dmode : int, optional
        The mode (permissions) to apply to directories. Default is 0o755
    fmode : int, optional
        The mode (permissions) to apply to files. Default is 0o644
    """
    path.chmod(dmode)
    for p in path.rglob("*"):
        if p.is_dir():
            p.chmod(dmode)
        else:
            p.chmod(fmode)
