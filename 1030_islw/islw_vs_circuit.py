#!/usr/bin/env python3
"""Series-circuit criterion (1010_sink/coupling_vs_circuit.py, README core claim evidence 2) applied to the width and lifetime sweeps.

In a series circuit the left STL operating point (I_left = |Is|, V_left = V_tap) lies on the standalone left STL I-V
(1028_leftstl/LSTL_P6e17, on-branch = down sweep). Both body lengths are fixed in every deck, so the same standalone curve
is the reference for every W and tau. Deviation dV = V_left(device) - V_left(standalone) at the same |I_left|.
Output: islw_vs_circuit.dat, islw_vs_circuit.png"""
import os, sys, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '..')
sys.path.insert(0, os.path.join(R, '1007_ddsplit')); sys.path.insert(0, os.path.join(R, 'tools'))
import analyze_ddsplit as A
from plog import load

I_LIST = [1e-6, 1e-5, 1e-4, 1e-3, 3e-3]
LP0 = 32.0                                   # nm, island hole diffusion length at tau 1e-8 s (as plot_islw.py)
RUNS = [('width', 15, 1e-8, 'ISLW015'), ('width', 30, 1e-8, '../1010_sink/NOKILL_TE8_XS60'), ('width', 45, 1e-8, 'ISLW045'),
        ('width', 60, 1e-8, 'ISLW060'), ('width', 90, 1e-8, 'ISLW090'), ('width', 120, 1e-8, 'ISLW120'), ('width', 200, 1e-8, 'ISLW200'),
        ('tau', 30, 1e-12, '../1007_ddsplit/DDS_TE8_XS60'), ('tau', 30, 1e-10, '../1029_isltau/ISL_TAU1em10_XS60'),
        ('tau', 30, 3e-9, '../1029_isltau/ISL_TAU3em9_XS60'),
        ('killed', 120, 1e-12, 'ISLW120_KILL')]


def get(fn):
    M, m = load(fn), A.columns(fn)
    c = lambda k: M[:, m[k]] if k in m else None
    return c('V[1]'), c('V[3]'), c('Adev_drain'), c('Adev_source')


def v_on_down(V, I, k, I0):
    """V on the down sweep at the last point where |I| >= I0 (on-branch just before turn-off)"""
    j = np.where(np.abs(I[k:]) >= I0)[0]
    return V[k + j[-1]] if len(j) else np.nan


v, _, Id, _ = get(os.path.join(R, '1028_leftstl', 'LSTL_P6e17.log_tr.log')); k = int(np.argmax(v))
std = np.array([v_on_down(v, Id, k, I0) for I0 in I_LIST])
rows = []
for s, w, t, b in RUNS:
    v, vt, Id, Is = get(os.path.join(H, b) + '.log_tr.log'); k = int(np.argmax(v))
    lp = LP0 * np.sqrt(t / 1e-8) / w
    rows.append((s, w, t, lp, os.path.basename(b), np.array([v_on_down(vt, Is, k, I0) for I0 in I_LIST]) - std))
with open(os.path.join(H, 'islw_vs_circuit.dat'), 'w') as fo:
    fo.write('# dV = V_left(device, V_tap) - V_left(standalone LSTL_P6e17) on the down-sweep on-branch at |I_left| (V); nan = never reaches that current\n')
    fo.write('# standalone V_left: ' + ' '.join('%.0e:%.3f' % x for x in zip(I_LIST, std)) + '\n')
    fo.write('%-7s %4s %8s %6s ' % ('sweep', 'W_nm', 'tau_s', 'Lp/W') + ' '.join('%8.0e' % I for I in I_LIST) + '  run\n')
    for s, w, t, lp, b, d in rows:
        fo.write('%-7s %4d %8.0e %6.3f ' % (s, w, t, lp) + ' '.join('%+8.3f' % x for x in d) + '  ' + b + '\n')
print(open(os.path.join(H, 'islw_vs_circuit.dat')).read())

fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
for j, I0 in enumerate((1e-3, 3e-3)):
    a = ax[j]; i = I_LIST.index(I0)
    for s, mk, c, lab in (('width', 'o-', 'tab:red', 'width sweep (tau 1e-8 s)'), ('tau', 's-', 'tab:blue', 'lifetime sweep (W 30 nm)'), ('killed', 'kx', 'k', 'W 120 nm, island killed')):
        pts = sorted((lp, d[i]) for ss, w, t, lp, b, d in rows if ss == s and np.isfinite(d[i]))
        a.semilogx(*zip(*pts), mk, color=c, label=lab)
    a.axhline(0, color='gray', lw=1, ls='--'); a.grid(alpha=.3, which='both'); a.legend(fontsize=8)
    a.set_xlabel('L_p / W_island  (coupling ->)'); a.set_ylabel('V_left - V_left(standalone STL) (V)')
    a.set_title(f'left STL operating point at |I_left| = {I0 * 1e3:g} mA (0 = series circuit)', fontsize=9)
fig.tight_layout(); fig.savefig(os.path.join(H, 'islw_vs_circuit.png'), dpi=100)
