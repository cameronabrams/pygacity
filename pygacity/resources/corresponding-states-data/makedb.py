import pandas as pd
import sys
prop=sys.argv[1]
with open(f'{prop}-departures.raw','r') as f:
    lines=f.read().split('\n')
blocks=[]
for l in lines:
    if l.startswith('#'):
        tok=l.split()
        tr=float(tok[2])
        if tr>1:
            d=dict(Tr=tr,Pr=[0.0],Dr=[0.0])
        else:
            d=dict(Tr=tr,Pr=[],Dr=[])
        blocks.append(d)
    else:
        tok=l.split(',')
        x=float(tok[0])
        y=float(tok[1])
        d['Pr'].append(x)
        d['Dr'].append(y)

dp=pd.DataFrame(columns=['Tr','Pr','Dr'])
for b in blocks:
    tmp=pd.DataFrame.from_dict(b)
    # print(tmp.head())
    dp=pd.concat((dp,tmp))
dp.to_csv(f'{prop}-departures.csv',index=False,header=True)
