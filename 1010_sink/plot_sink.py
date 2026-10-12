#!/usr/bin/env python3
"""Silicide-sink check and Auger check: overlay Id-Vd (MixedMode, applied V_D).
Data: 1007_ddsplit/DDS_{TE8_XS60,BASE}{,_AUGER}.log_tr.log, 1010_sink/{SINK,SINK5,NOKILL}_TE8_XS60.log_tr.log, SINK_BASE.log_tr.log
Output: 1010_sink/sink_compare.png, sink_summary.dat"""
import os, sys, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
H = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(H, '..', '1007_ddsplit'); sys.path.insert(0, D)
import analyze_ddsplit as A
G = [('(a) island 60 %, $\\tau_{0,Si}$ 1e-8 s', [(D, 'DDS_TE8_XS60', 'killed island ($\\tau_0$ 1 ps)', 'k', '-'),
                                              (D, 'DDS_TE8_XS60_AUGER', '+ Auger', '0.6', ':'),
                                              (H, 'NOKILL_TE8_XS60', 'island not killed (control)', 'tab:red', '-'),
                                              (H, 'SINK_TE8_XS60', 'metal core + n$^+$ shell 10 nm', 'tab:blue', '-'),
                                              (H, 'SINK5_TE8_XS60', 'metal core + n$^+$ shell 5 nm', 'tab:green', '-')]),
     ('(b) base device (island 50 %, $\\tau_{0,Si}$ 1e-7 s)', [(D, 'DDS_BASE', 'killed island', 'k', '-'), (D, 'DDS_BASE_AUGER', '+ Auger', '0.6', ':'),
                                                         (H, 'SINK_BASE', 'metal core + n$^+$ shell 10 nm', 'tab:blue', '-')])]
fig, axs = plt.subplots(1, 2, figsize=(10, 3.8)); out = []
for ax, (title, items) in zip(axs, G):
    for d, n, lab, c, ls in items:
        fn = os.path.join(d, n + '.log_tr.log')
        if not os.path.exists(fn): continue
        M, v, Id, Is, It, Vt = A.load_cols(fn); k = int(np.argmax(v)); I = np.abs(Id)
        ax.semilogy(v[:k + 1], I[:k + 1], color=c, ls=ls, lw=1.2, label=lab); ax.semilogy(v[k:], I[k:], color=c, ls='--' if ls == '-' else ls, lw=0.7)
        ups, dns, voffl, voffr, vmax = A.analyse(fn)
        r = [x for x in ups if x[1] == 'right']; l = [x for x in ups if x[1] == 'left']
        out.append((n, r[0][0] if r else np.nan, l[0][0] if l else np.nan, voffr, voffl, (voffl - r[0][0]) if r else np.nan))
    ax.set_xlim(0, 6); ax.set_ylim(1e-14, 1e-2); ax.grid(alpha=.3); ax.set_xlabel('$V_D$ (V)'); ax.set_title(title, fontsize=9); ax.legend(fontsize=7, loc='lower right')
axs[0].set_ylabel('$|I_D|$ (A)'); fig.tight_layout(); fig.savefig(os.path.join(H, 'sink_compare.png'), dpi=140)
with open(os.path.join(H, 'sink_summary.dat'), 'w') as f:
    f.write('# name V_on_right V_on_left V_off_right V_off_left sep(V_off_left - V_on_right; >0 = two separated loops)\n')
    for r in out: f.write('%-22s %.3f %.3f %.3f %.3f %.3f\n' % r)
print(open(os.path.join(H, 'sink_summary.dat')).read())
