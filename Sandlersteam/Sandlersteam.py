"""
Read steam tables from Sandler
"""
import pandas as pd
import os
import io
import importlib.resources
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import LinearNDInterpolator

def read_satd():
    with importlib.resources.path('Sandlersteam','__init__.py') as f:
        inst_root=os.path.split(os.path.abspath(f))[0]
    fn=['SandlerSatdSteamTableP1.txt','SandlerSatdSteamTableP2.txt','SandlerSatdSteamTableT1.txt','SandlerSatdSteamTableT2.txt']
    punits=['kPa','MPa','kPa','MPa']
    colorder=['T','PkPa','PMPa','VL','VV','UL','DU','UV','HL','DH','HV','SL','DS','SV']
    D=[]
    for f,pu in zip(fn,punits):
        data_abs_path=os.path.join(inst_root,'data',f)
        df=pd.read_csv(data_abs_path,sep='\s+',header=0,index_col=None)
        if pu=='kPa':
            df['PMPa']=df['PkPa']/1000.0
        elif pu=='MPa':
            df['PkPa']=df['PMPa']*1000.0
        ndf=df[colorder]
        print(ndf.head())
        D.append(ndf)
    DF=pd.concat(D,axis=0)
    DF.sort_values(by='T',inplace=True)
    return DF

def my_split(data,hder,P,Tsat):
    ndfs=[]
    with io.StringIO(data) as f:
        df=pd.read_csv(f,sep='\s+',header=None,index_col=None)
        df.columns=hder
        i=1
        for p,ts in zip(P,Tsat):
            ndf=pd.DataFrame({'T':df['T'].copy(),'P':np.array([p for _ in range(df.shape[0])])})
            if ndf.iloc[0,0]=='Sat.':
                ndf.iloc[0,0]=ts
            ndf['T']=ndf['T'].astype(float)
            tdf=df.iloc[:,i:i+4].copy()
            i+=4
            ndf=pd.concat((ndf,tdf),axis=1)
            ndfs.append(ndf)
    mdf=pd.concat(ndfs,axis=0)
    return mdf

class SUPH:
    def __init__(self):
        with importlib.resources.path('Sandlersteam','__init__.py') as f:
            inst_root=os.path.split(os.path.abspath(f))[0]
        fn=os.path.join(inst_root,'data','SandlerSuphSteamTables.txt')
        # read in entire text file
        with open(fn,'r') as f:
            lines=f.read().split('\n')
        # identify header
        hder=lines[0].split()
        # identify lines with pressures
        plines=[]
        for i,l in enumerate(lines):
            if 'P = ' in l:
                plines.append(i)
        # extract and format all blocks as concurrent dataframes
        DFS=[]
        for i,(l,r) in enumerate(zip(plines[:-1],plines[1:])):
            # get pressures, and saturation temperatures, if present
            tokens=lines[l].split()
            kills=['P','=','MPa']
            for k in kills:
                while k in tokens:
                    tokens.remove(k)
            P=[]
            Tsat=[]
            for x in tokens:
                if x[0]=='(':
                    y=x[1:-1]
                    Tsat.append(float(y))
                else:
                    P.append(float(x))
            while len(Tsat)<len(P):
                Tsat.append(None)

            data='\n'.join(lines[l+1:r])
            ndf=my_split(data,hder,P,Tsat)
            DFS.append(ndf)

        data='\n'.join(lines[plines[-1]+1:])
        ndf=my_split(data,hder,P,Tsat)
        DFS.append(ndf)
        self.data=pd.concat(DFS,axis=0).fillna(0)
        dof=self.data.columns
        self.interpolators={}
        for i in range(len(dof)):
            X=np.array(self.data[dof[i]].to_list())
            for j in range(i+1,len(dof)):
                Y=np.array(self.data[dof[j]].to_list())
                # print(dof[i],dof[j])
                self.interpolators[f'{dof[i]}{dof[j]}']={}
                for k in range(len(dof)):
                    if k != i and k != j:
                        # print(f'   -> {dof[k]}')
                        Z=np.array(self.data[dof[k]].to_list())
                        I=LinearNDInterpolator(list(zip(X,Y)),Z)
                        self.interpolators[f'{dof[i]}{dof[j]}'][dof[k]]=I
        # print(self.interpolators)

#_SATD=read_satd()
_SUPH=SUPH()

class SANDLER:
    _p=['T','P','u','v','s','h']
    def _resolve(self):
        if self.T:
            if self.P:
                self.u=self.suph.interpolators['TP']['U'](self.T,self.P)
                self.v=self.suph.interpolators['TP']['V'](self.T,self.P)
                self.s=self.suph.interpolators['TP']['S'](self.T,self.P)
                self.h=self.suph.interpolators['TP']['H'](self.T,self.P)
            elif self.v:
                self.P=self.suph.interpolators['TV']['P'](self.T,self.v)
                self.u=self.suph.interpolators['TV']['U'](self.T,self.v)
                self.s=self.suph.interpolators['TV']['S'](self.T,self.v)
                self.h=self.suph.interpolators['TV']['H'](self.T,self.v)
            elif self.u:
                self.P=self.suph.interpolators['TU']['P'](self.T,self.u)
                self.v=self.suph.interpolators['TU']['V'](self.T,self.u)
                self.s=self.suph.interpolators['TU']['S'](self.T,self.u)
                self.h=self.suph.interpolators['TU']['H'](self.T,self.u)
            elif self.s:
                self.P=self.suph.interpolators['TS']['P'](self.T,self.s)
                self.v=self.suph.interpolators['TS']['V'](self.T,self.s)
                self.u=self.suph.interpolators['TS']['U'](self.T,self.s)
                self.h=self.suph.interpolators['TS']['H'](self.T,self.s)
            elif self.h:
                self.P=self.suph.interpolators['TH']['P'](self.T,self.h)
                self.v=self.suph.interpolators['TH']['V'](self.T,self.h)
                self.u=self.suph.interpolators['TH']['U'](self.T,self.h)
                self.s=self.suph.interpolators['TH']['S'](self.T,self.h)
        elif self.P:
            if self.v:
                self.T=self.suph.interpolators['PV']['T'](self.P,self.v)
                self.u=self.suph.interpolators['PV']['U'](self.P,self.v)
                self.s=self.suph.interpolators['PV']['S'](self.P,self.v)
                self.h=self.suph.interpolators['PV']['H'](self.P,self.v)
            elif self.u:
                self.T=self.suph.interpolators['PU']['T'](self.P,self.u)
                self.v=self.suph.interpolators['PU']['V'](self.P,self.u)
                self.s=self.suph.interpolators['PU']['S'](self.P,self.u)
                self.h=self.suph.interpolators['PU']['H'](self.P,self.u)
            elif self.s:
                self.T=self.suph.interpolators['PS']['T'](self.P,self.s)
                self.v=self.suph.interpolators['PS']['V'](self.P,self.s)
                self.u=self.suph.interpolators['PS']['U'](self.P,self.s)
                self.h=self.suph.interpolators['PS']['H'](self.P,self.s)
            elif self.h:
                self.T=self.suph.interpolators['PH']['T'](self.P,self.h)
                self.v=self.suph.interpolators['PH']['V'](self.P,self.h)
                self.u=self.suph.interpolators['PH']['U'](self.P,self.h)
                self.s=self.suph.interpolators['PH']['S'](self.P,self.h)
        elif self.v:
            if self.u:
                self.T=self.suph.interpolators['VU']['T'](self.v,self.u)
                self.P=self.suph.interpolators['VU']['P'](self.v,self.u)
                self.s=self.suph.interpolators['VU']['S'](self.v,self.u)
                self.h=self.suph.interpolators['VU']['H'](self.v,self.u)
            elif self.s:
                self.T=self.suph.interpolators['VS']['T'](self.v,self.s)
                self.P=self.suph.interpolators['VS']['P'](self.v,self.s)
                self.u=self.suph.interpolators['VS']['U'](self.v,self.s)
                self.h=self.suph.interpolators['VS']['H'](self.v,self.s)
            elif self.h:
                self.T=self.suph.interpolators['VH']['T'](self.v,self.h)
                self.P=self.suph.interpolators['VH']['P'](self.v,self.h)
                self.u=self.suph.interpolators['VH']['U'](self.v,self.h)
                self.s=self.suph.interpolators['VH']['S'](self.v,self.h)
        elif self.u:
            if self.s:
                self.T=self.suph.interpolators['US']['T'](self.u,self.s)
                self.P=self.suph.interpolators['US']['P'](self.u,self.s)
                self.v=self.suph.interpolators['US']['V'](self.u,self.s)
                self.h=self.suph.interpolators['US']['H'](self.u,self.s)
            elif self.h:
                self.T=self.suph.interpolators['UH']['T'](self.u,self.h)
                self.P=self.suph.interpolators['UH']['P'](self.u,self.h)
                self.v=self.suph.interpolators['UH']['V'](self.u,self.h)
                self.s=self.suph.interpolators['UH']['S'](self.u,self.h)
        elif self.s:
            if self.h:
                self.T=self.suph.interpolators['SH']['T'](self.s,self.h)
                self.P=self.suph.interpolators['SH']['P'](self.s,self.h)
                self.v=self.suph.interpolators['SH']['V'](self.s,self.h)
                self.u=self.suph.interpolators['SH']['U'](self.s,self.h)
    def __init__(self,**kwargs):
        # satd=_SATD
        self.suph=_SUPH
        self.T=kwargs.get('T',None)
        self.P=kwargs.get('P',None)
        self.u=kwargs.get('u',None)
        self.v=kwargs.get('v',None)
        self.s=kwargs.get('s',None)
        self.h=kwargs.get('h',None)
        self._resolve()


if __name__=='__main__':
    state1=SANDLER(T=525,P=10)
    print(state1.T,state1.P,state1.v,state1.u,state1.h,state1.s)   
    state2=SANDLER(T=525,v=0.009)
    print(state2.T,state2.P,state2.v,state2.u,state2.h,state2.s)
    state3=SANDLER(T=525,u=2904.9)
    print(state3.T,state3.P,state3.v,state3.u,state3.h,state3.s)
    state4=SANDLER(T=525,s=6.24)
    print(state4.T,state4.P,state4.v,state4.u,state4.h,state4.s)
    state5=SANDLER(T=525,h=3140.6)
    print(state5.T,state5.P,state5.v,state5.u,state5.h,state5.s)
    