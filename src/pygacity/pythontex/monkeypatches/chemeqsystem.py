"""
Monkeypatches for ChemEqSystem class in sandler module (imported from sandlertools) to add LaTeX reporting capabilities.
"""

from sandlertools import ChemEqSystem
from ..texutils import format_sig, table_as_tex, Cp_as_tex, algebraify, symneg
import roman
import numpy as np

def texgen_kacalculations(self, simplified=False, sig=5) -> str:
    """
    Generates LaTeX string for equilibrium constant calculations.

    Parameters
    ----------
    simplified : bool, optional
        whether to use simplified van't Hoff equation (default is False)
    sig : int, optional
        number of significant figures for formatting (default is 5)
        
    Returns
    -------
    str
        LaTeX formatted string of equilibrium constant calculations
    """
    ka_calcslines = []
    R_val  = self.R.m_as('J/(mol*K)') if hasattr(self.R,  'magnitude') else float(self.R)
    T_val  = self.T.m_as('K')         if hasattr(self.T,  'magnitude') else float(self.T)
    T0_val = self.T0.m_as('K')        if hasattr(self.T0, 'magnitude') else float(self.T0)
    Rval  = f'{R_val:.3f}'
    Tval  = f'{T_val:.2f}'
    T0val = f'{T0_val:.2f}'
    for i in range(self.M):
        rxn_super = ''
        if self.M > 1:
            ka_calcslines.append(rf'\underline{{Reaction {roman.toRoman(i+1)}}}\\')
            rxn_super = f'^{{{roman.toRoman(i+1)}}}'
        ka0 = 'K_a'+rxn_super + r'(T_0)'
        kaT = 'K_a'+rxn_super + r'(T)'
        ka0_val = f'{format_sig(self.Ka0[i],sig)}'
        kaT_val = f'{format_sig(self.KaT[i],sig)}'
        kaT_simplified_val = f'{format_sig(self.KaT_simplified[i],sig)}'
        n_gr = r'-\gr'+rxn_super
        n_hr = r'-\hr'+rxn_super
        n_gr_val = symneg(self.dGr[i], 5)
        n_hr_val = symneg(self.dHr[i], 5)
        ka_calcslines.append(r'\begin{align*}')
        # first line -- show calculation of Ka0
        ka_calcslines.append(ka0 + r' & = ' + r'\exp\left[\frac{' + n_gr + r'}{R T_0}\right]')
        ka_calcslines.append(r' = ' + r'\exp\left[\frac{' + n_gr_val + r'}{(' + Rval + r')(' + T0val + r')}\right]')
        ka_calcslines.append(r' = ' + ka0_val + r'\\')
        if simplified:
            # second line -- show simplified van't Hoff calculation symbolically
            ka_calcslines.append( kaT + r' & = ' + ka0     + r'\exp\left[\frac{' + n_hr    + r'}{R}\left(\frac{1}{T} - \frac{1}{T_0}\right)\right]\\')
            # third line -- show simplified van't Hoff calculation numerically
            ka_calcslines.append(
                      r' & = (' + ka0_val + r')\exp\left[\frac{' + n_hr_val + r'}{' + Rval + r'}'    
                             r'\left(\frac{1}{' + Tval + r'} - \frac{1}{' + T0val + r'}\right)\right]\\')
            ka_calcslines.append(r'& = ' + kaT_simplified_val + r'\\')
        else:
            """
            arg1 = self.dCp[0]/self.R * np.log(self.T/self.T0)
            arg2 = self.dCp[1]/(2*self.R) * (self.T - self.T0)
            arg3 = self.dCp[2]/(6*self.R) * (self.T**2 - self.T0**2)
            arg4 = self.dCp[3]/(12*self.R) * (self.T**3 - self.T0**3)
            bigterm1 = arg1 + arg2 + arg3 + arg4
            rtdiff = 1/self.R*(1/self.T - 1/self.T0)
            term5 = -self.dHr
            term6 = self.dCp[0] * self.T0
            term7 = self.dCp[1] / 2 * self.T0**2
            term8 = self.dCp[2] / 3 * self.T0**3
            term9 = self.dCp[3] / 4 * self.T0**4
            bigterm2 = rtdiff * (term5 + term6 + term7 + term8 + term9)
            logratio = bigterm1 + bigterm2
            self.KaT = self.Ka0 * np.exp(logratio)"""
            vht = self.vantHoff_terms
            Cp = self.dCp[4*i:4*(i+1)]   # heat-capacity difference coefficients for reaction i
            # second line -- show full van't Hoff calculation symbolically
            lnKK = r'\ln\frac{' + kaT + r'}{' + ka0 + r'}'
            arg1 = r'\frac{a}{R}\ln{\frac{T}{T_0}}'
            arg2 = r'\frac{b}{2R}(T - T_0)'
            arg3 = r'\frac{c}{6R}(T^2 - T_0^2)'
            arg4 = r'\frac{d}{12R}(T^3 - T_0^3)'
            bigterm1 = arg1 + r' + ' + arg2 + r' + ' + arg3 + r' + ' + arg4
            rtdiff = r'\frac{1}{R}\left(\frac{1}{T} - \frac{1}{T_0}\right)'
            term5 = n_hr
            term6 = r'a T_0'
            term7 = r'\frac{b}{2} T_0^2'
            term8 = r'\frac{c}{3} T_0^3'
            term9 = r'\frac{d}{4} T_0^4'
            bigterm2 = rtdiff + r' \left(' + term5 + r' + ' + term6 + r' + ' + term7 + r' + ' + term8 + r' + ' + term9 + r'\right)'
            ka_calcslines.append( lnKK + r' & = ' + bigterm1 + r'\\')
            ka_calcslines.append(        r' & + ' + bigterm2 + r'\\')
            arg1_subst_var = f'\\frac{{{Cp[0]:.3f}}}{{{R_val:.3f}}}\\ln{{\\frac{{{T_val:.2f}}}{{{T0_val:.2f}}}}}'
            arg2_subst_var = f'\\frac{{{Cp[1]:.4f}}}{{2\\times{R_val:.3f}}}({T_val:.2f} - {T0_val:.2f})'
            arg3_subst_var = f'\\frac{{{Cp[2]:.4f}}}{{6\\times{R_val:.3f}}}({T_val**2:.2f} - {T0_val**2:.2f})'
            arg4_subst_var = f'\\frac{{{Cp[3]:.4f}}}{{12\\times{R_val:.3f}}}({T_val**3:.2f} - {T0_val**3:.2f})'
            bigterm1_subst = arg1_subst_var + r' + ' + arg2_subst_var + r' + ' + arg3_subst_var + r' + ' + arg4_subst_var
            rtdiff_subst = f'\\frac{{1}}{{{R_val:.3f}}}\\left(\\frac{{1}}{{{T_val:.2f}}} - \\frac{{1}}{{{T0_val:.2f}}}\\right)'
            term5_subst = n_hr_val
            term6_subst = f'{Cp[0]:.3f} \\times {T0_val:.2f}'
            term7_subst = f'\\frac{{{Cp[1]:.4f}}}{{2}} \\times {T0_val**2:.2f}'
            term8_subst = f'\\frac{{{Cp[2]:.4f}}}{{3}} \\times {T0_val**3:.2f}'
            term9_subst = f'\\frac{{{Cp[3]:.4f}}}{{4}} \\times {T0_val**4:.2f}'
            bigterm2_subst = rtdiff_subst + r' \left(' + term5_subst + r' + ' + term6_subst + r' + ' + term7_subst + r' + ' + term8_subst + r' + ' + term9_subst + r'\right)'
            ka_calcslines.append( r'& = ' + bigterm1_subst + r'\\')
            ka_calcslines.append( r'& + ' + bigterm2_subst + r'\\')
            arg1_eval = f'{vht["arg1"]:.5f}'
            arg2_eval = f'{vht["arg2"]:.5f}'
            arg3_eval = f'{vht["arg3"]:.5f}'
            arg4_eval = f'{vht["arg4"]:.5f}'
            bigterm1_eval = arg1_eval + r' + ' + arg2_eval + r' + ' + arg3_eval + r' + ' + arg4_eval
            rtdiff_eval = f'{vht["rtdiff"]:.5e}'
            term5_eval = n_hr_val
            term6_eval = f'{vht["term6"]:.5f}'
            term7_eval = f'{vht["term7"]:.5f}'
            term8_eval = f'{vht["term8"]:.5f}'
            term9_eval = f'{vht["term9"]:.5f}'
            bigterm2_eval = rtdiff_eval + r' \left(' + term5_eval + r' + ' + term6_eval + r' + ' + term7_eval + r' + ' + term8_eval + r' + ' + term9_eval + r'\right)'
            ka_calcslines.append( r'& = ' + bigterm1_eval + r'\\')
            ka_calcslines.append( r'& + ' + bigterm2_eval + r'\\')
            logratio_eval = f'{float(vht["logratio"][i]):.5f}'
            ka_calcslines.append( r'& = ' + logratio_eval + r'\\')
            ka_calcslines.append( kaT + r' & = ' + ka0_val + r'\exp\left[' + logratio_eval + r'\right]\\')
            ka_calcslines.append( r'& = ' + kaT_val + r'\\')
        ka_calcslines.append(r'\end{align*}')
    return '\n'.join(ka_calcslines)

def stoichiometrictable_as_tex(self, sig: int = 3):
    """
    Generates LaTeX formatted stoichiometric table.
    
    Parameters
    ----------
    sig : int, optional
        number of significant figures for floating point numbers (default is 3)
    
    Returns
    -------
    str
        LaTeX formatted stoichiometric table
    """
    total_row = ['Totals:']
    col1 = [c.as_tex() for c in self.components]
    # fstr = f'{{:.{sig}g}}'
    col2 = [r'\(' + format_sig(n, sig=sig) + r'\)' for n in self.N0] 
    total_row += [r'\(' + format_sig(self.N0.sum(), sig=sig) + r'\)']
    tabledict = {'Species': col1, r'$N_{0,i}$': col2}
    tabledict[f'$N_{{i}}$'] = []
    Nus = [self.nu[j].sum() for j in range(self.M)]
    Nis = []
    for i,c in enumerate(self.components):
        Ni = format_sig(self.N0[i], sig=sig)
        for j,r in enumerate(self.reactions):
            nu_sign = [' + ' if self.nu[j][i]>=0 else ' - ' for i in range(self.C)]
            Xj = f'X_{{{roman.toRoman(j+1)}}}' if self.M>1 else 'X'
            Ni += f'{nu_sign[i]}\\left({format_sig(np.fabs(self.nu[j][i]), sig=sig)}\\right){Xj}'
        Nis.append(Ni)
        tabledict[f'$N_{{i}}$'].append(r'\('+Ni+r'\)')
    Ni_total = format_sig(self.N0.sum(), sig=sig)
    for j in range(self.M):
        nu_sign = ' + ' if Nus[j]>=0 else ' - '
        Xj = f'X_{{{roman.toRoman(j+1)}}}' if self.M>1 else 'X'
        Ni_total += f'{nu_sign}\\left({format_sig(np.fabs(Nus[j]), sig=sig)}\\right){Xj}'
    total_row += [r'\('+Ni_total+r'\)']
    tabledict[f'$y_{{i}} = N_{{i}} / \\sum_{{i}} N_{{i}}$'] = []
    for i in range(self.C):
        yi = r'\left[' + Nis[i] + r'\right] / \left[' + Ni_total + r'\right]'
        tabledict[f'$y_{{i}} = N_{{i}} / \\sum_{{i}} N_{{i}}$'].append(r'\('+yi+r'\)')
    total_row += [r'\(1.0\)']
    return table_as_tex(tabledict, sig=sig, total_row=total_row, index=False)

def thermochemicaltable_as_tex(self, sig: int = 3):
    """
    Generates LaTeX formatted thermochemical data table for components.
    
    Parameters
    ----------
    sig : int, optional
        number of significant figures for floating point numbers (default is 3)
    
    Returns
    -------
    str
        LaTeX formatted thermochemical data table
    """
    # if self.dHf is a pint.Quantity, get its units
    # to use in the table header
    if hasattr(self.components[0].dHf, 'units'):
        dHf_units = f'{self.components[0].dHf.units:~P}'
        dGf_units = f'{self.components[0].dGf.units:~P}'
    else:
        dHf_units = 'J/mol'
        dGf_units = 'J/mol'
    return table_as_tex({
        'Species':[c.as_tex() for c in self.components],
        rf'$\hf$ ({dHf_units})':[c.dHf.m for c in self.components],
        rf'$\gf$ ({dGf_units})':[c.dGf.m for c in self.components]},
        drop_zeros=[False,True,True], sig = sig)

ChemEqSystem.texgen_kacalculations = texgen_kacalculations
ChemEqSystem.stoichiometrictable_as_tex = stoichiometrictable_as_tex
ChemEqSystem.thermochemicaltable_as_tex = thermochemicaltable_as_tex
