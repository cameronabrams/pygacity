"""
Read steam tables from Sandler
"""
import pandas as pd
import os
import io
import importlib.resources
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import LinearNDInterpolator, interp1d

class SATD:
    def __init__(self):
        with importlib.resources.path('Sandlersteam','__init__.py') as f:
            inst_root=os.path.split(os.path.abspath(f))[0]
        pfn=['SandlerSatdSteamTableP1.txt','SandlerSatdSteamTableP2.txt']
        tfn=['SandlerSatdSteamTableT1.txt','SandlerSatdSteamTableT2.txt']
        punits=['kPa','MPa']
        colorder=['T','PkPa','PMPa','VL','VV','UL','DU','UV','HL','DH','HV','SL','DS','SV']
        self.DF={}
        D=[]
        for f,pu in zip(pfn,punits):
            data_abs_path=os.path.join(inst_root,'data',f)
            df=pd.read_csv(data_abs_path,sep='\s+',header=0,index_col=None)
            if pu=='kPa':
                df['PMPa']=df['PkPa']/1000.0
            elif pu=='MPa':
                df['PkPa']=df['PMPa']*1000.0
            ndf=df[colorder]
            # print(ndf.head())
            D.append(ndf)
        self.DF['PMPa']=pd.concat(D,axis=0)
        self.DF['PMPa'].sort_values(by='PMPa',inplace=True)
        D=[]
        for f,pu in zip(tfn,punits):
            data_abs_path=os.path.join(inst_root,'data',f)
            df=pd.read_csv(data_abs_path,sep='\s+',header=0,index_col=None)
            if pu=='kPa':
                df['PMPa']=df['PkPa']/1000.0
            elif pu=='MPa':
                df['PkPa']=df['PMPa']*1000.0
            ndf=df[colorder]
            # print(ndf.head())
            D.append(ndf)
        self.DF['T']=pd.concat(D,axis=0)
        self.DF['T'].sort_values(by='T',inplace=True)

        self.interpolators={}
        for bp,cp in zip(['PMPa','T'],['T','PMPa']):
            self.interpolators[bp]={}
            X=np.array(self.DF[bp][bp].to_list())
            for p in [cp,'VL','VV','UL','UV','HL','HV','SL','SV']:
                Y=np.array(self.DF[bp][p].to_list())
                self.interpolators[bp][p]=interp1d(X,Y,kind='linear')

"""
                                                                                                    1         1
          1         2         3         4         5         6         7         8         9         0         1
012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123    
 260  0.0012749  1127.9  1134.3   2.8830  0.0012645  1121.1   1133.7   2.8699  0.0012550  1114.6   1133.4   2.8576
(0,4),(6,15),    (17,24),(25,32), (34,40),(42,51),   (53,60), (62,69), (71,77),(79,88),(90,97),(99,106),(108,114)
"""
def my_split(data,hder,P,Tsat,fixw=False):
    ndfs=[]
    with io.StringIO(data) as f:
        if fixw:
            df=pd.read_fwf(f,colspecs=((0,4),(6,15), (17,24),(25,32),(34,40),(42,51), (53,60),(62,69),(71,77),(79,88),(90,97),(99,106),(108,114)),header=None,index_col=None)
            # print(df.head())
        else:
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
            ndf.dropna(axis=0,inplace=True)
            # print(ndf.to_string())
            ndfs.append(ndf)
    mdf=pd.concat(ndfs,axis=0)
    return mdf

class SUPH:
    def __init__(self,phase='V',fixw=False):
        with importlib.resources.path('Sandlersteam','__init__.py') as f:
            inst_root=os.path.split(os.path.abspath(f))[0]
        if phase=='V':
            ff='SandlerSuphSteamTables.txt'
        elif phase=='L':
            ff='SandlerSubcSteamTables.txt'
        fn=os.path.join(inst_root,'data',ff)
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
            # print(hder)
            # print(data)
            ndf=my_split(data,hder,P,Tsat,fixw=(phase=='L'))
            DFS.append(ndf)

        data='\n'.join(lines[plines[-1]+1:])
        ndf=my_split(data,hder,P,Tsat,fixw=(phase=='L'))
        DFS.append(ndf)
        self.data=pd.concat(DFS,axis=0)
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

_SATD=SATD()
_SUPH=SUPH('V')
_SUBC=SUPH('L')

class PHASE:
    def __init__(self):
        pass

class SANDLER:
    _p=['T','P','u','v','s','h','x']
    def _resolve(self):
        if self.T:
            Psat=self.satd.interpolators['T']['PMPa'](self.T)
            VLsat=self.satd.interpolators['T']['VL'](self.T)
            VVsat=self.satd.interpolators['T']['VV'](self.T)
            ULsat=self.satd.interpolators['T']['UL'](self.T)
            UVsat=self.satd.interpolators['T']['UV'](self.T)
            HLsat=self.satd.interpolators['T']['HL'](self.T)
            HVsat=self.satd.interpolators['T']['HV'](self.T)
            SLsat=self.satd.interpolators['T']['SL'](self.T)
            SVsat=self.satd.interpolators['T']['SV'](self.T)
            if self.x:
                # saturated V+L
                self.P=Psat
                self.Liquid=PHASE()
                self.Liquid.v=VLsat
                self.Liquid.u=ULsat
                self.Liquid.h=HLsat
                self.Liquid.s=SLsat
                self.Vapor=PHASE()
                self.Vapor.v=VVsat
                self.Vapor.u=UVsat
                self.Vapor.h=HVsat
                self.Vapor.s=SVsat
                self.v=self.x*VVsat+(1-self.x)*VLsat
                self.u=self.x*UVsat+(1-self.x)*ULsat
                self.h=self.x*HVsat+(1-self.x)*HLsat
                self.s=self.x*SVsat+(1-self.x)*SLsat
            elif self.P:
                if self.P>Psat:
                    # subcooled liquid
                    self.u=self.subc.interpolators['TP']['U'](self.T,self.P)
                    self.v=self.subc.interpolators['TP']['V'](self.T,self.P)
                    self.s=self.subc.interpolators['TP']['S'](self.T,self.P)
                    self.h=self.subc.interpolators['TP']['H'](self.T,self.P)
                else:
                    # superheated vapor
                    self.u=self.suph.interpolators['TP']['U'](self.T,self.P)
                    self.v=self.suph.interpolators['TP']['V'](self.T,self.P)
                    self.s=self.suph.interpolators['TP']['S'](self.T,self.P)
                    self.h=self.suph.interpolators['TP']['H'](self.T,self.P)
            elif self.v:
                if self.v>VLsat:
                    #subcooled
                    self.P=self.subc.interpolators['TV']['P'](self.T,self.v)
                    self.u=self.subc.interpolators['TV']['U'](self.T,self.v)
                    self.s=self.subc.interpolators['TV']['S'](self.T,self.v)
                    self.h=self.subc.interpolators['TV']['H'](self.T,self.v)
                elif self.v<VVsat:
                    # superheated
                    self.P=self.suph.interpolators['TV']['P'](self.T,self.v)
                    self.u=self.suph.interpolators['TV']['U'](self.T,self.v)
                    self.s=self.suph.interpolators['TV']['S'](self.T,self.v)
                    self.h=self.suph.interpolators['TV']['H'](self.T,self.v)
                else:
                    # apply lever rule
                    self.x=(self.v-VLsat)/(VVsat-VLsat)
                    self.P=Psat
                    self.Liquid=PHASE()
                    self.Liquid.v=VLsat
                    self.Liquid.u=ULsat
                    self.Liquid.h=HLsat
                    self.Liquid.s=SLsat
                    self.Vapor=PHASE()
                    self.Vapor.v=VVsat
                    self.Vapor.u=UVsat
                    self.Vapor.h=HVsat
                    self.Vapor.s=SVsat
                    self.u=self.x*UVsat+(1-self.x)*ULsat
                    self.h=self.x*HVsat+(1-self.x)*HLsat
                    self.s=self.x*SVsat+(1-self.x)*SLsat
            elif self.u:
                if self.u<ULsat:
                    # subc
                    self.P=self.subc.interpolators['TU']['P'](self.T,self.u)
                    self.v=self.subc.interpolators['TU']['V'](self.T,self.u)
                    self.s=self.subc.interpolators['TU']['S'](self.T,self.u)
                    self.h=self.subc.interpolators['TU']['H'](self.T,self.u)
                elif self.u>UVsat:
                    self.P=self.suph.interpolators['TU']['P'](self.T,self.u)
                    self.v=self.suph.interpolators['TU']['V'](self.T,self.u)
                    self.s=self.suph.interpolators['TU']['S'](self.T,self.u)
                    self.h=self.suph.interpolators['TU']['H'](self.T,self.u)
                else:
                    self.x=(self.u-ULsat)/(UVsat-ULsat)
                    self.P=Psat
                    self.Liquid=PHASE()
                    self.Liquid.v=VLsat
                    self.Liquid.u=ULsat
                    self.Liquid.h=HLsat
                    self.Liquid.s=SLsat
                    self.Vapor=PHASE()
                    self.Vapor.v=VVsat
                    self.Vapor.u=UVsat
                    self.Vapor.h=HVsat
                    self.Vapor.s=SVsat
                    self.v=self.x*VVsat+(1-self.x)*VLsat
                    self.h=self.x*HVsat+(1-self.x)*HLsat
                    self.s=self.x*SVsat+(1-self.x)*SLsat
            elif self.s:
                if self.s<SLsat:
                    self.P=self.subc.interpolators['TS']['P'](self.T,self.s)
                    self.v=self.subc.interpolators['TS']['V'](self.T,self.s)
                    self.u=self.subc.interpolators['TS']['U'](self.T,self.s)
                    self.h=self.subc.interpolators['TS']['H'](self.T,self.s)
                elif self.s>SVsat:
                    self.P=self.suph.interpolators['TS']['P'](self.T,self.s)
                    self.v=self.suph.interpolators['TS']['V'](self.T,self.s)
                    self.u=self.suph.interpolators['TS']['U'](self.T,self.s)
                    self.h=self.suph.interpolators['TS']['H'](self.T,self.s)
                else:
                    self.x=(self.s-SLsat)/(SVsat-SLsat)
                    self.P=Psat
                    self.Liquid=PHASE()
                    self.Liquid.v=VLsat
                    self.Liquid.u=ULsat
                    self.Liquid.h=HLsat
                    self.Liquid.s=SLsat
                    self.Vapor=PHASE()
                    self.Vapor.v=VVsat
                    self.Vapor.u=UVsat
                    self.Vapor.h=HVsat
                    self.Vapor.s=SVsat
                    self.v=self.x*VVsat+(1-self.x)*VLsat
                    self.u=self.x*UVsat+(1-self.x)*ULsat
                    self.h=self.x*HVsat+(1-self.x)*HLsat
            elif self.h:
                if self.h<HLsat:
                    self.P=self.subc.interpolators['TH']['P'](self.T,self.h)
                    self.v=self.subc.interpolators['TH']['V'](self.T,self.h)
                    self.u=self.subc.interpolators['TH']['U'](self.T,self.h)
                    self.s=self.subc.interpolators['TH']['S'](self.T,self.h)
                elif self.h>HVsat:
                    self.P=self.suph.interpolators['TH']['P'](self.T,self.h)
                    self.v=self.suph.interpolators['TH']['V'](self.T,self.h)
                    self.u=self.suph.interpolators['TH']['U'](self.T,self.h)
                    self.s=self.suph.interpolators['TH']['S'](self.T,self.h)
                else:
                    self.x=(self.h-HLsat)/(HVsat-HLsat)
                    self.P=Psat
                    self.Liquid=PHASE()
                    self.Liquid.v=VLsat
                    self.Liquid.u=ULsat
                    self.Liquid.h=HLsat
                    self.Liquid.s=SLsat
                    self.Vapor=PHASE()
                    self.Vapor.v=VVsat
                    self.Vapor.u=UVsat
                    self.Vapor.h=HVsat
                    self.Vapor.s=SVsat
                    self.v=self.x*VVsat+(1-self.x)*VLsat
                    self.u=self.x*UVsat+(1-self.x)*ULsat
                    self.s=self.x*SVsat+(1-self.x)*SLsat
        elif self.P:
            Tsat=self.satd.interpolators['P']['T'](self.P)
            VLsat=self.satd.interpolators['P']['VL'](self.P)
            VVsat=self.satd.interpolators['P']['VV'](self.P)
            ULsat=self.satd.interpolators['P']['UL'](self.P)
            UVsat=self.satd.interpolators['P']['UV'](self.P)
            HLsat=self.satd.interpolators['P']['HL'](self.P)
            HVsat=self.satd.interpolators['P']['HV'](self.P)
            SLsat=self.satd.interpolators['P']['SL'](self.P)
            SVsat=self.satd.interpolators['P']['SV'](self.P)
            if self.v:
                if self.v<VLsat:
                    self.T=self.subc.interpolators['PV']['T'](self.P,self.v)
                    self.u=self.subc.interpolators['PV']['U'](self.P,self.v)
                    self.s=self.subc.interpolators['PV']['S'](self.P,self.v)
                    self.h=self.subc.interpolators['PV']['H'](self.P,self.v)
                elif self.s>VVsat:
                    self.T=self.suph.interpolators['PV']['T'](self.P,self.v)
                    self.u=self.suph.interpolators['PV']['U'](self.P,self.v)
                    self.s=self.suph.interpolators['PV']['S'](self.P,self.v)
                    self.h=self.suph.interpolators['PV']['H'](self.P,self.v)
                else:
                    self.x=(self.v-VLsat)/(VVsat-VLsat)
                    self.T=Tsat
                    self.Liquid=PHASE()
                    self.Liquid.v=VLsat
                    self.Liquid.u=ULsat
                    self.Liquid.h=HLsat
                    self.Liquid.s=SLsat
                    self.Vapor=PHASE()
                    self.Vapor.v=VVsat
                    self.Vapor.u=UVsat
                    self.Vapor.h=HVsat
                    self.Vapor.s=SVsat
                    self.u=self.x*UVsat+(1-self.x)*ULsat
                    self.h=self.x*HVsat+(1-self.x)*HLsat
                    self.s=self.x*SVsat+(1-self.x)*SLsat
            elif self.u:
                if self.u<ULsat:
                    self.T=self.subc.interpolators['PU']['T'](self.P,self.u)
                    self.v=self.subc.interpolators['PU']['V'](self.P,self.u)
                    self.s=self.subc.interpolators['PU']['S'](self.P,self.u)
                    self.h=self.subc.interpolators['PU']['H'](self.P,self.u)
                elif self.u>UVsat:
                    self.T=self.suph.interpolators['PU']['T'](self.P,self.u)
                    self.v=self.suph.interpolators['PU']['V'](self.P,self.u)
                    self.s=self.suph.interpolators['PU']['S'](self.P,self.u)
                    self.h=self.suph.interpolators['PU']['H'](self.P,self.u)
                else:
                    self.x=(self.u-ULsat)/(UVsat-ULsat)
                    self.T=Tsat
                    self.Liquid=PHASE()
                    self.Liquid.v=VLsat
                    self.Liquid.u=ULsat
                    self.Liquid.h=HLsat
                    self.Liquid.s=SLsat
                    self.Vapor=PHASE()
                    self.Vapor.v=VVsat
                    self.Vapor.u=UVsat
                    self.Vapor.h=HVsat
                    self.Vapor.s=SVsat
                    self.v=self.x*VVsat+(1-self.x)*VLsat
                    self.h=self.x*HVsat+(1-self.x)*HLsat
                    self.s=self.x*SVsat+(1-self.x)*SLsat
            elif self.s:
                if self.s<SLsat:
                    self.T=self.subc.interpolators['PS']['T'](self.P,self.s)
                    self.v=self.subc.interpolators['PS']['V'](self.P,self.s)
                    self.u=self.subc.interpolators['PS']['U'](self.P,self.s)
                    self.h=self.subc.interpolators['PS']['H'](self.P,self.s)
                elif self.s>SVsat:
                    self.T=self.suph.interpolators['PS']['T'](self.P,self.s)
                    self.v=self.suph.interpolators['PS']['V'](self.P,self.s)
                    self.u=self.suph.interpolators['PS']['U'](self.P,self.s)
                    self.h=self.suph.interpolators['PS']['H'](self.P,self.s)
                else:
                    self.x=(self.u-ULsat)/(UVsat-ULsat)
                    self.T=Tsat
                    self.Liquid=PHASE()
                    self.Liquid.v=VLsat
                    self.Liquid.u=ULsat
                    self.Liquid.h=HLsat
                    self.Liquid.s=SLsat
                    self.Vapor=PHASE()
                    self.Vapor.v=VVsat
                    self.Vapor.u=UVsat
                    self.Vapor.h=HVsat
                    self.Vapor.s=SVsat
                    self.v=self.x*VVsat+(1-self.x)*VLsat
                    self.h=self.x*HVsat+(1-self.x)*HLsat
                    self.s=self.x*SVsat+(1-self.x)*SLsat
            elif self.h:
                if self.h<HLsat:
                    self.T=self.subc.interpolators['PH']['T'](self.P,self.h)
                    self.v=self.subc.interpolators['PH']['V'](self.P,self.h)
                    self.u=self.subc.interpolators['PH']['U'](self.P,self.h)
                    self.s=self.subc.interpolators['PH']['S'](self.P,self.h)
                elif self.h>HVsat:
                    self.T=self.suph.interpolators['PH']['T'](self.P,self.h)
                    self.v=self.suph.interpolators['PH']['V'](self.P,self.h)
                    self.u=self.suph.interpolators['PH']['U'](self.P,self.h)
                    self.s=self.suph.interpolators['PH']['S'](self.P,self.h)
                else:
                    self.x=(self.h-HLsat)/(HVsat-HLsat)
                    self.T=Tsat
                    self.Liquid=PHASE()
                    self.Liquid.v=VLsat
                    self.Liquid.u=ULsat
                    self.Liquid.h=HLsat
                    self.Liquid.s=SLsat
                    self.Vapor=PHASE()
                    self.Vapor.v=VVsat
                    self.Vapor.u=UVsat
                    self.Vapor.h=HVsat
                    self.Vapor.s=SVsat
                    self.v=self.x*VVsat+(1-self.x)*VLsat
                    self.u=self.x*UVsat+(1-self.x)*ULsat
                    self.s=self.x*SVsat+(1-self.x)*SLsat
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
        self.satd=_SATD
        self.suph=_SUPH
        self.subc=_SUBC
        self.T=kwargs.get('T',None)
        self.P=kwargs.get('P',None)
        self.u=kwargs.get('u',None)
        self.v=kwargs.get('v',None)
        self.s=kwargs.get('s',None)
        self.h=kwargs.get('h',None)
        self.x=kwargs.get('x',None)
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
    