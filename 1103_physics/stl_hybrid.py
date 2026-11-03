#!/usr/bin/env python3
"""Hybrid two-body STL model: single-STL properties extracted, the coupling derived.

Left body hole balance (1103_model/model_latch.py):  (M(V) - 1) I + [eta_self(I_D) + eta_c(I_D; W, tau)] I_D + G0 = I / beta(I)
  extracted (single-STL properties, the same for every run):
    M(V) - 1   : impact-ionization holes per electron vs island potential (logistic fit to the snapshot balance, all runs)
    1/beta(I)  : hole loss per electron (Gummel-like extraction from the snapshot balance, all runs)
    eta_self   : the left STL's own impact-ionization holes generated on the island side of its drain junction that return to the
                 body (the "eta" of the killed reference DDS_TE8_XS60, where no hole crosses the island)
    V_R(I_D)   : right-STL on-branch. The island is the right STL's emitter, so its lifetime sets the right STL's back-injection
                 loss: a killed island needs ~0.45 V more right-STL voltage at the same current than a coupled one, while coupled islands
                 of any width give the same on-branch (V_R(0.2 uA) = 0.83-0.90 V for W 15-200 nm). Two references: the killed
                 W 30 nm device (DDS_TE8_XS60) for killed islands, the coupled W 30 nm device (NOKILL_TE8_XS60) for coupled islands
  derived (1103_physics/stl_phys.py; no per-run input):
    eta_c      = gamma_R(I_D) T(W, tau, I_D)
                 gamma_R: holes back-injected by the right STL into the island per drain electron (junction law, Webster, plasma limit
                 mu_p/(mu_n+mu_p)); T: drift-diffusion transmission of the n+ island, L_p = sqrt(D_p tau_p) from consrh, drift by the
                 ohmic field of I_D
Prediction for W 15-200 nm, island tau 3e-9 / 1e-10 s and the killed 120 nm island; turn-on, turn-off, jump, third jump.
Output: stl_hybrid.dat, stl_hybrid.png"""
import os, sys, runpy, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '..')
EM = runpy.run_path(os.path.join(R, '1103_model', 'model_latch.py'))          # extracted M(V), beta(I), tcad()
PH = runpy.run_path(os.path.join(H, 'stl_phys.py'))                          # gamma_R(I), transmission()
m_of, pm, g_of, pg, tcad, eta_tab = EM['m_of'], EM['pm'], EM['g_of'], EM['pg'], EM['tcad'], EM['eta_tab']
gamma, transmission, GR = PH['gamma'], PH['transmission'], PH['GR']
RTAP, G0 = 1e7, 1e-15
VR_K = tcad('DDS_TE8_XS60', '1007_ddsplit')['VR']; VR_C = tcad('NOKILL_TE8_XS60', '1010_sink')['VR']; eta_self = eta_tab('DDS_TE8_XS60')
RUNS = [('ISLW015', '1030_islw', 15, 1e-8), ('NOKILL_TE8_XS60', '1010_sink', 30, 1e-8), ('ISLW035', '1103_third', 35, 1e-8),
        ('ISLW040', '1103_third', 40, 1e-8), ('ISLW045', '1030_islw', 45, 1e-8), ('ISLW060', '1030_islw', 60, 1e-8),
        ('ISLW090', '1030_islw', 90, 1e-8), ('ISLW120', '1030_islw', 120, 1e-8), ('ISLW200', '1030_islw', 200, 1e-8),
        ('ISL_TAU3em9_XS60', '1029_isltau', 30, 3e-9), ('ISL_TAU1em10_XS60', '1029_isltau', 30, 1e-10),
        ('DDS_TE8_XS60', '1007_ddsplit', 30, 1e-12), ('ISLW120_KILL', '1030_islw', 120, 1e-12)]


def eta_of(W, tau):
    if tau < 1e-11: return lambda ID: eta_self(ID)
    return lambda ID: eta_self(ID) + gamma(ID, *GR) * transmission(W, tau, ID)


def model(W, tau):
    et = eta_of(W, tau); VR = VR_K if tau < 1e-11 else VR_C; I = np.logspace(-17, -1.3, 1600)
    h = lambda V: m_of(V, pm) * I + et(I + V / RTAP) * (I + V / RTAP) + G0 - g_of(I, pg) * I
    lo, hi = np.zeros_like(I), np.full_like(I, 8.0)
    for _ in range(50):
        mid = 0.5 * (lo + hi); pos = h(mid) > 0; hi = np.where(pos, mid, hi); lo = np.where(pos, lo, mid)
    V = np.where((h(np.zeros_like(I)) < 0) & (h(np.full_like(I, 8.0)) > 0), 0.5 * (lo + hi), np.nan)
    ID = I + V / RTAP; VD = V + VR(ID); g = np.isfinite(VD); I, V, ID, VD = I[g], V[g], ID[g], VD[g]
    up = VD >= np.maximum.accumulate(VD) - 1e-9; dn = VD <= np.minimum.accumulate(VD[::-1])[::-1] + 1e-9
    def gap(ix, lo_, hi_):
        d = np.diff(np.log10(ID[ix])); d = np.where((ID[ix][:-1] > lo_) & (ID[ix][:-1] < hi_), d, 0); j = int(np.argmax(d)) if len(d) else 0
        return (j, d[j]) if len(d) and d[j] > 0.1 else (None, 0.0)
    iu, idn = np.where(up)[0], np.where(dn)[0]
    j2, a2 = gap(iu, 5e-8, 1e-6); jd, ad = gap(idn, 5e-8, 1e-6); j3, a3 = gap(iu, 1e-4, 1e-1)
    return dict(I=I, VD=VD, ID=ID, up=up, dn=dn, von=VD[iu[j2]] if j2 is not None else np.nan, jump=a2,
                voff=VD[idn[jd + 1]] if jd is not None else np.nan, v3=VD[iu[j3]] if j3 is not None else np.nan, j3=a3)


def third_tcad(t):
    k = t['k']; x, I = t['v'][:k + 1], t['Id'][:k + 1]; m = (x > 2.9) & (x < 4.2) & (I > 1e-4); xs, l = x[m], np.log10(I[m]); j3, v3 = 0.0, np.nan
    for i in range(len(xs)):
        jj = np.where((xs >= xs[i]) & (xs <= xs[i] + 0.001))[0]; dd = l[jj].max() - l[i]
        if dd > j3: j3, v3 = dd, xs[i]
    return (v3, j3) if j3 > 0.05 else (np.nan, 0.0)


T, Mo, lines = {}, {}, []
f = lambda x: '%.2f' % x if np.isfinite(x) else '  - '
for run, d, w, tau in RUNS:
    T[run] = tcad(run, d); T[run]['v3'], T[run]['j3'] = third_tcad(T[run]); Mo[run] = model(w, tau); t, mo = T[run], Mo[run]
    lines.append('%-18s %4d %7.0e   %s %s   %s %s   %4.1f %4.1f   %s/%.2f  %s/%.2f' % (run, w, tau, f(t['von']), f(mo['von']), f(t['voff']), f(mo['voff']),
                 t['jump'], mo['jump'], f(t['v3']), t['j3'], f(mo['v3']), mo['j3']))
txt = ['# stl_hybrid.py: extracted M(V), beta(I), eta_self, V_R (killed / coupled W 30 nm references); derived coupling gamma_R(I) T(W, tau, I)',
       '# run                W  tau_isl   V_on TCAD model   V_off TCAD model   jump TCAD model   3rd TCAD (V/dec)  model (V/dec)'] + lines
open(os.path.join(H, 'stl_hybrid.dat'), 'w').write('\n'.join(txt) + '\n'); print('\n'.join(txt))

fig, ax = plt.subplots(3, 5, figsize=(20, 11)); ax = ax.ravel()
for n_, (run, d, w, tau) in enumerate(RUNS):
    t, mo = T[run], Mo[run]; a = ax[n_]; kk = t['k']
    a.plot(mo['VD'], mo['ID'], '-', color='0.8', lw=3)
    a.plot(t['v'][:kk + 1], t['Id'][:kk + 1], 'k-', lw=1, label='TCAD up'); a.plot(t['v'][kk:], t['Id'][kk:], 'k--', lw=1, label='TCAD down')
    a.plot(mo['VD'][mo['up']], mo['ID'][mo['up']], 'r-', lw=1.3, label='model up'); a.plot(mo['VD'][mo['dn']], mo['ID'][mo['dn']], 'b--', lw=1.3, label='model down')
    a.set_yscale('log'); a.set_ylim(1e-8, 1e-1); a.set_xlim(1.0, 6.0); a.grid(alpha=.3)
    a.set_title(('REFERENCE: ' if run in ('DDS_TE8_XS60', 'NOKILL_TE8_XS60') else '') + f'{run}  W {w} nm, tau {tau:.0e} s', fontsize=8)
    if n_ == 0: a.legend(fontsize=6, loc='lower right')
a = ax[13]; rs = [(r_, w) for r_, d_, w, t_ in RUNS if t_ == 1e-8]
for key, mk in (('von', 'o'), ('voff', 's'), ('v3', '^')):
    a.plot([w for r_, w in rs], [T[r_][key] for r_, w in rs], 'k' + mk + '-', ms=4, label='TCAD ' + key)
    a.plot([w for r_, w in rs], [Mo[r_][key] for r_, w in rs], 'r' + mk + '--', ms=4, mfc='w', label='model ' + key)
a.set_xlabel('W (nm)'); a.set_ylabel('V_D (V)'); a.legend(fontsize=6); a.grid(alpha=.3)
a = ax[14]
a.plot([w for r_, w in rs], [T[r_]['jump'] for r_, w in rs], 'ko-', label='TCAD 2nd jump'); a.plot([w for r_, w in rs], [Mo[r_]['jump'] for r_, w in rs], 'ro--', mfc='w', label='model 2nd jump')
a.plot([w for r_, w in rs], [T[r_]['j3'] for r_, w in rs], 'k^-', label='TCAD 3rd jump'); a.plot([w for r_, w in rs], [Mo[r_]['j3'] for r_, w in rs], 'r^--', mfc='w', label='model 3rd jump')
a.set_xlabel('W (nm)'); a.set_ylabel('jump (decades of I_D)'); a.legend(fontsize=6); a.grid(alpha=.3)
fig.suptitle('Hybrid model: extracted single-STL properties (M, beta, killed reference) + derived island coupling. All coupled runs predicted', fontsize=10)
fig.tight_layout(); fig.savefig(os.path.join(H, 'stl_hybrid.png'), dpi=90)
