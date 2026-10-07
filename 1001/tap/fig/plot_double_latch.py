#!/usr/bin/env python3
# Reproduces fig/DOUBLE_LATCH_DD_MM.png panel (a)-(c) directly from the MixedMode transient log.
# Source deck : novel/1001/tap/MM_TAPT_ISL_W30LK_L6_R7_R1e7_UD75S_MF_DD_VGm0p2.in
# Source log  : novel/1001/tap/MM_TAPT_ISL_W30LK_L6_R7_R1e7_UD75S_MF_DD_VGm0p2.log_tr.log
# Log columns (from its 'p' header line: 61 10000 10001 10002 82 1301..1308):
#   0 time | 1 V[1]=drain node | 2 V[2]=gate node | 3 V[3]=tap node | 4 temperature
#   5 I(Vdrain) 6 I(Vgate) 7 I(Rtap) | 8 Adev_drain 9 Adev_source 10 Adev_gate 11 Adev_tap 12 Adev_substrate
import numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt

LOG = '/home/ysseo/novel/1001/tap/MM_TAPT_ISL_W30LK_L6_R7_R1e7_UD75S_MF_DD_VGm0p2.log_tr.log'
rows = [[float(x) for x in l.split()[1:]] for l in open(LOG) if l.startswith('d ')]
M = np.array(rows)
vd, vtap = M[:, 1], M[:, 3]
Id, Is, Itap = M[:, 8], M[:, 9], M[:, 11]
up = np.arange(len(vd)) <= np.argmax(vd)      # rows before the 7.5 V peak = up sweep
dn = ~up

fig, ax = plt.subplots(1, 3, figsize=(17, 5.2), gridspec_kw=dict(width_ratios=[1.3, 1, 1]))
a = ax[0]
a.semilogy(vd[up], np.abs(Id[up]), color='#c0392b', lw=2.4, label='up (0 → 7.5 V)')
a.semilogy(vd[dn], np.abs(Id[dn]), color='#2c7fb8', lw=2.0, ls='--', label='down (7.5 → 0 V)')
a.set_xlim(0, 4); a.set_ylim(1e-14, 1e-3); a.grid(alpha=.3); a.legend(loc='lower right')
a.set_xlabel('Drain voltage Vd (V)'); a.set_ylabel('|Id| (A)'); a.set_title('(a) Id–Vd: two latches with hysteresis')
b = ax[1]
b.semilogy(vd[up], np.abs(Itap[up]), color='#2ca25f', lw=2, label='right STL → island → R (Itap)')
b.semilogy(vd[up], np.abs(Is[up]), color='#8856a7', lw=2, label='left STL → source (|Is|)')
b.semilogy(vd[up], np.abs(Id[up]), 'k:', lw=1, label='total |Id|')
b.set_xlim(0, 4); b.set_ylim(1e-16, 1e-3); b.grid(alpha=.3); b.legend(fontsize=9, loc='lower right')
b.set_xlabel('Vd (V)'); b.set_ylabel('current (A)'); b.set_title('(b) which path conducts (up sweep)')
c = ax[2]
c.plot(vd[up], vtap[up], color='#c0392b', lw=2.2, label='up'); c.plot(vd[dn], vtap[dn], color='#2c7fb8', lw=2, ls='--', label='down')
c.axhline(1.778, color='#8856a7', lw=1, ls='-.')
c.set_xlim(0, 4); c.set_ylim(-0.1, 2.2); c.grid(alpha=.3); c.legend(loc='upper left')
c.set_xlabel('Vd (V)'); c.set_ylabel('island (tap) voltage = Itap·R (V)'); c.set_title('(c) island = drain of the left STL')
fig.suptitle('data: ' + LOG.split('/home/ysseo/')[1], fontsize=9)
fig.tight_layout(); fig.savefig('/home/ysseo/novel/1001/tap/fig/DOUBLE_LATCH_DD_MM_repro.png', dpi=130)
print('rows', len(M), '| up rows', up.sum(), '| peak Vd', vd.max())
