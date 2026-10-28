#!/usr/bin/env python3
"""Step 15: structures (INIT .str) and hole-density maps at VD 4.0 V up-sweep (T_tr_6; C10p: T_tr_3, 2.5 V) of the finished ROB_* runs.
Output: robust_struct.png, robust_pmaps.png (this folder). Python rendering of .str, not Tonyplot."""
import sys, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.tri as mtri
sys.path.insert(0,'/home/ysseo/novel/tools'); from strstruct import draw
import os; D=os.path.dirname(os.path.abspath(__file__))+'/'; O=D
R=[('ROB_SR1e6','tap contact S=1e6 cm/s'),('ROB_W60','island 60 nm, core 40 nm'),('ROB_W100','island 100 nm, core 80 nm'),('ROB_SG_W100','split gate + top contact, island 100 nm'),('ROB_RES15','15 nm Si left under core'),('ROB_OFFP5','core shifted 5 nm right'),('ROB_C100p','tap + 100 pF'),('ROB_C10p','tap + 10 pF (running)')]
fig,ax=plt.subplots(4,2,figsize=(14,12))
for a,(n,t) in zip(ax.flat,R):
    draw(D+n+'_INIT.str',None,title=f'{n}: {t}',xlim=(0.45,0.85),ylim=(0.27,-0.13),ax=a,note='source: 1026_sinkrob/'+n+'_INIT.str')
fig.suptitle('Structures (Python rendering of .str, not Tonyplot)'); fig.tight_layout(); fig.savefig(O+'robust_struct.png',dpi=110)
def load(fn):
    C={};nodes={};codes=None
    for l in open(fn):
        if l[:2]=='c ': p=l.split(); C[int(p[1])]=(float(p[2]),float(p[3]))
        elif l[:2]=='s ': codes=l.split()[2:]
        elif l[:2]=='n ':
            p=l.split()
            if p[2]=='3': nodes[int(p[1])+1]=float(p[3+codes.index('107')])
    k=sorted(nodes); return np.array([C[i] for i in k]),np.array([nodes[i] for i in k])
fig,ax=plt.subplots(4,2,figsize=(14,10))
for a,(n,t) in zip(ax.flat,R):
    s='_T_tr_3' if 'C10p' in n else '_T_tr_6'; lab='t=3.57 ms, up VD 2.5 V' if 'C10p' in n else 't=5.71 ms, up VD 4.0 V'
    xy,p=load(D+n+s); m=(xy[:,0]>0.45)&(xy[:,0]<0.85); xy,p=xy[m],p[m]
    cs=a.tricontourf(mtri.Triangulation(xy[:,0],xy[:,1]),np.log10(np.maximum(p,1)),np.linspace(0,20,41),cmap='magma'); fig.colorbar(cs,ax=a)
    a.set_ylim(0.055,-0.005); a.set_title(f'{n} ({t})  {lab}: log10 p',fontsize=8)
fig.suptitle('Hole density in Si, Python rendering of 1026_sinkrob/*_T_tr_*.str (core region = drawing artifact)',fontsize=9); fig.tight_layout(); fig.savefig(O+'robust_pmaps.png',dpi=110)
