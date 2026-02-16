from sandlersteam import SaturatedSteamTables, UnsaturatedSteamTable
import pandas as pd
import numpy as np

def add_headers(tblstr, hdllist, strs):
    tbllns = tblstr.split('\n')
    for i in range(len(tbllns)):
        if tbllns[i].startswith(r'\begin{tabular}'):
            break
    if i < len(tbllns):
        i += 1
        tbllns.insert(i,r'\toprule')
        i += 1
        for ln, st in zip(hdllist, strs):
            lstr = ' & '.join(ln)
            tbllns.insert(i, lstr + r'\\')
            i += 1
            if len(st) > 0:
                tbllns.insert(i, st)
                i += 1
        tblstr = '\n'.join(tbllns)
    return tblstr

def satd_to_latex(self, **kwargs) -> str | None:
    by = kwargs.get('by', 'T')
    cp = 'T' if by == 'P' else 'P'
    assert by in 'PT'
    block = self.DF[by]
    if not block.empty:
        splits = [block[block['T'] < 97.0], block[block['T'] > 97.0]]
        splits[0].loc[:,'P']=splits[0].loc[:,'P']*1000 # kPa from MPa
        strsplits = []
        for bs, pu in zip(splits,['kPa', 'MPa']):
            block_floatsplit = pd.DataFrame()
            cols = [by, cp, 'vL', 'vV', 'uL', 'Du', 'uV', 'hL', 'Dh', 'hV', 'sL', 'Ds', 'sV']
            # fmts=r'r@{}l'*len(cols)
            fmts =  r'>{\raggedleft}p{4mm}@{}p{4mm}>{\raggedleft}p{4mm}@{}p{4mm}' # T/P, P/T
            fmts += r'>{\raggedleft}p{2mm}@{}p{10mm}' # VL
            fmts += r'>{\raggedleft}p{4mm}@{}p{10mm}'  # VV
            fmts +=r'>{\raggedleft}p{5mm}@{}p{3mm}'  # UL
            fmts +=r'>{\raggedleft}p{6mm}@{}p{2mm}'  # DU
            fmts +=r'>{\raggedleft}p{6mm}@{}p{2mm}'  # UV
            fmts +=r'>{\raggedleft}p{5mm}@{}p{3mm}'  # HL
            fmts +=r'>{\raggedleft}p{6mm}@{}p{2mm}'  # DH
            fmts +=r'>{\raggedleft}p{6mm}@{}p{2mm}'  # HV
            fmts +=r'>{\raggedleft}p{2mm}@{}p{6mm}'  # SL
            fmts +=r'>{\raggedleft}p{2mm}@{}p{6mm}'  # DS
            fmts +=r'>{\raggedleft\arraybackslash}p{2mm}@{}p{6mm}'  # SV

            hdgs = []
            for c in cols:
                hdgs.append(c)
                hdgs.append('~')
                W = np.floor(bs[c])
                F = bs[c] - W
                FS = [f'{x:.8f}'[1:] for x in F]
                PFS = []
                block_floatsplit[c+'w'] = W
                for w, f, fs in zip(W, F, FS):
                    v = w + f
                    # ss is the explicit decimal part, need to choose digits
                    if c == 'P' and by == 'T':
                        # pressure digit rules when table is indexed by T:
                        # if v<0.2: min of 5 dp
                        if v < 0.2:
                            while len(fs) > 6 and fs[-1] == '0': fs = fs[:-1]
                        # elif v<2.0: min of 4 dp
                        elif v < 2.0:
                            while len(fs) > 5 and fs[-1] == '0': fs = fs[:-1]
                        # elif v<20: min of 3 dp
                        elif v < 20.0:
                            while len(fs) > 4 and fs[-1] == '0': fs = fs[:-1]
                        else:
                            while len(fs) > 3 and fs[-1] == '0': fs = fs[:-1]
                    elif c == 'P' and by == 'P':
                        # pressure digit rules when table is indexed by P
                        if pu == 'kPa':
                            if v < 1.0:
                                while len(fs) > 5 and fs[-1] == '0': fs = fs[:-1]
                            elif v < 10:
                                while len(fs) > 2 and fs[-1] == '0': fs = fs[:-1]
                            else:
                                fs = ''
                        else:
                            # if v<0.4, min of 3 dp
                            if v < 0.4:
                                while len(fs) > 4 and fs[-1] == '0': fs = fs[:-1]
                            elif v < 4.0:
                                while len(fs) > 3 and fs[-1] == '0': fs = fs[:-1]
                            else:
                                if f == 0.0: fs = ''
                                else:
                                    while len(fs) > 3 and fs[-1] == '0': fs = fs[:-1]
                    elif c == 'T' and by == 'T':
                        if f == 0.0: fs = ''
                        else:
                            while len(fs) > 3 and fs[-1] == '0': fs = fs[:-1]
                    elif c == 'T' and by == 'P':
                        while len(fs) > 3 and fs[-1] == '0': fs = fs[:-1]
                    else:
                        if c == 'vL':
                            while len(fs) > 7 and fs[-1] == '0': fs = fs[:-1]
                            fs = fs[:4] + ' ' + fs[4:]
                        elif c == 'vV':
                            if v > 10:
                                while len(fs) > 3 and fs[-1] == '0': fs = fs[:-1]
                            elif v > 2:
                                while len(fs) > 4 and fs[-1] == '0': fs = fs[:-1]
                            elif v > 0.2:
                                while len(fs) > 5 and fs[-1] == '0': fs = fs[:-1]
                            elif v > 0.02:
                                while len(fs) > 6 and fs[-1] == '0': fs = fs[:-1]
                            elif v > 0.002:
                                while len(fs) > 7 and fs[-1] == '0': fs = fs[:-1]
                            if len(fs) == 6:
                                fs = fs[:3] + ' ' + fs[3:]
                            elif len(fs) == 7:
                                fs = fs[:4] + ' ' + fs[4:]

                        elif c == 'uL' or c == 'hL':
                            if v < 1400:
                                while len(fs) > 3 and fs[-1] == '0': fs = fs[:-1]
                            else:
                                while len(fs) > 2 and fs[-1] == '0': fs = fs[:-1]
                        elif 'S' in c:
                            while len(fs) > 5 and fs[-1] == '0': fs = fs[:-1]
                        else:
                            while len(fs) > 2 and fs[-1] == '0': fs = fs[:-1]
                    PFS.append(fs)
                block_floatsplit[c + 'd'] = PFS
            strsplits.append(block_floatsplit)
        title = r'\begin{minipage}{\textwidth}' + '\n' + r'\tiny' + '\n' + r'\begin{center}' + '\n'
        ht1 = [r'\multicolumn{2}{c}{~}', r'\multicolumn{2}{c}{~}', r'\multicolumn{4}{c}{Specific Volume}', r'\multicolumn{6}{c}{Internal Energy}', r'\multicolumn{6}{c}{Enthalpy}', r'\multicolumn{6}{c}{Entropy}']
        htst11 = r'\cmidrule(lr){5-8}\cmidrule(lr){9-14}\cmidrule(lr){15-20}\cmidrule(lr){21-26}'
        if by == 'T':
            first2 = [r'\multicolumn{2}{c}{Temp.}', r'\multicolumn{2}{c}{Press.}']
        else:
            first2 = [r'\multicolumn{2}{c}{Press.}', r'\multicolumn{2}{c}{Temp.}']
        ht2 = first2+[r'\multicolumn{2}{c}{Sat.}',r'\multicolumn{2}{c}{Sat.}',
        r'\multicolumn{2}{c}{Sat.}',r'\multicolumn{2}{c}{~}',r'\multicolumn{2}{c}{Sat.}',
        r'\multicolumn{2}{c}{Sat.}',r'\multicolumn{2}{c}{~}',r'\multicolumn{2}{c}{Sat.}',
        r'\multicolumn{2}{c}{Sat.}',r'\multicolumn{2}{c}{~}',r'\multicolumn{2}{c}{Sat.}']
        if by == 'T':
            first2 = [r'\multicolumn{2}{c}{($^\circ$C)}', r'\multicolumn{2}{c}{(kPa)}']
        else:
            first2 = [r'\multicolumn{2}{c}{(kPa)}', r'\multicolumn{2}{c}{($^\circ$C)}']
        ht3 = first2 + [r'\multicolumn{2}{c}{Liquid}', r'\multicolumn{2}{c}{Vapor}',
        r'\multicolumn{2}{c}{Liquid}', r'\multicolumn{2}{c}{Evap.}', r'\multicolumn{2}{c}{Vapor}',
        r'\multicolumn{2}{c}{Liquid}',r'\multicolumn{2}{c}{Evap.}',r'\multicolumn{2}{c}{Vapor}',
        r'\multicolumn{2}{c}{Liquid}',r'\multicolumn{2}{c}{Evap.}',r'\multicolumn{2}{c}{Vapor}']
        if by == 'T':
            first2 = [r'\multicolumn{2}{c}{$T$}', r'\multicolumn{2}{c}{$P$}']
        else:
            first2 = [r'\multicolumn{2}{c}{$P$}', r'\multicolumn{2}{c}{$T$}']
        ht4 = first2 + [r'\multicolumn{2}{c}{$\hat{V}^L$}', r'\multicolumn{2}{c}{$\hat{V}^V$}',
        r'\multicolumn{2}{c}{$\hat{U}^L$}',r'\multicolumn{2}{c}{$\Delta\hat{U}$}',r'\multicolumn{2}{c}{$\hat{U}^V$}',
        r'\multicolumn{2}{c}{$\hat{H}^L$}',r'\multicolumn{2}{c}{$\Delta\hat{H}$}',r'\multicolumn{2}{c}{$\hat{H}^V$}',
        r'\multicolumn{2}{c}{$\hat{S}^L$}',r'\multicolumn{2}{c}{$\Delta\hat{S}$}',r'\multicolumn{2}{c}{$\hat{S}^V$}']
        
        tbl1 = strsplits[0].to_latex(escape=False, header=False, column_format=fmts, index=False, float_format='%g')
        tbl1 = add_headers(tbl1,[ht1,ht2,ht3,ht4],[htst11,'','',''])
        # tbl1=set_width(tbl1)
        if by == 'T':
            first2 = [r'\multicolumn{2}{c}{~}', r'\multicolumn{2}{c}{MPa}']
        else:
            first2 = [r'\multicolumn{2}{c}{MPa}', r'\multicolumn{2}{c}{~}']
        ht3 = first2 + [r'\multicolumn{22}{c}{~}']
        tbl2 = strsplits[1].to_latex(escape=False, header=False, column_format=fmts, index=False, float_format='%g')
        tbl2 = add_headers(tbl2, [ht3], [''])
        # tbl2=set_width(tbl2)
        return title + tbl1 + r'\\' + '\n' + tbl2 + r'\end{center}' + '\n' + r'\end{minipage}' + '\n'
    else:
        return None

def unsatd_to_latex(self, P: float):
    # generates latex version of a P-block of the superheated/subcooled steam table
    block  = self.data[self.data['P'] == P][['T','v','u','h','s']]
    if not block.empty:
        block_floatsplit =  pd.DataFrame()
        for c in ['T', 'v', 'u', 'h', 's']:
            w = block[c].astype(int)
            dd = np.round((block[c] - w), 10).astype(str)
            d = []
            block_floatsplit[c+'w'] = w
            for a, s in zip(w, dd):
                if '.' in s:
                    ss = s[1:]
                if ss == '.0' and c == 'T':
                    d.append('')
                else:
                    if a == 0: # this is a fractional number
                        while len(ss) < 6:
                            ss = ss + '0'
                        iss = int(ss[1:])
                        if iss > 19999:
                            ss = ss[:-1]
                    elif a < 10:
                        while len(ss) < 5:
                            ss = ss + '0'
                    d.append(ss)
                
            block_floatsplit[c+'d'] = d
        title = r'\noindent\begin{minipage}{0.6\textwidth}' + '\n' + r'\footnotesize\vspace{5mm}' + '\n' + r'\begin{center}' + '\n' + r'$P$ = ' + f'{P}' + r' MPa\\*[1ex]' + '\n'
        fmts = r'>{\raggedleft}p{8mm}@{}p{5mm}' # T
        fmts += r'>{\raggedleft}p{4mm}@{}p{10mm}' # V
        fmts += r'>{\raggedleft}p{10mm}@{}p{3mm}' # U
        fmts += r'>{\raggedleft}p{10mm}@{}p{3mm}' # H
        fmts += r'>{\raggedleft\arraybackslash}p{3mm}@{}p{8mm}' # S
        tbl = block_floatsplit.to_latex(escape=False, header=False, column_format=fmts, index=False, float_format='%g')
        hdrs = [r'\multicolumn{2}{c}{$T$~($^\circ$C)}',
                r'\multicolumn{2}{c}{$\hat{V}$}',
                r'\multicolumn{2}{c}{$\hat{U}$}',
                r'\multicolumn{2}{c}{$\hat{H}$}',
                r'\multicolumn{2}{c}{$\hat{S}$}']
        tbl = add_headers(tbl, [hdrs], [''])
        return title + tbl  + r'\end{center}'+'\n'+r'\end{minipage}'+'\n'
    else:
        return None


# class RandomSample(State):
#     def __init__(self,phase='suph', satdDOF='T', seed=None, Prange=None, Trange=None):
#         if phase == 'satd':
#             if satdDOF == 'T':
#                 sample_this = SteamTables[phase].DF['T']
#             else:
#                 sample_this = SteamTables[phase].DF['P']
#         elif phase == 'suph' or phase == 'subc':
#             sample_this = SteamTables[phase].data
#         abs_mins = {'T': sample_this['T'].min(), 'P': sample_this['P'].min()}
#         abs_maxs = {'T': sample_this['T'].max(), 'P': sample_this['P'].max()}
#         sample = sample_this.sample(n=1, random_state=seed)
#         T = sample['T'].values[0]
#         P = sample['P'].values[0]
#         if Trange and not Prange:
#             if Trange[0] < abs_mins['T']:
#                 raise ValueError(f'Trange[0] ({Trange[0]}) is below the minimum T in the data ({abs_mins["T"]})')
#             if Trange[1] > abs_maxs['T']:
#                 raise ValueError(f'Trange[1] ({Trange[1]}) is above the maximum T in the data ({abs_maxs["T"]})')
#             while not Trange[0] < T < Trange[1]:
#                 sample = sample_this.sample(n=1)
#                 T = sample['T'].values[0]
#         if Prange and not Trange:
#             if Prange[0] < abs_mins['P']:
#                 raise ValueError(f'Prange[0] ({Prange[0]}) is below the minimum P in the data ({abs_mins["P"]})')
#             if Prange[1] > abs_maxs['P']:
#                 raise ValueError(f'Prange[1] ({Prange[1]}) is above the maximum P in the data ({abs_maxs["P"]})')
#             while not Prange[0] < P < Prange[1]:
#                 sample = sample_this.sample(n=1)
#                 P = sample['P'].values[0]
#         if Prange and Trange:
#             if Trange[0] < abs_mins['T']:
#                 raise ValueError(f'Trange[0] ({Trange[0]}) is below the minimum T in the data ({abs_mins["T"]})')
#             if Trange[1] > abs_maxs['T']:
#                 raise ValueError(f'Trange[1] ({Trange[1]}) is above the maximum T in the data ({abs_maxs["T"]})')
#             if Prange[0] < abs_mins['P']: 
#                 raise ValueError(f'Prange[0] ({Prange[0]}) is below the minimum P in the data ({abs_mins["P"]})')
#             if Prange[1] > abs_maxs['P']: 
#                 raise ValueError(f'Prange[1] ({Prange[1]}) is above the maximum P in the data ({abs_maxs["P"]})')
#             while not Prange[0] < P < Prange[1] or not Trange[0] < T < Trange[1]:
#                 sample = sample_this.sample(n=1)
#                 T = sample['T'].values[0]
#                 P = sample['P'].values[0]
#         if phase == 'satd':
#             if satdDOF == 'T':
#                 super().__init__(T=T, x=1.0)
#             else:
#                 super().__init__(P=P, x=1.0)
#         else:
#             super().__init__(T=T, P=P)
    

SaturatedSteamTables.to_latex = satd_to_latex
UnsaturatedSteamTable.to_latex = unsatd_to_latex