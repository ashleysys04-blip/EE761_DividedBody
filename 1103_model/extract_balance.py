#!/usr/bin/env python3
"""Left-STL hole balance from the .str snapshots of every coupling run (input for the body hole-balance model, model_latch.py).

For each MixedMode snapshot <run>_T_tr_N (0 -> 6 -> 0 V, 0.7 V/ms; N -> V_D from the tsave list) and the log at that time:
  V_isl = psi(island centre) - psi(source n+ at 0.45 um), mean over the film (code 100)
  IeL  = |I_S|                 left-STL electron current (A)
  Control volume = left p body, x = 0.50 um (source junction) .. 0.665 um (left island edge), full film:
  Iii  = q W int G_ii dA       impact-ionization holes generated in the body (code 105)
  Rb   = q W int U dA          recombination in the body (code 118)
  Rs   = -W int Jp_x dy        holes leaving the body into the n+ source (cut 1 nm inside the body; code 221) = emitter back-injection
  Ic   = -W int Jp_x dy        holes entering the body from the island (cut 1 nm inside the body, > 0 = into the body)
  m    = Iii / IeL  (= M - 1),  g = (Rb + Rs) / IeL (= base current / collector current = 1 / beta),  eta = Ic / |I_D|,
  res  = (Iii + Ic - Rb - Rs) / (Rb + Rs)  (steady-state closure check)
Island: left edge fixed at 0.665 um (left body 165 nm in every run), right edge 0.665 um + W. Python reading of .str.
Output: balance.dat"""
import os, sys, numpy as np, matplotlib.tri as mtri
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '..')
sys.path.insert(0, os.path.join(R, '1007_ddsplit')); sys.path.insert(0, os.path.join(R, 'tools'))
from mech2_ddsplit import read_full
from analyze_ddsplit import load_cols
Q, WD, TSI, XIL = 1.602e-19, 0.5e-4, 0.05, 0.665
TS = [2.142857e-03, 2.857143e-03, 3.571429e-03, 4.285714e-03, 5.000000e-03, 5.714286e-03, 7.142857e-03, 8.571429e-03, 1.000000e-02,
      1.142857e-02, 1.214286e-02, 1.285714e-02, 1.357143e-02, 1.428571e-02, 1.500000e-02, 1.571429e-02, 1.714286e-02]
RUNS = [('width', 15, 1e-8, '1030_islw/ISLW015'), ('width', 30, 1e-8, '1010_sink/NOKILL_TE8_XS60'), ('width', 45, 1e-8, '1030_islw/ISLW045'),
        ('width', 60, 1e-8, '1030_islw/ISLW060'), ('width', 90, 1e-8, '1030_islw/ISLW090'), ('width', 120, 1e-8, '1030_islw/ISLW120'),
        ('width', 200, 1e-8, '1030_islw/ISLW200'), ('tau', 30, 3e-9, '1029_isltau/ISL_TAU3em9_XS60'), ('tau', 30, 1e-10, '1029_isltau/ISL_TAU1em10_XS60'),
        ('killed', 30, 1e-12, '1007_ddsplit/DDS_TE8_XS60'), ('killed', 120, 1e-12, '1030_islw/ISLW120_KILL')]


def cut(nodes, ix, x0, code='221'):
    m = (nodes[:, 1] <= TSI + 1e-4) & (np.abs(nodes[:, 0] - x0) < 0.02); nd = nodes[m]
    f = mtri.LinearTriInterpolator(mtri.Triangulation(nd[:, 0], nd[:, 1]), nd[:, 2 + ix[code]])
    y = np.linspace(1e-4, TSI - 1e-4, 200); j = np.ma.filled(f(np.full_like(y, x0), y), np.nan)
    return WD * np.trapz(np.nan_to_num(j), y * 1e-4)


out = ['# sweep W_nm tau_s snap dir V_D V_tap V_isl IeL Iii Rb Rs Ic I_D m g eta res run   (extract_balance.py; currents A, voltages V; V_isl = psi(island centre) - psi(source))']
for s, w, tau, b in RUNS:
    M, v, Id, Is, It, Vt = load_cols(os.path.join(R, b + '.log_tr.log')); t = M[:, 0]
    for k, ts in enumerate(TS, 1):
        fn = os.path.join(R, f'{b}_T_tr_{k}')
        if not os.path.exists(fn) or ts > t[-1]: continue
        i = int(np.argmin(np.abs(t - ts)))
        cen, area, f, nodes, ix = read_full(fn); x, y = cen[:, 0], cen[:, 1]; film = y <= TSI + 5e-4
        G, U = f('105'), f('118'); S = lambda mk, z: Q * WD * np.sum(z[mk] * area[mk])
        body = film & (x > 0.5) & (x < XIL)
        Iii = S(body, G); Rb = S(body, U); Rs = -cut(nodes, ix, 0.501)
        Ic = -cut(nodes, ix, XIL - 0.001); IeL, ID = abs(Is[i]), abs(Id[i])
        psi = mtri.LinearTriInterpolator(mtri.Triangulation(nodes[:, 0], nodes[:, 1]), nodes[:, 2 + ix['100']])
        P = lambda x0: float(np.mean([psi(x0, yy) for yy in (0.01, 0.025, 0.04)]))
        Visl = P(XIL + w / 2000) - P(0.45)                     # island potential vs source (both n+ 1e20, so = quasi-Fermi difference)
        res = (Iii + Ic - Rb - Rs) / max(Rb + Rs, 1e-30)
        out.append('%-6s %3d %7.0e %2d %-4s %5.2f %6.3f %6.3f %10.3e %10.3e %10.3e %10.3e %10.3e %10.3e %10.3e %10.3e %10.3e %+.2f %s' % (
            s, w, tau, k, 'up' if k <= 8 else 'down', v[i], Vt[i], Visl, IeL, Iii, Rb, Rs, Ic, ID, Iii / IeL, (Rb + Rs) / IeL, Ic / ID, res, os.path.basename(b)))
    print(b, flush=True)
open(os.path.join(H, 'balance.dat'), 'w').write('\n'.join(out) + '\n')
