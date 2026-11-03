#!/usr/bin/env python3
"""Paper figure for the body hole-balance model (README Step 21): figU_model.
(a) state-II island coupling eta_II vs island width with eta0 exp(-W/L_p) and the lifetime points, (b) universal 1/beta(I),
(c) universal M-1(V), (d)-(e) model vs TCAD |I_D|-V_D, (f) second-latch turn-on / turn-off / jump vs W.
Runs 1103_model/model_latch.py (which also rewrites its own model_fit.dat / model_latch.png). Output: paper/fig/figU_model.{pdf,png}"""
import os, runpy, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '..'); O = os.path.join(H, 'fig')
G = runpy.run_path(os.path.join(R, '1103_model', 'model_latch.py'))
plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Nimbus Roman', 'Nimbus Roman No9 L', 'Times New Roman', 'DejaVu Serif'],
                     'font.size': 7, 'mathtext.fontset': 'stix', 'axes.linewidth': 0.6})
T, Mo, E, LP, ETA0 = G['T'], G['Mo'], G['E'], G['LP'], G['ETA0']
fig, ax = plt.subplots(2, 3, figsize=(7.16, 4.3)); ax = ax.ravel()
def tag(a, s): a.text(-0.2, 1.02, s, transform=a.transAxes, fontsize=8, weight='bold')
a = ax[0]
for k, v in E.items():
    a.semilogy(k[1], v, {'width': 'o', 'tau': 's', 'killed': 'x'}[k[0]], color={'width': 'tab:red', 'tau': 'tab:blue', 'killed': 'k'}[k[0]], ms=4,
               mfc='none' if k[0] == 'tau' else None)
    if k[0] == 'tau': a.annotate(r'$\tau_{0,isl}$ %s s' % ('3e-9' if k[2] > 1e-9 else '1e-10'), (k[1], v), fontsize=5.5, xytext=(5, -7), textcoords='offset points')
WW = np.linspace(0, 210, 50); a.semilogy(WW, ETA0 * np.exp(-WW / LP), 'tab:red', lw=.8, label=r'$\eta_0 e^{-W/L_p}$, $L_p$ = %.0f nm' % LP)
a.semilogy([30], [ETA0 * np.exp(-30 / (LP * np.sqrt(0.3)))], '+', color='tab:blue', ms=8, label=r'predicted, $L_p\sqrt{0.3}$')
a.set_xlabel(r'island width $W_{IS}$ (nm)'); a.set_ylabel(r'$\eta_{II}$ = island holes / $I_D$'); a.legend(fontsize=5.5, loc='upper right'); a.grid(alpha=.3); tag(a, '(a)')
a = ax[1]; II = np.logspace(-12, -1, 200)
a.loglog(G['gI'][:, 0], G['gI'][:, 1], '.', color='tab:red', ms=2.5, label='snapshots, all runs'); a.loglog(II, G['g_of'](II, G['pg']), 'k-', lw=.8, label='fit')
a.set_xlabel(r'left-STL current $|I_S|$ (A)'); a.set_ylabel(r'$1/\beta$'); a.legend(fontsize=5.5); a.grid(alpha=.3, which='both'); tag(a, '(b)')
a = ax[2]; VV = np.linspace(0.5, 3.0, 100)
a.semilogy(G['mV'][:, 0], G['mV'][:, 1], '.', color='tab:red', ms=2.5, label='snapshots, all runs'); a.semilogy(VV, G['m_of'](VV, G['pm']), 'k-', lw=.8, label='fit')
a.set_xlabel('island potential (V)'); a.set_ylabel(r'$M-1$'); a.legend(fontsize=5.5); a.grid(alpha=.3); tag(a, '(c)')
for a, runs, tg in ((ax[3], [('NOKILL_TE8_XS60', 'tab:red', '30 nm'), ('ISLW060', 'tab:orange', '60 nm')], '(d)'),
                    (ax[4], [('ISLW120', 'tab:green', '120 nm'), ('ISLW120_KILL', 'k', '120 nm, killed')], '(e)')):
    for run, c, lab in runs:
        t, mo = T[run], Mo[run]; k = t['k']
        a.plot(t['v'][:k + 1], t['Id'][:k + 1], '-', color=c, lw=.7, label='TCAD ' + lab); a.plot(t['v'][k:], t['Id'][k:], ':', color=c, lw=.7)
        a.plot(mo['VD'][mo['up']], mo['ID'][mo['up']], '-', color=c, lw=2.2, alpha=.35, label='model ' + lab)
        a.plot(mo['VD'][mo['dn']], mo['ID'][mo['dn']], '--', color=c, lw=1.6, alpha=.5)
    a.set_yscale('log'); a.set_ylim(1e-8, 1e-1); a.set_xlim(1.0, 5.5); a.set_xlabel(r'$V_D$ (V)'); a.set_ylabel(r'$|I_D|$ (A)')
    a.legend(fontsize=5.2, loc='lower right'); a.grid(alpha=.3); tag(a, tg)
a = ax[5]; cw = [(r_, w) for r_, d_, w, s in G['RUNS'] if s == 'width']; ws = [w for r_, w in cw]
MV = lambda r_, w, key: Mo[r_][key] if w < 200 else np.nan          # W 200 nm turn-on is outside the model (island > 3 V)
a.plot(ws, [T[r_]['von'] for r_, w in cw], 'ko-', ms=3, lw=.8, label='turn-on, TCAD'); a.plot(ws, [MV(r_, w, 'von') for r_, w in cw], 'ko--', ms=3, lw=.8, mfc='w', label='turn-on, model')
a.plot(ws, [T[r_]['voff'] for r_, w in cw], 'bs-', ms=3, lw=.8, label='turn-off, TCAD'); a.plot(ws, [Mo[r_]['voff'] for r_, w in cw], 'bs--', ms=3, lw=.8, mfc='w', label='turn-off, model')
a.set_xlabel(r'island width $W_{IS}$ (nm)'); a.set_ylabel(r'2nd latch $V_D$ (V)'); a.legend(fontsize=5.2, loc='upper left'); a.grid(alpha=.3); tag(a, '(f)')
b = a.twinx(); b.plot(ws, [T[r_]['jump'] for r_, w in cw], 'g^-', ms=3, lw=.8); b.plot(ws, [MV(r_, w, 'jump') for r_, w in cw], 'g^--', ms=3, lw=.8, mfc='w')
b.set_ylabel('2nd jump (decades), green', color='g')
fig.tight_layout(w_pad=.8); [fig.savefig(os.path.join(O, 'figU_model.' + e), dpi=200) for e in ('pdf', 'png')]
