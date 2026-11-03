#!/usr/bin/env python3
"""Mechanism of the current dependence of the island coupling: hole injection from the right body into the island.
Junction law at the right body / island junction: p_isl(0) n_isl(0) = p_R(0) n_R(0) = n_ie^2 exp(V/V_th), so with n_isl ~ N_D
the holes injected into the island scale with p_R(0) n_R(0) / N_D, the electrons injected into the body with n_R(0):
gamma = I_p,in / I_D  ~  p_R(0) / N_D  ->  gamma(I) = gamma_0 p_R(0) / N_A,R  (low injection: p_R = N_A; high injection: p_R ~ n_R).
For every snapshot (W 15-120 nm coupled, up and down): I_D, I_p,in (hole current into the island at its right edge),
p_R(0), n_R(0) at 3 nm inside the right body, p_isl(0) at 2 nm inside the island (film mean, codes 106 n, 107 p, 221 Jp_x).
Output: injection.dat, injection.png"""
import os, sys, numpy as np, matplotlib, matplotlib.tri as mtri
matplotlib.use('Agg'); import matplotlib.pyplot as plt
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '..')
sys.path.insert(0, os.path.join(R, '1007_ddsplit'))
from mech2_ddsplit import read_full
from analyze_ddsplit import load_cols
WD, TSI, XIL, NAR, ND = 0.5e-4, 0.05, 0.665, 7e17, 1e20
TS = [2.142857e-03, 2.857143e-03, 3.571429e-03, 4.285714e-03, 5.000000e-03, 5.714286e-03, 7.142857e-03, 8.571429e-03, 1.000000e-02,
      1.142857e-02, 1.214286e-02, 1.285714e-02, 1.357143e-02, 1.428571e-02, 1.500000e-02]
RUNS = [(15, '1030_islw/ISLW015'), (30, '1010_sink/NOKILL_TE8_XS60'), (60, '1030_islw/ISLW060'), (120, '1030_islw/ISLW120')]


def line(nodes, ix, code, x0):
    m = (nodes[:, 1] <= TSI + 1e-4) & (np.abs(nodes[:, 0] - x0) < 0.02); nd = nodes[m]
    fi = mtri.LinearTriInterpolator(mtri.Triangulation(nd[:, 0], nd[:, 1]), nd[:, 2 + ix[code]])
    y = np.linspace(1e-3, TSI - 1e-3, 100); return np.ma.filled(fi(np.full_like(y, x0), y), np.nan), y


out = ['# W VD dir  I_D  I_p,in  gamma=I_p,in/I_D  p_R(0)  n_R(0)  p_isl(0)  p_R/N_A   (injection.py)']
rows = []
for w, b in RUNS:
    M, v, Id, Is, It, Vt = load_cols(os.path.join(R, b + '.log_tr.log')); t = M[:, 0]; xir = XIL + w / 1000
    for k, ts in enumerate(TS, 1):
        i = int(np.argmin(np.abs(t - ts))); cen, area, f, nodes, ix = read_full(os.path.join(R, f'{b}_T_tr_{k}'))
        jp, y = line(nodes, ix, '221', xir - 0.001); Ipin = -WD * np.trapz(np.nan_to_num(jp), y * 1e-4)
        pR = np.nanmean(line(nodes, ix, '107', xir + 0.003)[0]); nR = np.nanmean(line(nodes, ix, '106', xir + 0.003)[0])
        pI = np.nanmean(line(nodes, ix, '107', xir - 0.002)[0]); ID = abs(Id[i])
        rows.append((w, v[i], 'up' if k <= 8 else 'dn', ID, Ipin, Ipin / ID, pR, nR, pI))
        out.append('%3d %4.1f %s %9.2e %9.2e %8.4f %9.2e %9.2e %9.2e %8.2f' % (w, v[i], rows[-1][2], ID, Ipin, Ipin / ID, pR, nR, pI, pR / NAR))
open(os.path.join(H, 'injection.dat'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
fig, ax = plt.subplots(1, 3, figsize=(15, 4.5)); cm = plt.get_cmap('viridis')
for n, w in enumerate([r[0] for r in RUNS]):
    rr = [r for r in rows if r[0] == w and r[3] > 1e-8]; c = cm(n / 4)
    ax[0].loglog([r[3] for r in rr], [r[5] for r in rr], 'o', color=c, label=f'W {w} nm')
    ax[1].loglog([r[3] for r in rr], [r[6] / NAR for r in rr], 'o', color=c, label=f'W {w} nm')
    ax[2].loglog([r[6] / NAR for r in rr], [r[5] for r in rr], 'o', color=c, label=f'W {w} nm')
ax[0].set_xlabel('|I_D| (A)'); ax[0].set_ylabel('gamma = holes into island / I_D'); ax[1].set_xlabel('|I_D| (A)'); ax[1].set_ylabel('p_R(0) / N_A,R')
ax[2].set_xlabel('p_R(0) / N_A,R'); ax[2].set_ylabel('gamma'); xx = np.logspace(0, 2, 10)
for a in ax: a.grid(alpha=.3, which='both'); a.legend(fontsize=7)
fig.suptitle('Hole injection into the island vs right-body hole density (.str read in Python)', fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(H, 'injection.png'), dpi=100)
