"""
Monkeypatches for the Component class to add LaTeX output functionality.
"""

from ..sandler import Component
from ..texutils import format_sig, table_as_tex

def as_tex(self):
    """
    Returns a LaTeX-formatted string of the compound's empirical formula
    using the mhchem package's \\ce{} command.
    
    Returns
    -------
    retstr : str
        LaTeX-formatted empirical formula string
    """
    return r'\ce{'+str(self)+r'}'

Component.as_tex = as_tex