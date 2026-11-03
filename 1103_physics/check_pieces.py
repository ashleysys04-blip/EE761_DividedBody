#!/usr/bin/env python3
"""Feasibility check of a physics-derived model (no TCAD fitting): two pieces against the snapshot extraction (1103_model/balance.dat).
(1) M-1 of the left drain junction: Selberherr alpha_n(E) = an exp(-bn/E) (ATLAS printed values, an 7.03e5 /cm, bn 1.23e6 V/cm)
    integrated over (a) the real field along the film at mid-depth from the .str (field code 103) and (b) a 1D abrupt n+/p
    junction, N_A = 6e17, reverse bias V_j = V_island - V_body (body potential from the .str).
(2) island hole transmission: holes injected at the right edge, collected at the left edge of an n+ base of width W:
    alpha_T = 1/cosh(W/L_p), L_p = sqrt(D_p tau_p), tau_p = tau0 / (1 + N_D / Nsrh) (consrh, ATLAS printed), D_p from mu_p(1e20).
Output: check_pieces.dat"""
import os, sys, numpy as np, matplotlib.tri as mtri
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '..')
sys.path.insert(0, os.path.join(R, '1007_ddsplit'))
from mech2_ddsplit import read_full
from analyze_ddsplit import load_cols
q, eps, kT = 1.602e-19, 11.7 * 8.854e-14, 0.02585
an, bn = 7.03e5, 1.231e6
NA, ND = 6e17, 1e20; ni = 1.0e10
Vbi = kT * np.log(NA * ND / ni ** 2)
alpha = lambda E: an * np.exp(-bn / np.maximum(E, 1.0))
TS = [2.142857e-03, 2.857143e-03, 3.571429e-03, 4.285714e-03, 5.000000e-03, 5.714286e-03]
B = [l.split() for l in open(os.path.join(R, '1103_model', 'balance.dat')) if not l.startswith('#')]
out = ['# (1) M-1 of the left drain junction.  run VD V_isl V_body  E_max(.str) E_max(1D)  M-1: extracted | Selberherr on .str field | 1D junction']
for run, d, w in [('NOKILL_TE8_XS60', '1010_sink', 30), ('ISLW120', '1030_islw', 120), ('DDS_TE8_XS60', '1007_ddsplit', 30)]:
    for k, ts in enumerate(TS, 1):
        rr = [r for r in B if r[-1] == run and int(r[3]) == k]
        if not rr or float(rr[0][8]) < 1e-8: continue
        m_ex = float(rr[0][14]); cen, area, f, nodes, ix = read_full(os.path.join(R, d, f'{run}_T_tr_{k}'))
        tri = mtri.Triangulation(nodes[:, 0], nodes[:, 1])
        Ef = mtri.LinearTriInterpolator(tri, nodes[:, 2 + ix['103']]); Pf = mtri.LinearTriInterpolator(tri, nodes[:, 2 + ix['100']])
        x = np.linspace(0.50, 0.665, 400)                                         # left body, film mid-depth and 3 depths averaged
        E = np.mean([np.ma.filled(Ef(x, np.full_like(x, y)), 0) for y in (0.01, 0.025, 0.04)], axis=0)
        m_str = np.trapz(alpha(E), x * 1e-4)
        P = lambda x0: float(np.mean([Pf(x0, yy) for yy in (0.01, 0.025, 0.04)]))
        Visl, Vb = P(0.665 + w / 2000) - P(0.45), P(0.58) - P(0.45)
        Vj = max(Visl - Vb, 0.0); Em = np.sqrt(2 * q * NA * (Vbi + Vj) / eps); xd = Em * eps / (q * NA)
        xx = np.linspace(0, xd, 400); m_1d = np.trapz(alpha(Em * (1 - xx / xd)), xx)
        out.append('%-16s %4.1f %6.3f %6.3f  %9.2e %9.2e   %.3f | %.3f | %.3f' % (run, 1.5 + 0.5 * (k - 1), Visl, Vb, E.max(), Em, m_ex, m_str, m_1d))
# (2) transmission
mup = 45.0                                       # cm2/Vs, holes in 1e20 n+ (Masetti / ATLAS conmob table ~45-50 at 1e20)
Dp = kT * mup; taup = 1e-8 / (1 + ND / 5e16); Lp = np.sqrt(Dp * taup) * 1e7
out += ['', '# (2) island transmission alpha_T = 1/cosh(W/L_p):  D_p %.2f cm2/s, tau_p %.2e s (consrh), L_p = %.1f nm  (measured eta_II slope: 21.3 nm)' % (Dp, taup, Lp),
        '# W_nm  alpha_T  2*exp(-W/Lp)  measured eta_II   eta_II / alpha_T (= injected holes per I_D)']
meas = {15: 1.42e-2, 30: 6.76e-3, 45: 3.56e-3, 60: 1.80e-3, 90: 4.42e-4, 120: 1.02e-4, 200: 2.36e-6}
for W, e in meas.items():
    aT = 1 / np.cosh(W / Lp); out.append('%4d  %.3e  %.3e  %.2e  %.4f' % (W, aT, 2 * np.exp(-W / Lp), e, e / aT))
open(os.path.join(H, 'check_pieces.dat'), 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
