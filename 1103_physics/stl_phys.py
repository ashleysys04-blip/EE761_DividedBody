#!/usr/bin/env python3
"""Physics-based equivalent-circuit model of the divided-body STL (structure after Park et al., EDL 2026), version 2.

Each floating body is a hole balance ("hole account"):  holes in = holes out
  left body :  (M_L - 1) I  +  eta I_D  +  G0  =  I / beta_L(I)           I = left-STL electron current, V_I = island potential
  right body:  (M_R - 1) I_D            =  I_D / beta_R(I_D)              (right STL latched in states II, III)
Pieces (no TCAD output used except the killed reference fit):
  M - 1   : Selberherr impact ionization (ATLAS coefficients an = 7.03e5 /cm, bn = 1.231e6 V/cm) integrated over the field of an
            abrupt n+/p junction with the body doping (6e17 left, 7e17 right); junction voltage = V - I R_LRS (V_bi - V_BS ~ 0 in the
            latched, high-injection body)
  1/beta  : back-injection into the emitter + recombination:  1/beta = gamma(I) + k_r (I / 1 uA)^-(1 - 1/n_r)
            gamma(I) = gamma_0 q_b(I) / (1 + gamma_0 q_b(I) / gamma_inf)   (junction law, Webster high injection, plasma limit)
            q_b = (1 + sqrt(1 + 4 I / I_KF)) / 2,   gamma_inf = mu_p / (mu_n + mu_p)  (holes drift with electrons in the plasma)
  eta     : holes the right STL back-injects into the island that reach the left body
            eta = gamma_R(I_D) T(W, I_D),  gamma_R = holes injected into the island per drain electron, the same physical form
            gamma_R = g_R q_b,R / (1 + g_R q_b,R / gamma_inf); W-independent (injection.py), its 2 parameters (g_R, I_KF,R)
            fitted on the W 30 nm run (NOKILL_TE8_XS60) injection only
            T = drift-diffusion transmission of the n+ island: L = L_p / sqrt(1 + L_p/t_si) (bulk L_p = sqrt(D_p tau_p),
                tau_p = tau_0 / (1 + N_D / N_SRH) (consrh), plus hole loss into the n+ via under the island),
                drift length L_E = mu_p E tau_p, E = J_D / (q N_D mu_n); T -> 1/cosh(W/L_p) at low current
Circuit:  I_D = I + V_I / R_tap,  V_D = V_I + V_R(I_D).  For every I the left balance gives V_I (bisection; the left side rises with
V_I); V_D(I) is S-shaped; the up sweep jumps at its local maxima (A_loop = 1, latch-up), the down sweep at its local minima.
Extracted like a Gummel plot from the body hole balance of the snapshots (1103_model/balance.dat, one curve for all runs): beta(I)
(gamma_0, I_KF, k_r, n_r); from the W 30 nm right-junction injection (injection.py): g_R, I_KF,R; terminal fit on the killed
W 30 nm device (DDS_TE8_XS60) only: R_LRS,L, R_LRS,R.
Every coupled run (W 15-200 nm, island tau 3e-9, 1e-10 s) and the killed 120 nm device are predictions.
Output: stl_phys.dat, stl_phys.png"""
import os, sys, numpy as np, matplotlib
from scipy.optimize import least_squares
matplotlib.use('Agg'); import matplotlib.pyplot as plt
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '..')
sys.path.insert(0, os.path.join(R, '1007_ddsplit'))
from analyze_ddsplit import load_cols, analyse

Q, EPS, VT = 1.602e-19, 11.7 * 8.854e-14, 0.02585
AN, BN = 7.03e5, 1.231e6
NA_L, NA_R, L_L, L_R = 6e17, 7e17, 165.0, 105.0
ND, NSRH, MUN, MUP = 1e20, 5e16, 90.0, 52.0                      # mu_p: the simulator's hole mobility in the 1e20 island (D_p = 1.35 cm2/s, extracted from J_p / grad p)
WDEV, TSI, RTAP, G0 = 0.5e-4, 50e-7, 1e7, 1e-15
GINF = MUP / (MUN + MUP)
S_RL = NA_R * L_R / (NA_L * L_L)

_u = np.linspace(1e-4, 1, 300)
def M1_table(NA):
    V = np.linspace(0, 12, 1201); Em = np.sqrt(2 * Q * NA * np.maximum(V, 1e-6) / EPS); xd = Em * EPS / (Q * NA)
    m = np.array([x * np.trapz(AN * np.exp(-BN / (e * _u)), _u) for e, x in zip(Em, xd)]); return V, m
VL_t, ML_t = M1_table(NA_L); VR_t, MR_t = M1_table(NA_R)
M1L = lambda V: np.interp(V, VL_t, ML_t)
VR_of_M1 = lambda m: np.interp(m, MR_t, VR_t)                       # inverse (M-1 rises with V)


def LP(tau):
    """lateral hole decay length in the island film: bulk L_p = sqrt(D_p tau_p) plus the loss into the n+ via (neck) under the island,
    a second sink of depth >> L_p below the t_si film: 1/tau_eff = (1/tau_p)(1 + L_p/t_si)  ->  L = L_p / sqrt(1 + L_p/t_si)"""
    Lp = np.sqrt(VT * MUP * tau / (1 + ND / NSRH)); return Lp / np.sqrt(1 + Lp / TSI)        # cm


def transmission(W_nm, tau, ID):
    """drift-diffusion transmission T = J_p(W) / J_p(0) of an n+ base, p(0) = p0, p(W) = 0 (collected)"""
    Lp = LP(tau); taup = tau / (1 + ND / NSRH); W = W_nm * 1e-7
    E = np.asarray(ID, float) / (WDEV * TSI) / (Q * ND * MUN); LE = MUP * E * taup
    r = np.sqrt(LE ** 2 + 4 * Lp ** 2); s1, s2 = (LE + r) / (2 * Lp ** 2), (LE - r) / (2 * Lp ** 2)
    a = np.exp((s2 - s1) * W); d = 1 - a
    dp0 = (-a * s1 + s2) / d; dpW = (-a * s1 * np.exp(s1 * W) + s2 * np.exp(s2 * W)) / d
    J = lambda pp, dpp: LE * pp - Lp ** 2 * dpp                                         # J_p / (q D/L_p^2 ...) up to a constant
    return J(0.0, dpW) / J(1.0, dp0)


def gamma(I, g0, IKF):
    qb = 0.5 * (1 + np.sqrt(1 + 4 * np.asarray(I, float) / IKF)); x = g0 * qb; return x / (1 + x / GINF)


def inv_beta(I, P):
    g0, IKF, kr, nr = P[:4]; return gamma(I, g0, IKF) + kr * (np.asarray(I, float) / 1e-6) ** (-(1 - 1 / nr))


INJ = np.array([[float(r[3]), float(r[5])] for r in (l.split() for l in open(os.path.join(H, 'injection.dat')) if not l.startswith('#'))
                if int(r[0]) == 30 and float(r[3]) > 1e-8])
GR = least_squares(lambda q: np.log(gamma(INJ[:, 0], 10 ** q[0], 10 ** q[1])) - np.log(INJ[:, 1]), [-1.7, -4.0]).x
GR = [10 ** GR[0], 10 ** GR[1]]


def eta_of(W_nm, tau, P):
    if tau < 1e-11: return lambda ID: np.zeros_like(np.asarray(ID, float))              # killed island: holes recombine
    return lambda ID: gamma(ID, *GR) * transmission(W_nm, tau, ID)


def curve(P, eta, I=np.logspace(-15, -1.3, 1400)):
    RL, RR = P[4], P[5]
    loss = I * inv_beta(I, P)
    h = lambda V: M1L(np.maximum(V - I * RL, 0)) * I + eta(I + V / RTAP) * (I + V / RTAP) + G0 - loss
    lo, hi = np.zeros_like(I), np.full_like(I, 11.0)
    ok = (h(lo) < 0) & (h(hi) > 0)
    for _ in range(55):
        mid = 0.5 * (lo + hi); pos = h(mid) > 0; hi = np.where(pos, mid, hi); lo = np.where(pos, lo, mid)
    V = np.where(ok, 0.5 * (lo + hi), np.nan); ID = I + V / RTAP
    VRv = VR_of_M1(inv_beta(ID, P)) + ID * RR
    return I, V, ID, V + VRv


def sweeps(I, VD, ID):
    g = np.isfinite(VD); I, VD, ID = I[g], VD[g], ID[g]
    up = VD >= np.maximum.accumulate(VD) - 1e-9; dn = VD <= np.minimum.accumulate(VD[::-1])[::-1] + 1e-9
    def gap(ix, lo, hi):
        d = np.diff(np.log10(ID[ix])); d = np.where((ID[ix][:-1] > lo) & (ID[ix][:-1] < hi), d, 0); j = int(np.argmax(d)) if len(d) else 0
        return (j, d[j]) if len(d) and d[j] > 0.15 else (None, 0.0)
    iu, idn = np.where(up)[0], np.where(dn)[0]
    j2, a2 = gap(iu, 5e-8, 2e-6); jd, ad = gap(idn, 5e-8, 2e-6); j3, a3 = gap(iu, 1e-4, 1e-1)
    return dict(I=I, VD=VD, ID=ID, up=up, dn=dn, von=VD[iu[j2]] if j2 is not None else np.nan, jump=a2,
                voff=VD[idn[jd + 1]] if jd is not None else np.nan, v3=VD[iu[j3]] if j3 is not None else np.nan, j3=a3)


RUNS = [('ISLW015', '1030_islw', 15, 1e-8), ('NOKILL_TE8_XS60', '1010_sink', 30, 1e-8), ('ISLW035', '1103_third', 35, 1e-8),
        ('ISLW040', '1103_third', 40, 1e-8), ('ISLW045', '1030_islw', 45, 1e-8), ('ISLW060', '1030_islw', 60, 1e-8),
        ('ISLW090', '1030_islw', 90, 1e-8), ('ISLW120', '1030_islw', 120, 1e-8), ('ISLW200', '1030_islw', 200, 1e-8),
        ('ISL_TAU3em9_XS60', '1029_isltau', 30, 3e-9), ('ISL_TAU1em10_XS60', '1029_isltau', 30, 1e-10),
        ('DDS_TE8_XS60', '1007_ddsplit', 30, 1e-12), ('ISLW120_KILL', '1030_islw', 120, 1e-12)]


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
K = T['DDS_TE8_XS60']; k = K['k']
onL = K['Is'] > 1e-6; onL[:k] = False
IL_on, VI_on = K['Is'][onL], K['Vt'][onL]
onR = (K['Id'] > 1e-7) & (K['v'] > 1.6); ID_R, VR_R = K['Id'][onR], (K['v'] - K['Vt'])[onR]
sub = lambda a: a[::max(1, len(a) // 60)]
IL_on, VI_on, ID_R, VR_R = sub(IL_on), sub(VI_on), sub(ID_R), sub(VR_R)


BAL = [l.split() for l in open(os.path.join(R, '1103_model', 'balance.dat')) if not l.startswith('#')]
GI = np.array([[float(r[8]), float(r[15])] for r in BAL if float(r[8]) > 1e-12 and abs(float(r[17])) < 0.3 and float(r[15]) > 0])
BF = least_squares(lambda q: np.log(inv_beta(GI[:, 0], [10 ** q[0], 10 ** q[1], 10 ** q[2], q[3]])) - np.log(GI[:, 1]),
                   [-1.5, -3.0, -1.5, 1.4], bounds=([-3.5, -9, -4, 1.0], [-0.3, 0, 0, 3.0])).x
BETA = [10 ** BF[0], 10 ** BF[1], 10 ** BF[2], BF[3]]


def unpack(p): return BETA + [p[0], p[1]]


def resid(p):
    P = unpack(p)
    r1 = np.log(M1L(np.maximum(VI_on - IL_on * P[4], 0)) + 1e-12) - np.log(inv_beta(IL_on, P))
    r2 = (VR_of_M1(inv_beta(ID_R, P)) + ID_R * P[5] - VR_R) / 0.1
    I, V, ID, VD = curve(P, lambda x: np.zeros_like(x), I=np.logspace(-15, -1.3, 500)); s = sweeps(I, VD, ID)
    pen = np.array([np.nan_to_num(s['von'] - K['von'], nan=3.0), np.nan_to_num(s['voff'] - K['voff'], nan=3.0)]) / 0.05
    return np.concatenate([r1, r2, pen])


fit = least_squares(resid, [10.0, 50.0], bounds=([0, 0], [500, 1000]), diff_step=1e-3, max_nfev=200)
P = unpack(fit.x)

Mo, lines = {}, []
for run, d, w, tau in RUNS:
    I, V, ID, VD = curve(P, eta_of(w, tau, P)); Mo[run] = sweeps(I, VD, ID); t = T[run]
    f = lambda x: '%.2f' % x if np.isfinite(x) else '  - '
    lines.append('%-18s %4d %7.0e  %8.2e   %s %s   %s %s   %4.1f %4.1f   %s %s' % (run, w, tau, eta_of(w, tau, P)(np.array([1.5e-7]))[0],
                 f(t['von']), f(Mo[run]['von']), f(t['voff']), f(Mo[run]['voff']), t['jump'], Mo[run]['jump'], f(t['v3']), f(Mo[run]['v3'])))
txt = ['# stl_phys.py (fit: DDS_TE8_XS60 only; all other runs predicted)',
       'physics: L_p(1e-8 s) %.1f nm, gamma_inf %.3f, Selberherr an %.3g bn %.4g' % (LP(1e-8) * 1e7, GINF, AN, BN),
       'injection (W 30 nm): g_R %.4f, I_KF,R %.3g A' % tuple(GR),
       'fitted : gamma_0 %.4f, I_KF %.3g A, k_r %.4f, n_r %.2f, R_LRS,L %.1f Ohm, R_LRS,R %.1f Ohm  (cost %.3g)' % (*P, fit.cost),
       '# run                W  tau_isl  eta(0.15uA)  V_on TCAD model  V_off TCAD model  jump TCAD model  3rd TCAD model  (V_D)'] + lines
open(os.path.join(H, 'stl_phys.dat'), 'w').write('\n'.join(txt) + '\n'); print('\n'.join(txt))

fig, ax = plt.subplots(3, 5, figsize=(20, 11)); ax = ax.ravel()
for n_, (run, d, w, tau) in enumerate(RUNS):
    t, mo = T[run], Mo[run]; a = ax[n_]; kk = t['k']
    a.plot(mo['VD'], mo['ID'], '-', color='0.8', lw=3)
    a.plot(t['v'][:kk + 1], t['Id'][:kk + 1], 'k-', lw=1, label='TCAD up'); a.plot(t['v'][kk:], t['Id'][kk:], 'k--', lw=1, label='TCAD down')
    a.plot(mo['VD'][mo['up']], mo['ID'][mo['up']], 'r-', lw=1.3, label='model up'); a.plot(mo['VD'][mo['dn']], mo['ID'][mo['dn']], 'b--', lw=1.3, label='model down')
    a.set_yscale('log'); a.set_ylim(1e-8, 1e-1); a.set_xlim(1.0, 6.0); a.grid(alpha=.3)
    a.set_title(('FIT: ' if run == 'DDS_TE8_XS60' else '') + f'{run}  W {w} nm, tau {tau:.0e} s', fontsize=8)
    if n_ == 0: a.legend(fontsize=6, loc='lower right')
a = ax[13]; rs = [(r_, w) for r_, d_, w, t_ in RUNS if t_ == 1e-8]
for key, mk in (('von', 'o'), ('voff', 's'), ('v3', '^')):
    a.plot([w for r_, w in rs], [T[r_][key] for r_, w in rs], 'k' + mk + '-', ms=4, label='TCAD ' + key)
    a.plot([w for r_, w in rs], [Mo[r_][key] for r_, w in rs], 'r' + mk + '--', ms=4, mfc='w', label='model ' + key)
a.set_xlabel('W (nm)'); a.set_ylabel('V_D (V)'); a.legend(fontsize=6); a.grid(alpha=.3)
a = ax[14]; II = np.logspace(-8, -1.2, 100)
for w, c in ((15, 'C0'), (30, 'C1'), (60, 'C2'), (120, 'C3')):
    a.loglog(II, eta_of(w, 1e-8, P)(II), '-', color=c, label=f'model eta W {w}')
B = [l.split() for l in open(os.path.join(R, '1103_model', 'balance.dat')) if not l.startswith('#')]
for w, c in ((15, 'C0'), (30, 'C1'), (60, 'C2'), (120, 'C3')):
    rr = [r for r in B if r[0] == 'width' and int(r[1]) == w and float(r[13]) > 1e-8]
    a.loglog([float(r[13]) for r in rr], [max(float(r[16]), 1e-7) for r in rr], 'o', color=c, ms=3)
a.set_xlabel('I_D (A)'); a.set_ylabel('eta (symbols: snapshots)'); a.legend(fontsize=6); a.grid(alpha=.3, which='both')
fig.suptitle('Physics-based two-body STL model v2. beta(I) and gamma_R(I) extracted, R_LRS fitted on killed W 30 nm; all other panels are predictions', fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(H, 'stl_phys.png'), dpi=90)
