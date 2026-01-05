"""
Sandler thermodynamics module imports and initializations.

This module is imported by pythontex if the `sandler` resource is specified
in a `pythontex` block of the document structure.
"""
from sandlertools import PropertiesDatabase, get_database
from sandlertools import SandlerSteamState as SANDLER
from sandlertools import SteamTables, SteamRequest
from sandlertools import Component, Reaction, ChemEqSystem
from sandlertools import (
    CorrespondingStatesChartReader, 
    GasConstant, IdealGasEOS, GeneralizedVDWEOS, PengRobinsonEOS )

R_pv = GasConstant("bar", "m3")
R = GasConstant("pa", "m3")

CSReader = CorrespondingStatesChartReader()
STReq = SteamRequest()
suphPavail = SteamTables['suph'].uniqs['P']
SandlerProps = PropertiesDatabase()
