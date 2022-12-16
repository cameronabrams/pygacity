import pandas as pd
import numpy as np
import os
import importlib.resources
from ThermoProblems.Chem.Compound import Compound
class PureProperties:
    ''' simple class for handling Sandler's pure properties database '''
    def __init__(self,inputfile='properties_binaries_database.xlsx',sheet_name='pure_properties'):
        with importlib.resources.path('Chem','__init__.py') as f:
            inst_root=os.path.split(os.path.abspath(f))[0]
        self.data_abs_path=os.path.join(inst_root,'Chem/data/'+inputfile)
        self.inputfile=self.data_abs_path
        self.df=pd.read_excel(self.inputfile,sheet_name=sheet_name,index_col=2)
        self.df.fillna(0,inplace=True)
    def report(self):
        print(self.df.columns)
        self.df.info()
    def get_crits(self,compound_name=''):
        if compound_name in self.df.index.values:
            Tc = self.df.loc[compound_name,'Tc (K)']
            Pc = self.df.loc[compound_name,'Pc (bar)']
            omega = self.df.loc[compound_name,'Omega']
            return Tc, Pc, omega
        else:
            print('Warning: %s is not found in %s.'%(compound_name,self.inputfile))
            return None, None, None
    def get_compound(self,compound_name=''):
        ''' Returns a fully loaded Compound instance '''
        if compound_name in self.df.index.values:
            cp=np.array([self.df.loc[compound_name,'CpA'],self.df.loc[compound_name,'CpB'],self.df.loc[compound_name,'CpC'],self.df.loc[compound_name,'CpD']])
            C=Compound(
                empirical_formula=self.df.loc[compound_name,'Formula'],
                name=compound_name,
                Tc=self.df.loc[compound_name,'Tc (K)'],
                Pc=self.df.loc[compound_name,'Pc (bar)'],
                omega = self.df.loc[compound_name,'Omega'],
                Cp=cp,
                H=self.df.loc[compound_name,'dHf'],
                G=self.df.loc[compound_name,'dGf']
                )
            return C
        else:
            matches=[]
            for i,row in self.df.iterrows():
                if compound_name in i:
                    cp=np.array([row['CpA'],row['CpB'],row['CpC'],row['CpD']])
                    matches.append(Compound(
                        empirical_formula=row['Formula'],name=i,
                        Tc=row['Tc (K)'],
                        Pc=row['Pc (bar)'],
                        omega = row['Omega'],
                        Cp=cp,
                        H=row['dHf'],
                        G=row['dGf']
                        )
                    )
            print(f'Possible matches for {compound_name}:')
            for c in matches:
                print(c.name)
            print(f'Returning {matches[0].name}')
            return matches[0]
    def match_ef(self,ef):
        A=Compound(ef)
        matches=[]
        for i,row in self.df.iterrows():
            B=Compound(row['Formula'],name=i)
            if A==B:
                matches.append(B)
        return matches
        
if __name__=='__main__':
    Prop=PureProperties()
    Prop.report()
    M=Prop.get_compound('cyclopentane')
    for p,v in M.thermoChemicalData.items():
        print(f'{p}: {v}')