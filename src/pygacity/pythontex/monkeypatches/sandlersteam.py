from sandlertools import SaturatedSteamTables, UnsaturatedSteamTable

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
            if P in st['suph'].uniqs['P'] and not P in self.suph:
                self.suph.append(P)
        if 'subcP' in kwargs:
            P = kwargs['subcP']
            if P in st['subc'].uniqs['P'] and not P in self.subc:
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
            tables.append(st['suph'].to_latex(P=p))
        if any(self.suph):
            tables.append(unit_string+r'\\*[1cm]')

        if any(self.subc):
            tables.append(r"""Subcooled liquid:\\*[1cm]""")
        for p in sorted(self.subc):
            tables.append(st['subc'].to_latex(P=p))
        
        if self.satdP or self.satdT:
            if len(self.suph) + len(self.subc) > 1:
                tables.append(r"""\clearpage""")
            tables.append(r"""Saturated steam:\\*[5mm]""")
            if self.satdP:
                tables.append(st['satd'].to_latex(by='P'))
                tables.append(unit_string)
            if self.satdT:
                if self.satdP:
                    tables.append(r"""\clearpage""")
                tables.append(st['satd'].to_latex(by='T'))
                tables.append(unit_string)
        
        return '\n'.join(tables)
        

def satd_to_latex(self, **kwargs) -> str | None:
    by = kwargs.get('by', 'TC')
    cp = 'TC' if by == 'P' else 'P'
    assert by in 'PT'
    block = self.DF[by]
    if not block.empty:
        splits = [block[block['TC'] < 97.0], block[block['TC'] > 97.0]]
        splits[0].loc[:,'P']=splits[0].loc[:,'P']*1000 # kPa from MPa
        strsplits = []
        for bs, pu in zip(splits,['kPa', 'MPa']):
            block_floatsplit = pd.DataFrame()
            cols = [by, cp, 'VL', 'VV', 'UL', 'DU', 'UV', 'HL', 'DH', 'HV', 'SL', 'DS', 'SV']
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
                    elif c == 'TC' and by == 'TC':
                        if f == 0.0: fs = ''
                        else:
                            while len(fs) > 3 and fs[-1] == '0': fs = fs[:-1]
                    elif c == 'TC' and by == 'P':
                        while len(fs) > 3 and fs[-1] == '0': fs = fs[:-1]
                    else:
                        if c == 'VL':
                            while len(fs) > 7 and fs[-1] == '0': fs = fs[:-1]
                            fs = fs[:4] + ' ' + fs[4:]
                        elif c == 'VV':
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

                        elif c == 'UL' or c == 'HL':
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
    block  = self.data[self.data['P'] == P][['TC','V','U','H','S']]
    if not block.empty:
        block_floatsplit =  pd.DataFrame()
        for c in ['TC', 'V', 'U', 'H', 'S']:
            w = block[c].astype(int)
            dd = np.round((block[c] - w), 10).astype(str)
            d = []
            block_floatsplit[c+'w'] = w
            for a, s in zip(w, dd):
                if '.' in s:
                    ss = s[1:]
                if ss == '.0' and c == 'TC':
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


SaturatedSteamTables.to_latex = satd_to_latex
UnsaturatedSteamTable.to_latex = unsatd_to_latex