#!/usr/bin/env python3
"""Step 15 sink robustness: overlay Id-Vd of every finished / running ROB_* run against the ideal sink and the
lifetime-killed reference, and tabulate latch metrics. Output: robust_compare.png, robust_summary.dat (this folder)."""
import os, sys, glob, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '..'); sys.path.insert(0, os.path.join(R, '1007_ddsplit'))
import analyze_ddsplit as A
REF = [('1007_ddsplit/DDS_TE8_XS60', 'lifetime-killed island', 'k'), ('1010_sink/SINK_TE8_XS60', 'ideal sink (W30, 10/10/10 nm)', '0.5')]
GROUPS = [('(a) contact: surface recombination', ['ROB_SR1e6', 'ROB_SR1e4', 'ROB_SR1e2']),
          ('(b) integration: split gate, top-contacted core', ['ROB_SG_W60', 'ROB_SG_W100']),
          ('(c) geometry: width, misalignment, residual Si', ['ROB_W60', 'ROB_W100', 'ROB_OFFP5', 'ROB_OFFM5', 'ROB_RES5', 'ROB_RES15']),
          ('(d) tap capacitance / gate WF check', ['ROB_C10p', 'ROB_C100p', 'WF417_BASE'])]
def metrics(fn):
    ups, dns, voffl, voffr, vmax = A.analyse(fn)
    r = [x[0] for x in ups if x[1] == 'right']; l = [x[0] for x in ups if x[1] == 'left']
    M, v, Id, Is, It, Vt = A.load_cols(fn)
    done = v[-1] < 0.05 and v.max() > 5.9
    return (r[0] if r else np.nan), (l[0] if l else np.nan), voffr, voffl, done
fig, axs = plt.subplots(2, 2, figsize=(10, 7)); rows = []
for ax, (title, names) in zip(axs.flat, GROUPS):
    items = [(os.path.join(R, p + '.log_tr.log'), lab, c, 1.6) for p, lab, c in REF]
    items += [(os.path.join(H, n + '.log_tr.log'), n, c, 1.0) for n, c in zip(names, plt.cm.tab10(np.arange(len(names))))]
    for fn, lab, c, lw in items:
        if not os.path.exists(fn): continue
        M, v, Id, Is, It, Vt = A.load_cols(fn); k = int(np.argmax(v)); I = np.abs(Id)
        r, l, offr, offl, done = metrics(fn)
        ax.semilogy(v[:k + 1], I[:k + 1], color=c, lw=lw, label=lab + ('' if done else (' (partial)' if os.path.isdir(fn[:-11] + '_partial') else ' (running)')))
        ax.semilogy(v[k:], I[k:], color=c, lw=lw * .6, ls='--')
        if lab.startswith(('ROB', 'WF')) or 'ideal' in lab or 'killed' in lab:
            nm = os.path.basename(fn)[:-11]
            st = 'done' if done else ('partial(killed)' if os.path.isdir(os.path.join(H, nm + '_partial')) else 'running')
            rows.append((nm, r, l, offr, offl, offl - r, st))
    ax.set_xlim(0, 6); ax.set_ylim(1e-14, 1e-2); ax.grid(alpha=.3); ax.set_title(title, fontsize=9); ax.legend(fontsize=6, loc='lower right')
    ax.set_xlabel('$V_D$ (V)'); ax.set_ylabel('$|I_D|$ (A)')
fig.tight_layout(); fig.savefig(os.path.join(H, 'robust_compare.png'), dpi=130)
seen = set()
with open(os.path.join(H, 'robust_summary.dat'), 'w') as f:
    f.write('# name V_on_right V_on_left V_off_right V_off_left sep(V_off_left-V_on_right, >0 separated) status\n')
    for r in rows:
        if r[0] in seen: continue
        seen.add(r[0]); f.write('%-22s %.3f %.3f %.3f %.3f %.3f %s\n' % r)
print(open(os.path.join(H, 'robust_summary.dat')).read())
