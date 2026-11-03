#!/usr/bin/env python3
"""Paper figure for the two-body hole-balance model (1103_physics/stl_hybrid.py): figU_model.
(a) island coupling with the left STL off vs island width, with the derived transmission (L = 21.0 nm) and the lifetime points;
(b) holes back-injected by the right STL into the island per drain electron vs current (junction law, plasma limit);
(c) island hole transmission vs current (drift-diffusion with the drain current's ohmic field);
(d), (e) model vs TCAD |I_D|-V_D; (f) second-latch turn-on / turn-off vs W and the third-jump height (TCAD) with the model onset.
Runs 1103_physics/stl_hybrid.py (which also rewrites its own outputs). Output: paper/fig/figU_model.{pdf,png}"""
import os, runpy, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '..'); O = os.path.join(H, 'fig'); P = os.path.join(R, '1103_physics')
G = runpy.run_path(os.path.join(P, 'stl_hybrid.py')); PH = G['PH']
gamma, transmission, GR, LP, GINF = PH['gamma'], PH['transmission'], PH['GR'], PH['LP'], PH['GINF']
T, Mo, RUNS = G['T'], G['Mo'], G['RUNS']
plt.rcParams.update({'font.family': 'serif', 'font.serif': ['Nimbus Roman', 'Nimbus Roman No9 L', 'Times New Roman', 'DejaVu Serif'],
                     'font.size': 7, 'mathtext.fontset': 'stix', 'axes.linewidth': 0.6})
fig, ax = plt.subplots(2, 3, figsize=(7.16, 4.4)); ax = ax.ravel()
def tag(a, s): a.text(-0.22, 1.02, s, transform=a.transAxes, fontsize=8, weight='bold')
cm = {15: 'tab:purple', 30: 'tab:red', 60: 'tab:orange', 120: 'tab:green'}

# (a) state-II coupling vs W
B = [l.split() for l in open(os.path.join(R, '1103_model', 'balance.dat')) if not l.startswith('#')]
E = {}
for r in B:
    if r[4] == 'up' and float(r[8]) < 1e-7 and float(r[13]) > 1e-9: E.setdefault((r[0], int(r[1]), float(r[2])), []).append(float(r[16]))
a = ax[0]
for k, v in E.items():
    e = np.exp(np.mean(np.log(v)))
    if k[0] == 'width': a.semilogy(k[1], e, 'o', color='k', ms=3.5)
    elif k[0] == 'tau': a.semilogy(k[1], e, 's', color='tab:blue', mfc='none', ms=4); a.annotate(r'$\tau_{0,isl}$ %s' % ('3e-9' if k[2] > 1e-9 else '1e-10'), (k[1], e), fontsize=5.5, xytext=(5, -6), textcoords='offset points')
    else: a.semilogy(k[1], e, 'x', color='0.4', ms=4)
WW = np.linspace(10, 210, 60); ID0 = 1.5e-7
a.semilogy(WW, gamma(ID0, *GR) * transmission(WW, 1e-8, np.full_like(WW, ID0)), 'r-', lw=.9, label=r'$\gamma_R\,T$, $L$ = %.0f nm (derived)' % (LP(1e-8) * 1e7))
a.semilogy([30], [gamma(ID0, *GR) * transmission(30, 3e-9, np.array([ID0]))[0]], '+', color='tab:blue', ms=8, label=r'derived, $\tau_{0,isl}$ 3e-9 s')
a.set_xlabel(r'island width $W_{IS}$ (nm)'); a.set_ylabel(r'$\eta$ (left STL off)'); a.legend(fontsize=5.3, loc='upper right'); a.grid(alpha=.3); tag(a, '(a)')

# (b) back-injection gamma_R(I)
inj = [l.split() for l in open(os.path.join(P, 'injection.dat')) if not l.startswith('#')]
a = ax[1]; II = np.logspace(-8, -1.1, 200)
for w, c in cm.items():
    rr = [r for r in inj if int(r[0]) == w and float(r[3]) > 1e-8]; a.loglog([float(r[3]) for r in rr], [float(r[5]) for r in rr], 'o', color=c, ms=2.5, label=f'{w} nm')
a.loglog(II, gamma(II, *GR), 'k-', lw=.9, label='junction law + plasma limit')
a.axhline(GINF, color='0.5', ls='--', lw=.7); a.text(1.5e-8, GINF * 1.08, r'$\mu_p/(\mu_n+\mu_p)$', fontsize=5.5, color='0.4')
a.set_xlabel(r'$|I_D|$ (A)'); a.set_ylabel(r'$\gamma_R$ = holes into island / $I_D$'); a.legend(fontsize=5.0, loc='upper left', ncol=2); a.grid(alpha=.3, which='both'); tag(a, '(b)')

# (c) transmission
tr = [l.split() for l in open(os.path.join(R, '1103_model', 'island_transport.dat')) if not l.startswith('#')]
a = ax[2]; II = np.logspace(-7, -1.1, 200)
for w, c in cm.items():
    rr = [r for r in tr if int(r[0]) == w and float(r[2]) > 1e-7 and float(r[8]) > 0]
    a.semilogx([float(r[2]) for r in rr], [float(r[8]) for r in rr], 'o', color=c, ms=2.5)
    a.semilogx(II, transmission(w, 1e-8, II), '-', color=c, lw=.9, label=f'{w} nm')
a.set_ylim(0, 1.05); a.set_xlabel(r'$|I_D|$ (A)'); a.set_ylabel(r'island transmission $T$'); a.legend(fontsize=5.3, loc='upper left'); a.grid(alpha=.3, which='both'); tag(a, '(c)')

# (d), (e) Id-Vd
for a, runs, tg in ((ax[3], [('NOKILL_TE8_XS60', 'tab:red', '30 nm (ref.)'), ('ISLW060', 'tab:orange', '60 nm')], '(d)'),
                    (ax[4], [('ISLW120', 'tab:green', '120 nm'), ('ISLW200', 'tab:blue', '200 nm'), ('ISLW120_KILL', 'k', '120 nm, killed')], '(e)')):
    for run, c, lab in runs:
        t, mo = T[run], Mo[run]; k = t['k']
        a.plot(t['v'][:k + 1], t['Id'][:k + 1], '-', color=c, lw=.7, label='TCAD ' + lab); a.plot(t['v'][k:], t['Id'][k:], ':', color=c, lw=.7)
        a.plot(mo['VD'][mo['up']], mo['ID'][mo['up']], '-', color=c, lw=2.2, alpha=.35, label='model ' + lab)
        a.plot(mo['VD'][mo['dn']], mo['ID'][mo['dn']], '--', color=c, lw=1.6, alpha=.5)
    a.set_yscale('log'); a.set_ylim(1e-8, 1e-1); a.set_xlim(1.0, 5.5); a.set_xlabel(r'$V_D$ (V)'); a.set_ylabel(r'$|I_D|$ (A)')
    a.legend(fontsize=4.8, loc='lower right'); a.grid(alpha=.3); tag(a, tg)

# (f) latch voltages vs W + third jump
a = ax[5]; cw = [(r_, w) for r_, d_, w, t_ in RUNS if t_ == 1e-8]; ws = [w for r_, w in cw]
a.plot(ws, [T[r_]['von'] for r_, w in cw], 'ko-', ms=3, lw=.8, label='turn-on, TCAD'); a.plot(ws, [Mo[r_]['von'] for r_, w in cw], 'ko--', ms=3, lw=.8, mfc='w', label='turn-on, model')
a.plot(ws, [T[r_]['voff'] for r_, w in cw], 'bs-', ms=3, lw=.8, label='turn-off, TCAD'); a.plot(ws, [Mo[r_]['voff'] for r_, w in cw], 'bs--', ms=3, lw=.8, mfc='w', label='turn-off, model')
a.set_xlabel(r'island width $W_{IS}$ (nm)'); a.set_ylabel(r'2nd latch $V_D$ (V)'); a.legend(fontsize=5.0, loc='upper left'); a.grid(alpha=.3); tag(a, '(f)')
J3 = {int(l.split()[0]): float(l.split()[1]) for l in open(os.path.join(R, '1103_model', 'third_onset.dat')) if not l.startswith('#')}
b = a.twinx(); b.plot(ws, [J3.get(w, 0.0) for w in ws], 'g^-', ms=3, lw=.8)       # third_onset.dat (fixed-bias rise within 1 mV); W >= 120: none; b.axvspan(40, 42.5, color='g', alpha=.15)
b.set_ylabel('3rd jump, TCAD (decades); band: predicted onset', color='g', fontsize=6); b.set_ylim(0, 1.0)
fig.tight_layout(w_pad=.6); [fig.savefig(os.path.join(O, 'figU_model.' + e), dpi=200) for e in ('pdf', 'png')]
