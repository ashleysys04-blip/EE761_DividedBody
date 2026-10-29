#!/usr/bin/env python3
"""Calibration stage 2: Id-Vd split (AN / BN / TAU) at V_G 0.4 V vs the measured double latch (Noh et al., EDL 2025).
Inputs: TRI_IV_CAL*.log_tr.log (MixedMode: Vdrain node 4 -> Rd 65 Ohm -> drain, source -> Rs 65 Ohm -> 0), calib_targets.dat.
x axis = applied V[4] (source-meter voltage, as in the measurement); I = drain current.
Output: TRI_cal2_compare.png, TRI_cal2_summary.dat"""
import os, sys, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', '1007_ddsplit'))
import analyze_ddsplit as A

RUNS = [('TRI_IV_CAL', 'base (AN 1, BN 1, TAU 1e-7)'), ('TRI_IV_CAL_BN0p9', 'BN 0.9'), ('TRI_IV_CAL_BN1p1', 'BN 1.1'),
        ('TRI_IV_CAL_BN1p2', 'BN 1.2'), ('TRI_IV_CAL_AN0p5', 'AN 0.5'), ('TRI_IV_CAL_AN2', 'AN 2'),
        ('TRI_IV_CAL_TAU1e-6', 'TAU 1e-6'), ('TRI_IV_CAL_TAU1e-8', 'TAU 1e-8')]
T = [l.split() for l in open(os.path.join(H, 'calib_targets.dat')) if l.strip() and not l.startswith('#')][0]
meas = dict(zip('VG VLU1 ILU1 VLD1 ILD1 VLU2 ILU2 VLD2 ILD2'.split(), map(float, T)))

def jumps(v, i, seg, s):
    """Jumps of >1 decade while V[4] moves <0.05 V (consecutive steps merged)."""
    lg = np.log10(np.abs(i) + 1e-30); ev = []; j0 = None
    for j in seg:
        if abs(lg[j] - lg[j - 1]) > 0.05 and abs(v[j] - v[j - 1]) < 0.01:
            j0 = j - 1 if j0 is None else j0
        elif j0 is not None:
            if abs(v[j - 1] - v[j0]) < 0.05 and abs(lg[j - 1] - lg[j0]) > 1: ev.append((s, v[j0], i[j0], i[j - 1]))
            j0 = None
    return ev

fig, ax = plt.subplots(1, 3, figsize=(13, 4)); rows = []
cols = dict(zip([r[0] for r in RUNS], ['k', 'C0', 'C1', 'C3', 'C2', 'C4', 'C5', 'C6']))
for name, lab in RUNS:
    f = os.path.join(H, name + '.log_tr.log')
    M = A.load(f); c = A.columns(f); v = M[:, c['V[4]']]; i = np.abs(M[:, c['Adev_drain']]); k = int(np.argmax(v))
    ev = jumps(v, i, range(1, k + 1), 'up') + jumps(v, i, range(k + 1, len(v)), 'down')
    rows.append((name, lab, v[k], v[-1], ev))
    for q, typ in ((ax[0], 'BN'), (ax[1], 'AN'), (ax[2], 'TAU')):
        if typ in name or name == 'TRI_IV_CAL':
            q.semilogy(v[:k + 1], i[:k + 1], color=cols[name], lw=1, label=lab + ('' if v[k] > 12.9 else ' (stopped %.1f V)' % v[k]))
            q.semilogy(v[k:], i[k:], color=cols[name], lw=.7, ls='--')
for q, typ in zip(ax, ('BN', 'AN', 'TAU')):
    for key in ('LU1', 'LD1', 'LU2', 'LD2'):
        q.plot(meas['V' + key], meas['I' + key], 'ks', mfc='none', ms=5); q.annotate('V' + key, (meas['V' + key], meas['I' + key]), fontsize=6)
    q.set_ylim(1e-10, 1e-1); q.set_xlim(0, 13.2); q.grid(alpha=.3); q.legend(fontsize=6, loc='lower right')
    q.set_xlabel('applied $V_D$ (V), series 65 $\\Omega$/side'); q.set_title('%s split, $V_G$ 0.4 V (solid up, dashed down)' % typ, fontsize=8)
ax[0].set_ylabel('$|I_D|$ (A)')
fig.tight_layout(); fig.savefig(os.path.join(H, 'TRI_cal2_compare.png'), dpi=130)
with open(os.path.join(H, 'TRI_cal2_summary.dat'), 'w') as f:
    f.write('# name Vmax V_last events(dir:V:I_before->I_after) | measured: VLU1 %.2f VLD1 %.2f VLU2 %.2f VLD2 %.2f\n' % (meas['VLU1'], meas['VLD1'], meas['VLU2'], meas['VLD2']))
    for n, lab, vm, vl, ev in rows:
        f.write('%s %.2f %.2f %s\n' % (n, vm, vl, ' '.join('%s:%.3f:%.1e->%.1e' % e for e in ev) or 'none'))
print(open(os.path.join(H, 'TRI_cal2_summary.dat')).read())
