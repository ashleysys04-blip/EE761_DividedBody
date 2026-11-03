#!/usr/bin/env python3
"""Why the island hole transmission length L_eff grows with current (third jump, third_latch.py).

For every snapshot of the coupled width sweep: inside the n+ island (x = 0.665 um .. 0.665 um + W, full film) the mean hole
density p_isl and recombination rate U_isl (node values, island box), the effective island hole lifetime tau_isl = p_isl / U_isl,
the hole current entering at the right edge (from the right body) and leaving at the left edge (into the left body),
transmission T = I_out / I_in, and L_T from T = exp(-W / L_T); compared with L_D = sqrt(D_p tau_isl), D_p = 2 cm^2/s.
Python reading of .str (codes 107 p, 118 U, 221 Jp_x). Output: island_transport.dat"""
import os, sys, numpy as np, matplotlib.tri as mtri
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '..')
sys.path.insert(0, os.path.join(R, '1007_ddsplit')); sys.path.insert(0, os.path.join(R, 'tools'))
from mech2_ddsplit import read_full
from analyze_ddsplit import load_cols
WD, TSI, XIL, DP = 0.5e-4, 0.05, 0.665, 2.0
TS = [2.142857e-03, 2.857143e-03, 3.571429e-03, 4.285714e-03, 5.000000e-03, 5.714286e-03, 7.142857e-03, 8.571429e-03]   # up sweep
RUNS = [(15, '1030_islw/ISLW015'), (30, '1010_sink/NOKILL_TE8_XS60'), (60, '1030_islw/ISLW060'), (120, '1030_islw/ISLW120'), (200, '1030_islw/ISLW200')]


def cut(nodes, ix, x0, code='221'):
    m = (nodes[:, 1] <= TSI + 1e-4) & (np.abs(nodes[:, 0] - x0) < 0.02); nd = nodes[m]
    f = mtri.LinearTriInterpolator(mtri.Triangulation(nd[:, 0], nd[:, 1]), nd[:, 2 + ix[code]])
    y = np.linspace(1e-4, TSI - 1e-4, 200); j = np.ma.filled(f(np.full_like(y, x0), y), np.nan)
    return WD * np.trapz(np.nan_to_num(j), y * 1e-4)


out = ['# W_nm VD I_D p_isl(cm-3) U_isl(cm-3s-1) tau_isl(s) I_in I_out T L_T(nm) L_D(nm) run   (island_transport.py, up sweep)']
for w, b in RUNS:
    M, v, Id, Is, It, Vt = load_cols(os.path.join(R, b + '.log_tr.log')); t = M[:, 0]; xir = XIL + w / 1000
    for k, ts in enumerate(TS, 1):
        i = int(np.argmin(np.abs(t - ts))); cen, area, f, nodes, ix = read_full(os.path.join(R, f'{b}_T_tr_{k}'))
        m = (nodes[:, 0] > XIL + 0.001) & (nodes[:, 0] < xir - 0.001) & (nodes[:, 1] <= TSI); nd = nodes[m]
        p, U = np.mean(nd[:, 2 + ix['107']]), np.mean(nd[:, 2 + ix['118']]); tau = p / U if U > 0 else np.nan
        Iin, Iout = -cut(nodes, ix, xir - 0.001), -cut(nodes, ix, XIL + 0.001)
        T = Iout / Iin if Iin > 0 else np.nan; LT = -w / np.log(T) if 0 < T < 1 else np.nan
        out.append('%3d %4.1f %9.2e %9.2e %9.2e %9.2e %9.2e %9.2e %6.3f %7.1f %7.1f %s' % (w, v[i], abs(Id[i]), p, U, tau, Iin, Iout, T, LT, 1e7 * np.sqrt(DP * tau), os.path.basename(b)))
open(os.path.join(H, 'island_transport.dat'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
