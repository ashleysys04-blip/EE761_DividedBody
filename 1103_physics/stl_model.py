#!/usr/bin/env python3
"""Analytical equivalent-circuit model of the divided-body STL (after Park et al., EDL 2026, "Analytical model for single
transistor latch in MOSFETs"), extended to two floating bodies coupled through the n+ island.

Left body node (steady state of dQ_B/dt):  I_II,L + I_c + G0 = Q_B/tau_B + I_DIFF
    I_L      = I_S exp(V_BS/V_th)                       left-STL BJT (electron) current
    I_II,L   = (M_L - 1) I_L,  M_L = [1 - ((V_I - I_L R_LRS) / V_BR)^n]^-1   Miller, V_I = island potential (left STL drain)
    hole loss = I_L / beta(I_L),  1/beta = q_b/beta_0 + k_r (I_L/1uA)^-(1 - 1/n_r)
               first term: back-injection into the n+ source and neutral-body recombination, with the Gummel-Poon high-injection
               factor q_b = (1 + sqrt(1 + 4 I_L/I_KF)) / 2 (Webster); second term: space-charge recombination at the body-source
               junction, ideality n_r (Park eq. (8), second term, with exp(V_BS/2V_th) -> exp(V_BS/n_r V_th)).
    (Park's Q_B/tau_B with Q_B = C_B V_BS is not used: tau_B/C_B = 5.4e6 Ohm gives a hole loss ~100x the body recombination
     extracted from the snapshots, because recombination in the p body scales with the minority electrons, i.e. with I_L.)
    I_c      = eta I_D  holes arriving from the right body through the island (lateral p-n+-p base transport):
               eta = gamma / sinh(W/L_p),  L_p = sqrt(D_p tau_p),  tau_p = tau_0,isl / (1 + N_D/N_SRH),  D_p = V_th mu_p(1e20)  [physics]
               gamma = holes the right body injects into the island per drain electron (one parameter, fixed on one coupled run)
Right STL (on in states II, III):  M_R - 1 = 1/beta_R(I_D)  ->  V_R = V_BR,R (1 - 1/M_R)^(1/n_R) + I_D R_LRS,R  (Park: V_D from M)
Circuit:  I_D = I_L + V_I/R_tap,  V_D = V_I + V_R(I_D).
For every I_L the body balance gives one V_I (its left side rises with V_I): the curve V_D(I_L) is S-shaped; the up sweep jumps at
its local maxima (latch-up), the down sweep at its local minima (latch-down).  Loop gain:  A_loop = 1 <-> dV_D/dI_L = 0.
Fit (killed island W 30 nm, DDS_TE8_XS60 only): left Miller V_BR, n, R_LRS, beta_0, k_r, n_r, I_KF; right V_BR,R, n_R, R_LRS,R, beta_0,R.
Then gamma from ISLW120 state II; every other run (W 15-200 nm, island tau 3e-9, 1e-10 s) is a prediction.
Output: stl_model.dat, stl_model.png"""
import os, sys, numpy as np, matplotlib
from scipy.optimize import least_squares
matplotlib.use('Agg'); import matplotlib.pyplot as plt
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '..')
sys.path.insert(0, os.path.join(R, '1007_ddsplit'))
from analyze_ddsplit import load_cols, analyse

# ---------------- physical constants and device data (ATLAS printed parameters, deck geometry) ----------------
VT, Q = 0.02585, 1.602e-19
RTAP, G0 = 1e7, 1e-15                     # tap resistor; G0: other hole generation (BTBT/thermal), off-state scale
NA_L, ND_ISL, NSRH, TAU0_SI = 6e17, 1e20, 5e16, 1e-8
TAU_B = TAU0_SI / (1 + NA_L / NSRH)                        # 7.7e-10 s
C_B = 3.45e-13 / 20e-7 * (0.165e-4 * 0.5e-4)               # C_ox x left-body area (165 nm x 0.5 um)
R_REC = TAU_B / C_B
MU_P = 45.0                                                # hole mobility in 1e20 n+ (Masetti / ATLAS conmob table)
LP = lambda tau_isl: np.sqrt(VT * MU_P * tau_isl / (1 + ND_ISL / NSRH)) * 1e7      # nm
RUNS = [('ISLW015', '1030_islw', 15, 1e-8), ('NOKILL_TE8_XS60', '1010_sink', 30, 1e-8), ('ISLW035', '1103_third', 35, 1e-8),
        ('ISLW040', '1103_third', 40, 1e-8), ('ISLW045', '1030_islw', 45, 1e-8), ('ISLW060', '1030_islw', 60, 1e-8),
        ('ISLW090', '1030_islw', 90, 1e-8), ('ISLW120', '1030_islw', 120, 1e-8), ('ISLW200', '1030_islw', 200, 1e-8),
        ('ISL_TAU3em9_XS60', '1029_isltau', 30, 3e-9), ('ISL_TAU1em10_XS60', '1029_isltau', 30, 1e-10),
        ('DDS_TE8_XS60', '1007_ddsplit', 30, 1e-12), ('ISLW120_KILL', '1030_islw', 120, 1e-12)]


def M_of(V, I, VBR, n, Rl):
    x = np.clip((V - I * Rl) / VBR, 0, 0.999999); return 1 / (1 - x ** n)


def inv_beta(I, b0, kr, nr, IKF):
    qb = 0.5 * (1 + np.sqrt(1 + 4 * I / IKF)); return qb / b0 + kr * (I / 1e-6) ** (-(1 - 1 / nr))


def curve(pL, pR, eta, I=np.logspace(-15, -1.3, 1500)):
    """V_I(I_L) from the left-body balance (bisection), V_D = V_I + V_R(I_D)"""
    VBR, n, Rl, b0, kr, nr, IKF = pL
    loss = I * inv_beta(I, b0, kr, nr, IKF)
    h = lambda V: (M_of(V, I, VBR, n, Rl) - 1) * I + eta(I + V / RTAP) * (I + V / RTAP) + G0 - loss
    lo, hi = np.zeros_like(I), np.full_like(I, VBR + I * Rl)
    ok = (h(lo) < 0) & (h(hi * 0.999999) > 0)
    for _ in range(60):
        mid = 0.5 * (lo + hi); pos = h(mid) > 0; hi = np.where(pos, mid, hi); lo = np.where(pos, lo, mid)
    V = np.where(ok, 0.5 * (lo + hi), np.nan); ID = I + V / RTAP
    VBRr, nr, Rr, b0r = pR
    MR = 1 + inv_beta(ID, b0r, kr, nr, IKF)
    VR = VBRr * (1 - 1 / MR) ** (1 / nr) + ID * Rr
    return I, V, ID, V + VR


def sweeps(I, VD, ID):
    g = np.isfinite(VD); I, VD, ID = I[g], VD[g], ID[g]
    up = VD >= np.maximum.accumulate(VD) - 1e-9; dn = VD <= np.minimum.accumulate(VD[::-1])[::-1] + 1e-9
    def gaps(ix, lo, hi):
        d = np.diff(np.log10(ID[ix])); m = (ID[ix][:-1] > lo) & (ID[ix][:-1] < hi); d = np.where(m, d, 0); j = int(np.argmax(d)) if len(d) else 0
        return (j, d[j]) if len(d) and d[j] > 0.15 else (None, 0.0)
    iu, idn = np.where(up)[0], np.where(dn)[0]
    j2, a2 = gaps(iu, 5e-8, 1e-6); jd, ad = gaps(idn, 5e-8, 1e-6); j3, a3 = gaps(iu, 1e-4, 1e-1)
    return dict(I=I, VD=VD, ID=ID, up=up, dn=dn, von=VD[iu[j2]] if j2 is not None else np.nan, jump=a2,
                voff=VD[idn[jd + 1]] if jd is not None else np.nan, v3=VD[iu[j3]] if j3 is not None else np.nan, j3=a3)


def tcad(run, d):
    fn = os.path.join(R, d, run + '.log_tr.log'); M, v, Id, Is, It, Vt = load_cols(fn); k = int(np.argmax(v))
    eu, ed = analyse(fn)[:2]; lu = [e for e in eu if e[1] == 'left']; ld = [e for e in ed if e[1] == 'left']
    x, I = v[:k + 1], np.abs(Id[:k + 1]); m = (x > 2.9) & (x < 4.2) & (I > 1e-4); xs, l = x[m], np.log10(I[m]); j3, v3 = 0.0, np.nan
    for i in range(len(xs)):
        jj = np.where((xs >= xs[i]) & (xs <= xs[i] + 0.001))[0]; dd = l[jj].max() - l[i]
        if dd > j3: j3, v3 = dd, xs[i]
    return dict(v=v, Id=np.abs(Id), Is=np.abs(Is), Vt=Vt, k=k, von=lu[0][0] if lu else np.nan, jump=lu[0][2] if lu else 0.0,
                voff=ld[0][0] if ld else np.nan, j3=j3 if j3 > 0.05 else 0.0, v3=v3 if j3 > 0.05 else np.nan)


T = {run: tcad(run, d) for run, d, w, t in RUNS}

# ---------------- fit on the killed W 30 nm device only ----------------
K = T['DDS_TE8_XS60']; k = K['k']
onL = (K['Is'] > 1e-6); onL[:k] = False                                            # left on-branch, down sweep
onR = (K['Id'] > 1e-7) & (K['v'] > 1.6)                                            # right STL on (states II, III)
IL_on, VI_on = K['Is'][onL], K['Vt'][onL]; ID_R, VR_R = K['Id'][onR], (K['v'] - K['Vt'])[onR]
eta0 = lambda ID: np.zeros_like(ID)


def resid(p):
    pL, pR = p[:7], p[7:]
    pL = [pL[0], pL[1], pL[2], 10 ** pL[3], 10 ** pL[4], pL[5], 10 ** pL[6]]
    VBR, n, Rl, b0, kr, nr, IKF = pL
    r1 = np.log(M_of(VI_on, IL_on, VBR, n, Rl) - 1) - np.log(inv_beta(IL_on, b0, kr, nr, IKF))
    MR = 1 + inv_beta(ID_R, 10 ** pR[3], kr, nr, IKF); VRm = pR[0] * (1 - 1 / MR) ** (1 / pR[1]) + ID_R * pR[2]
    I, V, ID, VD = curve(pL, [pR[0], pR[1], pR[2], 10 ** pR[3]], eta0, I=np.logspace(-15, -1.3, 500)); s = sweeps(I, VD, ID)
    pen = [np.nan_to_num(s['von'] - K['von'], nan=3.0), np.nan_to_num(s['voff'] - K['voff'], nan=3.0)]
    return np.concatenate([r1[::max(1, len(r1) // 60)], (VRm - VR_R)[::max(1, len(VR_R) // 60)] / 0.1, np.array(pen) / 0.05])


p0 = [4.0, 4.0, 20.0, 1.3, -1.5, 1.4, -3.0, 3.5, 4.0, 20.0, 1.0]
lb = [2.0, 1.0, 0.0, -1.0, -4.0, 1.0, -7.0, 1.5, 1.0, 0.0, -1.0]; ub = [12.0, 12.0, 500.0, 3.0, 0.0, 3.0, 0.0, 12.0, 12.0, 500.0, 3.0]
fit = least_squares(resid, p0, bounds=(lb, ub), diff_step=1e-3, max_nfev=400)
p = fit.x; PL = [p[0], p[1], p[2], 10 ** p[3], 10 ** p[4], p[5], 10 ** p[6]]; PR = [p[7], p[8], p[9], 10 ** p[10]]

# ---------------- gamma from one coupled run (ISLW120, state II) ----------------
B = [l.split() for l in open(os.path.join(R, '1103_model', 'balance.dat')) if not l.startswith('#')]
e120 = np.exp(np.mean([np.log(float(r[16])) for r in B if r[-1] == 'ISLW120' and r[4] == 'up' and float(r[8]) < 1e-7]))
GAMMA = e120 * np.sinh(120 / LP(1e-8))
eta_of = lambda W, tau: (lambda ID: np.full_like(ID, GAMMA / np.sinh(W / LP(tau))))

lines, Mo = [], {}
for run, d, w, tau in RUNS:
    I, V, ID, VD = curve(PL, PR, eta_of(w, tau)); Mo[run] = sweeps(I, VD, ID); t = T[run]
    lines.append('%-18s %4d %7.0e  %8.2e   %5.3f %5.3f   %5.3f %5.3f   %4.1f %4.1f   %5s %5s' % (
        run, w, tau, GAMMA / np.sinh(w / LP(tau)), t['von'], Mo[run]['von'], t['voff'], Mo[run]['voff'], t['jump'], Mo[run]['jump'],
        '%.2f' % t['v3'] if np.isfinite(t['v3']) else '-', '%.2f' % Mo[run]['v3'] if np.isfinite(Mo[run]['v3']) else '-'))
txt = ['# stl_model.py  (fit on DDS_TE8_XS60 only; gamma from ISLW120 state II; all other runs predicted)',
       'physics: L_p(tau_isl 1e-8 s) %.1f nm (D_p %.2f cm2/s, tau_p %.1e s); not used: R_REC = tau_B/C_B = %.2e Ohm' % (LP(1e-8), VT * MU_P, 1e-8 / (1 + ND_ISL / NSRH), R_REC),
       'left : V_BR %.3f V, n %.2f, R_LRS %.1f Ohm, beta_0 %.3g, k_r %.3g, n_r %.2f, I_KF %.3g A' % tuple(PL),
       'right: V_BR %.3f V, n %.2f, R_LRS %.1f Ohm, beta_0 %.3g' % tuple(PR),
       'gamma %.4f  (eta = gamma / sinh(W / L_p)); fit cost %.3g' % (GAMMA, fit.cost),
       '# run                W  tau_isl    eta_II    V_on TCAD model   V_off TCAD model   jump TCAD model   3rd TCAD model  (V_D in V)'] + lines
open(os.path.join(H, 'stl_model.dat'), 'w').write('\n'.join(txt) + '\n'); print('\n'.join(txt))

fig, ax = plt.subplots(3, 5, figsize=(20, 11)); ax = ax.ravel()
for n_, (run, d, w, tau) in enumerate(RUNS):
    t, mo = T[run], Mo[run]; a = ax[n_]; k = t['k']
    a.plot(mo['VD'], mo['ID'], '-', color='0.8', lw=3)
    a.plot(t['v'][:k + 1], t['Id'][:k + 1], 'k-', lw=1, label='TCAD up'); a.plot(t['v'][k:], t['Id'][k:], 'k--', lw=1, label='TCAD down')
    a.plot(mo['VD'][mo['up']], mo['ID'][mo['up']], 'r-', lw=1.3, label='model up'); a.plot(mo['VD'][mo['dn']], mo['ID'][mo['dn']], 'b--', lw=1.3, label='model down')
    a.set_yscale('log'); a.set_ylim(1e-8, 1e-1); a.set_xlim(1.0, 6.0); a.grid(alpha=.3)
    a.set_title(('FIT: ' if run == 'DDS_TE8_XS60' else 'gamma: ' if run == 'ISLW120' else '') + f'{run}  W {w} nm, tau {tau:.0e} s', fontsize=8)
    if n_ == 0: a.legend(fontsize=6, loc='lower right')
a = ax[13]; ws = [w for r_, d_, w, t_ in RUNS if t_ == 1e-8]; rs = [r_ for r_, d_, w, t_ in RUNS if t_ == 1e-8]
for key, mk in (('von', 'o'), ('voff', 's'), ('v3', '^')):
    a.plot(ws, [T[r_][key] for r_ in rs], 'k' + mk + '-', ms=4, label='TCAD ' + key); a.plot(ws, [Mo[r_][key] for r_ in rs], 'r' + mk + '--', ms=4, mfc='w', label='model ' + key)
a.set_xlabel('island width W (nm)'); a.set_ylabel('V_D (V)'); a.legend(fontsize=6); a.grid(alpha=.3)
a = ax[14]; WW = np.linspace(10, 210, 100)
a.semilogy(WW, GAMMA / np.sinh(WW / LP(1e-8)), 'r-', label='gamma / sinh(W/L_p), L_p = %.1f nm (physics)' % LP(1e-8))
E = {}
for r in B:
    if r[4] == 'up' and float(r[8]) < 1e-7 and float(r[13]) > 1e-9: E.setdefault((r[0], int(r[1]), float(r[2])), []).append(float(r[16]))
for kk, v in E.items(): a.semilogy(kk[1], np.exp(np.mean(np.log(v))), {'width': 'ko', 'tau': 'bs', 'killed': 'kx'}[kk[0]], ms=4)
a.semilogy([30], [GAMMA / np.sinh(30 / LP(3e-9))], 'b+', ms=9, label='model tau 3e-9 s')
a.set_xlabel('W (nm)'); a.set_ylabel('eta_II (snapshots: symbols)'); a.legend(fontsize=6); a.grid(alpha=.3)
fig.suptitle('Equivalent-circuit STL model (after Park et al. EDL 2026) with island coupling. Fit: killed W 30 nm only; gamma: ISLW120 state II; rest predicted', fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(H, 'stl_model.png'), dpi=90)
