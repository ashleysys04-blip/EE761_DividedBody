#!/usr/bin/env python3
"""Hole balance of the RIGHT p body (island right edge .. drain junction) for coupled and killed islands: why does the right-STL
on-branch V_R(I_D) depend on the island?  Per snapshot: m_R = I_ii,R / I_D, recombination R_b,R / I_D, holes leaving into the
island at its right edge (back-injection) / I_D, holes crossing the drain junction / I_D, and V_R = V_D - V_tap.
Codes: 105 G_ii, 118 U, 221 Jp_x. Python reading of .str. Output: right_balance.dat"""
import os, sys, numpy as np, matplotlib.tri as mtri
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '..')
sys.path.insert(0, os.path.join(R, '1007_ddsplit'))
from mech2_ddsplit import read_full
from analyze_ddsplit import load_cols
Q, WD, TSI, XIL = 1.602e-19, 0.5e-4, 0.05, 0.665
TS = [2.142857e-03, 2.857143e-03, 3.571429e-03, 4.285714e-03, 5.000000e-03, 5.714286e-03, 7.142857e-03, 8.571429e-03, 1.000000e-02,
      1.142857e-02, 1.214286e-02, 1.285714e-02, 1.357143e-02, 1.428571e-02, 1.500000e-02]


def cut(nodes, ix, x0, code='221'):
    m = (nodes[:, 1] <= TSI + 1e-4) & (np.abs(nodes[:, 0] - x0) < 0.02); nd = nodes[m]
    f = mtri.LinearTriInterpolator(mtri.Triangulation(nd[:, 0], nd[:, 1]), nd[:, 2 + ix[code]])
    y = np.linspace(1e-4, TSI - 1e-4, 200); j = np.ma.filled(f(np.full_like(y, x0), y), np.nan)
    return WD * np.trapz(np.nan_to_num(j), y * 1e-4)


out = ['# run W dir VD V_R I_D  m_R  rec/I_D  into_island/I_D  out_drain/I_D  residual   (right_balance.py)']
for run, d, w in [('NOKILL_TE8_XS60', '1010_sink', 30), ('ISLW120', '1030_islw', 120), ('ISLW200', '1030_islw', 200), ('DDS_TE8_XS60', '1007_ddsplit', 30)]:
    M, v, Id, Is, It, Vt = load_cols(os.path.join(R, d, run + '.log_tr.log')); t = M[:, 0]; xir = XIL + w / 1000; xd = 0.5 + 0.27 + w / 1000
    for k, ts in enumerate(TS, 1):
        i = int(np.argmin(np.abs(t - ts))); ID = abs(Id[i])
        if ID < 1e-7: continue
        cen, area, f, nodes, ix = read_full(os.path.join(R, d, f'{run}_T_tr_{k}')); x, y = cen[:, 0], cen[:, 1]
        body = (y <= TSI + 5e-4) & (x > xir) & (x < xd); G, U = f('105'), f('118')
        Iii = Q * WD * np.sum(G[body] * area[body]); Rb = Q * WD * np.sum(U[body] * area[body])
        Iisl = -cut(nodes, ix, xir + 0.001)                 # holes moving -x out of the right body into the island
        Idr = cut(nodes, ix, xd - 0.001)                    # holes moving +x into the drain
        res = (Iii - Rb - Iisl - Idr) / max(Iii, 1e-30)
        out.append('%-16s %3d %s %4.1f %5.3f %9.2e  %.3f  %.3f  %.3f  %.3f  %+.2f' % (run, w, 'up' if k <= 8 else 'dn', v[i], v[i] - Vt[i], ID,
                   Iii / ID, Rb / ID, Iisl / ID, Idr / ID, res))
open(os.path.join(H, 'right_balance.dat'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
