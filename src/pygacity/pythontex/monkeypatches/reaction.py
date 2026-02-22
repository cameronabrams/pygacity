"""
Monkeypatches for the Reaction class to add LaTeX output functionality.
"""

from sandlertools import Reaction
from ..texutils import frac_or_int_as_tex

import fractions as fr

def _component_subscripts(self, base: str) -> list[str]:
    """
    Generates a list of LaTeX strings with component names and subscripts.

    Parameters
    ----------
    base : str
        base string to which subscripts are added

    Returns
    -------
    list of str
        list of LaTeX formatted strings with subscripts
    """
    subscripts = []
    for c in self.components:
        subscripts.append(base + r'_{' + c.Formula + r'}')
    return subscripts

def _split_reactants_products(self):
    """
    Splits the reaction into reactants and products lists for LaTeX formatting.

    Returns
    -------
    tuple
        (reactants, products, nureactants, nuproducts) where each is a list of strings
    """

    self.reactants = []
    self.products = []
    self.nureactants = []
    self.nuproducts = []
    emps = [c.Formula for c in self.components]
    for e, n in zip(emps, self.nu):
        if n < 0:
            self.reactants.append(e)
            f = fr.Fraction(-n).limit_denominator(1000)
            self.nureactants.append(frac_or_int_as_tex(f))
        elif n > 0:
            self.products.append(e)
            f = fr.Fraction(n).limit_denominator(1000)
            self.nuproducts.append(frac_or_int_as_tex(f))

def sum_nu(self) -> fr.Fraction:
    """
    Computes the sum of stoichiometric coefficients as a Fraction.

    Returns
    -------
    fr.Fraction
        sum of stoichiometric coefficients
    """
    total = fr.Fraction(0)
    for n in self.nu:
        total += fr.Fraction(n).limit_denominator(1000)
    return total

def stoichiometric_product_as_tex(self, base_string: str = 'a', parens: bool = False) -> str:
    """
    Formats a stoichiometric expression as a LaTeX string.

    Parameters
    ----------
    base_string : str
        base string to which empirical-formula subscripts are added
    parens : bool, optional
        whether to enclose species in parentheses, default is False

    Returns
    -------
    str
        LaTeX formatted stoichiometric expression
    """
    self._split_reactants_products()
    base_strings = self._component_subscripts(base_string)
    reactants = base_strings[:len(self.reactants)]
    products = base_strings[len(self.reactants):]
    expreactants = ['' if n==1 else r'^{'+n+r'}' for n in self.nureactants]
    expproducts = ['' if n==1 else r'^{'+n+r'}' for n in self.nuproducts]
    if parens:
        numerator = ''.join([r'('+c+r')'+e for c,e in zip(products,expproducts)])
        denominator = ''.join([r'('+c+r')'+e for c,e in zip(reactants,expreactants)])
    else:
        numerator = ''.join([c+e for c,e in zip(products,expproducts)])
        denominator = ''.join([c+e for c,e in zip(reactants,expreactants)])
    return r'\frac{' + numerator + r'}{' + denominator + r'}'

def as_tex(self):
    """
    Returns a LaTeX-formatted string of the reaction using the mhchem package's \\ce{} command.

    Returns
    -------
    str
        LaTeX-formatted reaction string
    """
    self._split_reactants_products()
    rxnstr =  r'\ce{' + ' + '.join(['{:s} {:s}'.format(n, e) for n, e in zip(self.nureactants, self.reactants)]) 
    rxnstr += r' <=> ' + ' + '.join(['{:s} {:s}'.format(n, e) for n, e in zip(self.nuproducts, self.products)]) + r'}'
    return rxnstr


Reaction._split_reactants_products = _split_reactants_products
Reaction._component_subscripts = _component_subscripts
Reaction.as_tex = as_tex
Reaction.stoichiometric_product_as_tex = stoichiometric_product_as_tex
Reaction.sum_nu = sum_nu
