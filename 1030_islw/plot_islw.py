#!/usr/bin/env python3
"""Island-width sweep (make_islw.py) next to the island-lifetime sweep (1029_isltau): is the coupling one knob, L_p / W?

(a) Id-Vd of the width sweep (island tau 1e-8 s) + killed island reference (1007_ddsplit/DDS_TE8_XS60, W 30 nm)
(b) 2nd latch (up sweep) vs L_p / W_island for both sweeps. L_p = 32 nm * sqrt(tau / 1e-8 s) (consrh in 1e20 n+, see make_islw.py)
(c) hole density maps (.str snapshots, Python reading, not Tonyplot) at 2.5 / 3.5 / 5.0 V up
Missing logs (decks still in the queue) are skipped. Output: islw_summary.png, islw_summary.dat"""
import os, sys, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.tri as mtri
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '..')
sys.path.insert(0, os.path.join(R, '1007_ddsplit'))
from analyze_ddsplit import load_cols, analyse
from mech2_ddsplit import read_full

LP0 = 32.0                                   # nm, island hole diffusion length at tau 1e-8 s
WSW = [(15, 'ISLW015'), (30, '../1010_sink/NOKILL_TE8_XS60'), (45, 'ISLW045'), (60, 'ISLW060'), (90, 'ISLW090'),
       (120, 'ISLW120'), (200, 'ISLW200')]
TSW = [(1e-12, '../1007_ddsplit/DDS_TE8_XS60'), (1e-11, '../1029_isltau/ISL_TAU1em11_XS60'), (1e-10, '../1029_isltau/ISL_TAU1em10_XS60'),
       (1e-9, '../1029_isltau/ISL_TAU1em9_XS60'), (3e-9, '../1029_isltau/ISL_TAU3em9_XS60'), (1e-8, '../1010_sink/NOKILL_TE8_XS60')]
KILL = [(30, '../1007_ddsplit/DDS_TE8_XS60'), (120, 'ISLW120_KILL')]
SNAP = {3: 2.5, 5: 3.5, 7: 5.0}              # T_tr_N -> applied V on the up sweep (same tsave list in every deck)
P = lambda b: os.path.join(H, b)


def latches(b):
    """(1st up, 2nd up, 2nd down) in V, nan where missing; None if the log does not exist or is unfinished"""
    fn = P(b) + '.log_tr.log'
    q = P(b) + '.queue'                      # deck still running (queue file without an end line) -> skip
    if not os.path.exists(fn) or (os.path.exists(q) and 'end' not in open(q).read()): return None
    eu, ed, vl, vr, vmax = analyse(fn)
    up = {s: v for v, s, *_ in eu}; dn = {s: v for v, s, *_ in ed}
    return up.get('right', np.nan), up.get('left', np.nan), dn.get('left', np.nan)


rows = []
for w, b in WSW: rows.append(('width', w, 1e-8, LP0 / w, b, latches(b)))
for t, b in TSW: rows.append(('tau', 30, t, LP0 * np.sqrt(t / 1e-8) / 30, b, latches(b)))
for w, b in KILL: rows.append(('killed', w, 1e-12, LP0 * 0.01 / w, b, latches(b)))
with open(os.path.join(H, 'islw_summary.dat'), 'w') as fo:
    fo.write('# sweep  W_nm  island_tau_s  Lp/W  1st_up_V  2nd_up_V  2nd_down_V  run   (plot_islw.py; nan = no event / run unfinished)\n')
    for s, w, t, r, b, L in rows:
        if L is None: continue
        fo.write('%-7s %4d %8.0e %7.3f  %6.3f %6.3f %6.3f  %s\n' % (s, w, t, r, *L, os.path.basename(b)))
print(open(os.path.join(H, 'islw_summary.dat')).read())

fig = plt.figure(figsize=(15, 12)); gs = fig.add_gridspec(4, 2, height_ratios=[1.3, 1, 1, 1])
a = fig.add_subplot(gs[0, 0]); cm = plt.get_cmap('viridis')
for i, (w, b) in enumerate(WSW):
    if latches(b) is None: continue
    M, v, Id, *_ = load_cols(P(b) + '.log_tr.log'); a.semilogy(v, np.abs(Id), color=cm(i / len(WSW)), label=f'W {w} nm')
for w, b in KILL:
    if latches(b) is None: continue
    M, v, Id, *_ = load_cols(P(b) + '.log_tr.log'); a.semilogy(v, np.abs(Id), 'k--' if w == 30 else 'r--', lw=1, label=f'W {w} nm, island killed')
a.set_xlabel('applied drain voltage (V)'); a.set_ylabel('|I_D| (A)'); a.grid(alpha=.3); a.legend(fontsize=7)
a.set_title('(a) Island-width sweep, island tau 1e-8 s (0 -> 6 -> 0 V, 0.7 V/ms)', fontsize=9)
b_ = fig.add_subplot(gs[0, 1])
for s, mk, c, lab in (('width', 'o-', 'tab:red', 'width sweep (tau 1e-8 s)'), ('tau', 's-', 'tab:blue', 'lifetime sweep (W 30 nm)')):
    pts = sorted((r, L[1]) for ss, w, t, r, b, L in rows if ss == s and L is not None and np.isfinite(L[1]))
    if pts: b_.semilogx(*zip(*pts), mk, color=c, label=lab)
    for r, y in pts: b_.annotate(f'{y:.2f}', (r, y), textcoords='offset points', xytext=(4, 4), fontsize=7, color=c)
b_.axhline([L for s, w, t, r, b, L in rows if s == 'killed' and w == 30][0][1], color='gray', ls='--', lw=1, label='island killed (W 30 nm)')
b_.set_xlabel('L_p / W_island  (coupling ->)'); b_.set_ylabel('2nd latch, up sweep (V)'); b_.grid(alpha=.3, which='both'); b_.legend(fontsize=8)
b_.set_title('(b) Both knobs on one axis. L_p = 32 nm x sqrt(tau / 1e-8 s)', fontsize=9)
MAPS = [(60, 'ISLW060', 5), (120, 'ISLW120', 5), (200, 'ISLW200', 5), (200, 'ISLW200', 7), (120, 'ISLW120', 3), (200, 'ISLW200', 3)]
for i, (w, b, k) in enumerate(MAPS):
    ax = fig.add_subplot(gs[1 + i // 2, i % 2]); fn = f'{P(b)}_T_tr_{k}'
    if not os.path.exists(fn): ax.axis('off'); continue
    cen, area, f, nodes, ix = read_full(fn); wu = w / 1000
    m = (nodes[:, 1] <= 0.0501) & (nodes[:, 0] > 0.45) & (nodes[:, 0] < 0.85 + wu); nd = nodes[m]
    z = np.log10(np.maximum(nd[:, 2 + ix['107']], 1))
    cs = ax.tricontourf(mtri.Triangulation(nd[:, 0], nd[:, 1]), z, levels=np.linspace(4, 21, 35), cmap='viridis', extend='both')
    fig.colorbar(cs, ax=ax, label='log10 p (cm-3)')
    xs = 0.5 + 0.165 + wu / 2
    for xv in (0.5, xs - wu / 2, xs + wu / 2, 0.5 + 0.27 + wu): ax.axvline(xv, color='w', lw=.6, ls=':')
    ax.set_ylim(0.05, 0); ax.set_xlabel('x (um)'); ax.set_ylabel('y (um)')
    ax.set_title(f'(c) W {w} nm, {SNAP[k]} V up  ({os.path.basename(fn)})', fontsize=8)
fig.suptitle('Hole maps: Python reading of .str (not Tonyplot). Dotted = gate edges and n+ island edges. '
             'Left body = 0.50-0.665 um in every deck', fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(H, 'islw_summary.png'), dpi=100)
