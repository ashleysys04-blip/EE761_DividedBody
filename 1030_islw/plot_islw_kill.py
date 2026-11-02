"""Island-width sweep, part 2 (after plot_islw.py): ISLW120 vs ISLW120_KILL (same W, Lg; only island lifetime differs) and the hysteresis window vs L_p/W.
(a) left STL current, ISLW120 vs ISLW120_KILL vs DDS_TE8_XS60. (b) 2nd-stage hysteresis vs L_p/W from islw_summary.dat (run plot_islw.py first).
(c) hole maps at 3.0 V up / down (.str snapshots T_tr_4 / T_tr_12). Output: islw_kill.png"""
import os, sys, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.tri as mtri
R = '/home/ysseo/novel'; sys.path.insert(0, R + '/1007_ddsplit')
from analyze_ddsplit import load_cols
from mech2_ddsplit import read_full
OUT = os.path.join(R, '1030_islw')
fig = plt.figure(figsize=(15, 10)); gs = fig.add_gridspec(3, 2, height_ratios=[1.2, 1, 1])
a = fig.add_subplot(gs[0, 0])
for b, c, ls, lab in [('/1030_islw/ISLW120', 'tab:red', '-', 'W 120 nm, coupled (tau 1e-8 s)'), ('/1030_islw/ISLW120_KILL', 'k', '--', 'W 120 nm, island killed'),
                      ('/1007_ddsplit/DDS_TE8_XS60', 'gray', ':', 'W 30 nm, island killed')]:
    M, v, Id, Is, It, Vt = load_cols(R + b + '.log_tr.log'); a.semilogy(v, np.abs(Is), color=c, ls=ls, label=lab)
a.set_xlim(0.8, 5.2); a.set_ylim(1e-14, 1e-1); a.set_xlabel('applied drain voltage (V), up and down'); a.set_ylabel('|I_S| = left STL current (A)')
a.grid(alpha=.3); a.legend(fontsize=8); a.set_title('(a) killed: W 120 = W 30 (4.76 vs 4.78 V up, 2.58 vs 2.57 V down) -> Lg has no effect', fontsize=9)
d = np.genfromtxt(R + '/1030_islw/islw_summary.dat', dtype=None, encoding=None, comments='#')
a = fig.add_subplot(gs[0, 1])
for s, mk, c, lab in (('width', 'o-', 'tab:red', 'width sweep (tau 1e-8 s)'), ('tau', 's-', 'tab:blue', 'lifetime sweep (W 30 nm)'), ('killed', 'kx', 'k', 'island killed (W 30, 120 nm)')):
    pts = sorted((r[3], r[5] - r[6] if np.isfinite(r[5]) else 0.0) for r in d if r[0] == s and not (np.isnan(r[5]) and r[1] == 30))
    a.semilogx(*zip(*pts), mk, color=c, label=lab)
    for x, y in pts: a.annotate(f'{y:.2f}', (x, y), textcoords='offset points', xytext=(4, 4), fontsize=7, color=c)
a.set_xlabel('L_p / W_island  (coupling ->)'); a.set_ylabel('2nd-stage hysteresis = V_up - V_down (V)'); a.grid(alpha=.3, which='both'); a.legend(fontsize=8)
a.set_title('(b) hysteresis window: 2.27 V -> 0 continuously (W 15 nm: no latch, plotted as 0)', fontsize=9)
for r, (w, b) in enumerate([(120, R + '/1030_islw/ISLW120'), (120, R + '/1030_islw/ISLW120_KILL')]):
    for c_, (k, lab) in enumerate([(4, '3.0 V up'), (12, '3.0 V down')]):
        ax = fig.add_subplot(gs[1 + r, c_]); fn = f'{b}_T_tr_{k}'; wu = w / 1000
        cen, area, f, nodes, ix = read_full(fn)
        m = (nodes[:, 1] <= 0.0501) & (nodes[:, 0] > 0.45) & (nodes[:, 0] < 0.85 + wu); nd = nodes[m]
        z = np.log10(np.maximum(nd[:, 2 + ix['107']], 1))
        cs = ax.tricontourf(mtri.Triangulation(nd[:, 0], nd[:, 1]), z, levels=np.linspace(4, 21, 35), cmap='viridis', extend='both'); fig.colorbar(cs, ax=ax, label='log10 p (cm-3)')
        xs = 0.5 + 0.165 + wu / 2
        for xv in (0.5, xs - wu / 2, xs + wu / 2, 0.5 + 0.27 + wu): ax.axvline(xv, color='w', lw=.6, ls=':')
        ax.set_ylim(0.05, 0); ax.set_xlabel('x (um)'); ax.set_ylabel('y (um)')
        ax.set_title(f'{os.path.basename(b)}, {lab}  ({os.path.basename(fn)})', fontsize=8)
fig.suptitle('Hole maps: Python reading of .str (not Tonyplot); dotted = gate edges and n+ island edges', fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(OUT, 'islw_kill.png'), dpi=100)
