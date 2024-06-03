# Author: Cameron F. Abrams, <cfa22@drexel.edu>
from scipy.optimize import fsolve
import numpy as np

def Fenske_rec(FRD_LK,FRR_HK,alpha):
    return np.log(FRD_LK/(1-FRD_LK)*FRR_HK/(1-FRR_HK))/np.log(alpha)

def Fenske_mf(xD_LK,xB_HK,alpha):
    return np.log((xD_LK/(1-xD_LK))/(xB_HK/(1-xB_HK)))/np.log(alpha)

def Underwood_Phi(airef,Z,q):
    def Underwood_ZeroMe(phi,airef,Z,q):
        LHS=0
        for a,z in zip(airef,Z):
            LHS+=a*z/(a-phi)
        return LHS-(1-q)
    phi=fsolve(Underwood_ZeroMe,0.5*np.sum(airef),args=(airef,Z,q))[0]
    return phi

def Underwood(airef,Z,q,D,XD):
    phi=Underwood_Phi(airef,Z,q)
    Vmin=np.sum(D*airef*XD/(airef-phi))
    Lmin=Vmin-D
    LDmin=Lmin/D
    return LDmin

def Rusche(x):
    return 1-0.37*x-0.63*x**0.16

def Gilliland(LD,LDmin,Nmin):
    ux=(LD-LDmin)/(LD+1)
    uy=Rusche(ux)
    N=(uy+Nmin)/(1-uy)
    return N

if __name__=='__main__':
    z=np.array([0.33,0.33,0.34])
    q=1.0
    LD=2.0
    FRD_LK=0.99
    FRR_HK=0.995
    alpha=np.array([3.229,1.0,0.186])
    Nmin=Fenske_rec(FRD_LK,FRR_HK,alpha[0])
    print(f'Nmin={Nmin}')
    Dx1=FRD_LK*z[0]
    Dx2=(1-FRR_HK)*z[1]
    Dx3=0.0 # NDA
    Dx=np.array([Dx1,Dx2,Dx3])
    D=Dx1+Dx2+Dx3
    B=1-D
    Bx1=(1-FRD_LK)*z[0]
    Bx2=FRR_HK*z[1]
    Bx3=0.0 # NDA
    Bx=np.array([Bx1,Bx2,Bx3])
    xB=Bx/B
    xD=Dx/D
    phi=Underwood_Phi(alpha,z,q)
    LDmin=Underwood(alpha,z,q,D,xD)
    N=Gilliland(LD,LDmin,Nmin)
    NFmin=Fenske_mf(xD[0],xB[1],alpha[0])
    NF=NFmin/Nmin*N
    print(f'D={D}, B={B}')
    print(f'phi={phi}')
    print(f'LDmin={LDmin}')
    print(f'N={N}, NF={NF}')

