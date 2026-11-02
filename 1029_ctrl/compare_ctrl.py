#!/usr/bin/env python3
"""Compare the divided-body device with the two-device series circuits (1029_ctrl/make_ctrl.py).

Id-Vd : 1010_sink/SINK_TE8_XS60 vs CTRL_CUT_IDVD vs CTRL_SD_IDVD (and NOKILL_TE8_XS60 for the coupled case)
Osc.  : 1028_osc/OSC_{R_1n,L_450n} vs CTRL_CUT_OSC_{R_1n,L_450n}

Column mapping, so that the control circuit reads like the single device:
  Id   (current into the top drain)      = Adev_drain  | Aright_drain
  Is   (current into the bottom source)  = Adev_source | Aleft_source
  Itap (current into the internal node)  = Adev_tap    | Aleft_drain + Aright_source
  Vd = applied drain node V[1], Vtap = V[3]
Latch events use 1007_ddsplit/analyze_ddsplit.events (same criteria as the paper).
Output: ctrl_idvd.png, ctrl_osc.png, ctrl_summary.dat. Missing logs are skipped."""
import os, sys, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
H = os.path.dirname(os.path.abspath(__file__)); R = os.path.join(H, '..')
sys.path.insert(0, os.path.join(R, '1007_ddsplit')); sys.path.insert(0, os.path.join(R, 'tools'))
import analyze_ddsplit as A
from plog import load


def cols(fn):
    """t, Vd, Vtap, Id, Is, Itap for either the single device (Adev) or the two-device circuit (Aright/Aleft)."""
    M, m = load(fn), A.columns(fn)
    c = lambda k: M[:, m[k]]
    if 'Adev_drain' in m:
        Id, Is, It = c('Adev_drain'), c('Adev_source'), c('Adev_tap')
    else:
        Id, Is, It = c('Aright_drain'), c('Aleft_source'), c('Aleft_drain') + c('Aright_source')
    return M[:, 0], c('V[1]'), c('V[3]'), Id, Is, It


def latch_points(fn):
    t, v, vt, Id, Is, It = cols(fn); k = int(np.argmax(v))
    up = A.events(v[:k + 1], Id[:k + 1], Is[:k + 1], It[:k + 1], +1)
    first = lambda ev, side: next((e[0] for e in ev if e[1] in (side, 'both')), np.nan)
    vdn, sdn, tdn = v[k:], np.abs(Is[k:]), np.abs(It[k:])
    on_l = np.where(sdn > 1e-8)[0]; on_r = np.where(tdn > 1e-9)[0]
    off_l = vdn[on_l[-1]] if len(on_l) else np.nan
    off_r = vdn[on_r[-1]] if len(on_r) else np.nan
    return first(up, 'right'), first(up, 'left'), off_r, off_l, len(up)


def osc_metrics(fn, t0=1e-3):
    """Saw-tooth on the drain node: mean V_on (peaks), V_off (troughs), period. Ignores the start-up before t0."""
    t, v = cols(fn)[:2]; s = t > t0; t, v = t[s], v[s]
    dv = np.diff(v); pk = np.where((dv[:-1] > 0) & (dv[1:] <= 0))[0] + 1; tr = np.where((dv[:-1] < 0) & (dv[1:] >= 0))[0] + 1
    span = v.max() - v.min()
    pk = [i for i in pk if v[i] > v.min() + 0.5 * span]; tr = [i for i in tr if v[i] < v.min() + 0.5 * span]
    T = np.mean(np.diff(t[pk])) if len(pk) > 1 else np.nan
    return (np.mean(v[pk]) if pk else np.nan), (np.mean(v[tr]) if tr else np.nan), T, len(pk)


IDVD = [(os.path.join(R, '1010_sink', 'SINK_TE8_XS60'), 'single device (metal-core sink)', 'k', '-'),
        (os.path.join(H, 'CTRL_CUT_IDVD'), 'two devices: cut through core', 'tab:blue', '-'),
        (os.path.join(H, 'CTRL_SD_IDVD'), 'two devices: n$^+$ S/D + top contact', 'tab:green', '-'),
        (os.path.join(R, '1010_sink', 'NOKILL_TE8_XS60'), 'single device, island not killed', 'tab:red', ':')]
OSC = [('OSC_R_1n', 'right loop, 1 nA, 1 pF'), ('OSC_L_450n', 'left loop, 450 nA, 0.225 nF')]

rows = []
fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
for base, lab, col, ls in IDVD:
    fn = base + '.log_tr.log'
    if not os.path.exists(fn): print('missing', os.path.relpath(fn, R)); continue
    t, v, vt, Id, Is, It = cols(fn); k = int(np.argmax(v))
    ax[0].semilogy(v[:k + 1], np.abs(Id[:k + 1]), color=col, ls=ls, lw=1.2, label=lab)
    ax[0].semilogy(v[k:], np.abs(Id[k:]), color=col, ls='--' if ls == '-' else ls, lw=0.7)
    ax[1].plot(v[:k + 1], vt[:k + 1], color=col, ls=ls, lw=1.2); ax[1].plot(v[k:], vt[k:], color=col, ls='--' if ls == '-' else ls, lw=0.7)
    rows.append(('IDVD', os.path.basename(base)) + latch_points(fn))
ax[0].set(xlim=(0, 6), ylim=(1e-14, 1e-2), xlabel='$V_D$ (V)', ylabel='$|I_D|$ (A)'); ax[0].legend(fontsize=7, loc='lower right')
ax[1].set(xlim=(0, 6), xlabel='$V_D$ (V)', ylabel='internal node $V_{tap}$ (V)')
for a in ax: a.grid(alpha=.3)
fig.tight_layout(); fig.savefig(os.path.join(H, 'ctrl_idvd.png'), dpi=140)

fig, ax = plt.subplots(1, 2, figsize=(10, 3.4))
for a, (o, title) in zip(ax, OSC):
    for fn, lab, col in [(os.path.join(R, '1028_osc', o + '.log_tr.log'), 'single device', 'k'),
                         (os.path.join(H, 'CTRL_CUT_' + o + '.log_tr.log'), 'two devices (cut)', 'tab:blue')]:
        if not os.path.exists(fn): print('missing', os.path.relpath(fn, R)); continue
        t, v = cols(fn)[:2]; a.plot(t * 1e3, v, color=col, lw=0.9, label=lab)
        rows.append(('OSC', os.path.basename(fn).replace('.log_tr.log', '')) + osc_metrics(fn))
    a.set(xlabel='t (ms)', ylabel='$V_D$ (V)', title=title); a.grid(alpha=.3); a.legend(fontsize=7)
fig.tight_layout(); fig.savefig(os.path.join(H, 'ctrl_osc.png'), dpi=140)

with open(os.path.join(H, 'ctrl_summary.dat'), 'w') as f:
    f.write('# IDVD: name  V_on_right  V_on_left  V_off_right  V_off_left  n_up_events\n')
    f.write('# OSC : name  V_on(mean peak)  V_off(mean trough)  period(s)  n_peaks\n')
    for r in rows:
        f.write(r[0] + '  %-26s ' % r[1] + ' '.join('%.4g' % x for x in r[2:]) + '\n')
print(open(os.path.join(H, 'ctrl_summary.dat')).read())
