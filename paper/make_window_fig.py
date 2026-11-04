#!/usr/bin/env python3
"""Paper figure: latch windows (figV_windows), 2 x 3.
(a), (b) representative |I_D|-V_D (up solid, down dashed) of the width and lifetime sweeps; the second-stage window
         (V_LD,2 .. V_LU,2) of each curve is marked by a bracket at the curve's on-current;
(c), (d) secondary data extracted from every run: latch-up / latch-down voltages as hysteresis bands vs island width / lifetime,
         TCAD (symbols + bands, analyse() + third_onset.dat), model (lines, 1103_physics/stl_hybrid.py on a continuous grid);
(e) second-stage hysteresis V_LU,2 - V_LD,2 vs L/W for both knobs;
(f) jump heights of the second and third latches vs island width (TCAD, model; predicted third-jump onset).
The extracted numbers of (c)-(f) are written to paper/fig/figV_windows.dat (cited in the caption).
Output: paper/fig/figV_windows.{pdf,png,dat}"""
import os, sys, runpy, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '..'); O = os.path.join(H, 'fig'); P = os.path.join(R, '1103_physics')
sys.path.insert(0, os.path.join(R, '1007_ddsplit'))
from analyze_ddsplit import analyse, load_cols
G = runpy.run_path(os.path.join(P, 'stl_hybrid.py')); PH = G['PH']
model, eta_of, VR_C, VR_K, m_of, pm, LP = G['model'], G['eta_of'], G['VR_C'], G['VR_K'], G['m_of'], G['pm'], PH['LP']
plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Nimbus Roman', 'Nimbus Roman No9 L', 'Times New Roman', 'DejaVu Serif'],
                     'font.size': 7.5, 'mathtext.fontset': 'stix', 'axes.linewidth': 0.6, 'legend.fontsize': 6, 'legend.framealpha': .9,
                     'legend.handlelength': 1.6, 'xtick.major.size': 2.5, 'ytick.major.size': 2.5})
L8 = LP(1e-8) * 1e7                                                   # nm
RED, GRN, BLU, GRY = '#c0392b', '#2e8b3e', '#2563a8', '0.35'
BAND1, BAND2 = '0.86', '#f4c6bf'


def ev(path):
    eu, ed = analyse(os.path.join(R, path + '.log_tr.log'))[:2]
    g = lambda L, s, k=0: next((e[k] for e in L if e[1] == s), np.nan)
    return dict(u1=g(eu, 'right'), d1=g(ed, 'right'), u2=g(eu, 'left'), d2=g(ed, 'left'), j2=g(eu, 'left', 2))


def iv(path):
    M, v, Id, *_ = load_cols(os.path.join(R, path + '.log_tr.log')); k = int(np.argmax(v))
    return v[:k + 1], np.abs(Id[:k + 1]), v[k:], np.abs(Id[k:])


WR = [(15, '1030_islw/ISLW015'), (30, '1010_sink/NOKILL_TE8_XS60'), (35, '1103_third/ISLW035'), (40, '1103_third/ISLW040'), (45, '1030_islw/ISLW045'),
      (60, '1030_islw/ISLW060'), (90, '1030_islw/ISLW090'), (120, '1030_islw/ISLW120'), (200, '1030_islw/ISLW200')]
TR = [(1e-12, '1007_ddsplit/DDS_TE8_XS60'), (1e-11, '1029_isltau/ISL_TAU1em11_XS60'), (1e-10, '1029_isltau/ISL_TAU1em10_XS60'),
      (1e-9, '1029_isltau/ISL_TAU1em9_XS60'), (3e-9, '1029_isltau/ISL_TAU3em9_XS60'), (1e-8, '1010_sink/NOKILL_TE8_XS60')]
KILL = '1030_islw/ISLW120_KILL'
EW = {w: ev(b) for w, b in WR}; ET = {t: ev(b) for t, b in TR}; EK = ev(KILL)
T3 = [l.split() for l in open(os.path.join(R, '1103_model', 'third_onset.dat')) if not l.startswith('#')]
J3 = {int(s[0]): (float(s[2]) if s[2] != '-' else np.nan) for s in T3}; J3a = {int(s[0]): float(s[1]) for s in T3}


def fold(W, tau):
    mo = model(W, tau); VR = VR_K if tau < 1e-11 else VR_C
    iu = np.where(mo['up'])[0]; ID = mo['ID'][iu]; d = np.diff(np.log10(ID)); d = np.where((ID[:-1] > 5e-8) & (ID[:-1] < 1e-6), d, 0)
    if not len(d) or d.max() < 0.1: return mo, np.nan
    j = iu[int(np.argmax(d))]; I, IDj = mo['I'][j], mo['ID'][j]; V = mo['VD'][j] - VR(IDj)
    gen_ii = m_of(V, pm) * I; gen_c = eta_of(W, tau)(np.array([IDj]))[0] * IDj
    return mo, gen_c / (gen_ii + gen_c)


Wg = np.array([12, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80, 90, 100, 110, 120, 140, 160, 180, 200, 220])
MW = [fold(w, 1e-8) for w in Wg]
Tg = np.geomspace(1e-9, 1e-8, 9); MT = [fold(30, t) for t in Tg]

fig, ax = plt.subplots(2, 3, figsize=(7.16, 4.55)); ax = ax.ravel()
def tag(a, s): a.text(-0.2, 1.04, s, transform=a.transAxes, fontsize=9, weight='bold')


def iv_panel(a, runs, title, bracket):
    """runs: (label, path, colour, events). Symbols on each curve: V_LU,2 (filled, up sweep) and V_LD,2 (open, down sweep), as in (c), (d).
    bracket: (events, label) of one run whose second-stage window is drawn below the curves."""
    for lab, p, c, e in runs:
        vu, iu_, vd, id_ = iv(p)
        a.semilogy(vu, iu_, '-', color=c, lw=1.0, label=lab); a.semilogy(vd, id_, '--', color=c, lw=0.8)
        if np.isfinite(e['u2']): a.plot(e['u2'], np.interp(e['u2'] - 0.01, vu, iu_), 'o', color=c, ms=3.8, mec='w', mew=.4, zorder=5)
        if np.isfinite(e['d2']): a.plot(e['d2'], np.interp(e['d2'] + 0.01, vd[::-1], id_[::-1]), 'o', color=c, mfc='w', ms=3.8, zorder=5)
    e, lab = bracket; y = 3e-11
    a.annotate('', xy=(e['d2'], y), xytext=(e['u2'], y), arrowprops=dict(arrowstyle='|-|', color='k', lw=.8, mutation_scale=2.5))
    a.text(0.5 * (e['u2'] + e['d2']), y * 3, lab, ha='center', va='bottom', fontsize=6)
    a.set_xlabel(r'$V_D$ (V)'); a.set_ylabel(r'$|I_D|$ (A)'); a.set_xlim(0, 5.2); a.set_ylim(1e-13, 1e-1); a.grid(alpha=.25)
    a.set_title(title, fontsize=7, pad=3)
    a.legend(loc='upper left', labelspacing=.2, borderpad=.3, handlelength=1.4, fontsize=5.8)


# (a) I-V, width sweep (tau 1e-8 s) + killed 120 nm
cw = plt.get_cmap('Reds')(np.linspace(0.45, 0.95, 4))
iv_panel(ax[0], [(f'{w} nm', b, c, EW[w]) for (w, b), c in zip([WR[1], WR[5], WR[7], WR[8]], cw)] + [('120 nm, killed', KILL, 'k', EK)],
         r'width sweep, $\tau_{0,isl}=10^{-8}$ s', (EW[200], r'2nd window, 200 nm'))
tag(ax[0], '(a)')
# (b) I-V, lifetime sweep (W 30 nm)
cb = plt.get_cmap('Blues')(np.linspace(0.4, 0.95, 4))
iv_panel(ax[1], [(lab, b, c, ET[t]) for (lab, (t, b)), c in zip([('1 ps (killed)', TR[0]), ('1 ns (up only)', TR[3]), ('3 ns', TR[4]), ('10 ns', TR[5])], cb)],
         r'lifetime sweep, $W_{IS}=30$ nm', (ET[1e-12], r'2nd window, 1 ps (killed)'))
tag(ax[1], '(b)')


def band_panel(a, x, E, xs, logx):
    u1, d1 = np.array([E[k]['u1'] for k in x]), np.array([E[k]['d1'] for k in x])
    u2, d2 = np.array([E[k]['u2'] for k in x]), np.array([E[k]['d2'] for k in x])
    pl = a.semilogx if logx else a.plot
    a.fill_between(xs, d1, u1, color=BAND1, lw=0); m = np.isfinite(u2) & np.isfinite(d2)
    a.fill_between(xs[m], d2[m], u2[m], color=BAND2, lw=0)
    pl(xs, u1, '-^', color=GRY, ms=3.5, lw=.6, label=r'$V_{LU,1}$'); pl(xs, d1, '-v', color=GRY, mfc='w', ms=3.5, lw=.6, label=r'$V_{LD,1}$')
    pl(xs, u2, '-o', color=RED, ms=3.8, lw=.6, label=r'$V_{LU,2}$'); pl(xs, d2, '-o', color=RED, mfc='w', ms=3.8, lw=.6, label=r'$V_{LD,2}$')
    return u2, d2


# (c) window vs W
a = ax[2]; w = np.array([x for x, b in WR], float)
band_panel(a, [x for x, b in WR], EW, w, False)
a.plot([15, 15], [1.86, 2.0], color=RED, lw=3, alpha=.5, solid_capstyle='butt')
a.plot(w, [J3.get(int(x), np.nan) for x in w], 'D', color=GRN, ms=3.5, label=r'$V_{3}$ (3rd jump)')
a.plot(Wg, [mo['von'] for mo, f in MW], '-', color=RED, lw=1.3, alpha=.55, label='model')
a.plot(Wg, [mo['voff'] for mo, f in MW], '--', color=RED, lw=1.3, alpha=.55)
a.axhline(EK['u2'], color='k', lw=.6); a.axhline(EK['d2'], color='k', lw=.6, ls='--')
a.text(10, EK['u2'] - 0.06, r'killed: $V_{LU,2}$', fontsize=6, va='top'); a.text(10, EK['d2'] + 0.06, r'killed: $V_{LD,2}$', fontsize=6)
a.text(150, 1.22, '1st window', fontsize=6, ha='center', va='center', color='0.25'); a.text(172, 2.75, '2nd\nwindow', fontsize=6, ha='center', color=RED)
a.set_xlabel(r'island width $W_{IS}$ (nm)'); a.set_ylabel(r'latch voltage $V_D$ (V)'); a.set_ylim(0.9, 5.75); a.set_xlim(5, 212)
a.legend(loc='upper left', ncol=3, columnspacing=.6, handletextpad=.3, labelspacing=.2, fontsize=5.6, borderpad=.3)
a.grid(alpha=.25); tag(a, '(c)')
# (d) window vs tau
a = ax[3]; t = np.array([x for x, b in TR])
band_panel(a, [x for x, b in TR], ET, t, True)
a.semilogx(Tg, [mo['von'] for mo, f in MT], '-', color=RED, lw=1.3, alpha=.55); a.semilogx(Tg, [mo['voff'] for mo, f in MT], '--', color=RED, lw=1.3, alpha=.55)
a.text(1e-11, 3.65, 'decoupled\n(series pair)', fontsize=6, ha='center', color=RED); a.text(1e-11, 1.65, '1st window', fontsize=6, ha='center', color='0.25')
a.text(6e-9, 2.65, 'model', fontsize=6, color=RED, ha='right')
a.set_xlabel(r'island lifetime $\tau_{0,isl}$ (s), $W_{IS}=30$ nm'); a.set_ylabel(r'latch voltage $V_D$ (V)'); a.set_ylim(0.9, 5.75)
a.grid(alpha=.25, which='major'); tag(a, '(d)')
sec = a.secondary_xaxis('top', functions=(lambda x: L8 * np.sqrt(np.maximum(x, 1e-15) / 1e-8) / 30, lambda r: 1e-8 * (r * 30 / L8) ** 2))
sec.set_xlabel(r'$L/W_{IS}$', fontsize=7, labelpad=1); sec.tick_params(labelsize=6)
# (e) hysteresis vs L/W
a = ax[4]
rw = L8 / w; hw = np.array([EW[x]['u2'] - EW[x]['d2'] if np.isfinite(EW[x]['u2']) else 0.0 for x, b in WR])
rt = np.array([L8 * np.sqrt(x / 1e-8) / 30 for x in t]); ht = np.array([ET[x]['u2'] - ET[x]['d2'] for x in t])
hm = np.array([(mo['von'] - mo['voff']) if np.isfinite(mo['von']) and np.isfinite(mo['voff']) else np.nan for mo, f in MW])
a.semilogx(L8 / Wg, hm, '-', color=RED, lw=1.3, alpha=.55, label='model, width')
a.semilogx(L8 * np.sqrt(Tg / 1e-8) / 30, [(mo['von'] - mo['voff']) if np.isfinite(mo['von']) else 0.0 for mo, f in MT], '-', color=BLU, lw=1.3, alpha=.55, label='model, lifetime')
a.semilogx(rw, hw, 'o', color=RED, ms=4, label='TCAD, width'); a.semilogx(rt, ht, 's', color=BLU, mfc='w', ms=4, label='TCAD, lifetime')
a.axvspan(1e-3, 0.08, color='0.93', lw=0); a.text(0.019, 1.6, 'decoupled\n(series pair)', fontsize=6, ha='center')
a.set_xlim(4e-3, 2.5); a.set_ylim(-0.1, 2.6)
a.set_xlabel(r'coupling $L/W_{IS}$'); a.set_ylabel(r'2nd hysteresis $V_{LU,2}-V_{LD,2}$ (V)')
a.legend(loc='lower left', labelspacing=.2, fontsize=5.6, borderpad=.3); a.grid(alpha=.25, which='major'); tag(a, '(e)')
# (f) jump heights vs W
a = ax[5]
j2 = np.array([EW[x]['j2'] if np.isfinite(EW[x]['j2']) else 0.0 for x, b in WR]); j3 = np.array([J3a.get(int(x), 0.0) for x in w])
a.axvspan(40, 42.5, color=GRN, alpha=.2, lw=0, label='predicted 3rd-jump onset')
a.plot(Wg, [mo['jump'] if np.isfinite(mo['von']) else np.nan for mo, f in MW], '-', color=RED, lw=1.3, alpha=.55, label='2nd jump, model')
a.plot(w, j2, '-o', color=RED, ms=4, lw=.6, label='2nd jump, TCAD'); a.plot(w, j3, '-D', color=GRN, ms=3.5, lw=.6, label='3rd jump, TCAD')
a.axhline(EK['j2'], color='k', lw=.6, ls='--'); a.text(208, EK['j2'] + 0.08, 'killed', fontsize=6, ha='right')
a.set_xlabel(r'island width $W_{IS}$ (nm)'); a.set_ylabel(r'jump height (decades of $I_D$)'); a.set_ylim(-0.15, 4.6); a.set_xlim(5, 212)
a.legend(loc='upper left', labelspacing=.2, fontsize=5.6, borderpad=.3); a.grid(alpha=.25); tag(a, '(f)')
fig.tight_layout(w_pad=.8, h_pad=.6); [fig.savefig(os.path.join(O, 'figV_windows.' + e), dpi=220) for e in ('pdf', 'png')]

# secondary data of (c)-(f)
with open(os.path.join(O, 'figV_windows.dat'), 'w') as f:
    f.write('# figV_windows secondary data (paper/make_window_fig.py). V in volts; jumps in decades of |I_D|; L/W with L = 21 nm sqrt(tau/1e-8 s)\n')
    f.write('# knob  W_nm  tau_s  L/W  V_LU1  V_LD1  V_LU2  V_LD2  hyst2  jump2  jump3  V3  source_log\n')
    rows = [('width', x, 1e-8, EW[x], J3a.get(x, 0.0), J3.get(x, np.nan), b) for x, b in WR] + \
           [('tau', 30, x, ET[x], np.nan, np.nan, b) for x, b in TR] + [('killed', 120, 1e-12, EK, np.nan, np.nan, KILL)]
    for k, W, tau, e, j3_, v3, b in rows:
        f.write(f"{k:6s} {W:4d} {tau:8.1e} {L8 * np.sqrt(tau / 1e-8) / W:7.4f} {e['u1']:6.3f} {e['d1']:6.3f} {e['u2']:6.3f} {e['d2']:6.3f} "
                f"{e['u2'] - e['d2']:6.3f} {e['j2']:5.2f} {j3_:5.2f} {v3:6.3f}  {b}.log_tr.log\n")
