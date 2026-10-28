#!/usr/bin/env python3
"""Step 16: drain-node voltage, tap (island) voltage and electrode currents vs time for every OSC_* run (finished or running),
plus hole density of the latest .str snapshot of each run. Output: osc_waveforms.png, osc_pmaps.png (this folder).
Dashed lines = latch voltages of the DC sweep (1010_sink/SINK_TE8_XS60): right on/off 1.50/1.09 V, left on/off 4.62/2.09 V."""
import os, sys, glob, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.tri as mtri
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', '1007_ddsplit'))
import analyze_ddsplit as A
RUNS = ['OSC_R_1n', 'OSC_L_600n', 'OSC_R_3n', 'OSC_L_800n']
LV = [(1.50, 'right on'), (1.09, 'right off'), (4.62, 'left on'), (2.09, 'left off')]
have = [r for r in RUNS if os.path.exists(os.path.join(H, r + '.log_tr.log'))]
fig, ax = plt.subplots(2, len(have), figsize=(6 * len(have), 6.5), squeeze=False)
for j, r in enumerate(have):
    fn = os.path.join(H, r + '.log_tr.log'); M = A.load(fn); c = A.columns(fn); t = M[:, 0] * 1e3
    done = os.path.exists(os.path.join(H, r + '.queue')) and 'end' in open(os.path.join(H, r + '.queue')).read()
    a = ax[0, j]; a.plot(t, M[:, c['V[1]']], 'C3', label='drain node V_D'); a.plot(t, M[:, c['V[3]']], 'C0', lw=.8, label='tap / island V_tap')
    for v, lab in LV: a.axhline(v, ls='--', lw=.6, color='k' if 'right' in lab else '0.5'); a.text(t.max(), v, ' ' + lab, fontsize=6, va='center')
    a.set_title('%s (%s, up to t = %.2f ms)' % (r, 'done' if done else 'running', t.max()), fontsize=9); a.set_ylabel('V'); a.legend(fontsize=7, loc='upper left'); a.grid(alpha=.3)
    a = ax[1, j]
    for k, lab, col in (('Adev_drain', 'drain', 'C3'), ('Adev_source', 'source (left STL)', 'C2'), ('Adev_tap', 'tap (island -> Rtap)', 'C0')):
        a.semilogy(t, np.abs(M[:, c[k]]) + 1e-16, col, lw=.8, label=lab)
    a.set_ylim(1e-14, 1e-2); a.set_xlabel('t (ms)'); a.set_ylabel('|I| (A)'); a.legend(fontsize=7); a.grid(alpha=.3)
fig.suptitle('Constant-current oscillation (I source + C on the drain), data: 1028_osc/OSC_*.log_tr.log', fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(H, 'osc_waveforms.png'), dpi=120)
def pmap(fn):
    C, nodes, codes = {}, {}, None
    for l in open(fn):
        if l[:2] == 'c ': p = l.split(); C[int(p[1])] = (float(p[2]), float(p[3]))
        elif l[:2] == 's ': codes = l.split()[2:]
        elif l[:2] == 'n ':
            p = l.split()
            if p[2] == '3': nodes[int(p[1]) + 1] = float(p[3 + codes.index('107')])
    k = sorted(nodes); return np.array([C[i] for i in k]), np.array([nodes[i] for i in k])
snaps = [(r, sorted(glob.glob(os.path.join(H, r + '_T_tr_*')), key=lambda s: int(s.split('_')[-1]))) for r in have]
snaps = [(r, s[-1]) for r, s in snaps if s]
if snaps:
    fig, ax = plt.subplots(len(snaps), 1, figsize=(9, 2.6 * len(snaps)), squeeze=False)
    for a, (r, f) in zip(ax[:, 0], snaps):
        xy, p = pmap(f); m = (xy[:, 0] > 0.45) & (xy[:, 0] < 0.85)
        cs = a.tricontourf(mtri.Triangulation(xy[m, 0], xy[m, 1]), np.log10(np.maximum(p[m], 1)), np.linspace(0, 20, 41), cmap='magma'); fig.colorbar(cs, ax=a, label='log10 p')
        a.set_ylim(0.055, -0.005); a.set_title('%s: hole density at snapshot %s (Python rendering of .str, not Tonyplot)' % (r, os.path.basename(f)), fontsize=8)
    ax[-1, 0].set_xlabel('x (um)'); fig.tight_layout(); fig.savefig(os.path.join(H, 'osc_pmaps.png'), dpi=120)
