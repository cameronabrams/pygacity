"""
Binary distillation column sizing using the McCabe-Thiele approach

Cameron F Abrams cfa22@drexel.edu

"""
import json
import pandas as pd
from scipy.interpolate import interp1d
from scipy.optimize import fsolve
import matplotlib.pyplot as plt
import numpy as np
import argparse as ap

class line:
    def __init__(self,m=None,b=None,p1=None,p2=None,x=None,vert=False):
        self.vert=vert
        self.x=x
        if m!=None and b!=None:
            self.m=m
            self.b=b
        elif m!=None and p1!=None:
            self.b=p1[1]-m*p1[0]
            self.m=m
        elif p1!=None and p2!=None:
            if p1[0]!=p2[0]:
                self.m=(p2[1]-p1[1])/(p2[0]-p1[0])
                self.b=p1[1]-self.m*p1[0]
            else:
                self.x=p1[0]
        elif vert!=None and x!=None:
            self.vert=True
            self.x=x
        else:
            raise Exception('Not enough info to parameterize a line')
    def __str__(self):
        return f'y=({self.m:.3f})x+({self.b:.3f})'
    def y(self,x):
        return self.m*x+self.b
    def inv(self,y):
        return (y-self.b)/self.m
    def intersect(self,other):
        if not self.vert and not other.vert:
            # m*x+b=n*x+c -> x(m-n)=c-b -> x=(c-b)/(m-n)
            m,b=self.m,self.b
            n,c=other.m,other.b
            x=(c-b)/(m-n)
            return x,self.y(x)
        elif self.m==other.m:
            return None
        elif self.vert and not other.vert:
            return self.x,other.y(self.x)
        elif not self.vert and other.vert:
            return other.x,self.y(other.x)
    def intersect_interp(self,interp):
        if self.vert:
            return [[self.x,float(interp(self.x))]]
        ipts=[]
        z=interp
        for xl,xr,yl,yr in zip(z.x[:-1],z.x[1:],z.y[0:-1],z.y[1:]):
            lyl=self.y(xl)
            lyr=self.y(xr)
            if (yl>lyl and yr<lyr) or (yl<lyl and yr>lyr):
                seg=line(p1=[xl,yl],p2=[xr,yr])
                ipt=self.intersect(seg)
                ipts.append(ipt)
        return ipts
        
def get_specs(jfile):
    with open(jfile,'r') as f:
        return complete_specs(json.load(f))

def complete_specs(specs):
    """ complete_specs performs all allowed mass balance calculations based on specifications 
        currently it can only handle the standard case where Feed rate and composition are given
        along with the distillate and bottoms compositions """
    
    Feeds=[]
    for f in specs.keys():
        if 'Feed' in f:
            Feeds.append(f)
    if len(Feeds)==1:
        if not 'F' in specs['Feed']:
            if 'Bottoms' in specs and 'Distillate' in specs:
                if not 'B' in specs['Bottoms'] and not 'D' in specs['Distillate']:
                    specs['Feed']['F']=1.0 # basis
            elif 'Raffinate' in specs and 'Extract' in specs:
                if not 'R' in specs['Raffinate'] and not 'E' in specs['Extract']:
                    specs['Feed']['F']=1.0 # basis
        if 'F' in specs['Feed'] and 'z' in specs['Feed']:
            if 'Bottoms' in specs and 'Distillate' in specs:
                if not 'B' in specs['Bottoms'] and not 'D' in specs['Distillate']:
                    # z F = x_D D + x_B B = x_D (F-B) + x_B B = x_D F + (x_B-x_D) B
                    # B = F (z-x_D)/(x_B-x_D)
                    specs['Bottoms']['B']=specs['Feed']['F']*(specs['Feed']['z']-specs['Distillate']['x'])/(specs['Bottoms']['x']-specs['Distillate']['x'])
                    specs['Distillate']['D']=specs['Feed']['F']-specs['Bottoms']['B']
    return specs

def get_xy(xyfile=None,l=None):
    if xyfile:
        """ reads the CSV file containing a column of x and a column of y data """
        data=pd.read_csv(xyfile,header=0,index_col=None)
        y_of_x=interp1d(data['x'],data['y'])
        x_of_y=interp1d(data['y'],data['x'])
        """ returns three things: a function for interpolaing y(x), another for x(y), and the actual data as a pandas dataframe """
        return {'y_of_x':y_of_x,'x_of_y':x_of_y,'data':data}
    elif l:
        # equilibrium data is just a line
        return {'y_of_x':l.y,'x_of_y':l.inv}
    
def plot_xy(y_of_x,data=[],lines=[],steps=[],annotation={},**kwargs):
    fig,ax=plt.subplots(1,1,figsize=kwargs.get('figsize',(8,8)))
    plt.rcParams.update({'font.size': kwargs.get('fontsize',16)})
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_xticks(kwargs.get('xticks',np.arange(0,1.1,0.1)))
    ax.set_yticks(kwargs.get('yticks',np.arange(0,1.1,0.1)))
    ax.set_xlim(kwargs.get('xlim',[0,1]))
    ax.set_ylim(kwargs.get('ylim',[0,1]))
    ax.grid(which='major')
    if not type(data)==pd.core.frame.DataFrame:
        xdomain=np.linspace(*(kwargs.get('xlim',[0,1])),101)
        ax.plot(xdomain,y_of_x(xdomain),'b-',label='equilibrium',linewidth=kwargs.get('linewidth',1.0))
    else:
        ax.plot(data['x'],data['y'],'b-',label='equilibrium',linewidth=kwargs.get('linewidth',1.0))
    for L in lines:
        p0=L['p0']
        p1=L['p1']
        if 'shortcode' in L:
            ax.plot([p0[0],p1[0]],[p0[1],p1[1]],L['shortcode'],label=L['label'])
        else:
            ax.plot([p0[0],p1[0]],[p0[1],p1[1]],label=L['label'])
    if len(steps)>0:
        for si,sj in zip(steps[:-1],steps[1:]):
            ax.plot([si[0],sj[0]],[si[1],sj[1]],color='black')
    ax.legend()
    if len(annotation)>0:
        x,y=annotation['xy']
        label=annotation['label']
        ax.text(x,y,label)
    return fig,ax

def stepoff(x_of_y,top=[0,1],bot=[1,0],lines=[],lim=200):
    xtop,ytop=top
    xbot,ybot=bot
    # compute intersections of adjacent section operating lines
    joints=[]
    for l1,l2 in zip(lines[:-1],lines[1:]):
        joints.append(l1.intersect(l2))

    # step off from top
    steps=[[xtop,ytop]]
    nstages=0
    # curr_jidx=0
    curr_lidx=0
    while steps[-1][0]>xbot and nstages<lim:
        y=steps[-1][1]
        x=x_of_y(y)
        steps.append([x,y])
        if curr_lidx<len(joints) and x<joints[curr_lidx][0]:
            # curr_jidx+=1
            curr_lidx+=1
        ol=lines[curr_lidx]
        y=ol.y(x)
        steps.append([x,y])
        nstages+=1
    if nstages>lim:
        raise Exception('Too many stages')
#    determine the fractional stage
    f=0
    if steps[-1][0]<xbot:
        f=(steps[-3][0]-xbot)/(steps[-3][0]-steps[-1][0])
        nstages-=1
        nstages+=f
        steps[-2][0]=xbot
        steps[-1]=[xbot,lines[-1].y(xbot)]
    return steps,nstages

def get_feedstage(steps,p0):
    for i in range(0,len(steps)-2,2):
        if steps[i][0]>p0[0]>steps[i+1][0]:
            return i//2 + 1
    return 0

if __name__=='__main__':
    parser=ap.ArgumentParser()
    parser.add_argument('-f',default='example-LLE.json',help='input JSON file')
    args=parser.parse_args()

    # get specifications from input file
    specs=get_specs(args.f)
    q=specs['Feed']['q']
    F=specs['Feed']['F']
    z=specs['Feed']['z']

    Ein=specs['Extract']['Ein']
    yin=specs['Extract']['yin']
    Eout=specs['Extract']['Eout']
    yout=specs['Extract']['yout']
    Rin=specs['Raffinate']['Rin']
    xin=specs['Raffinate']['xin']
    Rout=specs['Raffinate']['Rout']
    xout=specs['Raffinate']['xout']

    # parameterize the feed line and operating lines
    feed_line=line(m=q/(q-1),b=z/(1-q))
    top_line=line(m=Rin/Eout,p1=(xin,yout))
    bot_line=line(m=Rout/Ein,p1=(xout,yin))
    print(f'Top:',str(top_line))
    print(f'Bottom:',str(bot_line))

    intersection_point=top_line.intersect(bot_line)
    # get the equilibrium data and two interpolators y(x) and x(y)
    fdict=get_xy(l=line(m=specs['Data']['Kd'],p1=[0,0]))

    # step off stages using equilibrium data and operating lines; get feed stage
    nstages,steps=stepoff(fdict,specs,lines=[top_line,bot_line])
    feed_stage=get_feedstage(steps,intersection_point)
    
    # generate the plot
    plot_xy(fdict,outfile=specs['Output']['plotfile'],
            lines=[
                {'label':'feed',  'line':feed_line,  'p0':(z,z),  'p1':intersection_point},
                {'label':'top',   'line':top_line,   'p0':(xin,yout),'p1':intersection_point},
                {'label':'bottom','line':bot_line,'p0':(xout,yin),'p1':intersection_point}
                ],
            steps=steps,annotation={'xy':(0.01,0.01),'label':f'{nstages:.2f} stages\nfeed at stage {feed_stage}'},
            xlim=[0,0.013],ylim=[0,0.020],xticks=np.arange(0,0.013,0.002),yticks=np.arange(0,0.020,0.002))
