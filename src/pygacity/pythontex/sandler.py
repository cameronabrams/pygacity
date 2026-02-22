"""
Sandler thermodynamics module imports and initializations.

This module is imported by pythontex if the `sandler` resource is specified
in a `pythontex` block of the document structure.
"""
from sandlertools import PropertiesDatabase, get_database
from sandlertools import SandlerSteamState as SANDLER
from sandlertools import get_tables
from sandlertools import Component, Reaction, ChemEqSystem
from sandlertools import (
    CSState, ureg,
    R, IdealGasEOS, VanDerWaalsEOS, PengRobinsonEOS )

SandlerProps = get_database()

SteamTables = get_tables()
suphPavail = SteamTables['suph'].uniqs['P']

class Request:
    """ Class to handle requests for latex-formatted steam tables"""
    def __init__(self):
        self.suph = []
        self.subc = []
        self.satdP = False
        self.satdT = False

    def register(self, *args, **kwargs):
        if 'satdP' in args:
            self.satdP = True
        if 'satdT' in args:
            self.satdT = True
        if 'suphP' in kwargs:
            P = kwargs['suphP']
            if P in SteamTables['suph'].uniqs['P'] and not P in self.suph:
                self.suph.append(P)
        if 'subcP' in kwargs:
            P = kwargs['subcP']
            if P in SteamTables['subc'].uniqs['P'] and not P in self.subc:
                self.subc.append(P)
        return self

    def to_latex(self):
        unit_string = r"""\noindent $\hat{V}\ [=]\ \mbox{m$^3$/kg}$; $\hat{U}\ [=]\ \mbox{kJ/kg}$; $\hat{H}\ [=]\ \mbox{kJ/kg}$; $\hat{S}\ [=]\ \mbox{kJ/kg-K}$"""
        tables = []
        if any(self.suph) or self.satdP or self.satdP:
            tables.append(r"""
\clearpage
\noindent THERMODYNAMIC PROPERTIES OF STEAM (Selected)\\*[1cm]""")
        if any(self.suph):
            tables.append(r"""Superheated steam:\\*[0mm]""")
        for p in sorted(self.suph):
            tables.append(SteamTables['suph'].to_latex(P=p))
        if any(self.suph):
            tables.append(unit_string+r'\\*[1cm]')

        if any(self.subc):
            tables.append(r"""Subcooled liquid:\\*[1cm]""")
        for p in sorted(self.subc):
            tables.append(SteamTables['subc'].to_latex(P=p))
        
        if self.satdP or self.satdT:
            if len(self.suph) + len(self.subc) > 1:
                tables.append(r"""\clearpage""")
            tables.append(r"""Saturated steam:\\*[5mm]""")
            if self.satdP:
                tables.append(SteamTables['satd'].to_latex(by='P'))
                tables.append(unit_string)
            if self.satdT:
                if self.satdP:
                    tables.append(r"""\clearpage""")
                tables.append(SteamTables['satd'].to_latex(by='T'))
                tables.append(unit_string)
        
        return '\n'.join(tables)
        

STReq = Request()

from .monkeypatches.component import *
from .monkeypatches.reaction import *
from .monkeypatches.chemeqsystem import *
from .monkeypatches.sandlersteam import *