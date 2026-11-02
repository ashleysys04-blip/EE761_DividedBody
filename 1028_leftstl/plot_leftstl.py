#!/usr/bin/env python3
"""Step 16b: Id-Vd of the standalone left STL vs left doping (LSTL_P*), with turn-on (V_on, I_off) and turn-off
(V_hold, I_h = current where the collapse starts on the down sweep, read on the time axis). Output: leftstl_compare.png,
leftstl_summary.dat (this folder)."""
import os, sys, glob, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', '1007_ddsplit'))
import analyze_ddsplit as A
def ana(fn):
    M = A.load(fn); c = A.columns(fn); t = M[:, 0] * 1e6; v = M[:, c['V[1]']]; I = np.abs(M[:, c['Adev_drain']]); lg = np.log10(I + 1e-30); k = int(np.argmax(v))
    j = int(np.argmax(np.diff(lg[:k + 1]))); von = v[j]; ioff = I[np.where(v[:k] >= von - 0.01)[0][0]]
    r = dict(v=v, I=I, k=k, von=von, ioff=ioff, vhold=np.nan, ih=np.nan, done=v[-1] < 0.1)
    if r['done']:
        dn = np.arange(k, len(v)); rate = -np.diff(lg[dn]) / np.maximum(np.diff(t[dn]), 1e-12)   # decades per us
        q = [x for x in np.where(rate > 0.5)[0] if I[dn][x] < 1e-4]                                 # collapse onset
        if q: r['vhold'], r['ih'] = v[dn][q[0]], I[dn][q[0]]
    return r
fig, ax = plt.subplots(figsize=(7.5, 4.6)); rows = []
for fn, col in zip(sorted(glob.glob(os.path.join(H, 'LSTL_P*.log_tr.log'))), ('C0', 'C1', 'C3', 'C2')):
    n = os.path.basename(fn)[:-11]; r = ana(fn); k = r['k']
    ax.semilogy(r['v'][:k + 1], r['I'][:k + 1], col, lw=1.2, label=n + ('' if r['done'] else ' (running)')); ax.semilogy(r['v'][k:], r['I'][k:], col + '--', lw=.8)
    ax.plot(r['von'], r['ioff'], 'o', color=col, ms=4)
    if r['done']: ax.plot(r['vhold'], r['ih'], 's', color=col, ms=5)
    rows.append((n, r['von'], r['ioff'], r['vhold'], r['ih'], 'done' if r['done'] else 'running'))
ax.set_xlim(0, 6); ax.set_ylim(1e-14, 1e-1); ax.grid(alpha=.3); ax.legend(fontsize=7, loc='lower right')
ax.set_xlabel('V_D (V)'); ax.set_ylabel('|I_D| (A)'); ax.set_title('standalone left STL (solid up / dashed down); o = turn-on, square = collapse onset\ndata: 1028_leftstl/LSTL_P*.log_tr.log', fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(H, 'leftstl_compare.png'), dpi=130)
with open(os.path.join(H, 'leftstl_summary.dat'), 'w') as f:
    f.write('# name V_on I_off(V_on-10mV) V_hold I_h(collapse onset) status\n')
    for x in rows: f.write('%-12s %.3f %.2e %.3f %.2e %s\n' % x)
print(open(os.path.join(H, 'leftstl_summary.dat')).read())
