# Author: Cameron F. Abrams, <cfa22@drexel.edu>
"""
Binary distillation column sizing using the McCabe-Thiele approach
"""
import json
import pandas as pd
from scipy.interpolate import interp1d
from scipy.optimize import fsolve
import matplotlib.pyplot as plt
import numpy as np
import argparse as ap
from matplotlib.ticker import AutoMinorLocator, MultipleLocator

class point:
    def __init__(self,x=0,y=0):
        self.x=x
        self.y=y

class line:
    def __init__(self,m=None,b=None,p1:point=None,p2:point=None,x=None,vert=False,shortcode='b-',label=''):
        self.vert=vert
        self.x=x
        self.shortcode=shortcode
        self.label=label
        if m!=None and b!=None:
            self.m=m
            self.b=b
        elif m!=None and p1!=None:
            self.b=p1.y-m*p1.x
            self.m=m
        elif p1!=None and p2!=None:
            if p1.x!=p2.x:
                self.m=(p2.y-p1.y)/(p2.x-p1.x)
                self.b=p1.y-self.m*p1.x
            else:
                self.x=p1.x
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
            return point(x,self.y(x))
        elif self.m==other.m:
            # parallel lines cannot intersect
            return None
        elif self.vert and not other.vert:
            return point(self.x,other.y(self.x))
        elif not self.vert and other.vert:
            return point(other.x,self.y(other.x))
    def intersect_interp(self,interp):
        if self.vert:
            return [point(self.x,float(interp(self.x)))]
        ipts=[]
        z=interp
        for xl,xr,yl,yr in zip(z.x[:-1],z.x[1:],z.y[0:-1],z.y[1:]):
            lyl=self.y(xl)
            lyr=self.y(xr)
            if (yl>lyl and yr<lyr) or (yl<lyl and yr>lyr):
                seg=line(p1=point(xl,yl),p2=point(xr,yr))
                ipt=self.intersect(seg)
                ipts.append(ipt)
        return ipts

class OperatingLineEnvelope:
    def __init__(self,start_x=0.0,start_from='BOTTOM',shortcode='b-'):
        assert start_from in ['TOP','BOTTOM'],f'Error: unrecognized value {start_from} for parameter "start_from"'
        self.start_from=start_from
        self.start_x=start_x
        self.vertices=[]
        self.lines=[]
        self.shortcode=shortcode

    def add_operating_line(self,a_line):
        if len(self.vertices)==0:
            self.vertices.append(point(self.start_x,a_line.y(self.start_x)))
        else:
            self.vertices.append(self.lines[-1].intersect(a_line))
        self.lines.append(a_line)
    
    def terminate(self,end_x):
        self.vertices.append(point(end_x,self.lines[-1].y(end_x)))

    def y_of_x(self,x):
        for i,p in enumerate(self.vertices):
            if self.start_from=='TOP':
                if x>p.x:
                    return self.lines[i-1].y(x)
            else:
                if x<p.x:
                    return self.lines[i-1].y(x)
        return None
    
    def x_of_y(self,y):
        for i,p in enumerate(self.vertices):
            if self.start_from=='TOP':
                if y>p.y:
                    return self.lines[i-1].inv(y)
            else:
                if y<p.y:
                    return self.lines[i-1].inv(y)
        return None
    
    def plot(self,ax,**kwargs):
        for i,l in enumerate(self.lines):
            x1,x2=self.vertices[i].x,self.vertices[i+1].x
            y1,y2=l.y(x1),l.y(x2)
            ax.plot([x1,x2],[y1,y2],l.shortcode,label=l.label)

class EquilibriumEnvelope:
    def __init__(self,csv_filename='',a_line=None,a_fake=1):
        self.y_of_x=None
        self.x_of_y=None
        self.data=None
        if csv_filename:
            """ reads the CSV file containing a column of x and a column of y data """
            self.data=pd.read_csv(csv_filename,header=0,index_col=None)
            assert 'x' in self.data and 'y' in self.data,f'file {csv_filename} does not have either an x or y column'
            self.y_of_x=interp1d(self.data['x'],self.data['y'])
            self.x_of_y=interp1d(self.data['y'],self.data['x'])
        elif a_line:
            # equilibrium data is just a line
            self.y_of_x=a_line.y
            self.x_of_y=a_line.inv
            self.data=pd.DataFrame({'x':np.linspace(0,1,101)})
            self.data['y']=self.y_of_x(self.data['x'])
        else: # make a fake one
            def yfake(x,a):
                return x/((1-a)*x+a)
            self.data=pd.DataFrame({'x':np.linspace(0,1,101)})
            self.data['y']=yfake(self.data['x'],a_fake)
            self.y_of_x=interp1d(self.data['x'],self.data['y'])
            self.x_of_y=interp1d(self.data['y'],self.data['x'])
    def plot(self,ax,**kwargs):
        ax.plot(self.data['x'],self.data['y'],kwargs.get('shortcode','b-'),label=kwargs.get('label','eq'))

class Stages:
    def __init__(self,eq=None,op=None):
        self.eq=eq
        self.op=op
    def step_off(self,**kwargs):
        limit=kwargs.get('limit',100)
        tol=kwargs.get('tolerance',0.001)
        self.points=[op.vertices[0]]
        # print(self.points[0].x,self.points[0].y)
        n=0
        if op.start_from=='BOTTOM':
            next_x=this_x=self.points[-1].x
            while this_x<=op.vertices[-1].x and n<limit:
                next_y=eq.y_of_x(this_x)
                if next_y>=op.vertices[-1].y:
                    break
                self.points.append(point(this_x,next_y))
                # print(n,this_x,next_y)
                next_x=op.x_of_y(next_y)
                self.points.append(point(next_x,next_y))
                # print(n,next_x,next_y)
                this_x=next_x
                n+=1
            f=0.0
            if next_y-op.vertices[-1].y>tol:
                f=(op.vertices[-1].y-self.points[-1].y)/(next_y-self.points[-1].y)
                self.points.append(point(next_x,op.vertices[-1].y))
                self.points.append(op.vertices[-1])
            self.nstages=float(n+f)
        else:
            next_y=this_y=self.points[-1].y
            while this_y>=op.vertices[-1].y and n<limit:
                next_x=eq.x_of_y(this_y)
                if next_x<op.vertices[-1].x:
                    break
                self.points.append(point(next_x,this_y))
                next_y=op.y_of_x(next_x)
                self.points.append(point(next_x,next_y))
                this_y=next_y
                n+=1
            f=0.0
            if op.vertices[-1].x-next_x>tol:
                f=(self.points[-1].y-op.vertices[-1].y)/(eq.y_of_x(op.vertices[-1].x)-op.vertices[-1].y)
                self.points.append(point(op.vertices[-1].x,this_y))
                self.points.append(op.vertices[-1])
            self.nstages=float(n+f)
    def feed_stages(self):
        feeds=[]
        if len(self.points)>0:
            # look for interior vertices of the operating envelope
            for v in op.vertices[1:-1]:
                stage=0
                for p1,p2 in zip(self.points[:-1],self.points[1:]):
                    if p1.x!=p2.x:
                        stage+=1
                        if p1.x<=v.x<=p2.x:
                            feeds.append(stage)
                        elif p2.x<=v.x<=p1.x:
                            feeds.append(stage)
        return feeds
    def plot(self,ax,**kwargs):
        for v1,v2 in zip(self.points[:-1],self.points[1:]):
            ax.plot([v1.x,v2.x],[v1.y,v2.y],kwargs.get('shortcode','k-'))

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

def xy_diagram(ax,eq=None,op=None,st=None,annotation={},**kwargs):
    ax.grid(visible=True,which='major',axis='both',color='k',linestyle='-',linewidth=0.8,alpha=0.6)
    ax.grid(visible=True,which='minor',axis='both',color='k',linestyle='-',linewidth=0.5,alpha=0.4)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_xlim([0,1])
    ax.set_ylim([0,1])
    ax.set_xticks(np.arange(0,1.1,0.1))
    ax.set_yticks(np.arange(0,1.1,0.1))
    ax.xaxis.set_minor_locator(MultipleLocator(0.02))
    ax.yaxis.set_minor_locator(MultipleLocator(0.02))

    # plot 45-degree line
    ax.plot([0,1],[0,1],'k--',linewidth=0.6,alpha=0.4)

    # plot equilibrium envelope
    eq.plot(ax)

    # plot the operating line envelope
    op.plot(ax)

    # plot stages
    st.plot(ax)

    ax.legend()
    if len(annotation)>0:
        x,y=annotation['xy']
        label=annotation['label']
        ax.text(x,y,label)
    return ax

if __name__=='__main__':
    eq=EquilibriumEnvelope(a_fake=0.2)

    # stepping from bottom
    op=OperatingLineEnvelope(start_x=0.025,start_from='BOTTOM')
    op.add_operating_line(line(p1=point(0.025,0.025),m=1.8,shortcode='g-',label='bottom'))
    op.add_operating_line(line(p1=point(0.5,0.7),m=1.0,shortcode='r-',label='middle'))
    op.add_operating_line(line(p1=point(0.975,0.975),m=0.4,shortcode='m-',label='top'))
    op.terminate(end_x=0.975)
    st=Stages(op=op,eq=eq)
    st.step_off()
    feeds=st.feed_stages()
    print(f'Feeds at {feeds}')
    fig,ax=plt.subplots(1,1,figsize=(8,8))
    plt.rcParams.update({'font.size':16})
    xy_diagram(ax,eq=eq,op=op,st=st)
    plt.title(f'Stepping from bottom; N={st.nstages:.2f}')
    plt.savefig('bot.png')
    plt.clf()

    # stepping from top
    op=OperatingLineEnvelope(start_x=0.975,start_from='TOP')
    op.add_operating_line(line(p1=point(0.975,0.975),m=0.4,shortcode='r-',label='top'))
    op.add_operating_line(line(p1=point(0.025,0.025),m=1.6,shortcode='g-',label='bottom'))
    op.terminate(end_x=0.025)
    st=Stages(op=op,eq=eq)
    st.step_off()
    feeds=st.feed_stages()
    print(f'Feeds at {feeds}')
    fig,ax=plt.subplots(1,1,figsize=(8,8))
    plt.rcParams.update({'font.size':16})
    xy_diagram(ax,eq=eq,op=op,st=st)
    plt.title(f'Stepping from top; N={st.nstages:.2f}')
    plt.savefig('top.png')
    
