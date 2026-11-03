#!/usr/bin/env python3
"""Onset of the third jump vs island width: TCAD (incl. 1103_third/ISLW035, ISLW040) against the model prediction
(third_latch.dat: present for W <= 40 nm, gone from 42.5 nm).
Jump = largest rise of log|I_D| within 1 mV of applied V_D above 0.1 mA on the up sweep (a fixed-bias jump).
Hole maps (.str read in Python, not Tonyplot) at 3.0 V (before) and 4.0 V up (after) for W 30, 35, 40, 45 nm.
Output: third_onset.png, third_onset.dat"""
import os, sys, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.tri as mtri
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '..')
sys.path.insert(0, os.path.join(R, '1007_ddsplit'))
from analyze_ddsplit import load_cols
from mech2_ddsplit import read_full
RUNS = [(15, '1030_islw/ISLW015'), (30, '1010_sink/NOKILL_TE8_XS60'), (35, '1103_third/ISLW035'), (40, '1103_third/ISLW040'),
        (45, '1030_islw/ISLW045'), (60, '1030_islw/ISLW060'), (90, '1030_islw/ISLW090')]
pred = {float(l.split()[0]): l.split()[1] for l in open(os.path.join(H, 'third_latch.dat')) if l[:1].isdigit() or l[:2].strip().replace('.', '').isdigit()}
rows, fig = [], plt.figure(figsize=(15, 11)); gs = fig.add_gridspec(3, 4, height_ratios=[1.2, 1, 1], hspace=0.55, wspace=0.3)
a = fig.add_subplot(gs[0, :2]); cm = plt.get_cmap('viridis')
for n, (w, b) in enumerate(RUNS):
    M, v, Id, Is, It, Vt = load_cols(os.path.join(R, b + '.log_tr.log')); k = int(np.argmax(v)); x, I = v[:k + 1], np.abs(Id[:k + 1])
    m = (x > 2.9) & (x < 4.2) & (I > 1e-4); xs, l = x[m], np.log10(I[m]); best, at = 0.0, np.nan
    for i in range(len(xs)):
        j = np.where((xs >= xs[i]) & (xs <= xs[i] + 0.001))[0]; d = l[j].max() - l[i]
        if d > best: best, at = d, xs[i]
    rows.append((w, best, at if best > 0.05 else np.nan, pred.get(float(w), '?')))
    a.semilogy(x, I, color=cm(n / len(RUNS)), label=f'W {w} nm')
a.set_xlim(2.9, 4.2); a.set_ylim(1e-4, 3e-2); a.set_xlabel('V_D (V), up sweep'); a.set_ylabel('|I_D| (A)'); a.legend(fontsize=8); a.grid(alpha=.3)
a.set_title('third jump, TCAD up sweep (1030_islw, 1103_third, 1010_sink)', fontsize=9)
a = fig.add_subplot(gs[0, 2:])
W = [r[0] for r in rows]; a.plot(W, [r[1] for r in rows], 'ko-', label='TCAD: rise within 1 mV (decades)')
a.axvspan(40, 42.5, color='tab:red', alpha=.15, label='model: third fold disappears (40 -> 42.5 nm)')
a.set_xlabel('island width W (nm)'); a.set_ylabel('third jump (decades of I_D)'); a.grid(alpha=.3); a.legend(fontsize=8)
a.set_title('onset: TCAD jump vs model prediction (third_latch.py)', fontsize=9)
for r_, (w, b) in enumerate([(30, '1010_sink/NOKILL_TE8_XS60'), (35, '1103_third/ISLW035'), (40, '1103_third/ISLW040'), (45, '1030_islw/ISLW045')]):
    for c_, (k, lab) in enumerate([(4, '3.0 V up'), (6, '4.0 V up')]):
        ax = fig.add_subplot(gs[1 + r_ // 2, (r_ % 2) * 2 + c_]); cen, area, f, nodes, ix = read_full(os.path.join(R, f'{b}_T_tr_{k}')); wu = w / 1000
        mm = (nodes[:, 1] <= 0.0501) & (nodes[:, 0] > 0.47) & (nodes[:, 0] < 0.80 + wu); nd = nodes[mm]
        z = np.log10(np.maximum(nd[:, 2 + ix['107']], 1))
        cs = ax.tricontourf(mtri.Triangulation((nd[:, 0] - 0.5) * 1e3, nd[:, 1] * 1e3), z, levels=np.linspace(4, 21, 35), cmap='viridis', extend='both')
        for xv in (0, 165, 165 + w, 270 + w): ax.axvline(xv, color='w', lw=.5, ls=':')
        isl = (nodes[:, 0] > 0.666) & (nodes[:, 0] < 0.664 + wu) & (nodes[:, 1] <= 0.05)
        ax.set_ylim(50, 0); ax.set_title(f'W {w} nm, {lab}\nisland p {np.mean(nodes[isl, 2 + ix["107"]]):.1e} cm-3', fontsize=8)
        ax.set_xlabel('x from source (nm)'); ax.set_ylabel('y (nm)')
fig.colorbar(cs, ax=fig.axes[2:], label='log10 p (cm-3)', shrink=.8)
fig.suptitle('Third-jump onset. Hole maps: Python reading of .str (not Tonyplot); dotted = source edge, island edges, drain edge', fontsize=9)
fig.savefig(os.path.join(H, 'third_onset.png'), dpi=100, bbox_inches='tight')
txt = ['# W_nm  TCAD third jump (dec, within 1 mV)  at V_D  model fold V_D (third_latch.dat)'] + ['%3d  %.2f  %s  %s' % (w, j, '%.3f' % a_ if np.isfinite(a_) else '-', p) for w, j, a_, p in rows]
open(os.path.join(H, 'third_onset.dat'), 'w').write('\n'.join(txt) + '\n'); print('\n'.join(txt))
