#!/usr/bin/env python3
"""Triristor calibration: compare simulated Id-Vd / Id-Vg with the measured values of Noh et al. (EDL 2025).
Inputs: devonly_1010/TRI_*.log (device-only runs), TRI_*.log_tr.log (MixedMode runs), calib_targets.dat.
Output: TRI_calib_compare.png, TRI_calib_summary.dat"""
import os, re, sys, glob, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(H, '..', 'tools'))
from plog import load

def dev(fn):
    names, probes, codes = [], {}, None
    for l in open(fn):
        if l.startswith('f '): names = re.findall(r'"([^"]+)"', l)
        elif l.startswith('o '): p = l.split(); probes[3000 + int(p[1]) - 1] = p[2]
        elif l.startswith('p '): codes = [int(c) for c in l.split()[2:]]
        elif l.startswith('d '): break
    d = load(fn); out = {}
    for i, c in enumerate(codes):
        if c == 61: out['t'] = d[:, i]
        elif 601 <= c <= 600 + len(names): out['V:' + names[c - 601]] = d[:, i]
        elif 20 <= c <= 19 + len(names): out['I:' + names[c - 20]] = d[:, i]
        elif c in probes: out[probes[c]] = d[:, i]
    return out

def latches(v, i, k):
    """Up/down jumps: >1 decade change within 0.1 V (consecutive points merged)."""
    lg = np.log10(np.abs(i) + 1e-30); ev = []
    for seg, s in ((range(1, k + 1), 'up'), (range(k + 1, len(v)), 'down')):
        j0 = None
        for j in seg:
            if abs(lg[j] - lg[j - 1]) > 0.3 and abs(v[j] - v[j - 1]) < 0.02:
                j0 = j - 1 if j0 is None else j0
            elif j0 is not None:
                if abs(lg[j - 1] - lg[j0]) > 1: ev.append((s, v[j0], i[j0], i[j - 1]))
                j0 = None
    return ev

T = [l.split() for l in open(os.path.join(H, 'calib_targets.dat')) if l.strip() and not l.startswith('#')][0]
meas = dict(zip('VG VLU1 ILU1 VLD1 ILD1 VLU2 ILU2 VLD2 ILD2'.split(), map(float, T)))
fig, ax = plt.subplots(1, 2, figsize=(10, 3.8)); rows = []
for fn, c in zip(sorted(glob.glob(os.path.join(H, 'devonly_1010', 'TRI_DEF_*.log'))), 'rbgmc'):
    name = os.path.basename(fn)[:-4]; d = dev(fn); v, i = d['V:drain'], np.abs(d['I:drain']); k = int(np.argmax(v))
    ax[0].semilogy(v[:k + 1], i[:k + 1], c, label=name + ' up'); ax[0].semilogy(v[k:], i[k:], c + '--', lw=.8)
    ev = latches(v, i, k); rows.append((name, v[k], v[-1], ev))
for key, (x, y) in (('VLU1', (meas['VLU1'], meas['ILU1'])), ('VLD1', (meas['VLD1'], meas['ILD1'])), ('VLU2', (meas['VLU2'], meas['ILU2'])), ('VLD2', (meas['VLD2'], meas['ILD2']))):
    ax[0].plot(x, y, 'ko', ms=4); ax[0].annotate(key, (x, y), fontsize=7)
ax[0].set_ylim(1e-9, 1e-1); ax[0].set_xlabel('$V_D$ (V)'); ax[0].set_ylabel('$|I_D|$ (A)'); ax[0].grid(alpha=.3); ax[0].legend(fontsize=6)
ax[0].set_title('Id-Vd: default model vs measured (black, V_G 0.4 V)', fontsize=8)
for fn, c, lab in ((os.path.join(H, 'devonly_1010', 'TRI_IDVG_vd0p05_up.log'), 'g', 'sim V_D 0.05'), (os.path.join(H, 'devonly_1010', 'TRI_IDVG_vd1_up.log'), 'k', 'sim V_D 1')):
    if os.path.exists(fn): d = dev(fn); ax[1].semilogy(d['V:gate'], np.abs(d['I:drain']), c, label=lab)
# measured Id-Vg read from Noh Fig. 1(d) (+-0.3 decade)
ax[1].semilogy([-2, 0, 0.5, 1, 2, 4], [8e-11, 3e-10, 3e-5, 1e-4, 2.5e-4, 3.5e-4], 'gs', ms=4, label='meas 0.05 (read)')
ax[1].semilogy([-2, 0, 0.5, 1, 2, 4], [3.5e-10, 5e-10, 2e-4, 1.5e-3, 5e-3, 7e-3], 'ks', ms=4, label='meas 1 (read)')
ax[1].set_xlabel('$V_G$ (V)'); ax[1].grid(alpha=.3); ax[1].legend(fontsize=6); ax[1].set_title('Id-Vg', fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(H, 'TRI_calib_compare.png'), dpi=130)
with open(os.path.join(H, 'TRI_calib_summary.dat'), 'w') as f:
    f.write('# name Vmax V_last events(dir:V:I_before->I_after)  | measured VG0.4: VLU1 %.2f VLD1 %.2f VLU2 %.2f VLD2 %.2f\n' % (meas['VLU1'], meas['VLD1'], meas['VLU2'], meas['VLD2']))
    for n, vm, vl, ev in rows:
        f.write('%s %.2f %.2f %s\n' % (n, vm, vl, ' '.join('%s:%.3f:%.1e->%.1e' % e for e in ev) or 'none'))
print(open(os.path.join(H, 'TRI_calib_summary.dat')).read())
